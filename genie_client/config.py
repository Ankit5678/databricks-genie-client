from pydantic import AnyHttpUrl, BaseModel, Field, model_validator, field_validator, ValidationInfo
from typing import Optional, Union
from .utils.prompts import DEFAULT_SYSTEM_PROMPT, DEFAULT_USER_PROMPT

class BaseGenieClientConfig(BaseModel):
    """Base configuration with common fields"""
    databricks_url: AnyHttpUrl = Field(..., description="Databricks workspace URL")
    workspace_id: str = Field(..., min_length=1, description="Databricks workspace ID")
    default_space_id: Optional[str] = Field(None, description="Default Genie space ID")
    poll_interval: int = Field(5, description="Polling interval in seconds")
    poll_timeout: int = Field(600, description="Polling timeout in seconds")
    enable_natural_language: bool = Field(False, description="Enable NL answer generation")
    model_endpoint_name: Optional[str] = Field(None, description="Model serving endpoint name")
    system_prompt_template: Optional[str] = Field(None, description="System prompt template")
    user_prompt_template: Optional[str] = Field(None, description="User prompt template")

    # Pydantic V2 field validator (runs before other validators)
    @field_validator('databricks_url', mode='before')
    @classmethod
    def convert_url_to_string(cls, v):
        """Convert AnyHttpUrl to string before validation"""
        return str(v) if hasattr(v, '__str__') else v
    
    # Pydantic V2 model validator (runs after field validation)
    @model_validator(mode='after')
    def validate_natural_language_settings(self):
        """Validate NL generation settings when enabled"""
        if self.enable_natural_language:
            # Validate model endpoint
            if not self.model_endpoint_name:
                raise ValueError("Model endpoint name is required when NL generation is enabled")
            
            # Validate user prompt template
            if self.user_prompt_template:
                required_placeholders = {'{formatted_query_results}', '{question}'}
                missing = required_placeholders - set(self.user_prompt_template.split())
                if missing:
                    raise ValueError(
                        f"User prompt template missing required placeholders: {', '.join(missing)}"
                    )
            else:
                # Use default template
                self.user_prompt_template = DEFAULT_USER_PROMPT
                
            # Set default system prompt if not provided
            if not self.system_prompt_template:
                self.system_prompt_template = DEFAULT_SYSTEM_PROMPT
                
        return self

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