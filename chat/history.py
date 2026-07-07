
from typing import List
from chat.message import ChatMessage
from core.logger import Logger

class ChatHistoryManager:
    """
    Manages the history of chat messages, providing methods to add, retrieve,
    and potentially persist messages.
    """
    def __init__(self, max_history_size: int = 100):
        self.logger = Logger.get_logger()
        self._messages: List[ChatMessage] = []
        self.max_history_size = max_history_size
        self.logger.info(f"ChatHistoryManager initialized with max size: {self.max_history_size}")

    def add_message(self, message: ChatMessage):
        """
        Adds a new chat message to the history. If the history exceeds `max_history_size`,
        the oldest message is removed.
        """
        self._messages.append(message)
        if len(self._messages) > self.max_history_size:
            self._messages.pop(0) # Remove the oldest message
        self.logger.debug(f"Added message to history: {message.sender}: {message.content[:50]}...")

    def get_messages(self) -> List[ChatMessage]:
        """
        Retrieves all messages currently in the history.
        """
        return list(self._messages) # Return a copy to prevent external modification

    def clear_history(self):
        """
        Clears all messages from the history.
        """
        self._messages.clear()
        self.logger.info("Chat history cleared.")

    # TODO: Implement persistence (save to file, load from file) if required in the future.
    # For now, it's an in-memory history.
