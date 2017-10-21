vcl 4.0;
import vsthrottle;
import shield;
import std;
import directors;

### {{{ PROBES, BACKENDS , ACLS , DIRECTORS
## Probes
include "includes/probes.vcl";

## Backends
include "includes/backends.vcl";

## ACLs
include "includes/acls.vcl";

## Directors
include "includes/directors.vcl";

### }}} PROBES, BACKENDS , ACLS , DIRECTORS

### {{{ RECV
sub vcl_recv {

    include "includes/wp-protection.vcl";

    if (req.restarts == 0) {
        if (req.http.X-Forwarded-For) {
            set req.http.X-Forwarded-For = req.http.X-Forwarded-For + ", " + client.ip;
        } else {
            set req.http.X-Forwarded-For = client.ip;
        }
    }

    # Normalisation des headers, suppression du port (si on utilise plusieurs ports TCP)
    set req.http.Host = regsub(req.http.Host, ":[0-9]+", "");

    # Normalisation des arguments
    # Mis en commentaire : probleme sur les cms wp, drupal etc
    # http://stackoverflow.com/questions/29929164/issue-with-wordpress-and-varnish-breaking-loadscript-php
    # set req.url = std.querysort(req.url);


    # Bye Bye w00tw00t
    if (req.url ~ "^/w00tw00t") {
        return (synth(404, "Not Found"));
    }

    # Authorisation pour les purge
    if (req.method == "PURGE") {
        if (!client.ip ~ purge) {
            # Non autorisé ! On lui fourni l'erreur 405 avec le message qui va bien,
            return (synth(405, "This IP is not allowed to send PURGE requests."));
        }
        # Autorisé on purge le cache demandé
        return (purge);
    }

    # Ne traiter que les type normaux, tout le reste est à passer directement aux backends
    if (req.method != "GET" &&
            req.method != "HEAD" &&
            req.method != "PUT" &&
            req.method != "POST" &&
            req.method != "TRACE" &&
            req.method != "OPTIONS" &&
            req.method != "PATCH" &&
            req.method != "DELETE") {
        return (pipe);
    }

    # Ne mettre en cache que les requetes de type GET ou HEAD. Ceci permet de s'assurer que les requetes POST sont transmises directement aux backends
    if (req.method != "GET" && req.method != "HEAD") {
        return (pass);
    }

    # Support de websocket , plus d'infos => https://www.varnish-cache.org/docs/4.0/users-guide/vcl-example-websockets.html
    if (req.http.Upgrade ~ "(?i)websocket") {
            return (pipe);
    }

    # Suppression des parametres ajouté par Google Analytics, inutile pour les backends
    if (req.url ~ "(\?|&)(utm_source|utm_medium|utm_campaign|gclid|cx|ie|cof|siteurl)=") {
        set req.url = regsuball(req.url, "&(utm_source|utm_medium|utm_campaign|gclid|cx|ie|cof|siteurl)=([A-z0-9_\-\.%25]+)", "");
        set req.url = regsuball(req.url, "\?(utm_source|utm_medium|utm_campaign|gclid|cx|ie|cof|siteurl)=([A-z0-9_\-\.%25]+)", "?");
        set req.url = regsub(req.url, "\?&", "?");
        set req.url = regsub(req.url, "\?$", "");
    }

    # Suppression des # envoyés pour le backend.
    if (req.url ~ "\#") {
        set req.url = regsub(req.url, "\#.*$", "");
    }

    # Suppression des / à la fin des Urls pour eviter le duplicate content
    if (req.url ~ "\?$") {
        set req.url = regsub(req.url, "\?$", "");
    }

    # Suppression de "has_js" cookie si present
    set req.http.Cookie = regsuball(req.http.Cookie, "has_js=[^;]+(; )?", "");

    # Suppression de tous les cookies basés sur Google Analytics
    set req.http.Cookie = regsuball(req.http.Cookie, "__utm.=[^;]+(; )?", "");
    set req.http.Cookie = regsuball(req.http.Cookie, "_ga=[^;]+(; )?", "");
    set req.http.Cookie = regsuball(req.http.Cookie, "utmctr=[^;]+(; )?", "");
    set req.http.Cookie = regsuball(req.http.Cookie, "utmcmd.=[^;]+(; )?", "");
    set req.http.Cookie = regsuball(req.http.Cookie, "utmccn.=[^;]+(; )?", "");

    # Remove DoubleClick offensive cookies
    set req.http.Cookie = regsuball(req.http.Cookie, "__gads=[^;]+(; )?", "");

    # Suppression des cookies de Quant Capital (ajoutés par certains plugin, all __qca)
    set req.http.Cookie = regsuball(req.http.Cookie, "__qc.=[^;]+(; )?", "");

    # Suppression des cookies AddThis
    set req.http.Cookie = regsuball(req.http.Cookie, "__atuvc=[^;]+(; )?", "");

    # Suppression du prefix ";" du cookies si present
    set req.http.Cookie = regsuball(req.http.Cookie, "^;\s*", "");

    # Cookies vides ou seulement avec des espaces ?
    if (req.http.cookie ~ "^\s*$") {
        unset req.http.cookie;
    }

    # Normalisation Accept-Encoding header
    # Cf manuel => https://www.varnish-cache.org/docs/3.0/tutorial/vary.html
    if (req.http.Accept-Encoding) {
        if (req.url ~ "\.(jpg|png|gif|gz|tgz|bz2|tbz|mp3|ogg)$") {
            unset req.http.Accept-Encoding;
        } elsif (req.http.Accept-Encoding ~ "gzip") {
            set req.http.Accept-Encoding = "gzip";
        } elsif (req.http.Accept-Encoding ~ "deflate") {
            set req.http.Accept-Encoding = "deflate";
        } else {
            # algorithm non connu
            unset req.http.Accept-Encoding;
        }
    }

    # On passe les gros fichiers directements aux backends pour eviter les resets de connexions | CF vcl_backend_response
    if (req.url ~ "^[^?]*\.(mp[34]|rar|tar|tgz|gz|wav|zip)(\?.*)?$") {
        unset req.http.Cookie;
        return (hash);
    }

    # Suppression des cookies sur les fichiers static
    if (req.url ~ "^[^?]*\.(bmp|bz2|css|doc|eot|flv|gif|gz|ico|jpeg|jpg|js|less|pdf|png|rtf|swf|txt|woff|xml)(\?.*)?$") {
        unset req.http.Cookie;
        return (hash);
    }

    # Envoie de Surrogate-Capability headers pour le support des ESI au niveau des backend
    set req.http.Surrogate-Capability = "key=ESI/1.0";

    if (req.http.Authorization) {
        # Ne pas mettre en cache par defaut
        return (pass);
    }

    return (hash);
}
### }}} RECV

 ### {{{ PIPE :: PASS 
