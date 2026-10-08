# Adaptive TTL Cache Reaper

This example demonstrates an adaptive Time-To-Live (TTL) cache reaper in Python. Instead of a single, synchronous sweep that can cause CPU spikes, a background thread periodically checks and removes a small, random batch of expired items. This distributes the cleanup load over time, ensuring efficient cache management without performance bottlenecks, alongside lazy expiration on item access.

## Language

`python`

## How to Run

Save the code as `main.py`.
Run from your terminal: `python main.py`

## Original Article

This example accompanies the Turkish article: [Adaptif TTL Reaper'lar: CPU Yükü Olmadan Önbellek Süresi Yönetimi](https://fatihsoysal.com/blog/adaptif-ttl-reaperlar-cpu-yuku-olmadan-onbellek-suresi-yonetimi/).

## License

MIT — see [LICENSE](LICENSE).
