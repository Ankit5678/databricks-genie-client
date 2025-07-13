from ..exceptions.custom_errors import InvalidInputError

def validate_input(question: str, space_id: str, follow_up: bool, conversation_id: str):
    """Validates input parameters for Genie operations"""
    if not question.strip():
        raise InvalidInputError("Question cannot be empty")
    if not space_id.strip():
        raise InvalidInputError("Space ID cannot be empty")
    if follow_up and not conversation_id.strip():
        raise InvalidInputError("Conversation ID required for follow-up")