import pyutilib.workflow
import math

# @class:
class TaskD(pyutilib.workflow.Task):

    def __init__(self, *args, **kwds):
        """Constructor."""
        pyutilib.workflow.Task.__init__(self, *args, **kwds)
        self.inputs.declare('x', action='append')
        self.outputs.declare('z')

    def execute(self):
        """Compute the sum of the inputs."""
        self.z = sum(self.x)
# @:class

# @usage:
class TaskE(pyutilib.workflow.Task):

    def __init__(self, *args, **kwds):
        """Constructor."""
        pyutilib.workflow.Task.__init__(self, *args, **kwds)
        self.inputs.declare('Y')
        self.outputs.declare('Z')

    def execute(self):
        """Compute the sum of the inputs."""
        self.Z = int(math.floor(self.Y/7.0))

D = TaskD()

# there is currently an issue with memory leaks and the workflow/task/port structure.
# to correct this issue in the interim, all tasks that are to be retained in memory
# (not garbage collected) should be referenced by the user. thus, the introduction of 
# e_tasks. ultimately, the workflow should own a reference to all composite tasks.
e_tasks = []

for i in range(100):
    E = TaskE()
    e_tasks.append(E)
    D.inputs.x = E.outputs.Z

w = pyutilib.workflow.Workflow()
w.add(D)
print(w(Y=100))
# @:usage
