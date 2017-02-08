import base64
import os
import re

from charms.reactive import hook, when, when_not, set_state, remove_state, is_state
from charmhelpers.core import hookenv
from charmhelpers.core.host import add_group, adduser, service_running, service_start, service_restart, chownr
from charmhelpers.core.templating import render
from charmhelpers.fetch import archiveurl, apt_install, apt_update
from charmhelpers.payload.archive import extract_tarfile
from charmhelpers.core.unitdata import kv


def get_install_context():
    """ Gives the installation context
    """
    return {
        'home': '/opt/gogs',
        'user': 'gogs',
        'group': 'gogs'
    }


def create_url(version):
    url = "https://cdn.gogs.io/gogs_%s_linux_amd64.tar.gz"
    vpart = 'v' + version if re.match(r'\d+(\.\d+)+', version) else version

    return url % vpart


@hook('install')
def install():
    conf = hookenv.config()
    version = conf.get('version', '0.9.97')
    context = get_install_context()

    handler = archiveurl.ArchiveUrlFetchHandler()
    handler.download(create_url(version), dest='/opt/gogs.tar.gz')

    extract_tarfile('/opt/gogs.tar.gz', destpath="/opt")

    # Create gogs user & group
    add_group(context['group'])
    adduser(context['user'], system_user=True)

    for dir in ('.ssh', 'repositories', 'data', 'logs'):
        os.makedirs(
            os.path.join(context['home'], dir), mode=0o700, exist_ok=True)
    os.makedirs(os.path.join(context['home'], 'custom', 'conf'),
                mode=0o755, exist_ok=True)
    chownr(context['home'], context['user'], context['group'], True, True)

    render(source='upstart',
           target="/etc/init/gogs.conf",
           perms=0o644,
           context=context)
    render(source='gogs.service',
           target="/lib/systemd/system/gogs.service",
           perms=0o644,
           context=context)
    hookenv.status_set('maintenance', 'installation complete')


@hook("config-changed")
def config_changed():
    conf = hookenv.config()
    for port in ('http_port', 'ssh_port'):
        if conf.changed(port) and conf.previous(port):
            hookenv.close_port(conf.previous(port))
        if conf.get(port):
            hookenv.open_port(conf[port])
    setup()


@when("db.database.available")
def db_available(db):
    unit_data = kv()
    unit_data.set('gogs.db', {
        'host': db.master.host,
        'port': db.master.port,
        'user': db.master.user,
        'password': db.master.password,
        'database': db.master.dbname,
    })
    setup()
    remove_state("db.database.available")


def setup():
    unit_data = kv()
    if not unit_data.get('gogs.db'):
        hookenv.status_set('blocked', 'need relation to postgresql')
        return

    secret_key = unit_data.get('gogs.secret_key')
    if not secret_key:
        secret_key = base64.b64encode(os.urandom(32)).decode('utf-8')
        unit_data.set('gogs.secret_key', secret_key)

    conf = hookenv.config()
    if not conf.get('host'):
        conf['host'] = hookenv.unit_public_ip()

    root = unit_data.get('gogs.root', '')
    if root and not root.endswith('/'):
        root = root + '/'

    install_context = get_install_context()

    render(source='app.ini',
           target="/opt/gogs/custom/conf/app.ini",
           perms=0o644,
           context={
               'conf': conf,
               'db': unit_data.get('gogs.db'),
               'secret_key': secret_key,
               'root': root,
               'home': install_context['home'],
               'user': install_context['user'],
           })
    restart_service()
    hookenv.status_set('active', 'ready')


@when("website.available")
def website_available(website):
    conf = hookenv.config()
    website.configure(conf['http_port'])


def restart_service():
    if service_running("gogs"):
        service_restart("gogs")
    else:
        service_start("gogs")
