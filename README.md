# py-stream-analyzer
A terminal-based streaming log analyzer. Uses generator pipelines and regex to parse massive log files incrementally without loading them entirely into system memory.

A memory-efficient CLI tool for parsing and analyzing live server access logs. Instead of loading entire log files into memory, it uses Python generators to `tail` files incrementally and maintains a rolling-window deque to calculate real-time error rates and telemetry.

## Features
* **O(1) Memory Footprint:** Safe to run on massive, multi-gigabyte log files.
* **Rolling Analytics:** Calculates localized error rates based on an adjustable sliding window of recent events.
* **Regex Extraction:** Pre-configured to parse standard NGINX and Apache access logs cleanly.

## Usage

```bash
# Run the analyzer against a live production log file
python3 analyzer.py /var/log/nginx/access.log
