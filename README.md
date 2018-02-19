# HyperProxmox

* Author : Tlams
* Date : 2017/2018
* Version : Alpha 1.O
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
    
    
## Installation (Debian type - Full standalone stack)

### Install all packages
``` bash
apt-get nginx php-fpm php-curl php-json python3-pip python3-redis python3-netaddr mongodb nginx redis-server git
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
cd /opt/ && git git@github.com:ThomasGsp/HyperProxmox.git

# set www dir
mkdir /var/www/hyperproxmox
cp -R /opt/HyperProxmox/ /var/www/hyperproxmox/
chown www-data: -R /var/www/hyperproxmox
# No www-data write (useless)
chmod 550 -R /var/www/hyperproxmox

# Set hyperproxmox
chown hyperproxmox: -R /opt/HyperProxmox
chmod 760 -R /opt/HyperProxmox

# Log dir (you can change it)
mkdir /var/log/hyperproxmox/
chown hyperproxmox: /var/log/hyperproxmox/
```

``` bash
# Create system.d file
vi  /etc/systemd/system/hyperproxmox.service

[Unit]
Description=hyperproxmox - Service for Proxmox infrastructure
After=syslog.target network.target

[Service]
Type=simple
User=hyperproxmox
Group=hyperproxmox
WorkingDirectory=/opt/HyperProxmox/code/scripts/main
ExecStart=/usr/bin/python3.5 /opt/HyperProxmox/code/scripts/main/startup.py
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target

# enable it
systemctl enable hyperproxmox.service

```

``` bash
# Configurations
vi /opt/HyperProxmox/code/scripts/main/private/conf/config
< set your values >
```

### Init:
``` bash
# Start & generate your key
systemctl start hyperproxmox.service

< generate a key, with strong passphrase (SAVE IT!) >
```

### Insert your first cluster
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
