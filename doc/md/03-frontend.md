# Frontend

###  Web server
The frontend is writing in php/html/css/js.  
You can use every web servers that support theses technologies.  
For this installation, we'll setting up nginx with php-fpm.

``` bash
apt-get install nginx php-fpm php-curl php-json
```

#### Nginx
vi /etc/nginx/sites-available/hyperproxmox.conf
``` bash
server {
   listen *:443 ssl;
   server_name yourdomain.name;
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

In this example, i used the pre-generates nginx key: "/etc/nginx/ssl/nginx.key"  
You should change this part and generate your keys.

#### Php-fpm
vi /etc/php/7.0/fpm/pool.d/www.conf
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

####  Web application
``` bash
# set www dir
mkdir /var/www/hyperproxmox
cp -R /opt/HyperProxmox/code/web/www/* /var/www/hyperproxmox/
chown www-data: -R /var/www/hyperproxmox
# No www-data write (useless)
chmod 550 -R /var/www/hyperproxmox
```

[Setup - Backend](02-backend.md) <-- Previous | Next --> [Setup - Configs](04-configs.md)
