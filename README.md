# ssync
A tool for Satellite incremental yum repository sync management for disconnected environments. The tool has been developed for Satellite 6.8, and uses Python 3.6 for its runtime environment.

## Prerequisites

* A Satellite server that's connected to the internet.
* Python 3 installed on the connected Satellite server.

```
<satellite-server> $ foreman-maintain packages install python3
```
