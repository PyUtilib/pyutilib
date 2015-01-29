import os

def strip_example(file):
    base, name = os.path.split(file)
    prefix = os.path.splitext(name)[0]
    if prefix.endswith('_strip'):
        return
    print "STRIPPING",file
    OUTPUT = open(base+'/'+prefix+'_strip.py','w')
    INPUT = open(file,'r')
    for line in INPUT:
        if line[0] == '#' and '@' in line:
            continue
        print >>OUTPUT, line,
    INPUT.close()
    OUTPUT.close()


for root, dirs, files in os.walk(os.path.abspath(os.path.dirname(__file__)), topdown=True):
    for name in files:
        if name == 'example_exec.py':
            continue
        if name.endswith('.py'):
            strip_example(root+'/'+name)
