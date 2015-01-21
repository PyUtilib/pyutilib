import pyutilib.workflow

# @ex:
class TaskF1(pyutilib.workflow.Task):

    def __init__(self, *args, **kwds):
        """Constructor."""
        pyutilib.workflow.Task.__init__(self, *args, **kwds)
        self.inputs.declare('a',)
        self.inputs.declare('aval')
        self.outputs.declare('a', self.inputs.a)
        self.outputs.declare('aval', self.inputs.aval)

    def execute(self):
        pass

class TaskF2(pyutilib.workflow.Task):

    def __init__(self, *args, **kwds):
        """Constructor."""
        pyutilib.workflow.Task.__init__(self, *args, **kwds)
        self.inputs.declare('A',)
        self.inputs.declare('Aval')
        self.outputs.declare('A', self.inputs.A)
        self.outputs.declare('Aval', self.inputs.Aval)

    def execute(self):
        pass

class TaskG(pyutilib.workflow.Task):

    def __init__(self, *args, **kwds):
        """Constructor."""
        pyutilib.workflow.Task.__init__(self, *args, **kwds)
        self.inputs.declare('x', action='map')
        self.inputs.declare('y', action='map')
        self.outputs.declare('z')

    def execute(self):
        """Compute the sum of the inputs."""
        self.z = {}
        for key in self.x:
            self.z[ self.x[key] ] = self.y[key]

F1 = TaskF1()
F2 = TaskF2()
G = TaskG()
G.inputs.x = F1.outputs.a
G.inputs.y = F1.outputs.aval
G.inputs.x = F2.outputs.A
G.inputs.y = F2.outputs.Aval

w = pyutilib.workflow.Workflow()
w.add(G)
print("IGNORE %s" % str(w(a='a', aval=1, A='A', Aval=2)))
# @:ex
