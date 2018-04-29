# HyperProxmox

HyperProxmox provides a centralized platform for managing your Proxmox environments.  
The web based client lets you manage the essential functions of your Proxmox infrastructure from any browser, 
offering more responsiveness and usability than ever before.  
Gain the visibility and control needed for your virtual machines, hosts and datastore.  
Assign users to custom roles, search in inventory or provision new virtual machines at the click of a button.

* Author :  [ThomasGSP](https://www.thomasgsp.fr)
* Date : 2017/2018
* Version : Alpha 1.0
* Status: Dev
* Object :   Massive LXC CT / KVM deployment, management and viewer system for Proxmox clusters.
* Proxmox version supported: 3.x/4.x/5/x
* Information : 
This project is currently in active development. 
You shouldn't use in production mode or... use at your risks !

### This version provide:
- Web interface to list instances, nodes and clusters
- Current usage (cpu / ram / disks...) for your nodes, instances...
- Quick usage visualisation by color (Green for low, yellow, red)
- Node scoring based on their usage
- Infrastructure historic
- Instance management (stop/start/restart...)
- Search system by VM-name, mac address ...
- Proxmox crawler (Get and store information)
- Security : Encipher the critical data (cluster access)
- LDAP authentication for web interface
- Group & cluster viewing in web interface
- Api

### Weak on this version (in progress):
- Logs system 
- Purge system 
- Crawler work without parallel tasks (can be a bit slow on large infrastructure) 

### This version don't provide (next features):
- Advanced management
- Provision new virtual machines
- ...

# Documentation
* [Prerequisites](doc/md/01-prerequisites.md)
* [Setup - Backend](doc/md/02-backend.md)
* [Setup - Frontend](doc/md/03-frontend.md)
* [Setup - Configs](doc/md/04-configs.md)
* [Usage - First start](doc/md/05-first_start.md)
* [Usage - Logs system](doc/md/06-logs.md)
* [Usage - API](doc/md/06-api.md)
* [Usage - Web interface](doc/md/08-usages.md)



