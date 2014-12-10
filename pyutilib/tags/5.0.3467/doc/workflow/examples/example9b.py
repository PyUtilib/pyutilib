import pyutilib.workflow

# @code:
class TaskA(pyutilib.workflow.Task):

    def __init__(self, *args, **kwds):
        pyutilib.workflow.Task.__init__(self, *args, **kwds)
        self.inputs.declare('x', constant=True)
        self.inputs.declare('y')
        self.outputs.declare('z')

    def execute(self):
        """Compute the sum of the inputs."""
        self.z = self.x + self.y

class TaskZ(pyutilib.workflow.Task):

    def __init__(self, *args, **kwds):
        pyutilib.workflow.Task.__init__(self, *args, **kwds)
        self.inputs.declare('z', action='store_any')
        self.outputs.declare('z', self.inputs.z)

    def execute(self):
        pass

B = pyutilib.workflow.TaskFactory('workflow.switch')
A1 = TaskA()
A1.inputs.x = 1
B.add_branch('a', A1)
A2 = TaskA()
A2.inputs.x = -2
B.add_branch('b', A2)
Z = TaskZ()
Z.inputs.z = A1.outputs.z
Z.inputs.z = A2.outputs.z
w = pyutilib.workflow.Workflow()
w.add(B)

print("Branch a")
print(w(value='a', y=100))
w.reset()
print("Branch b")
print(w(value='b', y=100))
# @:code

try:
    print(w(value='c', y=100))
except ValueError:
    pass

