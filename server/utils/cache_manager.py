import os
import json
import pickle
import hashlib
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class CacheManager:
    """
    Comprehensive cache manager for optimizing scraper performance.
    Supports multiple cache backends and automatic cache invalidation.
    """
    
    def __init__(self, cache_dir: str = "cache", default_ttl: int = 3600):
        """
        Initialize the cache manager.
        
        Args:
            cache_dir (str): Directory to store cache files
            default_ttl (int): Default time-to-live in seconds (1 hour default)
        """
        self.cache_dir = Path(cache_dir)
        self.default_ttl = default_ttl
        self.logger = logger
        
        # Create cache directory if it doesn't exist
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize cache subdirectories
        self._init_cache_structure()
        
        # Cache statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'invalidations': 0,
            'size_bytes': 0
        }
    
    def _init_cache_structure(self):
        """Initialize cache directory structure."""
        subdirs = ['scraped_data', 'processed_data', 'metadata', 'temp']
        for subdir in subdirs:
            (self.cache_dir / subdir).mkdir(exist_ok=True)
    
    def _generate_cache_key(self, namespace: str, key: str, params: Dict = None) -> str:
        """
        Generate a unique cache key based on namespace, key, and parameters.
        
        Args:
            namespace (str): Cache namespace (e.g., 'game_logs', 'snapcounts')
            key (str): Base key (e.g., team code, URL)
            params (Dict): Additional parameters to include in key
            
        Returns:
            str: Unique cache key
        """
        key_data = {
            'namespace': namespace,
            'key': key,
            'params': params or {}
        }
        
        # Create hash of the key data for uniqueness
        key_string = json.dumps(key_data, sort_keys=True)
        key_hash = hashlib.md5(key_string.encode()).hexdigest()
        
        return f"{namespace}_{key_hash}"
    
    def _get_cache_path(self, cache_key: str, cache_type: str = 'scraped_data') -> Path:
        """Get the file path for a cache key."""
        return self.cache_dir / cache_type / f"{cache_key}.cache"
    
    def _get_metadata_path(self, cache_key: str) -> Path:
        """Get the metadata file path for a cache key."""
        return self.cache_dir / 'metadata' / f"{cache_key}.meta"
    
    def _is_cache_valid(self, cache_key: str, ttl: Optional[int] = None) -> bool:
        """
        Check if a cache entry is still valid based on TTL.
        
        Args:
            cache_key (str): Cache key to check
            ttl (int, optional): Time-to-live override
            
        Returns:
            bool: True if cache is valid, False otherwise
        """
        metadata_path = self._get_metadata_path(cache_key)
        
        if not metadata_path.exists():
            return False
        
        try:
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            created_time = datetime.fromisoformat(metadata['created_at'])
            ttl_seconds = ttl or metadata.get('ttl', self.default_ttl)
            
            expiry_time = created_time + timedelta(seconds=ttl_seconds)
            return datetime.now() < expiry_time
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            self.logger.warning(f"Invalid cache metadata for {cache_key}: {e}")
            return False
    
    def get(self, namespace: str, key: str, params: Dict = None, 
            ttl: Optional[int] = None) -> Optional[Any]:
        """
        Retrieve data from cache.
        
        Args:
            namespace (str): Cache namespace
            key (str): Cache key
            params (Dict): Additional parameters
            ttl (int, optional): TTL override for validation
            
        Returns:
            Any: Cached data if valid, None otherwise
        """
        cache_key = self._generate_cache_key(namespace, key, params)
        
        if not self._is_cache_valid(cache_key, ttl):
            self.stats['misses'] += 1
            return None
        
        cache_path = self._get_cache_path(cache_key)
        
        if not cache_path.exists():
            self.stats['misses'] += 1
            return None
        
        try:
            with open(cache_path, 'rb') as f:
                data = pickle.load(f)
            
            self.stats['hits'] += 1
            self.logger.debug(f"Cache hit for {namespace}:{key}")
            return data
            
        except (pickle.PickleError, IOError) as e:
            self.logger.warning(f"Failed to load cache for {cache_key}: {e}")
            self.stats['misses'] += 1
            return None
    
    def set(self, namespace: str, key: str, data: Any, params: Dict = None, 
            ttl: Optional[int] = None) -> bool:
        """
        Store data in cache.
        
        Args:
            namespace (str): Cache namespace
            key (str): Cache key
            data (Any): Data to cache
            params (Dict): Additional parameters
            ttl (int, optional): TTL override
            
        Returns:
            bool: True if successful, False otherwise
        """
        cache_key = self._generate_cache_key(namespace, key, params)
        cache_path = self._get_cache_path(cache_key)
        metadata_path = self._get_metadata_path(cache_key)
        
        try:
            # Store the data
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f)
            
            # Store metadata
            metadata = {
                'namespace': namespace,
                'key': key,
                'params': params or {},
                'created_at': datetime.now().isoformat(),
                'ttl': ttl or self.default_ttl,
                'size_bytes': cache_path.stat().st_size
            }
            
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            self.stats['sets'] += 1
            self.stats['size_bytes'] += metadata['size_bytes']
            self.logger.debug(f"Cached data for {namespace}:{key}")
            return True
            
        except (pickle.PickleError, IOError, OSError) as e:
            self.logger.error(f"Failed to cache data for {cache_key}: {e}")
            return False
    
    def invalidate(self, namespace: str, key: str = None, params: Dict = None) -> int:
        """
        Invalidate cache entries.
        
        Args:
            namespace (str): Cache namespace
            key (str, optional): Specific key to invalidate (None for all in namespace)
            params (Dict): Additional parameters
            
        Returns:
            int: Number of entries invalidated
        """
        invalidated_count = 0
        
        if key is not None:
            # Invalidate specific key
            cache_key = self._generate_cache_key(namespace, key, params)
            cache_path = self._get_cache_path(cache_key)
            metadata_path = self._get_metadata_path(cache_key)
            
            for path in [cache_path, metadata_path]:
                if path.exists():
                    try:
                        path.unlink()
                        invalidated_count += 1
                    except OSError as e:
                        self.logger.warning(f"Failed to delete {path}: {e}")
        else:
            # Invalidate all entries in namespace
            for cache_type in ['scraped_data', 'metadata']:
                cache_dir = self.cache_dir / cache_type
                for cache_file in cache_dir.glob(f"{namespace}_*.cache"):
                    try:
                        cache_file.unlink()
                        invalidated_count += 1
                    except OSError as e:
                        self.logger.warning(f"Failed to delete {cache_file}: {e}")
                
                for meta_file in cache_dir.glob(f"{namespace}_*.meta"):
                    try:
                        meta_file.unlink()
                        invalidated_count += 1
                    except OSError as e:
                        self.logger.warning(f"Failed to delete {meta_file}: {e}")
        
        self.stats['invalidations'] += invalidated_count
        self.logger.info(f"Invalidated {invalidated_count} cache entries for {namespace}")
        return invalidated_count
    
    def warm_cache(self, warm_functions: List[Dict]) -> Dict[str, bool]:
        """
        Warm the cache by pre-loading frequently accessed data.
        
        Args:
            warm_functions (List[Dict]): List of functions to call for cache warming
                Each dict should have: {'function': callable, 'args': tuple, 'kwargs': dict}
                
        Returns:
            Dict[str, bool]: Results of warming operations
        """
        results = {}
        
        for i, warm_config in enumerate(warm_functions):
            try:
                func = warm_config['function']
                args = warm_config.get('args', ())
                kwargs = warm_config.get('kwargs', {})
                
                self.logger.info(f"Warming cache with function {func.__name__}")
                result = func(*args, **kwargs)
                results[f"warm_{i}_{func.__name__}"] = True
                
            except Exception as e:
                self.logger.error(f"Cache warming failed for function {i}: {e}")
                results[f"warm_{i}_error"] = False
        
        return results
    
    def cleanup_expired(self) -> int:
        """
        Clean up expired cache entries.
        
        Returns:
            int: Number of expired entries removed
        """
        cleaned_count = 0
        
        # Check all metadata files for expiry
        metadata_dir = self.cache_dir / 'metadata'
        for meta_file in metadata_dir.glob('*.meta'):
            try:
                with open(meta_file, 'r') as f:
                    metadata = json.load(f)
                
                created_time = datetime.fromisoformat(metadata['created_at'])
                ttl_seconds = metadata.get('ttl', self.default_ttl)
                expiry_time = created_time + timedelta(seconds=ttl_seconds)
                
                if datetime.now() >= expiry_time:
                    # Remove both cache and metadata files
                    cache_key = meta_file.stem
                    cache_path = self._get_cache_path(cache_key)
                    
                    for path in [cache_path, meta_file]:
                        if path.exists():
                            path.unlink()
                            cleaned_count += 1
                
            except (json.JSONDecodeError, KeyError, ValueError, OSError) as e:
                self.logger.warning(f"Error processing {meta_file}: {e}")
        
        self.logger.info(f"Cleaned up {cleaned_count} expired cache entries")
        return cleaned_count
    
    def get_stats(self) -> Dict[str, Union[int, float]]:
        """
        Get cache statistics.
        
        Returns:
            Dict: Cache statistics including hit rate, size, etc.
        """
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        # Calculate current cache size
        current_size = 0
        for cache_type in ['scraped_data', 'processed_data']:
            cache_dir = self.cache_dir / cache_type
            for cache_file in cache_dir.glob('*.cache'):
                try:
                    current_size += cache_file.stat().st_size
                except OSError:
                    pass
        
        return {
            'hits': self.stats['hits'],
            'misses': self.stats['misses'],
            'sets': self.stats['sets'],
            'invalidations': self.stats['invalidations'],
            'hit_rate_percent': round(hit_rate, 2),
            'current_size_bytes': current_size,
            'current_size_mb': round(current_size / (1024 * 1024), 2)
        }
    
    def clear_all(self) -> int:
        """
        Clear all cache data.
        
        Returns:
            int: Number of files removed
        """
        removed_count = 0
        
        for cache_type in ['scraped_data', 'processed_data', 'metadata', 'temp']:
            cache_dir = self.cache_dir / cache_type
            for cache_file in cache_dir.glob('*'):
                try:
                    cache_file.unlink()
                    removed_count += 1
                except OSError as e:
                    self.logger.warning(f"Failed to delete {cache_file}: {e}")
        
        # Reset stats
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'invalidations': 0,
            'size_bytes': 0
        }
        
        self.logger.info(f"Cleared all cache data ({removed_count} files)")
        return removed_count


