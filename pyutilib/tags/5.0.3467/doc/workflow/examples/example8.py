import pyutilib.workflow

# @class:
class TaskA(pyutilib.workflow.Task):

    def __init__(self, *args, **kwds):
        """Constructor."""
        pyutilib.workflow.Task.__init__(self, *args, **kwds)
        self.inputs.declare('z')
        self.outputs.declare('z')

    def execute(self):
        """Compute the sum of the inputs."""
        self.z = -1*self.z


class TaskB(pyutilib.workflow.Task):

    def __init__(self, *args, **kwds):
        """Constructor."""
        pyutilib.workflow.Task.__init__(self, *args, **kwds)
        self.inputs.declare('y')
        self.outputs.declare('y')

    def execute(self):
        """Compute the sum of the inputs."""
        self.y = -1*self.y

class TaskC(pyutilib.workflow.Task):

    def __init__(self, *args, **kwds):
        """Constructor."""
        pyutilib.workflow.Task.__init__(self, *args, **kwds)
        self.inputs.declare('x', action='store_any')
        self.outputs.declare('x')

    def execute(self):
        pass
# @:class

# @usage:
A = TaskA()
B = TaskB()

C = pyutilib.workflow.TaskFactory('workflow.branch')
C.add_branch(True, A)
C.add_branch(False, B)

D = TaskC()
D.inputs.x = A.outputs.z
D.inputs.x = B.outputs.y

w = pyutilib.workflow.Workflow()
w.add(C)

print(w(value=True, z=1, y=2))
w.reset()
print(w(value=False, z=1, y=2))
# @:usage
