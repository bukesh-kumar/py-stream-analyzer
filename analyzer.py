```python
"""
analyzer.py
A generator-based stream processor for live log analysis.
Demonstrates memory-efficient file reading and rolling metric aggregation.
"""

import sys
import time
import re
from collections import deque
from typing import Iterator, Dict

# Regex pattern for standard NGINX/Apache style access logs
LOG_PATTERN = re.compile(
    r'(?P<ip>[\d\.]+)\s-\s-\s\[(?P<date>.*?)\]\s"(?P<request>.*?)"\s(?P<status>\d{3})\s(?P<size>\d+)'
)

class StreamAnalyzer:
    def __init__(self, window_size: int = 1000):
        self.window_size = window_size
        self.status_codes: deque = deque(maxlen=window_size)
        self.metrics = {
            "total_processed": 0,
            "errors_4xx": 0,
            "errors_5xx": 0
        }

    def tail_file(self, file_path: str) -> Iterator[str]:
        """Generator that yields new lines appended to a file in real-time."""
        try:
            with open(file_path, 'r') as f:
                # Jump to the end of the file
                f.seek(0, 2)
                while True:
                    line = f.readline()
                    if not line:
                        time.sleep(0.1)
                        continue
                    yield line
        except KeyboardInterrupt:
            print("\n[Analyzer] Terminating log stream gracefully.")
            sys.exit(0)
        except FileNotFoundError:
            print(f"[Error] Log file '{file_path}' not found.")
            sys.exit(1)

    def process_stream(self, stream: Iterator[str]):
        """Parses the stream and maintains rolling aggregated metrics."""
        print(f"Listening to stream... (Rolling window: {self.window_size} events)\n")
        
        for line in stream:
            match = LOG_PATTERN.match(line)
            if not match:
                continue

            data = match.groupdict()
            status = int(data['status'])
            
            self.status_codes.append(status)
            self.metrics["total_processed"] += 1
            
            if 400 <= status < 500:
                self.metrics["errors_4xx"] += 1
            elif status >= 500:
                self.metrics["errors_5xx"] += 1

            # Print telemetry every 50 events
            if self.metrics["total_processed"] % 50 == 0:
                self._print_diagnostics()

    def _print_diagnostics(self):
        """Renders current rolling metrics to the terminal."""
        recent_errors = sum(1 for s in self.status_codes if s >= 400)
        error_rate = (recent_errors / len(self.status_codes)) * 100 if self.status_codes else 0
        
        print(f"--- [TELEMETRY UPDATE] ---")
        print(f"Total Events: {self.metrics['total_processed']}")
        print(f"Recent Error Rate (Last {len(self.status_codes)}): {error_rate:.2f}%")
        print(f"Absolute 5xx Faults:  {self.metrics['errors_5xx']}")
        print("--------------------------\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyzer.py <path_to_log_file>")
        sys.exit(1)

    target_file = sys.argv[1]
    analyzer = StreamAnalyzer(window_size=500)
    
    # Connect the generator pipeline
    live_stream = analyzer.tail_file(target_file)
    analyzer.process_stream(live_stream)
File: README.md
Markdown
# py-stream-analyzer

A memory-efficient CLI tool for parsing and analyzing live server access logs. Instead of loading entire log files into memory, it uses Python generators to `tail` files incrementally and maintains a rolling-window deque to calculate real-time error rates and telemetry.

## Features
* **O(1) Memory Footprint:** Safe to run on massive, multi-gigabyte log files.
* **Rolling Analytics:** Calculates localized error rates based on an adjustable sliding window of recent events.
* **Regex Extraction:** Pre-configured to parse standard NGINX and Apache access logs cleanly.

## Usage

```bash
# Run the analyzer against a live production log file
python3 analyzer.py /var/log/nginx/access.log
