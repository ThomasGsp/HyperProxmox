# HyperProxmox

* Author : Tlams
* Date : 2017/2018
* Status: Dev
* Object :   Massive LXC CT / KVM deployment system for Proxmox clusters.

## Requirement:
* Proxmox infrastructure (standalone, clusters...)
    * Administrative pve user (full access)
    * Vztemplate uploaded

* MongoDB server
    * Version 3.6
    * Standalone or with replicats for hight availability
    
* Redis server

* Web stack
    * Nginx
    * PHP7
        * php-curl, php-mysql, php7.0-json

* Python softwares
    * Version 3.5 min
    * python-redis
    * pymongo
    * web.py
    * python-requests
    * Crypto
    
    
## Installation (Debian type - Full standalone stack)

### Install all packages
``` bash
apt-get nginx php-fpm php-curl php-json python3-pip python3-redis python3-netaddr mongodb redis-server
pip3 install pymongo db utils web.py requests
```

### Configurations (bases)

#### NGINX
``` bash
...

```
#### PHP
``` bash
...
```

#### Hyperproxmox
``` bash
...
```

### Init:
``` bash
# Start & generate your key
python3.5 startup.py
```

### Insert your first cluster
``` bash
curl -H -XPOST -d '{ "name": "Cluster_1",
                        "url":"proxmox.cluster.net",
                        "port": "8006",
                        "user": "user@pve",
                        "password": "******",
                        "template": "local:vztmpl/debian-9.0-standard_9.0-2_amd64.tar.gz",
                        "storage_disk": "disks",
                        "exclude_nodes": [""],
                        "weight": 1 }'  localhost:8080/api/v1/administration/cluster/new\
```

### Create your first CT
``` bash
curl -H -XPOST -d '{"count":"1"}' localhost:8080/api/v1/instance/new
```

### Delete it
``` bash
curl -XDELETE  localhost:8080/api/v1/instance/<id>
```
