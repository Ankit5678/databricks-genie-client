import pytest
from unittest.mock import patch, MagicMock
from genie_client.core.client import GenieClient
from genie_client.config import GenieClientConfig
from genie_client.exceptions.custom_errors import APIRequestError, RateLimitError, InvalidInputError
from genie_client.utils.constants import Status

@pytest.fixture
def mock_config():
    return GenieClientConfig(
        client_id="test",
        client_secret="test",
        tenant_id="test",
        databricks_url="https://test.databricks.com",
        workspace_id="test"
    )

@patch("genie_client.core.api_client.GenieAPIClient.start_conversation")
def test_successful_query(mock_start, mock_config):
    # Mock API responses
    mock_start.return_value = {
        "conversation": {"id": "conv1"},
        "message": {"id": "msg1", "status": Status.IN_PROGRESS}
    }
    
    # Additional mocks would go here for polling and results
    
    client = GenieClient(mock_config)
    response = client.ask_genie("Test question", "space1")
    
    assert response.success is True
    assert response.status == Status.COMPLETED
    assert response.conversation_id == "conv1"
    assert response.message_id == "msg1"

@patch("genie_client.core.api_client.GenieAPIClient.start_conversation")
def test_rate_limit_handling(mock_start, mock_config):
    mock_start.side_effect = RateLimitError(
        "Rate limited",
        status_code=429,
        response_body="",
        context={}
    )
    
    client = GenieClient(mock_config)
    response = client.ask_genie("Test question", "space1")
    
    assert response.success is False
    assert response.error_type == "RateLimitError"
    assert "Rate limited" in response.error_message

def test_input_validation(mock_config):
    client = GenieClient(mock_config)
    
    with pytest.raises(InvalidInputError):
        client.ask_genie("", "space1")
    
    with pytest.raises(InvalidInputError):
        client.ask_genie("Valid", "", follow_up=True, conversation_id="")