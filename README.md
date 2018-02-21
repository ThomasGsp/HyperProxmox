# HyperProxmox

* Author : Tlams
* Date : 2017/2018
* Version : Alpha 1.0
* Status: Dev
* Object :   Massive LXC CT / KVM deployment and management system for Proxmox clusters.
* Information : 
This project is currently in active development. 
You shouldn't use in production mode, use at your risks !

## Version informations:
* Provide:
    - Basic web interface to list instances, nodes and clusters (with details)
    - Basic instance management by the web interface(stop/start/restart...)
    - Proxmox data crawler 
    - API for the system management and data
    - Encipher the critical data (cluster access)

* Not provide:
    - Advanced security (No API/Web interface authentification - DO NOT EXPOSE API ON "0.0.0.0")
    - Instance deployment
    - Group & cluster viewing in web interface
    - Advanced logs system
    - Purge data system
    - Lot of others things

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



## Installation (Debian type - Full standalone stack)
### Install all packages
``` bash
apt-get install php-fpm php-curl php-json python3-pip python3-redis python3-netaddr mongodb nginx redis-server git
pip3 install pymongo db utils web.py requests
```

### Configurations (bases)

#### NGINX
``` bash
server {
   listen *:443 ssl;
   server_name youdomain.name;
   root /var/www/hyperproxmox;
   
   ssl on;
   ssl_certificate /etc/nginx/ssl/nginx.crt;
   ssl_certificate_key /etc/nginx/ssl/nginx.key;
   ssl_protocols       TLSv1 TLSv1.1 TLSv1.2;
   ssl_ciphers HIGH:!aNULL:!eNULL:!EXPORT:!CAMELLIA:!DES:!MD5:!PSK:!RC4;
   ssl_prefer_server_ciphers on;
   add_header Strict-Transport-Security "max-age=86400";

    location ~ \.php$ {
        include snippets/fastcgi-php.conf;
        fastcgi_pass unix:/var/run/php-www.sock;
    }
}

```
#### PHP
``` bash
[www]

user                         = www-data
group                        = www-data

listen                       = /var/run/php-www.sock
listen.owner                 = www-data
listen.group                 = www-data
listen.mode                  = 0660

pm                           = dynamic
pm.start_servers             = 5
pm.min_spare_servers         = 5
pm.max_spare_servers         = 35
pm.max_children              = 50

pm.max_requests              = 200

pm.status_path               = /fpm-status
ping.path                    = /ping
ping.response                = pong

request_slowlog_timeout = 0

request_terminate_timeout    = 0
catch_workers_output = yes

```

#### Hyperproxmox
``` bash
useradd hyperproxmox
cd /opt/ && git clone https://github.com/ThomasGsp/HyperProxmox.git

# set www dir
mkdir /var/www/hyperproxmox
cp -R /opt/HyperProxmox/code/web/www/* /var/www/hyperproxmox/
chown www-data: -R /var/www/hyperproxmox
# No www-data write (useless)
chmod 550 -R /var/www/hyperproxmox

# Set hyperproxmox
chown hyperproxmox: -R /opt/HyperProxmox
chmod 760 -R /opt/HyperProxmox

# Log dir (you can change it)
mkdir /var/log/hyperproxmox/
chown hyperproxmox: /var/log/hyperproxmox/

#Rm demo keys
rm /opt/HyperProxmox/code/scripts/main/private/keys/Ragnarok.p*
```

```

``` bash
# Configurations
vi /opt/HyperProxmox/code/scripts/main/private/conf/config
< set your values >
```

### Init:
``` bash
# Start & generate your key (root user/sudo)
runuser -l hyperproxmox -c '/usr/bin/python3.5 /opt/HyperProxmox/code/scripts/main/startup.py'

OUTPUT:
######################
No key found, auto-generation started ...
Need a passphrase to start the generation:
This action can take some minutes, please wait.
Your new key has been generate ! 
 - Private Key: private/keys/Ragnarok.pvt.key 
 - Public Key: private/keys/Ragnarok.pvt.key
Passphrase HASH: 10e06b990d44de0091a2(......)5591c161ecc35944fc69c4433a49d10fc6b04a33611
You MUST save your passphrase hash in a security place !
Start API server...
http://127.0.0.1:8080/
######################
```
The HASH will be ask at each start.
Without it, the privite key can be read and the access cannot be load in the memory.
If you loose it, you must delete the keys, delete the different entries in the collection "clusters_conf" in mongoDB database.


### Insert your first cluster (from host)
``` bash
curl -H -XPOST -d '{    "name": "Cluster_1",
                        "url":"proxmox.cluster.net",
                        "port": "8006",
                        "user": "user@pve",
                        "password": "******",
                        "template": "local:vztmpl/debian-9.0-standard_9.0-2_amd64.tar.gz",
                        "storage_disk": "disks",
                        "exclude_nodes": [""],
                        "groups" : ["group1", "group2..."],
                        "weight": 1 
                    }'  localhost:8080/api/v1/administration/cluster/new\
```

