import pyutilib.workflow

# @class:
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
# @:class
# @usage:
A = TaskA()
w = pyutilib.workflow.Workflow()
w.add(A)
print(w(x=1, y=3))
# @:usage
