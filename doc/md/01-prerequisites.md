# Prerequisites

## Your Proxmox infrastructure
For using this project, you need have an pre-existing Proxmox infrastructure.  
To test, a single Proxmox server with some machines is enough.  
In this case, the cluster is represented by your single node.  

You should use a PVE user to access on the Proxmox API setup with administrative permissions.  
Setting up Proxmox policies and network is out of scope for this tutorial.  
See the official Proxmox documentation.  

## Environment
This project need a recent environment to work properly.  
In this documentation, we'll use an Debian 9 environment.  
You can use an other distribution, but just check if theses software are available on your distribution:

* Python 3.4 +  with python-redis, pymongo, webpy, python-request, python-crypto
* MongoDB 3.2 + / Redis
* Web server : Nginx (or apache)
* PHP(5 or 7) with this extensions: php-curl, php7.0-json 

This project is separate in two parts: frontend and backend.  
Backend is writing in python and frontend in PHP/HTML/CSS/JS.
You have the possibility to setup these two parts on different virtual machines,
but due to performance you should use the same (low network latency).  
In more, the API authentication system is currently not implemented and this kind of architecture can generate security issues.

## Hardware
To run smoothly, the hardware requirement will depend to your goal and infrastructure.  
For a basic test, you can run this project on a very small machine (1cpu/2gb ram/10G disk) without problem.  
But on a large production system, more resources can be necessary, especially for the crawler and the databases.
If your Proxmox infrastructure is very large, the data generated can be really important,
and cause a slowly working if your hardware is too weak.

[Readme](../../README2.md) <-- Previous | Next --> [Setup - Backend](02-backend.md)
