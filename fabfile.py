from __future__ import with_statement
from fabric.api import run, sudo, cd, env, prefix, local
from fabric.contrib.console import confirm

env.hosts = ['localshot.org.il']
env.user = 'oshot'

def deploy(branch='master',flatblocks="no"):
    local('git push origin ' + branch)
    with cd('~oshot/src/oshot'):
        run('git pull origin ' + branch)
        with prefix('. ENV/bin/activate'):
            run('pip install -r requirements.txt')
            run('python manage.py test')
            if flatblocks[0] == "y":
                run('honcho run python manage.py loaddata < fixtures/flatblock.json')
            run('honcho run python manage.py syncdb --no-initial-data')
            run('honcho run python manage.py migrate --no-initial-data')
            run('honcho run python manage.py collectstatic --noinput')
    sudo('restart oshot')
