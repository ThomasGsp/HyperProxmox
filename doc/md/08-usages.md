# Usages

## API

Insert your first cluster (from host)
``` bash
# Minimum:
curl -H -XPOST -d '{
                        "name": "Cluster_name",
                        "url":"proxmox.cluster.net",
                        "port": "8006",
                        "user": "user@pve",
                        "password": "******",
                        "template": "",
                        "storage_disk": "",
                        "exclude_nodes": [""],
                        "groups" : [""],
                        "weight": 1 
                    }'  localhost:8080/api/v1/administration/cluster

# Other example:
curl -H -XPOST -d '{
                        "name": "Cluster_name",
                        "url":"proxmox.cluster.net",
                        "port": "8006",
                        "user": "user@pve",
                        "password": "******",
                        "template": "local:vztmpl/debian-9.0-standard_9.0-2_amd64.tar.gz",
                        "storage_disk": "disks",
                        "exclude_nodes": ["node_shit1"],
                        "groups" : ["group1", "group2..."],
                        "weight": 1 
                    }'  localhost:8080/api/v1/administration/cluster
                    
```

* "name": Symbolic cluster name. Should be uniq (string)  [VALUE NOT EMPTY REQUIRED]
* "url":  Proxmox - Web GUI URL access (string)           [VALUE NOT EMPTY REQUIRED] 
* "port": Proxmox - Web PORT access (string)              [VALUE NOT EMPTY REQUIRED]
* "user": Proxmox - Administrative PVE user (string)      [VALUE NOT EMPTY REQUIRED]
* "password": Proxmox - PVE password (string)             [VALUE NOT EMPTY REQUIRED]
* "template": Default template for LXC (string)
* "storage_disk": Default shared disk for KVM/LXC (string)
* "exclude_nodes": Do not use this nodes - Not visible (list) 
* "groups" : Symbolics groups for this node (list)
* "weight": Weight for the cluster auto-selection (int) [VALUE NOT EMPTY REQUIRED]


![alt text](https://github.com/ThomasGsp/HyperProxmox/blob/master/doc/screenshots/h-nodes.jpg)
![alt text](https://github.com/ThomasGsp/HyperProxmox/blob/master/doc/screenshots/h-vms.jpg)
![alt text](https://github.com/ThomasGsp/HyperProxmox/blob/master/doc/screenshots/h-sto.jpg)


[Usage - api](07-api.md) <-- Previous