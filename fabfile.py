from fabric.api import *
from time import strftime, gmtime

env.forward_agent = True
env.roledefs = {
    'production': ['ubuntu@direct.conferencus.com'],
}

WEBSITE_PATH = "/var/www"

def deploy_server(version):
    with cd(WEBSITE_PATH):
        run('git fetch')
        run('git reset --hard %s' % version)

def restart_workers():
    sudo('supervisorctl reload')

@task
def deploy():
    time = strftime("%Y-%m-%d-%H.%M.%S", gmtime())
    tag = "prod/%s" % time
    local('git checkout master')
    local('git tag -a %s -m "Prod"' % tag)
    local('git push --tags')

    env.roles=['production']
    execute(deploy_server, tag)
    execute(restart_workers)

@task
def rollback(num_revs=1):
    with cd(WEBSITE_PATH):
        run('git fetch')
        tag = run('git tag -l prod/* | sort | tail -n' + \
            str(1 + int(num_revs)) + ' | head -n1')
        run('git checkout ' + tag)