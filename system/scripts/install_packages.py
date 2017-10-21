import ConfigParser
import os

from fabric.contrib import files
from fabric.api import *
from fabric.utils import warn

SERVER_ROLES = ['cache']
env.user = 'root'
env.key_filename = '~/.ssh/id_rsa'


env.roledefs = dict.fromkeys(SERVER_ROLES, [])

# Directory structure
PROJECT_ROOT = os.path.dirname(__file__)
CONF_ROOT = os.path.join(PROJECT_ROOT, 'lamp-debian9')

def install_packages(*roles):
    """
    Install packages for the given roles.
    """
    roles = list(roles)
    if roles == ['all', ]:
        roles = SERVER_ROLES
    if 'base' not in roles:
        roles.insert(0, 'base')
    config_file = os.path.join(CONF_ROOT, u'debian9.ini' % env)
    print(config_file)
    config = ConfigParser.SafeConfigParser()
    config.read(config_file)
    for role in roles:
        if config.has_section(role):
            # Get ppas
            if config.has_option(role, 'ppas'):
                for ppa in config.get(role, 'ppas').split(' '):
                    sudo(u'add-apt-repository %s' % ppa)
            # Get sources
            if config.has_option(role, 'sources'):
                for section in config.get(role, 'sources').split(' '):
                    source = config.get(section, 'source')
                    key = config.get(section, 'key')
                    files.append(u'/etc/apt/sources.list', source, use_sudo=True)
                    sudo(u"wget -q %s -O - | sudo apt-key add -" % key)
            sudo(u"apt-get update")

            for package in config.get(role, 'packages'):
                if role == "database":
                    pass
                sudo(u"apt-get install -y %s" % package)




def install_mysql():
    with settings(hide('warnings', 'stderr'), warn_only=True):
        result = sudo('dpkg-query --show mysql-server')
    if result.failed is False:
        warn('MySQL is already installed')
        return
    mysql_password = prompt('Please enter MySQL root password:')
    sudo('echo "mysql-server-5.0 mysql-server/root_password password ' \
                              '%s" | debconf-set-selections' % mysql_password)
    sudo('echo "mysql-server-5.0 mysql-server/root_password_again password ' \
                              '%s" | debconf-set-selections' % mysql_password)
    apt_get('mysql-server')

def host_type():
    run('uname -s')