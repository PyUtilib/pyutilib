import pyutilib.workflow
import os.path
import os
currdir = os.path.dirname(os.path.abspath(__file__))+os.sep

import sys
if sys.platform.startswith('win'):
    INPUT = open('example7a.txt','r')
    for line in INPUT:
        sys.stdout.write(line)
    INPUT.close()
else:

# @ex:
  class TaskH(pyutilib.workflow.Task):

    def __init__(self, *args, **kwds):
        """Constructor."""
        pyutilib.workflow.Task.__init__(self, *args, **kwds)
        self.inputs.declare('dir')
        self.outputs.declare('list')
        self.add_resource(pyutilib.workflow.ExecutableResource(executable='/bin/ls'))

    def execute(self):
        self.resource('ls').run(self.dir, logfile=currdir+'logfile', debug=True)
        self.list = []
        INPUT = open(currdir+'logfile','r')
        for line in INPUT:
            self.list.append( line.strip() )
        INPUT.close()
        self.list.sort()

  H = TaskH()
  w = pyutilib.workflow.Workflow()
  w.add(H)
  print(w(dir=currdir+'dummy'))
# @:ex

  if os.path.exists(currdir+'logfile'):
    os.remove(currdir+'logfile')
