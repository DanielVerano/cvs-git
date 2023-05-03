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

cvs_module_path = '/usr/local/projecto1/myapp'
git_path = '~/gitlab/myapp'

os.system('find {} | cvs-fast-export > ~/gitlab/stream.fe'.format(cvs_module_path))
os.system('git init {}'.format(git_path))
with cd(git_path):
  os.system('cd {}'.format(git_path))
  os.system('git fast-import < ~/gitlab/stream.fe'.format(git_path))

  os.system('git remote rename origin old')
  os.system('git remote add origin ssh://git@localhost:8022/root/myapp.git')
  os.system('git push -u origin --all')