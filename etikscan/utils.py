"""
Utility functions for EtikScan agents.
"""

import os
import json
import logging
import traceback
import functools
from typing import Dict, Any, Optional, Union, TypeVar, cast, List, Callable, TypedDict, Set

logger = logging.getLogger(__name__)

T = TypeVar('T')
R = TypeVar('R')

class FileError(Exception):
    """File operation related errors."""
    pass

class JsonError(Exception):
    """JSON parsing or serialization errors."""
    pass

class ConfigError(Exception):
    """Configuration related errors."""
    pass

# LRU cache for file loading to avoid repeated disk access
@functools.lru_cache(maxsize=64)
def load_json_file(file_path: str) -> Dict[str, Any]:
    """Load and parse a JSON file.
    
    This function is cached using LRU cache to improve performance
    when the same file is loaded multiple times.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Dict[str, Any]: The parsed JSON data
        
    Raises:
        FileError: If the file doesn't exist or can't be read
        JsonError: If the file contains invalid JSON
    """
    if not os.path.exists(file_path):
        error_msg = f"File not found: {file_path}"
        logger.error(error_msg)
        raise FileError(error_msg)
        
    try:
        with open(file_path, 'r') as f:
            try:
                return cast(Dict[str, Any], json.load(f))
            except json.JSONDecodeError as e:
                error_msg = f"Invalid JSON in file {file_path}: {str(e)}"
                logger.error(error_msg)
                raise JsonError(error_msg) from e
    except PermissionError as e:
        error_msg = f"Permission denied when reading file {file_path}"
        logger.error(error_msg)
        raise FileError(error_msg) from e
    except IOError as e:
        error_msg = f"IO error when reading file {file_path}: {str(e)}"
        logger.error(error_msg)
        raise FileError(error_msg) from e
    except Exception as e:
        error_msg = f"Unexpected error loading file {file_path}: {str(e)}"
        logger.error(f"{error_msg}\n{traceback.format_exc()}")
        raise FileError(error_msg) from e

def save_json_file(data: Any, file_path: str) -> None:
    """Save data to a JSON file.
    
    Args:
        data: The data to save
        file_path: Path to save the data to
        
    Raises:
        FileError: If the file can't be written
        JsonError: If the data can't be serialized to JSON
    """
    # Create directory if it doesn't exist
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        try:
            os.makedirs(directory, exist_ok=True)
        except Exception as e:
            error_msg = f"Failed to create directory {directory}: {str(e)}"
            logger.error(error_msg)
            raise FileError(error_msg) from e
    
    try:
        with open(file_path, 'w') as f:
            try:
                json.dump(data, f, indent=2)
                
                # Invalidate the cache for this file path
                if file_path in load_json_file.cache_info().currsize:  # type: ignore
                    load_json_file.cache_clear()  # type: ignore
            except (TypeError, OverflowError) as e:
                error_msg = f"Failed to serialize data to JSON: {str(e)}"
                logger.error(error_msg)
                raise JsonError(error_msg) from e
    except PermissionError as e:
        error_msg = f"Permission denied when writing to file {file_path}"
        logger.error(error_msg)
        raise FileError(error_msg) from e
    except IOError as e:
        error_msg = f"IO error when writing to file {file_path}: {str(e)}"
        logger.error(error_msg)
        raise FileError(error_msg) from e
    except Exception as e:
        error_msg = f"Unexpected error saving to file {file_path}: {str(e)}"
        logger.error(f"{error_msg}\n{traceback.format_exc()}")
        raise FileError(error_msg) from e

def merge_configs(base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
    """Merge two configuration dictionaries.
    
    Args:
        base_config: The base configuration
        override_config: Configuration to override base values
        
    Returns:
        Dict[str, Any]: Merged configuration dictionary
        
    Raises:
        ConfigError: If either input is not a dictionary
    """
    if not isinstance(base_config, dict):
        error_msg = f"Base config must be a dictionary, got {type(base_config)}"
        logger.error(error_msg)
        raise ConfigError(error_msg)
        
    if not isinstance(override_config, dict):
        error_msg = f"Override config must be a dictionary, got {type(override_config)}"
        logger.error(error_msg)
        raise ConfigError(error_msg)
    
    result: Dict[str, Any] = base_config.copy()
    
    # Fast-path for empty override
    if not override_config:
        return result
    
    for key, value in override_config.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value
            
    return result

def safe_execute(func: Callable[..., T], *args: Any, **kwargs: Any) -> Optional[T]:
    """Execute a function safely, catching and logging any exceptions.
    
    Args:
        func: The function to execute
        *args: Positional arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function
        
    Returns:
        The result of the function or None if an exception occurred
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        func_name = getattr(func, "__name__", str(func))
        logger.error(f"Error executing function {func_name}: {str(e)}")
        logger.debug(f"Exception details: {traceback.format_exc()}")
        return None

def memoize(func: Callable[..., R]) -> Callable[..., R]:
    """Memoize a function, caching its results.
    
    Args:
        func: The function to memoize
        
    Returns:
        A memoized version of the function
    """
    cache: Dict[Any, R] = {}
    
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> R:
        # Create a hashable key from the arguments
        key = str(args) + str(sorted(kwargs.items()))
        
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    
    wrapper.cache_clear = lambda: cache.clear()  # type: ignore
    wrapper.cache_info = lambda: f"Cache size: {len(cache)}"  # type: ignore
    
    return wrapper

def flatten_dict(d: Dict[str, Any], parent_key: str = '', separator: str = '.') -> Dict[str, Any]:
    """Flatten a nested dictionary into a single level.
    
    Args:
        d: The dictionary to flatten
        parent_key: The parent key for nested dictionaries
        separator: The separator to use between keys
        
    Returns:
        Dict[str, Any]: The flattened dictionary
    """
    items: List[tuple] = []
    for k, v in d.items():
        new_key = f"{parent_key}{separator}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, separator).items())
        else:
            items.append((new_key, v))
    return dict(items)

def batch_process(items: List[T], 
                  process_func: Callable[[T], R], 
                  batch_size: int = 10) -> List[R]:
    """Process a list of items in batches.
    
    Args:
        items: The items to process
        process_func: The function to apply to each item
        batch_size: The number of items to process in each batch
        
    Returns:
        List[R]: The processed items
    """
    results: List[R] = []
    
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        batch_results = [process_func(item) for item in batch]
        results.extend(batch_results)
        
    return results