import requests
from typing import Any, Dict, Optional
from ..utils.constants import GenieEndpoints, ModelServingEndpoints
from ..utils.retry import retry_api_call
from ..exceptions.custom_errors import APIRequestError, RateLimitError
from .auth import TokenManager
from ..utils.logging import logger

class GenieAPIClient:
    """Low-level client for Genie REST API operations"""
    
    def __init__(self, base_url: str, token_manager: TokenManager):
        self.base_url = str(base_url).rstrip('/')
        self.token_manager = token_manager
        self.session = requests.Session()
        logger.debug("API client initialized")
        
    def _build_url(self, endpoint: str) -> str:
        """Constructs full URL from endpoint template"""
        return f"{self.base_url}{endpoint}"


    @retry_api_call
    def _make_request(self, method: str, endpoint: str, payload: Optional[Dict] = None, 
                    path_params: Optional[Dict] = None, 
                    query_params: Optional[Dict] = None) -> Dict[str, Any]:
        """Executes API request with retry logic and parameters"""
        url = self._build_url(endpoint)
        if path_params:
            url = url.format(**path_params)
        
        headers = {
            "Authorization": f"Bearer {self.token_manager.get_access_token()}",
            "Content-Type": "application/json"
        }
        
        try:
            logger.debug(f"Making {method} request to {url}")
            response = self.session.request(
                method,
                url,
                headers=headers,
                params=query_params,  # Add query parameters
                json=payload,
                timeout=30
            )

            if response.status_code == 429:
                raise RateLimitError(
                    "Rate limit exceeded",
                    status_code=429,
                    response_body=response.text
                )
                
            if response.status_code >= 400:
                self._handle_error_response(response, endpoint)
                
            return response.json()
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error: {str(e)}")
            raise APIRequestError(
                f"Network error: {str(e)}",
                status_code=0,
                response_body=str(e)
            ) from e

    def _handle_error_response(self, response: requests.Response, endpoint: str):
        """Processes API error responses"""
        try:
            error_data = response.json()
            error_msg = error_data.get("error", {}).get("message", response.text)
        except ValueError:
            error_msg = response.text
            
        context = {
            "endpoint": endpoint,
            "status_code": response.status_code,
            "response_body": response.text[:500]  # Truncate long responses
        }
        
        if response.status_code == 401:
            from ..exceptions.custom_errors import AuthenticationError
            raise AuthenticationError(
                "Authentication failed",
                context=context
            )
            
        raise APIRequestError(
            f"API request failed: {error_msg}",
            status_code=response.status_code,
            response_body=response.text,
            context=context
        )
    
    def start_conversation(self, space_id: str, question: str) -> Dict[str, Any]:
        """Starts a new Genie conversation"""
        return self._make_request(
            "POST",
            GenieEndpoints.START_CONVERSATION,
            payload={"content": question},
            path_params={"space_id": space_id}
        )
    
    def send_message(self, space_id: str, conversation_id: str, question: str) -> Dict[str, Any]:
        """Sends message to existing conversation"""
        return self._make_request(
            "POST",
            GenieEndpoints.SEND_MESSAGE,
            payload={"content": question},
            path_params={
                "space_id": space_id,
                "conversation_id": conversation_id
            }
        )
    
    def get_message(self, space_id: str, conversation_id: str, message_id: str) -> Dict[str, Any]:
        """Retrieves message status and content"""
        return self._make_request(
            "GET",
            GenieEndpoints.GET_MESSAGE,
            path_params={
                "space_id": space_id,
                "conversation_id": conversation_id,
                "message_id": message_id
            }
        )
    
    # def get_query_result(self, space_id: str, conversation_id: str, 
    #                     message_id: str, attachment_id: str) -> Dict[str, Any]:
    #     """Fetches query execution results"""
    #     return self._make_request(
    #         "GET",
    #         GenieEndpoints.GET_QUERY_RESULT,
    #         path_params={
    #             "space_id": space_id,
    #             "conversation_id": conversation_id,
    #             "message_id": message_id,
    #             "attachment_id": attachment_id
    #         }
    #     )

    def get_query_result(self, space_id: str, conversation_id: str, 
                    message_id: str, attachment_id: str, 
                    chunk_index: Optional[int] = None) -> Dict[str, Any]:
        """Fetches query execution results with chunk support"""
        endpoint = GenieEndpoints.GET_QUERY_RESULT
        path_params = {
            "space_id": space_id,
            "conversation_id": conversation_id,
            "message_id": message_id,
            "attachment_id": attachment_id
        }
        
        # Add chunk_index parameter if provided
        query_params = {}
        if chunk_index is not None:
            query_params["chunk_index"] = chunk_index
        
        return self._make_request(
            "GET",
            endpoint,
            path_params=path_params,
            query_params=query_params or None
        )
    
    def generate_natural_language(self, endpoint_name: str, payload: dict) -> str:
        """Generates natural language response from model endpoint"""

        endpoint = ModelServingEndpoints.MODEL_ENDPOINT_BASE.format(endpoint_name=endpoint_name)

        # Get access token
        # token = self.token_manager.get_access_token()

        response = self._make_request(
            "POST",
            endpoint,
            payload=payload,
            # headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
        )
        
        # Handle different response formats
        if "choices" in response:
            # OpenAI-compatible format
            return response["choices"][0]["message"]["content"]
        elif "predictions" in response:
            # Standard serving endpoint format
            return response["predictions"][0]
        elif "candidates" in response:
            # PaLM/other format
            return response["candidates"][0]["text"]
        else:
            raise ValueError("Unexpected response format from model endpoint")