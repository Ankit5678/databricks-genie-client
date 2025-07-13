import time
import requests
from typing import Optional
from ..config import AzureADGenieClientConfig, PATGenieClientConfig
from ..exceptions.custom_errors import TokenRefreshError

class TokenManager:
    """Manages authentication tokens for Databricks API"""
    
    def __init__(self, config):
        self.config = config
        self.access_token: Optional[str] = None
        self.token_expiry: float = 0.0
        
    def get_access_token(self) -> str:
        """Returns valid access token based on configuration type"""
        if isinstance(self.config, PATGenieClientConfig):
            return self.config.personal_access_token
            
        if isinstance(self.config, AzureADGenieClientConfig):
            if self._token_is_valid():
                return self.access_token
            return self._refresh_azure_token()
            
        raise TokenRefreshError("Invalid configuration type")
    
    def _refresh_azure_token(self) -> str:
        """Acquires Azure AD token using client credentials flow"""
        config = self.config  # Type: AzureADGenieClientConfig
        token_url = f"https://login.microsoftonline.com/{config.tenant_id}/oauth2/v2.0/token"
        
        try:
            payload = {
                "client_id": config.client_id,
                "client_secret": config.client_secret,
                "scope": "2ff814a6-3304-4ab8-85cb-cd0e6f879c1d/.default",
                "grant_type": "client_credentials"
            }
            
            response = requests.post(token_url, data=payload, timeout=10)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data["access_token"]
            self.token_expiry = time.time() + token_data["expires_in"]
            
            return self.access_token
            
        except requests.exceptions.RequestException as e:
            raise TokenRefreshError(f"Azure token refresh failed: {str(e)}")
        except KeyError:
            raise TokenRefreshError("Invalid Azure token response format")
    
    def _token_is_valid(self) -> bool:
        """Checks if Azure AD token exists and hasn't expired"""
        if not self.access_token:
            return False
        return time.time() < (self.token_expiry - 300)  # 5-minute buffer