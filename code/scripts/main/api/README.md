### General

For all get request, there are a possibility to pass a payloads with differents param in json
```code
{'key1': 'value1', 'key2': 'value2'}
```

All actions need a valid ticket. This ticket is generate when the client valid the connexion on the backend php.
it's saved in the database with an expiration key.
Each tickets are uniq.

Example to dump database:
``` code
GET /api/v1/instance/<instanceid>/database/<databaseid>  -d '{'userid': '1', 'ticket': 'SFQSF22dFF','action': 'dump'}'
```

##### Instance management
Actions limited to proxmox api (wrapper)
```code
GET /api/v1/instance
GET /api/v1/instance/<instanceid>
POST /api/v1/instance/<instanceid>
PUT /api/v1/instance/<instanceid>
DELETE /api/v1/instance/<instanceid>
```

##### Packages management
Actions in the instances for packages managements
```code
GET /api/v1/instance/<instanceid>/package
POST /api/v1/instance/<instanceid>/packages
PUT /api/v1/instance/<instanceid>/packages
DELETE /api/v1/instance/<instanceid>/package
```

##### vhosts management
Actions in the instances for packages managements
```code
GET /api/v1/instance/<instanceid>/vhost
GET /api/v1/instance/<instanceid>/vhost/<vhostid>
POST /api/v1/instance/<instanceid>/vhost/<vhostid>
PUT /api/v1/instance/<instanceid>/vhost/<vhostid>
DELETE /api/v1/instance/<instanceid>/vhost/<vhostid>
```

##### Databases
Actions in the instances for packages managements
```code
GET /api/v1/instance/<instanceid>/database
GET /api/v1/instance/<instanceid>/database/<databaseid>
POST /api/v1/instance/<instanceid>/database/<databaseid>
PUT /api/v1/instance/<instanceid>/database/<databaseid>
DELETE /api/v1/instance/<instanceid>/database/<databaseid>
```

##### Nodes management
Actions to proxmox nodes availables
```code
GET /api/v1/node
GET /api/v1/node/<nodeid>
```

##### services management
```code
GET /api/v1/service/ssl/instance/<instanceid>/vhost/<vhostid>
GET /api/v1/service/ssl/instance/<instanceid>/vhost/<vhostid>
POST api/v1/service/ssl/instance/<instanceid>/vhost/<vhostid>
PUT /api/v1/service/ssl/instance/<instanceid>/vhost/<vhostid>
DELETE /api/v1/service/ssl/instance/<instanceid>/vhost/<vhostid>

GET /api/v1/service/cache/instance/<instanceid>/vhost/<vhostid>
GET /api/v1/service/cache/instance/<instanceid>/vhost/<vhostid>
POST api/v1/service/cache/instance/<instanceid>/vhost/<vhostid>
PUT /api/v1/service/cache/instance/<instanceid>/vhost/<vhostid>
DELETE /api/v1/service/cache/instance/<instanceid>/vhost/<vhostid>
```
