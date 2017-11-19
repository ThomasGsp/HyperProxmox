# HyperProxmox

* Author : Tlams
* Date : 2017/2018
* Status: Dev
* Object :   Massive LXC CT / KVM deployment system for Proxmox clusters.

## Quick start

### Requirement:
* Proxmox server or cluster (or multiples clusters !)
* administrative pve user (full access)
* Vztemplate uploaded

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