sub vcl_pipe {
    # On renvoie toujours le X-Forwarded-For , pas uniquement sur la première requete envoyé aux backends
    set bereq.http.Connection = "Close";

    # Support de websocket , plus d'infos => https://www.varnish-cache.org/docs/4.0/users-guide/vcl-example-websockets.html
    if (req.http.upgrade) {
       set bereq.http.upgrade = req.http.upgrade;
    }
    return (pipe);
}

sub vcl_pass {
#    return (pass);
}

### }}} PIPE :: PASS

### {{{ HASH :: HIT :: MISS
sub vcl_hash {
    hash_data(req.url);

    if (req.http.host) {
        hash_data(req.http.host);
    } else {
        hash_data(server.ip);
    }

    if (req.http.Cookie) {
        hash_data(req.http.Cookie);
    }
}

sub vcl_hit {
    if (obj.ttl >= 0s) {
        return (deliver);
    }

    if (std.healthy(req.backend_hint)) {
       if (obj.ttl + 10s > 0s) {
           return (deliver);
       } else {
         return(fetch);
      }
    } else {
        if (obj.ttl + obj.grace > 0s) {
            return (deliver);
        } else {
            return (fetch);
        }
    }
    return (fetch);
}

sub vcl_miss {
    return (fetch);
}
### }}} HASH :: HIT :: MISS

### {{{ BACKEND RESPONSE
sub vcl_backend_response {
    # Parse des requetes ESI et suppression des headers Surrogate-Control
    if (beresp.http.Surrogate-Control ~ "ESI/1.0") {
        unset beresp.http.Surrogate-Control;
        set beresp.do_esi = true;
    }

    if (bereq.url ~ "^[^?]*\.(bmp|bz2|css|doc|eot|flv|gif|gz|ico|jpeg|jpg|js|less|mp[34]|pdf|png|rar|rtf|swf|tar|tgz|txt|wav|woff|xml|zip)(\?.*)?$") {
        unset beresp.http.set-cookie;
    }

    if (bereq.url ~ "^[^?]*\.(mp[34]|rar|tar|tgz|gz|wav|zip|bz2|xz|7z|avi|mov|ogm|mpe?g|mk[av])(\?.*)?$") {
        unset beresp.http.set-cookie;
        set beresp.do_stream = true;
        set beresp.do_gzip = false;
    }

    # On s'assure que s'il y a des 301 ou des 302 , les port TCP sont remis en place.
    if (beresp.status == 301 || beresp.status == 302) {
        set beresp.http.Location = regsub(beresp.http.Location, ":[0-9]+", "");
    }
    
        # On affiche le contenu en cache (Périmé) si les backends sont downs
    set beresp.grace = 6h;
    
    return (deliver);
}

### }}} BACKEND RESPONSE

### {{{ DELIVER
sub vcl_deliver {
    if (obj.hits > 0) {
        set resp.http.X-Cache = "HIT";
    } else {
        set resp.http.X-Cache = "MISS";
    }

    #if (resp.http.X-marker == "pass" ) {
    #      remove resp.http.X-marker;
    #      set resp.http.X-Varnish-Cache = "PASS";
    #}
    set resp.http.X-Cache-Hits = obj.hits;

    if (client.ip ~ debug) {
           set resp.http.X-Served-By = server.hostname;
           set resp.http.X-Varnish-Ip   = server.ip;
           set resp.http.X-Varnish-Port = std.port(server.ip);
    } else {
    # Suppression des headers: PHP version, Apache , OS ...
    unset resp.http.X-Powered-By;
    unset resp.http.Server;
    unset resp.http.X-Varnish;
    unset resp.http.Via;
    unset resp.http.Link;
    }

    return (deliver);
}
### }}} DELIVER

### {{{ SYNTH
sub vcl_synth {
    if (resp.status == 720) {
        set resp.http.Location = resp.reason;
        set resp.status = 301;
        set resp.reason = "Moved Permanently";
    } elseif (resp.status == 721) {
        set resp.http.Location = resp.reason;
        set resp.status = 302;
        set resp.reason = "Moved Temporary";
    }

    return (deliver);
}
### }}} SYNTH

### {{{ INIT
sub vcl_init {
    return (ok);
}

sub vcl_fini {
    return (ok);
}

 ### }}} INIT :: FINI 