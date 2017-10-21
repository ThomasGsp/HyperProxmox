
    set req.http.X-Actual-IP = regsub(req.http.X-Forwarded-For, "[, ].*$", "");

    #Prevent hammering on wp-login page and users doing excessive searches (2 per second)
    if(vsthrottle.is_denied(req.http.X-Actual-IP, 10, 20s) && (req.url ~ "xmlrpc|wp-login.php|\?s\=")) {
                return (synth(429, "Too Many Request - Calm down"));
                # Use shield vmod to reset connection
                shield.conn_reset();
        }

    #Prevent users from making excessive POST requests that aren't for admin-ajax
    if(vsthrottle.is_denied(req.http.X-Actual-IP, 15, 10s) && ((!req.url ~ "\/wp-admin\/|(xmlrpc|admin-ajax)\.php") && (req.method == "POST"))){
                return (synth(429, "Too Many Requests"));
                # Use shield vmod to reset connection
                shield.conn_reset();
        }
