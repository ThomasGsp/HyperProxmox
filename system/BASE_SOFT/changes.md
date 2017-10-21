
# Apache 2.4
apache2.conf --> ServerName
apache2.conf --> Header set X-Apache-Server-ID
sites-available --> 010-mywebsite.com.conf
010-mywebsite.com.conf --> ServerName
010-mywebsite.com.conf --> ServerAlias
010-mywebsite.com.conf --> DocumentRoot
010-mywebsite.com.conf --> mod_fastcgi
010-mywebsite.com.conf --> Directory
010-mywebsite.com.conf --> Header set X-Vhost-ID
.htpasswd --> ajout user random

# HaProxy
userlist htaccess