import time
import threading
import random

class AdaptiveCache:
    def __init__(self, reap_interval_seconds=1, reap_batch_size=5):
        self._cache = {}  # Stores {'value': ..., 'expires_at': ...}
        self._lock = threading.Lock() # Protects cache access for thread safety
        self._reap_interval = reap_interval_seconds
        self._reap_batch_size = reap_batch_size
        self._running = False
        self._reaper_thread = None
        print(f"Cache initialized with reap interval: {reap_interval_seconds}s, batch size: {reap_batch_size}")

    def start_reaper(self):
        """Starts the background thread for adaptive cache reaping."""
        if not self._running:
            self._running = True
            # Daemon thread ensures it exits when the main program exits
            self._reaper_thread = threading.Thread(target=self._reap_expired_items_adaptive, name="CacheReaper", daemon=True)
            self._reaper_thread.start()
            print("Cache reaper started.")

    def stop_reaper(self):
        """Stops the background reaper thread gracefully."""
        if self._running:
            self._running = False
            if self._reaper_thread:
                self._reaper_thread.join() # Wait for the thread to finish its current cycle
            print("Cache reaper stopped.")

    def set(self, key, value, ttl_seconds):
        """Adds or updates an item in the cache with a Time-To-Live (TTL)."""
        expires_at = time.time() + ttl_seconds
        with self._lock:
            self._cache[key] = {'value': value, 'expires_at': expires_at}
        print(f"Set '{key}' with TTL {ttl_seconds}s (expires at {time.ctime(expires_at)})")

    def get(self, key):
        """Retrieves an item from the cache. Performs lazy expiration check."""
        with self._lock:
            item = self._cache.get(key)
            if item is None:
                return None

            if time.time() > item['expires_at']:
                # Lazy expiration: remove on access if expired, distributing work
                del self._cache[key]
                print(f"Get '{key}': Expired and removed (lazy expiration).")
                return None
            else:
                print(f"Get '{key}': Found '{item['value']}'.")
                return item['value']

    def _reap_expired_items_adaptive(self):
        """
        The adaptive reaper function that runs in a background thread.
        It periodically checks a small, random batch of cache items for expiration.
        This distributes the CPU load over time, avoiding sudden spikes from full scans.
        """
        while self._running:
            time.sleep(self._reap_interval)
            
            keys_to_check = []
            with self._lock:
                # Get a snapshot of keys to avoid modifying dict while iterating
                all_keys = list(self._cache.keys())
                if not all_keys:
                    print(f"[REAPER] Cache is empty. Current cache size: {len(self._cache)}")
                    continue
                # Select a random subset of keys to check (adaptive batch processing)
                keys_to_check = random.sample(all_keys, min(len(all_keys), self._reap_batch_size))

            expired_count = 0
            for key in keys_to_check:
                with self._lock: # Re-acquire lock for actual deletion
                    # Check if key still exists and is expired (could have been removed by get() or another reaper cycle)
                    item = self._cache.get(key)
                    if item and time.time() > item['expires_at']:
                        del self._cache[key]
                        expired_count += 1
                        print(f"[REAPER] Removed expired item: '{key}'.")
            
            if expired_count > 0:
                print(f"[REAPER] Cleaned up {expired_count} items in this cycle. Current cache size: {len(self._cache)}")
            else:
                print(f"[REAPER] No expired items found in batch. Current cache size: {len(self._cache)}")

    def size(self):
        """Returns the current number of items in the cache."""
        with self._lock:
            return len(self._cache)

# --- Example Usage ---
if __name__ == "__main__":
    # Initialize cache with a fast reap interval and small batch size for demonstration
    cache = AdaptiveCache(reap_interval_seconds=0.5, reap_batch_size=3)
    cache.start_reaper()

    # Add items with various TTLs
    cache.set("user:1", {"name": "Alice"}, 2) # Expires in 2 seconds
    cache.set("product:101", {"price": 99.99}, 5) # Expires in 5 seconds
    cache.set("session:abc", {"data": "xyz"}, 3) # Expires in 3 seconds
    cache.set("config:app", {"version": "1.0"}, 10) # Expires in 10 seconds
    cache.set("temp:data1", "value1", 2) # Expires in 2 seconds
    cache.set("temp:data2", "value2", 3) # Expires in 3 seconds
    cache.set("temp:data3", "value3", 4) # Expires in 4 seconds
    cache.set("temp:data4", "value4", 5) # Expires in 5 seconds

    print("\n--- Initial cache state ---")
    time.sleep(0.1) # Give a moment for prints to settle
    print(f"Current cache size: {cache.size()}")

    print("\n--- Accessing items before expiration ---")
    cache.get("user:1")
    cache.get("product:101")
    time.sleep(1) # Wait a bit

    print("\n--- Waiting for some items to expire and reaper to start working ---")
    time.sleep(2.5) # user:1, temp:data1 should be expired; session:abc, temp:data2 might be expired or close

    print("\n--- Accessing potentially expired items ---")
    cache.get("user:1") # Should be expired and removed by lazy or background reaper
    cache.get("session:abc") # Might be expired
    cache.get("config:app") # Should still be active

    print("\n--- Waiting for more items to expire and reaper to clean up ---")
    time.sleep(3) # Wait for product:101, temp:data3, temp:data4 to expire, and reaper to clean up

    print("\n--- Final cache state check ---")
    time.sleep(0.1) # Give reaper a chance to print
    print(f"Current cache size: {cache.size()}")
    
    # Final checks for items that should be gone or still present
    print("\n--- Final item checks ---")
    cache.get("product:101") # Should be expired
    cache.get("config:app") # Depending on total time, might still be active or just expired

    print("\n--- Stopping reaper and ending example ---")
    cache.stop_reaper()
    print("Example finished.")
