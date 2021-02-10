Script that periodically collects jvm thread dumps from multiple kubernetes pods.  
Tested with Python 3.8 on Linux.

    python main.py

Collected dumps then could be analyzed with
https://fastthread.io/,
https://github.com/brendangregg/FlameGraph,
https://github.com/mchr3k/javathreaddumpanalyser,
...
