# First Start
Now, we are ready to start !  
In root, you can start directly HyperProxmox using the dedicated user.

``` bash
# Start & generate your key (root user/sudo)
runuser -l hyperproxmox -c '/usr/bin/python3.5 /opt/HyperProxmox/code/scripts/main/startup.py'
```

You should have this output:
``` bash
No key found, auto-generation started ...
```
If you don't have this output, probably that you miss a task (delete old keys) in "Backend" page.

``` bash
Need a passphrase to start the generation:
This action can take some minutes, please wait.
Your new key has been generate ! 
 - Private Key: private/keys/Ragnarok.pvt.key 
 - Public Key: private/keys/Ragnarok.pvt.key
You MUST save your passphrase hash in a security place !
Start API server...
http://127.0.0.1:8080/
```

Passphrase will be ask at each start.
Without it, the privite key can be read and the access cannot be load in the memory.
If you loose it, you must delete the keys and delete the different entries in the collection "clusters_conf" in mongoDB database.
Currently there are not system to provide a full reset function. Use MongoDB shell to do it.




[Config](04-configs.md) <-- Previous | Next --> [Usage - Logs](05-first_start.md)
