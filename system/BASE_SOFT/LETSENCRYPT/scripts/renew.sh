#!/usr/bin/env bash
for SITE in $(ls /etc/letsencrypt/live/)
do
	cd /etc/letsencrypt/live/$SITE
	cat fullchain.pem privkey.pem > /opt/certbot/$SITE.pem

done
