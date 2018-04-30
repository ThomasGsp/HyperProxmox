# Prerequisites

## Your Proxmox infrastructure
For using this project, you need to have an pre-existing Proxmox infrastructure.  
If you want just test, a single Proxmox server with some machines is enough.  
In this case, your cluster is represented by your single node.  

You have to the possibility to access on the Proxmox API with an Administrative pve user (not root).  
Setting up Proxmox policies is out of scope for this tutorial.  
Report you to the official Proxmox documentation.  

## Environment
This project need an recent environment to work correctly.  
Typically, in this documentation, we'll use an Debian 9 environment.  
You can use an other distribution, but just check if theses software are available:

* Python 3.4 +  with python-redis, pymongo, webpy, python-request, python-crypto
* MongoDB 3.2 + / Redis
* Web server : Nginx (or apache)
* PHP(5 or 7) with this extensions: php-curl, php7.0-json 

This project is separate in two parts: Frontend and backend.  
Backend is writing in python and frontend in PHP/HTML/CSS/JS.
You have the possibility to use these two parts on different machines,
but due to performance you should use the same (low network latency).  
In more, the API authentication system is currently not implemented and this architecture can expose you
to security issues.

## Hardware
To run smoothly, the hardware requirement will depend to your goal and infrastructure.  
For a basic test, you can run this project on a very small machine (1cpu/2gb ram/10G disk) without problem.  
But on a large production system, it can need more resources, especially for the crawler and the databases.
If your Proxmox infrastructure is very large, the data generated can be really important,
and cause a slowly working if your hardware is too low.

In some case, it can be necessary to use an independent MongoDB server or cluster.

[Readme](../../README2.md) <-- Previous | Next --> [Setup - Backend](02-backend.md)
