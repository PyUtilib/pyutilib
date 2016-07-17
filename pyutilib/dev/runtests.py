import os
import sys
import pyutilib.subprocess
import glob
import optparse

if sys.platform.startswith('win'):
    platform = 'win'
    use_exec = True
else:
    platform = 'linux'
    use_exec = True


def run(package, argv, use_exec=use_exec):
    parser = optparse.OptionParser(usage='run [OPTIONS] <dirs>')

    parser.add_option(
        '-v',
        '--verbose',
        action='store_true',
        dest='verbose',
        default=False,
        help='Verbose output')
    parser.add_option(
        '--coverage',
        action='store_true',
        dest='coverage',
        default=False,
        help='Enable the computation of coverage information')
    parser.add_option(
        '-p',
        '--package',
        action='store',
        dest='pkg',
        default='pyutilib',
        help='Limit the coverage to this package')
    parser.add_option(
        '-o',
        '--output',
        action='store',
        dest='output',
        default=None,
        help='Redirect output to a file')

    options, args = parser.parse_args(argv)

    if len(args) == 1:
        parser.print_help()
        sys.exit(1)

    _cat = os.environ.get('PYUTILIB_UNITTEST_CATEGORY', None)
    if _cat == 'performance':
        os.environ['NOSE_WITH_TESTDATA'] = '1'
        os.environ['NOSE_WITH_FORCED_GC'] = '1'
        attr = ['-a', 'performance', '--with-testdata']
    elif not _cat is None:
        attr = ['-a', _cat]
    else:
        attr = []

    if options.pkg != "":
        cpkg = ['--cover-package=%s' % options.pkg]
    else:
        cpkg = []
    if options.verbose:
        vflag = ['-v']
    else:
        vflag = []

    if options.coverage:
        coverage_flags = ['--with-coverage', '--cover-erase'] + cpkg
        os.environ['COVERAGE_FILE'] = os.getcwd() + os.sep + '.coverage'
    else:
        coverage_flags = []

    cwd = os.path.dirname(os.getcwd())

    dirs = set()
    if len(args[1:]) == 0:
        dirs.add(os.getcwd())
    for arg in args[1:]:
        for dir_ in glob.glob(arg):
            dirs.add(dir_)
    if len(dirs) == 0:
        print("No valid test directory has been specified!")
        return 1

    if platform == 'win':
        srcdirs = []
        for dir in glob.glob('*'):
            if os.path.isdir(dir):
                srcdirs.append(os.path.abspath(dir))
        os.environ['PYTHONPATH'] = os.pathsep.join(srcdirs)
        #cmd = [ os.path.join(sys.exec_prefix,'Scripts','python.exe'),
        #        os.path.join(sys.exec_prefix,'Scripts','nosetests-script.py') ]
        cmd = [os.path.join(sys.exec_prefix, 'Scripts', 'nosetests.exe')]
        os.environ['PATH'] = os.path.join(cwd,'Scripts') + os.pathsep + \
                             os.environ.get('PATH','')
    else:
        fname = os.path.join(sys.exec_prefix, 'bin', 'nosetests')
        if not os.path.exists(fname):
            cmd = ['nosetests']
        else:
            cmd = [fname]
        os.environ['PATH'] = os.path.join(cwd,'bin') + os.pathsep + \
                             os.environ.get('PATH','')

    cmd.extend(coverage_flags)
    cmd.extend(vflag)
    cmd.append('--with-xunit')
    cmd.append('--xunit-file=TEST-' + package + '.xml')
    cmd.extend(attr)
    cmd.extend(list(dirs))

    print("Running... " + ' '.join(cmd))
    print("")
    rc = 0
    if sys.platform.startswith('java'):
        import subprocess
        p = subprocess.Popen(cmd)
        p.wait()
        rc = p.returncode
    elif options.output:
        sys.stdout.write("Redirecting output to file '%s' ..." % options.output)
        sys.stdout.flush()
        rc, _ = pyutilib.subprocess.run(cmd, outfile=options.output)
        print("done.")
        sys.stdout.flush()
    elif use_exec:
        rc = None
        os.execvp(cmd[0], cmd)
    else:
        rc, _ = pyutilib.subprocess.run(cmd, tee=True)
    return rc


def runPyUtilibTests():
    parser = optparse.OptionParser(usage='test.pyutilib [options] <dirs>')

    parser.add_option(
        '-d',
        '--dir',
        action='store',
        dest='dir',
        default=None,
        help='Top-level source directory where the tests are applied.')
    parser.add_option(
        '--cat',
        '--category',
        action='store',
        dest='cat',
        default='smoke',
        help='Specify the test category.')
    parser.add_option(
        '--cov',
        '--coverage',
        action='store_true',
        dest='coverage',
        default=False,
        help='Indicate that coverage information is collected')
    parser.add_option(
        '-v',
        '--verbose',
        action='store_true',
        dest='verbose',
        default=False,
        help='Verbose output')
    parser.add_option(
        '-o',
        '--output',
        action='store',
        dest='output',
        default=None,
        help='Redirect output to a file')

    _options, args = parser.parse_args(sys.argv)

    if _options.output:
        outfile = os.path.abspath(_options.output)
    else:
        outfile = None
    if _options.dir is None:
        # the /src directory (for development installations)
        dir_ = os.path.dirname(
            os.path.dirname(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        os.chdir(dir_)
    else:
        if os.path.exists(_options.dir):
            os.chdir(_options.dir)

    print("Running tests in directory %s" % os.getcwd())
    _options.cat = os.environ.get('PYUTILIB_UNITTEST_CATEGORY', _options.cat)
    if _options.cat == 'all':
        if 'PYUTILIB_UNITTEST_CATEGORY' in os.environ:
            del os.environ['PYUTILIB_UNITTEST_CATEGORY']
    elif _options.cat:
        os.environ['PYUTILIB_UNITTEST_CATEGORY'] = _options.cat
        print(" ... for test category: %s" %
              os.environ['PYUTILIB_UNITTEST_CATEGORY'])

    options = []
    if _options.coverage:
        options.append('--coverage')
    if _options.verbose:
        options.append('-v')
    if outfile:
        options.append('-o')
        options.append(outfile)
    if len(args) == 1:
        dirs = ['pyutilib*']
    else:
        dirs = []
        for dir in args[1:]:
            if dir.startswith('-'):
                options.append(dir)
            if dir.startswith('pyutilib'):
                if os.path.exists(dir):
                    dirs.append(dir)
                elif '.' in dir:
                    dirs.append(
                        os.path.join('pyutilib', 'pyutilib', dir.split('.')[1]))
                else:
                    dirs.append(os.path.join('pyutilib', 'pyutilib'))
            else:
                if os.path.exists('pyutilib.' + dir):
                    dirs.append('pyutilib.' + dir)
                else:
                    dirs.append(os.path.join('pyutilib', 'pyutilib', dir))
        if len(dirs) == 0:
            dirs = ['pyutilib*']

    return pyutilib.dev.runtests.run(
        'pyutilib', ['runtests'] + options + ['-p', 'pyutilib'] + dirs)
