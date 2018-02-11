<?php

function ldaplogin($username, $password)
{
    require 'ldap.conf.php';
    $ldaprdn = 'cn='.$username.','.$ldapOrgUnit.','.$baseDN;
    $ldap = @ldap_connect($ldapserver, $ldapServerPort);
    ldap_set_option($ldap, LDAP_OPT_PROTOCOL_VERSION, 3);
    $bind = @ldap_bind($ldap, $ldaprdn, $password);
    if ($bind)
    {
        ldap_close($ldap);
        return true;
    }
    else
        return false;
}
