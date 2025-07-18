"""
Orchestrator for managing multiple EtikScan agents.
"""

import logging
import json
import os
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any, Optional, Union, Mapping, List, Set, Tuple, Callable
from .agent import Agent
from .utils import memoize, batch_process

logger = logging.getLogger(__name__)

class OrchestratorError(Exception):
    """Base exception class for Orchestrator errors."""
    pass

class ConfigError(OrchestratorError):
    """Configuration related errors."""
    pass

class AgentError(OrchestratorError):
    """Agent operation related errors."""
    pass

class Orchestrator:
    """Manages multiple EtikScan agents."""
    
    def __init__(self, config_path: Optional[str] = None) -> None:
        """Initialize the orchestrator.
        
        Args:
            config_path: Optional path to a configuration file
            
        Raises:
            ConfigError: If the configuration file exists but cannot be loaded
        """
        self.agents: Dict[str, Agent] = {}
        self.config: Dict[str, Any] = {}
        self._lock = threading.RLock()  # Reentrant lock for thread safety
        self._running_agents: Set[str] = set()
        
        if config_path:
            if not os.path.exists(config_path):
                logger.warning(f"Configuration file not found: {config_path}")
            else:
                self.load_config(config_path)
    
    def load_config(self, config_path: str) -> None:
        """Load configuration from a file.
        
        Args:
            config_path: Path to the configuration file
            
        Raises:
            ConfigError: If the configuration file cannot be loaded or parsed
        """
        if not os.path.exists(config_path):
            error_msg = f"Configuration file not found: {config_path}"
            logger.error(error_msg)
            raise ConfigError(error_msg)
            
        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
                logger.info(f"Loaded configuration from {config_path}")
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON in configuration file {config_path}: {str(e)}"
            logger.error(error_msg)
            raise ConfigError(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to load configuration: {str(e)}"
            logger.error(error_msg)
            raise ConfigError(error_msg) from e
    
    def register_agent(self, agent: Any) -> bool:
        """Register a new agent with the orchestrator.
        
        Args:
            agent: The agent to register
            
        Returns:
            bool: True if registration was successful, False otherwise
            
        Raises:
            AgentError: If the agent is not a valid Agent instance
        """
        if not isinstance(agent, Agent):
            error_msg = f"Cannot register non-Agent object: {type(agent)}"
            logger.error(error_msg)
            raise AgentError(error_msg)
        
        with self._lock:    
            if agent.name in self.agents:
                logger.warning(f"Agent with name {agent.name} already registered")
                return False
                
            self.agents[agent.name] = agent
            logger.info(f"Registered agent: {agent.name}")
            return True
    
    def register_multiple_agents(self, agents: List[Agent]) -> Dict[str, bool]:
        """Register multiple agents at once.
        
        Args:
            agents: List of agents to register
            
        Returns:
            Dict[str, bool]: Dictionary mapping agent names to registration results
        """
        results: Dict[str, bool] = {}
        
        with self._lock:
            for agent in agents:
                try:
                    results[agent.name] = self.register_agent(agent)
                except Exception as e:
                    logger.error(f"Error registering agent {agent.name}: {str(e)}")
                    results[agent.name] = False
                    
        return results
    
    def unregister_agent(self, agent_name: str) -> bool:
        """Unregister an agent.
        
        Args:
            agent_name: Name of the agent to unregister
            
        Returns:
            bool: True if unregistration was successful, False otherwise
        """
        with self._lock:
            if agent_name not in self.agents:
                logger.warning(f"Agent {agent_name} not found")
                return False
                
            # Stop the agent if it's running
            if agent_name in self._running_agents:
                self.stop_agent(agent_name)
                
            del self.agents[agent_name]
            logger.info(f"Unregistered agent: {agent_name}")
            return True
    
    def start_agent(self, agent_name: str) -> bool:
        """Start an agent.
        
        Args:
            agent_name: Name of the agent to start
            
        Returns:
            bool: True if the agent was started successfully, False otherwise
            
        Raises:
            AgentError: If the agent does not exist
        """
        with self._lock:
            if agent_name not in self.agents:
                error_msg = f"Agent {agent_name} not found"
                logger.error(error_msg)
                raise AgentError(error_msg)
                
            result = self.agents[agent_name].start()
            if result:
                self._running_agents.add(agent_name)
                
            return result
    
    def start_all_agents(self) -> Dict[str, bool]:
        """Start all registered agents.
        
        Returns:
            Dict[str, bool]: Dictionary mapping agent names to start results
        """
        results: Dict[str, bool] = {}
        
        with ThreadPoolExecutor() as executor:
            # Create a future for each agent start operation
            future_to_agent = {
                executor.submit(self.start_agent, name): name 
                for name in self.agents.keys()
            }
            
            # Process results as they complete
            for future in as_completed(future_to_agent):
                agent_name = future_to_agent[future]
                try:
                    results[agent_name] = future.result()
                except Exception as e:
                    logger.error(f"Error starting agent {agent_name}: {str(e)}")
                    results[agent_name] = False
                    
        return results
    
    def stop_agent(self, agent_name: str) -> bool:
        """Stop an agent.
        
        Args:
            agent_name: Name of the agent to stop
            
        Returns:
            bool: True if the agent was stopped successfully, False otherwise
            
        Raises:
            AgentError: If the agent does not exist
        """
        with self._lock:
            if agent_name not in self.agents:
                error_msg = f"Agent {agent_name} not found"
                logger.error(error_msg)
                raise AgentError(error_msg)
                
            result = self.agents[agent_name].stop()
            if result and agent_name in self._running_agents:
                self._running_agents.remove(agent_name)
                
            return result
    
    def stop_all_agents(self) -> Dict[str, bool]:
        """Stop all running agents.
        
        Returns:
            Dict[str, bool]: Dictionary mapping agent names to stop results
        """
        results: Dict[str, bool] = {}
        
        with ThreadPoolExecutor() as executor:
            # Create a future for each running agent stop operation
            with self._lock:
                running_agents = list(self._running_agents)
                
            future_to_agent = {
                executor.submit(self.stop_agent, name): name 
                for name in running_agents
            }
            
            # Process results as they complete
            for future in as_completed(future_to_agent):
                agent_name = future_to_agent[future]
                try:
                    results[agent_name] = future.result()
                except Exception as e:
                    logger.error(f"Error stopping agent {agent_name}: {str(e)}")
                    results[agent_name] = False
                    
        return results
    
    def broadcast_message(self, message: Any) -> Dict[str, Any]:
        """Broadcast a message to all running agents.
        
        Args:
            message: The message to broadcast
            
        Returns:
            Dict[str, Any]: Dictionary mapping agent names to their responses
        """
        responses: Dict[str, Any] = {}
        errors: List[str] = []
        
        with ThreadPoolExecutor() as executor:
            # Create a future for each running agent message processing
            with self._lock:
                running_agent_names = list(self._running_agents)
                
            def process_message_for_agent(name: str) -> Tuple[str, Any]:
                """Process message for a single agent and return name, result tuple."""
                try:
                    agent = self.agents[name]
                    result = agent.process_message(message)
                    return name, result
                except Exception as e:
                    error_msg = f"Error processing message by agent {name}: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
                    return name, {"error": str(e)}
            
            # Submit all tasks and gather results
            futures = [
                executor.submit(process_message_for_agent, name) 
                for name in running_agent_names
            ]
            
            for future in as_completed(futures):
                try:
                    name, result = future.result()
                    responses[name] = result
                except Exception as e:
                    logger.error(f"Unexpected error in broadcast: {str(e)}")
        
        if errors:
            logger.warning(f"Encountered {len(errors)} errors during broadcast")
            
        return responses
    
    @memoize    
    def get_agent(self, agent_name: str) -> Agent:
        """Get an agent by name.
        
        This method is memoized for better performance when
        the same agent is requested multiple times.
        
        Args:
            agent_name: Name of the agent to get
            
        Returns:
            Agent: The requested agent
            
        Raises:
            AgentError: If the agent does not exist
        """
        with self._lock:
            if agent_name not in self.agents:
                error_msg = f"Agent {agent_name} not found"
                logger.error(error_msg)
                raise AgentError(error_msg)
                
            return self.agents[agent_name]
    
    def get_all_agents(self) -> Dict[str, Agent]:
        """Get all registered agents.
        
        Returns:
            Dict[str, Agent]: Dictionary mapping agent names to agent instances
        """
        with self._lock:
            return self.agents.copy()
    
    def get_running_agents(self) -> Dict[str, Agent]:
        """Get all running agents.
        
        Returns:
            Dict[str, Agent]: Dictionary mapping agent names to agent instances
        """
        with self._lock:
            return {
                name: self.agents[name] 
                for name in self._running_agents
                if name in self.agents
            }
    
    def batch_operation(self, 
                        operation: Callable[[Agent], Any], 
                        agent_names: Optional[List[str]] = None,
                        batch_size: int = 10) -> Dict[str, Any]:
        """Perform an operation on multiple agents in batches.
        
        Args:
            operation: The operation to perform on each agent
            agent_names: Optional list of agent names to operate on (all if None)
            batch_size: The number of agents to process in each batch
            
        Returns:
            Dict[str, Any]: Dictionary mapping agent names to operation results
        """
        with self._lock:
            if agent_names is None:
                agents_to_process = list(self.agents.values())
            else:
                agents_to_process = [
                    self.agents[name] for name in agent_names 
                    if name in self.agents
                ]
            
        results: Dict[str, Any] = {}
        
        def process_agent(agent: Agent) -> Tuple[str, Any]:
            try:
                return agent.name, operation(agent)
            except Exception as e:
                logger.error(f"Error processing agent {agent.name}: {str(e)}")
                return agent.name, {"error": str(e)}
                
        batch_results = batch_process(agents_to_process, process_agent, batch_size)
        
        for name, result in batch_results:
            results[name] = result
            
        return results