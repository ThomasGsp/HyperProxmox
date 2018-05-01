# Logs

A log system is available, but not complete.

Format:  [DATE] [THREAD_ID] [LEVEL] [TYPE] : JSON-DATA
* DATE = When the log is generated. (If bulk system is activate, date is respected)
* THREAD_ID = Hyperproxmox work with different thread (Core, API, crawler, sub-crawler...). If you wan debug correctly, you can use 
grep to follow your thread.
* LEVEL = WARNING, INFO, DEBUG...
* TYPE = Who generate this log

Log example:
```bash
[2018-04-29 15:59] [140273766102784] [ERROR] [HYPERPROXMOX] : 
{
"target": "my.promoxserver.com:8006", 
"result": "ERROR", "
value": "Cannot get ticket session my.promoxserver.com:8006 (HTTPSConnectionPool(host='my.promoxserver.com:8006', port=8006): Max retries exceeded with url: /api2/json/access/ticket?username=***YOUR_USER***&password=***PWD***(Caused by ConnectTimeoutError(<urllib3.connection.VerifiedHTTPSConnection object at 0x7f9405c83630>, 'Connection to my.promoxserver.com:8006 timed out. (connect timeout=5)')))", 
"type": "PYTHON"
} 
```

This log show a bad connection to Proxmox server.

User and password are hidden:
```bash 
username=***YOUR_USER***&password=***PWD*** 
```

[Usage - First start](05-first_start.md) <-- Previous | Next --> [Usage - API](07-api.md)