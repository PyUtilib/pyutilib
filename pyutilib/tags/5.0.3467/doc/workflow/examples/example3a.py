import pyutilib.workflow

class TaskA(pyutilib.workflow.Task):

    def __init__(self, *args, **kwds):
        """Constructor."""
        pyutilib.workflow.Task.__init__(self, *args, **kwds)
        self.inputs.declare('x')
        self.inputs.declare('y')
        self.outputs.declare('z')

    def execute(self):
        """Compute the sum of the inputs."""
        self.z = self.x + self.y

# @class:
class TaskD(pyutilib.workflow.Task):

    def __init__(self, *args, **kwds):
        """Constructor."""
        pyutilib.workflow.Task.__init__(self, *args, **kwds)
        self.inputs.declare('X')
        self.inputs.declare('y')
        self.inputs.declare('a', constant=True)
        self.outputs.declare('W')
        self.outputs.declare('Z')

    def execute(self):
        """Compute the sum of the inputs."""
        self.W = self.X+self.y+self.a
        self.Z = 2*self.W
# @:class

A = TaskA()
D = TaskD()
D.inputs.a = 100
A.inputs.x = D.outputs.Z

w = pyutilib.workflow.Workflow()
w.add(A)
print(w(X=1, y=3))
