import os
from contextlib import contextmanager

@contextmanager
def cd(newdir):
  prevdir = os.getcwd()
  os.chdir(os.path.expanduser(newdir))
  try:
    yield
  finally:
    os.chdir(prevdir)

CVS_MODULE_PATH = '/usr/local/projecto1/myapp'
GIT_PATH = '~/gitlab/myapp'
GITLAB_SSH_PORT = 8022

os.system('find {} | cvs-fast-export > ~/gitlab/stream.fe'.format(CVS_MODULE_PATH))
os.system('git init {}'.format(GIT_PATH))
with cd(GIT_PATH):
  os.system('git fast-import < ~/gitlab/stream.fe'.format(GIT_PATH))
  os.system('git remote rename origin old')
  os.system('git remote add origin ssh://git@localhost:{}/root/myapp.git'.format(GITLAB_SSH_PORT))
  os.system('git push -u origin --all')