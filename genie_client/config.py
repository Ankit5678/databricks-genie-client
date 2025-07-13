from pydantic import AnyHttpUrl, BaseModel, Field
from typing import Optional

class BaseGenieClientConfig(BaseModel):
    """Base configuration with common fields"""
    databricks_url: AnyHttpUrl = Field(..., description="Databricks workspace URL")
    workspace_id: str = Field(..., min_length=1, description="Databricks workspace ID")
    default_space_id: Optional[str] = Field(None, description="Default Genie space ID")
    poll_interval: int = Field(5, description="Polling interval in seconds")
    poll_timeout: int = Field(600, description="Polling timeout in seconds")

class AzureADGenieClientConfig(BaseGenieClientConfig):
    """Configuration for Azure AD authentication"""
    client_id: str = Field(..., min_length=1, description="Azure AD Client ID")
    client_secret: str = Field(..., min_length=1, description="Azure AD Client Secret")
    tenant_id: str = Field(..., min_length=1, description="Azure AD Tenant ID")
    
    class Config:
        schema_extra = {
            "example": {
                "client_id": "your-client-id",
                "client_secret": "your-client-secret",
                "tenant_id": "your-tenant-id",
                "databricks_url": "https://your-workspace.cloud.databricks.com",
                "workspace_id": "1234567890"
            }
        }

class PATGenieClientConfig(BaseGenieClientConfig):
    """Configuration for Personal Access Token authentication"""
    personal_access_token: str = Field(..., min_length=1, description="Databricks Personal Access Token")
    
    class Config:
        schema_extra = {
            "example": {
                "personal_access_token": "dapi1234567890abcdef1234567890abcdef",
                "databricks_url": "https://your-workspace.cloud.databricks.com",
                "workspace_id": "1234567890"
            }
        }