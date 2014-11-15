from pyutilib.workflow import *

class BusyResource(Resource):

    def __init__(self, name=None):
        resource.Resource.__init__(self)
        self._counter = 1

    def available(self):
        if self._counter > 0:
            print("BUSY %d" % self._counter)
            self._counter -= 1
            return False
        return True

class TaskA(pyutilib.workflow.Task):

    def __init__(self, *args, **kwds):
        pyutilib.workflow.Task.__init__(self, *args, **kwds)
        self.inputs.declare('x')
        self.outputs.declare('x', self.inputs.x)

    def execute(self):
        pass

A = TaskA()
A.add_resource(BusyResource())
w = pyutilib.workflow.Workflow()
w.add(A)

print(w(x=1))
