# Configs

Configurations are managed by single point:

vi /opt/HyperProxmox/code/scripts/main/private/conf/config
``` bash
[system]
; System configurations
user: hyperproxmox

; If not exist at startup, the key will be auto-generate.
key_pvt: private/keys/Ragnarok.pvt.key
key_pub: private/keys/Ragnarok.pub.key

admin_mail: tlams@localhost

[web]
user: www-data

[api]:
user: hyperproxmox

[databases]
; Databases configurations
; NOSQL databases, should use a password
mongodb_user:
mongodb_password:
mongodb_ip: 127.0.0.1
mongodb_port: 27017

redis_user:
redis_password:
redis_ip: 127.0.0.1
redis_port: 6379

[deploy]
; Maximum concurrent deployment
; A high value can overcharge your physicals servers
concurrencydeploy: 2

; Delay between two deployment round
; If your infrastructure isn't very large, you should'nt reduce this delay.
; A low delay can overcharge your physicals servers
delayrounddeploy: 15

[walker]
; Delay in seconds between to crawl (update)
walker: 300

; Lock file -- prevent concurrent crawling
walker_lock: /tmp/hyperproxmoxwalker.lock

; Set an unique ID (change comment part)
uid = False

[logger]
; logs level    1: "INFO",  2: "WARNING", 3: "ERROR", 4: "CRITICAL",  5: "DEBUG"
logs_level = 5

; Limit IO write, if debug level is active, this value is overwrite to 0
bulk_write = 1

; Buffer size
bulk_size = 1000

; log output
logs_dir = /var/log/hyperproxmox/
```

#### Purge system
You should setup an cron to purge old data.
``` bash
RET=4 # older than the current date less this delay in days
DATETIMESTAMP=$(($(date +%s)-$((86400*$RET))))
curl -H -XPOST -d '{ "action": "purge", "type":"strict", "date": $DATETIMESTAMP }'  localhost:8080/api/v1/administration/purge
```
* action: actiontype (only purge is currently available)
* type: purge type (strict = all data before this date)
* date: delete data before this date - in seconds(timestamp)




[Readme](03-frontend.md) <-- Previous | Next --> [Usage - First start](05-first_start.md)
