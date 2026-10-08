# adaptive-ttl-cache-reaper
This example demonstrates an adaptive Time-To-Live (TTL) cache reaper in Python. Instead of a single, synchronous sweep that can cause CPU spikes, a background thread periodically checks and removes a small, random batch of expired items. This distributes the cleanup load over time, ensuring efficient cache management without performance bottleneck
