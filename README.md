# Databricks Genie Client

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-0.1.0-green.svg)](https://github.com/your-repo/databricks-genie-client)

An enterprise-grade Python client for seamless interaction with Databricks Genie API. This client provides a robust, production-ready interface for natural language querying of your Databricks data assets.

## Features

- **Multiple Authentication Methods**: Support for Azure AD and Personal Access Token authentication
- **Conversation Management**: Handle both single queries and multi-turn conversations
- **Robust Error Handling**: Comprehensive exception handling with detailed error context
- **Automatic Polling**: Built-in status polling with configurable timeouts and intervals
- **Result Processing**: Automatic handling of chunked query results and attachments
- **Enterprise Ready**: Production-grade logging, metrics, and validation
- **Type Safety**: Full Pydantic model validation for all configurations and responses

## Installation

```bash
pip install databricks-genie-client
```

### Development Installation

```bash
git clone https://github.com/your-repo/databricks-genie-client.git
cd databricks-genie-client
pip install -e .
```

## Quick Start

### Azure AD Authentication

```python
from genie_client import GenieClient
from genie_client.config import AzureADGenieClientConfig

# Configure client with Azure AD
config = AzureADGenieClientConfig(
    client_id="your-client-id",
    client_secret="your-client-secret", 
    tenant_id="your-tenant-id",
    databricks_url="https://your-workspace.cloud.databricks.com",
    workspace_id="1234567890",
    default_space_id="your-genie-space-id"
)

client = GenieClient(config)

# Ask a question
response = client.ask_genie("Show top 5 customers by revenue")

if response.success:
    print(f"Query completed in {response.duration_ms:.2f}ms")
    if response.results:
        print(f"Retrieved {response.results['row_count']} rows")
        for row in response.results["data"][:5]:
            print(row)
```

### Personal Access Token Authentication

```python
from genie_client.config import PATGenieClientConfig

config = PATGenieClientConfig(
    personal_access_token="dapi1234567890abcdef1234567890abcdef",
    databricks_url="https://your-workspace.cloud.databricks.com",
    workspace_id="1234567890"
)

client = GenieClient(config)
response = client.ask_genie("What are our monthly sales trends?")
```

## Advanced Usage

### Multi-turn Conversations

```python
# Initial question
response = client.ask_genie("Show customer revenue by region")

if response.success:
    # Follow-up question in same conversation
    follow_up = client.ask_genie(
        question="Now filter for only Q4 2024",
        follow_up=True,
        conversation_id=response.conversation_id
    )
```

### Custom Configuration

```python
config = AzureADGenieClientConfig(
    client_id="your-client-id",
    client_secret="your-client-secret",
    tenant_id="your-tenant-id", 
    databricks_url="https://your-workspace.cloud.databricks.com",
    workspace_id="1234567890",
    poll_interval=3,  # Poll every 3 seconds
    poll_timeout=300  # Timeout after 5 minutes
)
```

### Error Handling

```python
try:
    response = client.ask_genie("Complex analytical query")
    
    if not response.success:
        print(f"Query failed: {response.error_type}")
        print(f"Error details: {response.error_message}")
        
except Exception as e:
    print(f"Client error: {str(e)}")
```

## Configuration Options

### Common Configuration

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `databricks_url` | str | Yes | Databricks workspace URL |
| `workspace_id` | str | Yes | Databricks workspace ID |
| `default_space_id` | str | No | Default Genie space ID |
| `poll_interval` | int | No | Polling interval in seconds (default: 5) |
| `poll_timeout` | int | No | Polling timeout in seconds (default: 600) |

### Azure AD Configuration

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `client_id` | str | Yes | Azure AD application client ID |
| `client_secret` | str | Yes | Azure AD application client secret |
| `tenant_id` | str | Yes | Azure AD tenant ID |

### Personal Access Token Configuration

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `personal_access_token` | str | Yes | Databricks personal access token |

## Response Structure

The `GenieResponse` object provides comprehensive information about your query:

```python
response = client.ask_genie("Your query")

# Core response data
print(response.success)           # bool: Operation success status
print(response.status)            # str: Current status (COMPLETED, FAILED, etc.)
print(response.conversation_id)   # str: Conversation identifier
print(response.message_id)        # str: Message identifier

# Results (when available)
if response.results:
    print(response.results["data"])        # List: Query result rows
    print(response.results["columns"])     # List: Column names
    print(response.results["row_count"])   # int: Total row count

# Timing and metrics
print(response.duration_ms)       # float: Total operation time
print(response.start_time)        # datetime: Operation start
print(response.end_time)          # datetime: Operation end

# Error information (when applicable)
print(response.error_type)        # str: Error classification
print(response.error_message)     # str: Detailed error message
```

## Status Values

The client handles various query statuses automatically:

- `INITIATED`: Query has been submitted
- `IN_PROGRESS`: Query is being processed
- `EXECUTING_QUERY`: SQL query is running
- `COMPLETED`: Query completed successfully
- `FAILED`: Query failed with error
- `CANCELLED`: Query was cancelled

## Error Types

The client provides specific error types for different failure scenarios:

- `ValidationError`: Input validation failures
- `AuthenticationError`: Authentication issues
- `APIRequestError`: API communication errors
- `TimeoutError`: Operation timeout
- `ResultRetrievalError`: Issues fetching query results

## Requirements

- Python 3.8+
- `requests >= 2.28.1`
- `pydantic >= 1.10.2`

## Development

### Running Tests

```bash
pip install -e ".[dev]"
pytest tests/
```

### Project Structure

```
genie_client/
├── core/           # Core client functionality
├── config.py       # Configuration models
├── models/         # Response and data models
├── exceptions/     # Custom exception classes
└── utils/          # Utility functions and constants
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues and questions:

1. Check the [documentation](https://github.com/your-repo/databricks-genie-client/wiki)
2. Search [existing issues](https://github.com/your-repo/databricks-genie-client/issues)
3. Create a [new issue](https://github.com/your-repo/databricks-genie-client/issues/new)

## Changelog

### v0.1.0
- Initial release
- Azure AD and PAT authentication support
- Conversation management
- Automatic result polling and processing
- Comprehensive error handling and logging