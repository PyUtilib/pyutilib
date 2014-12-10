import pyutilib.workflow

# @code:
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

B = pyutilib.workflow.TaskFactory('workflow.selection')
A = TaskA()
A.inputs.x = B.outputs.selection
w = pyutilib.workflow.Workflow()
w.add(B)

print(w(index='a', y=100, data={'a':1, 'b':2}))
w.reset()
print(w(index='b', y=100, data={'a':1, 'b':2}))
# @:code
