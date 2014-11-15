import pyutilib.workflow
import pyutilib.component.core

# @class:
class PluginTaskZ(pyutilib.workflow.TaskPlugin):

    pyutilib.component.core.alias('TaskZ')

    def __init__(self, *args, **kwds):
        """Constructor."""
        pyutilib.workflow.Task.__init__(self, *args, **kwds)
        self.inputs.declare('x')
        self.inputs.declare('y')
        self.add_argument('--x', dest='x', type=int)
        self.add_argument('--y', dest='y', type=int)
        self.outputs.declare('z')

    def execute(self):
        """Compute the sum of the inputs."""
        self.z = self.x + self.y

class PluginTaskY(pyutilib.workflow.TaskPlugin):

    pyutilib.component.core.alias('TaskY')

    def __init__(self, *args, **kwds):
        """Constructor."""
        pyutilib.workflow.Task.__init__(self, *args, **kwds)
        self.inputs.declare('X')
        self.inputs.declare('Y')
        self.add_argument('--X', dest='X', type=int)
        self.add_argument('--Y', dest='Y', type=int)
        self.outputs.declare('Z')

    def execute(self):
        """Compute the sum of the inputs."""
        self.Z = self.X * self.Y
# @:class