# Global cache manager instance
_cache_manager = None

def get_cache_manager(cache_dir: str = "cache", default_ttl: int = 3600) -> CacheManager:
    """
    Get the global cache manager instance.
    
    Args:
        cache_dir (str): Cache directory
        default_ttl (int): Default TTL in seconds
        
    Returns:
        CacheManager: Global cache manager instance
    """
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager(cache_dir, default_ttl)
    return _cache_manager


# Decorator for caching function results
def cached(namespace: str, ttl: Optional[int] = None, 
           key_func: Optional[callable] = None):
    """
    Decorator for caching function results.
    
    Args:
        namespace (str): Cache namespace
        ttl (int, optional): TTL override
        key_func (callable, optional): Function to generate cache key from args
        
    Returns:
        Decorator function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            cache = get_cache_manager()
            
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}_{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Try to get from cache
            cached_result = cache.get(namespace, cache_key, ttl=ttl)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(namespace, cache_key, result, ttl=ttl)
            
            return result
        
        return wrapper
    return decorator


if __name__ == "__main__":
    # Example usage and testing
    cache = CacheManager()
    
    # Test basic caching
    cache.set('test', 'key1', {'data': 'test_value'})
    result = cache.get('test', 'key1')
    print(f"Cache test result: {result}")
    
    # Test cache stats
    stats = cache.get_stats()
    print(f"Cache stats: {stats}")
    
    # Test cache invalidation
    invalidated = cache.invalidate('test')
    print(f"Invalidated {invalidated} entries") 