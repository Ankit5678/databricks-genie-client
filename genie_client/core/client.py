import time
from datetime import datetime
from typing import Optional
from ..config import AzureADGenieClientConfig, PATGenieClientConfig
from ..models.response_models import GenieResponse, Attachment
from ..exceptions.custom_errors import *
from ..utils.validation import validate_input
from .api_client import GenieAPIClient
from .auth import TokenManager
from ..utils.constants import Status, TERMINAL_STATUSES, POLLABLE_STATUSES, POLL_TIMEOUT
from ..utils.logging import logger

class GenieClient:
    """High-level client for interacting with Databricks Genie"""
    
    def __init__(self, config: AzureADGenieClientConfig | PATGenieClientConfig):
        """
        Initialize the Genie client with configuration
        
        Args:
            config: AzureADGenieClientConfig or PATGenieClientConfig
        """
        self.config = config
        self.token_manager = TokenManager(config)
        self.api_client = GenieAPIClient(
            base_url=config.databricks_url,
            token_manager=self.token_manager
        )
        logger.info("Genie client initialized")
        
    def ask_genie(
        self,
        question: str,
        space_id: Optional[str] = None,
        follow_up: bool = False,
        conversation_id: Optional[str] = None
    ) -> GenieResponse:
        """
        Main method to interact with Genie API
        
        Args:
            question: Natural language query
            space_id: Target Genie space ID (uses default if not provided)
            follow_up: Whether this is a follow-up question
            conversation_id: Existing conversation ID for follow-ups
            
        Returns:
            GenieResponse object with full results and metadata
        """
        start_time = datetime.now()
        response = GenieResponse(
            start_time=start_time,
            status="INITIATED",
            success=False
        )
        
        try:
            # Validate and resolve inputs
            space_id = space_id or self.config.default_space_id
            validate_input(question, space_id, follow_up, conversation_id or "")
            
            # Create or continue conversation
            if follow_up and conversation_id:
                logger.info(f"Continuing conversation: {conversation_id}")
                response.conversation_id = conversation_id
                message = self._send_message(space_id, conversation_id, question)
            else:
                logger.info("Starting new conversation")
                conversation, message = self._start_conversation(space_id, question)
                response.conversation_id = conversation["id"]
            
            response.message_id = message["id"]
            response.status = message["status"]
            
            # Poll for completion with timeout handling
            response = self._poll_message_status(space_id, response)
            
            # Process results if completed
            if response.status == Status.COMPLETED:
                response = self._process_attachments(space_id, response)
            
            response.success = True
            logger.info("Operation completed successfully")
            
        except GenieBaseError as e:
            logger.error(f"Genie operation failed: {str(e)}", exc_info=True)
            response.error_message = str(e)
            response.error_type = type(e).__name__
            if hasattr(e, "context"):
                response.metrics["error_context"] = e.context
        finally:
            response.finalize()
            self._log_metrics(response)
            return response
            
    def _start_conversation(self, space_id: str, question: str) -> tuple:
        """Initiates a new Genie conversation"""
        try:
            result = self.api_client.start_conversation(space_id, question)
            return result["conversation"], result["message"]
        except APIRequestError as e:
            context = {"space_id": space_id, "question": question[:100]}
            raise APIRequestError(
                "Failed to start conversation",
                status_code=e.status_code,
                response_body=e.response_body,
                context=context
            ) from e
    
    def _send_message(self, space_id: str, conversation_id: str, question: str) -> dict:
        """Sends message to existing conversation"""
        try:
            result = self.api_client.send_message(space_id, conversation_id, question)
            return result
        except APIRequestError as e:
            context = {
                "space_id": space_id,
                "conversation_id": conversation_id,
                "question": question[:100]
            }
            raise APIRequestError(
                "Failed to send message",
                status_code=e.status_code,
                response_body=e.response_body,
                context=context
            ) from e
            
    def _poll_message_status(self, space_id: str, response: GenieResponse) -> GenieResponse:
        """Polls message status until terminal state or timeout"""
        start_time = time.time()
        
        while response.status in POLLABLE_STATUSES:
            # Handle timeout
            elapsed = time.time() - start_time
            if elapsed > POLL_TIMEOUT:
                context = {
                    "conversation_id": response.conversation_id,
                    "message_id": response.message_id,
                    "elapsed_seconds": elapsed
                }
                raise TimeoutError(
                    "Polling timeout reached after 10 minutes",
                    context=context
                )
                
            # Wait before next poll
            time.sleep(self.config.poll_interval)
            
            try:
                message = self.api_client.get_message(
                    space_id,
                    response.conversation_id,
                    response.message_id
                )
                response.status = message["status"]
                
                # Update attachments
                if "attachments" in message:
                    response.attachments = [
                        Attachment(
                            type=self._determine_attachment_type(att),
                            content=att,
                            attachment_id=att.get("attachment_id")
                        ) for att in message["attachments"]
                    ]
                
                # Handle terminal states
                if response.status in TERMINAL_STATUSES:
                    logger.info(f"Message reached terminal state: {response.status}")
                    if response.status != Status.COMPLETED and "error" in message:
                        response.error_message = message["error"].get("message")
                        response.error_type = message["error"].get("type")
                    break
                    
            except APIRequestError as e:
                logger.warning(f"Polling error: {str(e)}. Retrying...")
                # Continue polling on recoverable errors
                if e.status_code < 500:
                    raise
        
        return response
    
    def _determine_attachment_type(self, attachment: dict) -> str:
        """Identifies attachment type based on content"""
        if "query" in attachment:
            return "query"
        elif "text" in attachment:
            return "text"
        elif "error" in attachment:
            return "error"
        return "unknown"
    
    # def _process_attachments(self, space_id: str, response: GenieResponse) -> GenieResponse:
    #     """Processes attachments and fetches query results"""
    #     for attachment in response.attachments:
    #         if attachment.type == "query" and attachment.attachment_id:
    #             try:
    #                 result = self.api_client.get_query_result(
    #                     space_id,
    #                     response.conversation_id,
    #                     response.message_id,
    #                     attachment.attachment_id
    #                 )
    #                 print(result)
    #                 # Store results in response
    #                 if "result" in result:
    #                     response.results = {
    #                         "data": result["result"].get("data_array"),
    #                         "columns": result["result"].get("metadata", {}).get("column_names"),
    #                         "row_count": result["result"].get("metadata", {}).get("row_count")
    #                     }
    #                     # Add metrics
    #                     response.metrics["result_row_count"] = result["result"].get("metadata", {}).get("row_count", 0)
    #             except APIRequestError as e:
    #                 logger.error(f"Failed to fetch results: {str(e)}")
    #                 response.error_message = f"Result fetch failed: {str(e)}"
    #                 response.error_type = "RESULT_RETRIEVAL_ERROR"
    #     return response

    def _process_attachments(self, space_id: str, response: GenieResponse) -> GenieResponse:
        """Processes attachments and fetches query results with chunk handling"""
        for attachment in response.attachments:
            if attachment.type == "query" and attachment.attachment_id:
                try:
                    result_data = self.api_client.get_query_result(
                        space_id,
                        response.conversation_id,
                        response.message_id,
                        attachment.attachment_id
                    )
                    
                    # Extract the statement response
                    stmt_response = result_data.get("statement_response", {})
                    
                    # Check execution status
                    status = stmt_response.get("status", {}).get("state", "")
                    if status != "SUCCEEDED":
                        raise ResultRetrievalError(
                            f"Query execution failed with status: {status}",
                            status_code=400,
                            response_body=result_data
                        )
                    
                    # Extract manifest and result data
                    manifest = stmt_response.get("manifest", {})
                    result_chunk = stmt_response.get("result", {})
                    
                    # Process schema
                    schema = manifest.get("schema", {})
                    columns = [col["name"] for col in schema.get("columns", [])]
                    
                    # Handle chunked results
                    total_chunks = manifest.get("total_chunk_count", 1)
                    total_rows = manifest.get("total_row_count", 0)
                    
                    if total_chunks == 1:
                        # Single chunk - simple case
                        data_array = result_chunk.get("data_array", [])
                    else:
                        # Multiple chunks - fetch all chunks
                        data_array = []
                        logger.info(f"Fetching {total_chunks} result chunks...")
                        
                        # Fetch first chunk (already retrieved)
                        if result_chunk.get("chunk_index", 0) == 0:
                            data_array.extend(result_chunk.get("data_array", []))
                        
                        # Fetch remaining chunks
                        for chunk_index in range(1, total_chunks):
                            chunk_data = self.api_client.get_query_result(
                                space_id,
                                response.conversation_id,
                                response.message_id,
                                attachment.attachment_id,
                                chunk_index=chunk_index  # New parameter needed in API client
                            )
                            chunk_result = chunk_data.get("statement_response", {}).get("result", {})
                            data_array.extend(chunk_result.get("data_array", []))
                    
                    # Store results in response
                    response.results = {
                        "data": data_array,
                        "columns": columns,
                        "row_count": total_rows,
                        "chunk_count": total_chunks
                    }
                    # Add metrics
                    response.metrics["result_row_count"] = total_rows
                    response.metrics["result_chunk_count"] = total_chunks
                    
                except APIRequestError as e:
                    logger.error(f"Failed to fetch results: {str(e)}")
                    response.error_message = f"Result fetch failed: {str(e)}"
                    response.error_type = "RESULT_RETRIEVAL_ERROR"
        return response
    
    def _log_metrics(self, response: GenieResponse):
        """Logs operation metrics"""
        metrics = {
            "success": response.success,
            "status": response.status,
            "duration_ms": response.duration_ms,
            "attachments_count": len(response.attachments),
            "error_type": response.error_type or "NONE"
        }
        if response.results:
            metrics["result_row_count"] = response.results.get("row_count", 0)
        
        logger.info("Operation metrics", extra={"metrics": metrics})
        response.metrics.update(metrics)