class GenieEndpoints:
    """Centralized API endpoint templates"""
    START_CONVERSATION = "/api/2.0/genie/spaces/{space_id}/start-conversation"
    SEND_MESSAGE = "/api/2.0/genie/spaces/{space_id}/conversations/{conversation_id}/messages"
    GET_MESSAGE = "/api/2.0/genie/spaces/{space_id}/conversations/{conversation_id}/messages/{message_id}"
    GET_QUERY_RESULT = "/api/2.0/genie/spaces/{space_id}/conversations/{conversation_id}/messages/{message_id}/query-result/{attachment_id}"

class Status:
    """Status constants for Genie operations"""
    INITIATED = "INITIATED"
    SUBMITTED = "SUBMITTED"
    IN_PROGRESS = "IN_PROGRESS"
    PENDING_WAREHOUSE = "PENDING_WAREHOUSE"
    ASKING_AI = "ASKING_AI"
    EXECUTING_QUERY = "EXECUTING_QUERY"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

TERMINAL_STATUSES = {Status.COMPLETED, Status.FAILED, Status.CANCELLED}
POLLABLE_STATUSES = {Status.INITIATED, Status.IN_PROGRESS, Status.EXECUTING_QUERY, Status.SUBMITTED, Status.PENDING_WAREHOUSE, Status.ASKING_AI}
MAX_RETRIES = 3
RETRY_INTERVAL = 5  # seconds
RATE_LIMIT_WAIT = 60  # seconds for 429 errors
POLL_TIMEOUT = 600  # 10 minutes