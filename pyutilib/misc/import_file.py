#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________

import os
import imp
import sys

import pyutilib.common

try:
    import runpy
    runpy_available = True
except ImportError:  #pragma:nocover
    try:
        import runpy2 as runpy
        runpy_available = True
    except ImportError:  #pragma:nocover
        runpy_available = False


def import_file(filename, context=None, name=None, clear_cache=False):
    """
    Import a Python file as a module

    The filename argument can be a module name or a python script
    (.py, .pyc).  The module name will be extracted from the filename
    argument by removing any directory components along with the
    .py (or .pyc) suffix if any of these exist. If the module name
    already appears in sys.modules, the corresponding module entry
    will be returned from this dictionary (unless clear_cache is
    True). Otherwise, an attempt will be made to import the module
    name extracted from the filename argument (using any directory
    information that was included).

    The name keyword can be used to always force reloading of the
    module from scratch. The module, if succesully imported, will be
    assigned the supplied name in sys.modules. This option is not
    currently supported for module names that contain one or more
    periods that indicate a submodule.

    This function returns the module object that is created.
    """

    #
    # Parse the filename to get the name of the module to be imported
    # and determine if it contains any directory information about
    # where to find the module.
    #
    dirname = os.path.dirname(filename)
    implied_dirname = None
    if dirname == '':
        dirname = None
        implied_dirname = os.path.dirname(os.path.abspath(filename))
    modulename = os.path.basename(filename)
    is_file = False
    # NB: endswith accepts tuples of strings starting in python 2.5.
    # For 2.4 compatibility we will call endswith() twice.
    if modulename.endswith('.py') or modulename.endswith('.pyc'):
        if not os.path.exists(filename):
            if not os.path.exists(os.path.expanduser(filename)):
                raise IOError("File %s does not exist" % (filename))
            filename = os.path.expanduser(filename)
        if filename.endswith('.pyc'):
            filename = filename[:-1]
        modulename = modulename.rsplit('.', 1)[0]
        is_file = True

    module = None
    # If the name keyword is not used we will first check if the
    # module name (as extracted from filename) already exists
    # sys.modules. Only if it does not already exist in sys.modules do
    # we try to import.
    # **NOTE**: This will ignore any directory specifications that
    #           were included in the filename, meaning
    #              filename=foo/bar.py
    #           would be overlooked if someone previously imported any
    #           module 'bar' from a different source. As a workaround
    #           for this issue, the 'name' keyword was added to this
    #           function, which indicates that the module source
    #           should be located, loaded from scratch, and assigned
    #           the module name specified by this keyword.
    if name is None:
        name = modulename
        if not clear_cache and modulename in sys.modules:
            module = sys.modules[modulename]
        else:
            if clear_cache and modulename in sys.modules:
                del sys.modules[modulename]
            if dirname is not None:
                sys.path.insert(0, dirname)
            else:
                sys.path.insert(0, implied_dirname)
            try:
                module = __import__(modulename)
            except ImportError:
                pass
            finally:
                if dirname is not None:
                    sys.path.remove(dirname)
                else:
                    sys.path.remove(implied_dirname)
            # This extra assignment seems redundant, but it is necessary
            # when the module name contains one or more periods to
            # indicate a submodule, in which case the __import__
            # function only returns the top level module. The true
            # submodule must be located inside the sys.modules dict.
            if modulename in sys.modules:
                module = sys.modules[modulename]

    # If we are entering this next block, it means that the optional
    # name keyword was used or that we encountered an issue with the
    # __import__ function (which can happen if the true filename on
    # disk contained periods in its name, e.g., file_1.0.py)
    if module is None:
        pathname = None
        if is_file:
            # .py or .pyc were found in the filename
            pathname = filename
        else:
            if dirname is not None:
                # find_module will return the .py file (never .pyc)
                fp, pathname, description = imp.find_module(modulename,
                                                            [dirname])
                fp.close()
            else:
                sys.path.insert(0, implied_dirname)
                try:
                    # find_module will return the .py file
                    # (never .pyc)
                    fp, pathname, description = imp.find_module(modulename)
                    fp.close()
                except ImportError:
                    raise
                finally:
                    sys.path.remove(implied_dirname)
        try:
            # Note: we are always handing load_source a .py file, but
            #       it will use the .pyc or .pyo file if it exists
            module = imp.load_source(name, pathname)
        except:
            et, e, tb = sys.exc_info()
            import traceback
            _, line, _, txt = traceback.extract_tb(tb, 2)[-1]
            import logging
            logger = logging.getLogger('pyutilib.misc')
            msg = ''
            if isinstance(e, Exception):
                msg = " raised %s:\n%s" % (et.__name__, e)
            logger.error('Failed to load python module "%s"\n'
                         '%s line %s ("%s")%s' %
                         (filename, pathname, line, txt, msg))
            raise

    #
    # Add module to the given context
    #
    if not context is None:
        context[name] = module
    return module


def run_file(filename, logfile=None, execdir=None):
    """
    Execute a Python file and optionally redirect output to a logfile.
    """
    if not runpy_available:  #pragma:nocover
        raise pyutilib.common.ConfigurationError(
            "Cannot apply the run_file() function because runpy is not available")
    #
    # Open logfile
    #
    if not logfile is None:
        sys.stderr.flush()
        sys.stdout.flush()
        save_stdout = sys.stdout
        save_stderr = sys.stderr
        OUTPUT = open(logfile, "w")
        sys.stdout = OUTPUT
        sys.stderr = OUTPUT
    #
    # Add the file directory to the system path
    #
    currdir_ = ''
    if '/' in filename:
        currdir_ = "/".join((filename).split("/")[:-1])
        tmp_import = (filename).split("/")[-1]
        sys.path.append(currdir_)
    elif '\\' in filename:
        currdir_ = "\\".join((filename).split("\\")[:-1])
        tmp_import = (filename).split("\\")[-1]
        sys.path.append(currdir_)
    else:
        tmp_import = filename
    name = ".".join((tmp_import).split(".")[:-1])
    #
    # Run the module
    #
    try:
        if not execdir is None:
            tmp = os.getcwd()
            os.chdir(execdir)
            tmp_path = sys.path
            sys.path = [execdir] + sys.path
        runpy.run_module(name, None, "__main__")
        if not execdir is None:
            os.chdir(tmp)
            sys.path = tmp_path
    except Exception:  #pragma:nocover
        if not logfile is None:
            OUTPUT.close()
            sys.stdout = save_stdout
            sys.stderr = save_stderr
        raise
    if currdir_ in sys.path:
        sys.path.remove(currdir_)
    if execdir in sys.path:
        sys.path.remove(execdir)
    #
    # Close logfile
    #
    if not logfile is None:
        OUTPUT.close()
        sys.stdout = save_stdout
        sys.stderr = save_stderr
