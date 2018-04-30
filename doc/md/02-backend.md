# Backend


### Databases
The backend need two database servers: MongoDB and Redis.  
MongoDB is the main data storage and redis is used like a cache system.  
HyperProxmox can run with default configuration, but you should setup redis to work in full memory, and the same
for the MongoDB indexes.
 
``` bash
apt-get install mongodb nginx redis-server
```

#### Setup Redis

Redis-server can work with a small memory-cache dedicated.

vi /etc/redis/redis.conf
```bash
# Networking
bind 127.0.0.1
port 6379
tcp-keepalive 60
 
# Maximum memory
maxmemory 256mb
maxmemory-policy allkeys-lru
 
# Disable disk persistence
appendonly no
save ""
```

#### Setup MongoDB

vi /etc/mongodb.conf
```bash
bind_ip = 127.0.0.1
port = 27017
```

## Install python

``` 
apt-get install python3-redis python3-netaddr python3-pip python3-webpy python3-requests
pip3 install pymongo
```

##  Install sources files
``` bash
apt-get install git

useradd hyperproxmox
cd /opt/ && git clone https://github.com/ThomasGsp/HyperProxmox.git

# Set hyperproxmox
chown hyperproxmox: -R /opt/HyperProxmox
chmod 760 -R /opt/HyperProxmox

# Log dir (you can change it)
mkdir /var/log/hyperproxmox/
chown hyperproxmox: /var/log/hyperproxmox/

#Rm demo keys
rm /opt/HyperProxmox/code/scripts/main/private/keys/Ragnarok.p*
```

[Prerequisites](01-prerequisites.md) <-- Previous | Next --> [Setup - Backend](03-frontend.md)
