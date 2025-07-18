"""
Base agent implementation for EtikScan.
"""

import os
import json
import logging
import traceback
from typing import Dict, Any, Optional, Union, List

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AgentError(Exception):
    """Base exception class for Agent errors."""
    pass

class StateError(AgentError):
    """Agent state related errors."""
    pass

class ConfigError(AgentError):
    """Agent configuration related errors."""
    pass

class Agent:
    """Base agent class for EtikScan."""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize a new agent.
        
        Args:
            name: Agent name
            config: Optional configuration dictionary
            
        Raises:
            ValueError: If name is empty or None
        """
        if not name:
            error_msg = "Agent name cannot be empty"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        self.name: str = name
        self.config: Dict[str, Any] = config or {}
        self.is_running: bool = False
        self.errors: List[str] = []
        logger.info(f"Agent {name} initialized")
    
    def start(self) -> bool:
        """Start the agent.
        
        Returns:
            bool: True if the agent was started, False if it was already running
        """
        if self.is_running:
            logger.warning(f"Agent {self.name} is already running")
            return False
            
        try:
            # Perform any startup tasks here
            self._on_start()
            
            self.is_running = True
            logger.info(f"Agent {self.name} started")
            return True
        except Exception as e:
            error_msg = f"Failed to start agent {self.name}: {str(e)}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            self.errors.append(error_msg)
            return False
    
    def _on_start(self) -> None:
        """Hook called when the agent starts.
        
        This method can be overridden by subclasses to perform
        initialization tasks when the agent starts.
        """
        pass
    
    def stop(self) -> bool:
        """Stop the agent.
        
        Returns:
            bool: True if the agent was stopped, False if it wasn't running
        """
        if not self.is_running:
            logger.warning(f"Agent {self.name} is not running")
            return False
            
        try:
            # Perform any cleanup tasks here
            self._on_stop()
            
            self.is_running = False
            logger.info(f"Agent {self.name} stopped")
            return True
        except Exception as e:
            error_msg = f"Error while stopping agent {self.name}: {str(e)}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            self.errors.append(error_msg)
            # Force stop even if there was an error
            self.is_running = False
            return False
    
    def _on_stop(self) -> None:
        """Hook called when the agent stops.
        
        This method can be overridden by subclasses to perform
        cleanup tasks when the agent stops.
        """
        pass
    
    def process_message(self, message: Any) -> Any:
        """Process a message.
        
        Args:
            message: The message to process
            
        Returns:
            The processed result
            
        Raises:
            ValueError: If the agent is not running
        """
        if not self.is_running:
            error_msg = f"Cannot process message: Agent {self.name} is not running"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        try:
            # Base implementation just returns the message
            return message
        except Exception as e:
            error_msg = f"Error processing message in agent {self.name}: {str(e)}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            self.errors.append(error_msg)
            raise
    
    def save_state(self, path: str) -> None:
        """Save agent state to disk.
        
        Args:
            path: Path to save state
            
        Raises:
            StateError: If the state cannot be saved
        """
        state: Dict[str, Any] = {
            "name": self.name,
            "config": self.config,
            "is_running": self.is_running,
            "errors": self.errors,
        }
        
        directory = os.path.dirname(path)
        if directory and not os.path.exists(directory):
            try:
                os.makedirs(directory, exist_ok=True)
            except Exception as e:
                error_msg = f"Failed to create directory {directory}: {str(e)}"
                logger.error(error_msg)
                raise StateError(error_msg) from e
        
        try:
            with open(path, 'w') as f:
                json.dump(state, f, indent=2)
                logger.info(f"Agent {self.name} state saved to {path}")
        except Exception as e:
            error_msg = f"Failed to save agent state to {path}: {str(e)}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            raise StateError(error_msg) from e
    
    def load_state(self, path: str) -> bool:
        """Load agent state from disk.
        
        Args:
            path: Path to load state from
            
        Returns:
            bool: True if the state was loaded successfully, False otherwise
            
        Raises:
            StateError: If the state file exists but cannot be loaded
        """
        if not os.path.exists(path):
            logger.error(f"State file not found: {path}")
            return False
            
        try:
            with open(path, 'r') as f:
                try:
                    state: Dict[str, Any] = json.load(f)
                except json.JSONDecodeError as e:
                    error_msg = f"Invalid JSON in state file {path}: {str(e)}"
                    logger.error(error_msg)
                    raise StateError(error_msg) from e
                
            self.name = state.get("name", self.name)
            self.config = state.get("config", self.config)
            self.is_running = state.get("is_running", self.is_running)
            self.errors = state.get("errors", self.errors)
            logger.info(f"Agent {self.name} state loaded from {path}")
            return True
        except Exception as e:
            if isinstance(e, StateError):
                raise
            error_msg = f"Failed to load agent state from {path}: {str(e)}"
            logger.error(f"{error_msg}\n{traceback.format_exc()}")
            raise StateError(error_msg) from e
            
    def get_last_error(self) -> Optional[str]:
        """Get the most recent error message.
        
        Returns:
            Optional[str]: The most recent error message or None if no errors
        """
        if self.errors:
            return self.errors[-1]
        return None
        
    def clear_errors(self) -> None:
        """Clear all error messages."""
        self.errors = []
        logger.info(f"Cleared error history for agent {self.name}")