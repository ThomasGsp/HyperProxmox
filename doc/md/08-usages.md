# Usages

## API

### New cluster
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

* "name": Symbolic cluster name. Should be unique (string)  [VALUE NOT EMPTY REQUIRED]
* "url":  Proxmox - Web GUI URL access (string)           [VALUE NOT EMPTY REQUIRED] 
* "port": Proxmox - Web PORT access (string)              [VALUE NOT EMPTY REQUIRED]
* "user": Proxmox - Administrative PVE user (string)      [VALUE NOT EMPTY REQUIRED]
* "password": Proxmox - PVE password (string)             [VALUE NOT EMPTY REQUIRED]
* "template": Default template for LXC (string)           [USELESS IN THIS VERSION]
* "storage_disk": Default shared disk for KVM/LXC (string) [USELESS IN THIS VERSION]
* "exclude_nodes": Do not use this nodes - Not visible (list) 
* "groups" : Symbolics groups for this node (list)
* "weight": Weight for the cluster auto-selection (int) [VALUE NOT EMPTY REQUIRED]


### Manage virtual machine (status)
To manage an virtual machine, there are two way: use MongoID or the long path.  
The first possibility is probably more efficient in a scripting/program way and the second for human.
Indeed, it's just a wrapper.

First possibility:
```bash
# 1 - Get the last date
curl '/api/v1/static/dates/last' 
{"value": 1525013945}

# 2 - Get VM-ID
curl  'http://127.0.0.1:8080/api/v1/static/instances/1525188197/Cluster_1/my_node/105'  
{"result": "OK", "value": [
 {"netin": 0,
  "name": "templatevm", 
  "type": "qemu", 
  "macaddr": ["BA:B6:C5:8C:F3:55"],
  "cluster": "Cluster_1", 
  "diskread": 0,
  "mem": 0, 
  "maxmem": 1073741824, 
  "_id": {"$oid": "5ae886660e8d893fd32734e8"}, 
  "disk": 0, 
  "node": "my_node",
  "netout": 0,
  "vmid": 105,
  "uptime": 0, 
  "uniqid": "1524672808.5396078_ULBPKPXZ",
  "template": "", 
  "diskwrite": 0, 
  "status": "stopped", 
  "cpu": 0, 
  "maxdisk": 53687091200,
  "date": 1525188197, 
  "cpus": 1, 
  "pid": null
 }
]}

# 3 - Action on VM
curl /api/v1/instance/id/5ae886660e8d893fd32734e8/status/start
{"result": "OK", "value": {"data": "UPID:sd-81592:00006C57:371A9F0B:5AE8884D:qmstart:105:api@pve:"}}%  
```

Second:
```bash
curl  'http://127.0.0.1:8080/api/v1/static/instances/last/Cluster_1/my_node/510/stop' 
{"result": "OK", "value": {'data': 'UPID:sd-81592:00003E35:379BC306:5AE9D2E7:qmstop:510:api@pve:'}}%  
```


[Usage - api](07-api.md) <-- Previous
