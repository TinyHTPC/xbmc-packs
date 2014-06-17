#!/usr/bin/env python

import subprocess, signal
import os

p = subprocess.Popen(['ps', '-w'], stdout=subprocess.PIPE)
out, err = p.communicate()

for line in out.splitlines():
   if 'SickBeard.py' in line:
      pid = int(line.split(None, 1)[0])
      os.kill(pid, signal.SIGKILL)
   if 'CouchPotato.py' in line:
      pid = int(line.split(None, 1)[0])
      os.kill(pid, signal.SIGKILL)
   if 'Headphones.py' in line:
      pid = int(line.split(None, 1)[0])
      os.kill(pid, signal.SIGKILL)
