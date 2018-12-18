# Configs

Configurations are managed by a single point:

vi /opt/HyperProxmox/code/scripts/main/private/conf/config
``` bash
[system]
; System configurations
user: hyperproxmox
```
User created in the "Backend" page.   
This user will run HyperProxmox.

``` bash
; If not exist at startup, the key will be auto-generate.
key_pvt: private/keys/Ragnarok.pvt.key
key_pub: private/keys/Ragnarok.pub.key
```
Directory and private/public key generated to protect the critical data in MongoDB.  
Private key is set up with an Passphrase. You should save this keys in an other security place.  
Indeed, you can backup your MongoDB server, but without this key, the data will be not readable.

``` bash
admin_mail: tlams@localhost
```
Receive alerts and information by mail. Currently not implemented.

``` bash
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
```
Databases settings (backend).  
User / Password are not currently supported.  
Don't expose your database on 0.0.0.0 or without firewall.


``` bash
[deploy]
; Maximum concurrent deployment
; A high value can overcharge your physicals servers
concurrencydeploy: 2

; Delay between two deployment round
; If your infrastructure isn't very large, you should'nt reduce this delay.
; A low delay can overcharge your physicals servers
delayrounddeploy: 15
```
Currently not implemented (machine provision)


``` bash
[walker]
; Delay in seconds between to crawl (update)
walker: 300
```
Delay minimum between to crawling on your Proxmox infrastructure.  
A lock will block a new crawl if the precedent is not terminated. If this situation append, the next crawl is
canceled and reported to the next windows.
A delay too short can generate massive(and useless) data if your infrastructure is large ! 
```

``` bash
; Lock file -- prevent concurrent crawling
walker_lock: /tmp/hyperproxmoxwalker.lock
```
Lock file. The directory have to be writable by Hyperproxmox user.

``` bash
; Set an unique ID (change comment part)
uid = False
```
Work but useless in this version.  
HyperProxmox will set an unique ID in the comment area (machine configuration),
with in the future the goal to have the possibility to follow an virtual machine everywhere in the infrastructure.
The currents comments are not deleted, just reported after this ID.
  
``` bash
[logger]
; logs level    1: "INFO",  2: "WARNING", 3: "ERROR", 4: "CRITICAL",  5: "DEBUG"
logs_level = 5
```
Log level definite the logs verbosity.  
In production, you should definite this setting on "WARNING".  
In "DEBUG", hyperproxmox can generate lot of logs.
This system is currently only implemented on the main functions.

``` bash
; Limit IO write, if debug level is active, this value is overwrite to 0
bulk_write = 1

; Buffer size
bulk_size = 1000
```
The goal is to limit the I/O usage on your hard drive. 
HyperProxmox will save the logs in memory and write on the disk only when the buffer(bulk_size) is full.  


``` bash
; log output
logs_dir = /var/log/hyperproxmox/
```
Logs directory have to be writable by Hyperproxmox user.


#### Purge system
You should setup an cron to purge old data (not an obligation).  
This cron allow the possibility to delete automatically old data in your database.  

``` bash
RET=90 # older than the current date less this delay in days
DATETIMESTAMP=$(($(date +%s)-$((86400*$RET))))
0 0 * * * hyperproxmox curl -H -XPOST -d '{ "action": "purge", "type":"strict", "date": $DATETIMESTAMP }'  localhost:8080/api/v1/administration/purge >/var/log/hyperproxmox/purge.log 2>&1
```
* action: actiontype (only purge is currently available)
* type: purge type (strict = all data before this date)
* date: delete data before this date - in seconds(timestamp)

Currently, just one mod is available: strict.  
It's mean that ALL data will be delete before the date. 
Some others possibility should be available in the future, like keep one day per week.



[Setup - Frontend](03-frontend.md) <-- Previous | Next --> [Usage - First start](05-first_start.md)
