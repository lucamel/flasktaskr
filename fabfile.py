
# fabfile.py

from fabric.api import local, settings, abort
from fabric.contrib.console import confirm

def test():
    with settings(warn_only=True):
        result = local("nosetests -v", capture=True)
    if result.failed and not confirm("Tests failed. Continue?"):
        abort("Aborted at user request.")

def commit():
    message = input("Enter a git commit message: ")
    local("git add -A && git commit -am '{}'".format(message))

def push():
    local("git branch")
    branch = input("Which branch do you want to push to? ")
    local("git push origin {}".format(branch))

def prepare():
    test()
    commit()
    push()

def rollback():
    local("heroku rollback")