* "name": Symbolic cluster name. Should be uniq (string)
* "url":  Proxmox - Web GUI URL access (string)
* "port": Proxmox - Web PORT access (string)
* "user": Proxmox - Administrative PVE user (string)
* "password": Proxmox - PVE password (string)
* "template": Default template for LXC (string)
* "storage_disk": Default shared disk for KVM/LXC (string)
* "exclude_nodes": Do not use this nodes - Not visible (list) 
* "groups" : Symbolics groups for this node (list)
* "weight": Weight for the cluster auto-selection (int)


![alt text](https://github.com/ThomasGsp/HyperProxmox/blob/master/doc/screenshots/h-nodes.jpg)
![alt text](https://github.com/ThomasGsp/HyperProxmox/blob/master/doc/screenshots/h-vms.jpg)
![alt text](https://github.com/ThomasGsp/HyperProxmox/blob/master/doc/screenshots/h-sto.jpg)



## API Information

### General informations
``` bash
([a-z0-9]+) = MongoID
([0-9]+) = Timestamp/vmid
([0-9a-zA-Z\_\-]+) = Cluster/node name
```


### Instance status management
``` bash
'/api/v1/instance/id/([a-z0-9]+)/status/(start|stop|current|reset|shutdown)' | GET 
```

### Cluster management
``` bash
'/api/v1/administration/cluster/(?:[0-9a-zA-Z\_\-]+)' | GET - Return the informations for an specific cluster
                                                      | PUT - Update the configurations for an specific cluster
                                                      | DELETE - Delete the configuration for an specific cluster
                                                      
'/api/v1/administration/cluster/'                     | GET - Return all clusters information
'/api/v1/administration/cluster/new'                  | POST - Inster a new cluster
```

### Cache Data - MongoDB
This data are manage by the crawler, you can't insert or change data yourself
``` bash
# date/cluster/node/vmid
# Disks mapping
'/api/v1/static/disks/([0-9]+)/([0-9a-zA-Z\_\-]+)/([0-9a-zA-Z\_\-]+)/([0-9]+)' | GET - Return the informations for an specific disk
'/api/v1/static/disks/([0-9]+)/([0-9a-zA-Z\_\-]+)/([0-9a-zA-Z\_\-]+)/'         | GET - Return all disks used in a node
'/api/v1/static/disks/([0-9]+)/([0-9a-zA-Z\_\-]+)/'                            | GET - Return all disks used in a cluster
'/api/v1/static/disks/([0-9]+)/'                                               | GET - Return all disks

# Storages mapping
'/api/v1/static/storages/([0-9]+)/([0-9a-zA-Z\_\-]+)/([0-9a-zA-Z\_\-]+)/'    | GET - Return all storage used in a node
'/api/v1/static/storages/([0-9]+)/([0-9a-zA-Z\_\-]+)/'                       | GET - Return all storages used in a cluster
'/api/v1/static/storages/([0-9]+)/'                                          | GET - Return all storages

# Instances mapping
'/api/v1/static/instances/([0-9]+)/([0-9a-zA-Z\_\-]+)/([0-9a-zA-Z\_\-]+)/([0-9]+)  | GET - Return the informations for an specific instance
'/api/v1/static/instances/([0-9]+)/([0-9a-zA-Z\_\-]+)/([0-9a-zA-Z\_\-]+)/          | GET - Return all instances for a node
'/api/v1/static/instances/([0-9]+)/([0-9a-zA-Z\_\-]+)/                             | GET - Return all instances for a cluster
'/api/v1/static/instances/([0-9]+)                                                 | GET - Return all instances (the dump can be very big, in a large infrastructure)

# Nodes mapping
'/api/v1/static/(nodes)/([0-9]+)/([0-9a-zA-Z\_\-]+)/([0-9a-zA-Z\_\-]+)'            | GET - Return the informations for an specific node
'/api/v1/static/(nodes)/([0-9]+)/([0-9a-zA-Z\_\-]+)/'                              | GET - Return all nodes for a cluster
'/api/v1/static/(nodes)/([0-9]+)/'                                                 | GET - Return all nodes 

# cluster mapping
'/api/v1/static/(clusters)/([0-9]+)/(?:[0-9a-zA-Z\_\-]+)'                          | GET - Return the insformations for a specific cluster
'/api/v1/static/(clusters)/([0-9]+)/'                                              | GET - Return all cluster informations

# date
'/api/v1/static/dates/(all|last)'                                                  | GET - Return all or the last date available (generated by the crawler)

# mongoid
'/api/v1/static/(instances|nodes|clusters|storages|disks)/id/([a-z0-9]+)'          | GET - Return an information by mongoid
```

### Typical use
``` bash
curl  http://127.0.0.1:8080/api/v1/static/nodes/1519040226/Cluster_1/sd-817348
```
