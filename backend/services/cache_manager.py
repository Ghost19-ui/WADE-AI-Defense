import time

class SmartCache:
    def __init__(self):
        # This acts like a Redis Database in memory
        self._cache = {}
        self._ttl = 3600  # Time To Live: 1 hour (in seconds)

    def get(self, key):
        """Retrieve data if it exists and hasn't expired."""
        if key in self._cache:
            data, timestamp = self._cache[key]
            # Check if the data is still fresh (less than 1 hour old)
            if time.time() - timestamp < self._ttl:
                print(f"🚀 Cache HIT: Serving instant result for {key}")
                return data
            else:
                # Data is too old, delete it
                print(f"⌛ Cache EXPIRED for {key}")
                del self._cache[key]
        return None

    def set(self, key, value):
        """Save data with the current timestamp."""
        # We simulate Redis 'SET' command here
        self._cache[key] = (value, time.time())

# Create a global instance to be used everywhere
cache = SmartCache()