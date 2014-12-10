#  _________________________________________________________________________
#
#  PyUtilib: A Python utility library.
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  _________________________________________________________________________

import inspect
import sys
import os
import os.path
try:
    import unittest2 as unittest
except:
    import unittest
import pyutilib.misc.comparison
from pyutilib.misc.config import ConfigValue, ConfigBlock, ConfigList
currdir = os.path.dirname(os.path.abspath(__file__))

try:
    import yaml
    using_yaml=True
except ImportError:
    using_yaml=False


class Test(unittest.TestCase):

    def setUp(self):
        self.config = config = ConfigBlock(
            "Basic configuration for Flushing models" )
        net = config.declare('network', ConfigBlock())
        net.declare( 'epanet file', ConfigValue( 
                'Net3.inp', str, 
                'EPANET network inp file', 
                None ) )

        sc = config.declare('scenario', ConfigBlock(
                "Single scenario block" ) )
        sc.declare( 'scenario file', ConfigValue(
                'Net3.tsg', str,
                'Scenario generation file, see the TEVASIM documentation', 
                """This is the (long) documentation for the 'scenario
file' parameter.  It contains multiple lines, and some internal
formatting; like a bulleted list:
  - item 1
  - item 2
""" ) )
        sc.declare( 'merlion', ConfigValue( 
                False, bool, 
                'Water quality model',
                """This is the (long) documentation for the 'merlion'
parameter.  It contains multiple lines, but no apparent internal
formatting; so the outputter should re-warp everything.
""" ) )
        sc.declare( 'detection', ConfigValue(
                # Note use of lambda for an "integer list domain"
                [1,2,3], lambda x: list(int(i) for i in x),
                'Sensor placement list, epanetID',
                None ) )
    
        config.declare('scenarios', ConfigList(
                [], sc, 
                "List of scenario blocks", 
                None ) )

        config.declare('nodes', ConfigList(
                [], ConfigValue(0, int, 'Node ID', None), 
                "List of node IDs", 
                None ) )

        im = config.declare('impact', ConfigBlock())
        im.declare( 'metric', ConfigValue(
                'MC', str,
                'Population or network based impact metric',
                None ) )
        
        fl = config.declare( 'flushing', ConfigBlock() )
        n = fl.declare( 'flush nodes', ConfigBlock() )
        n.declare( 'feasible nodes', ConfigValue(
                'ALL', str,
                'ALL, NZD, NONE, list or filename',
                None ) )
        n.declare( 'infeasible nodes', ConfigValue(
                'NONE', str,
                'ALL, NZD, NONE, list or filename',
                None ) )
        n.declare( 'max nodes', ConfigValue(
                2, int,
                'Maximum number of nodes to flush',
                None ) )
        n.declare( 'rate', ConfigValue(
                600, float,
                'Flushing rate [gallons/min]',
                None ) )
        n.declare( 'response time', ConfigValue(
                60, float,
                'Time [min] between detection and flushing',
                None ) )
        n.declare( 'duration', ConfigValue(
                600, float,
                'Time [min] for flushing',
                None ) )
    
        v = fl.declare( 'close valves', ConfigBlock() )
        v.declare( 'feasible pipes', ConfigValue(
                'ALL', str,
                'ALL, DIAM min max [inch], NONE, list or filename',
                None ) )
        v.declare( 'infeasible pipes', ConfigValue(
                'NONE', str,
                'ALL, DIAM min max [inch], NONE, list or filename',
                None ) )
        v.declare( 'max pipes', ConfigValue(
                2, int,
                'Maximum number of pipes to close',
                None ) )
        v.declare( 'response time', ConfigValue(
                60, float,
                'Time [min] between detection and closing valves',
                None ) )
    
    
    # Utility method for generating and validating a template description
    def _validateTemplate(self, reference_template, **kwds):
        test = self.config.generate_yaml_template(**kwds)
        width = kwds.get('width', 80)
        indent = kwds.get('indent_spacing', 2)
        sys.stdout.write(test)
        for l in test.splitlines():
            self.assertLessEqual(len(l), width)
            if l.strip().startswith("#"):
                continue
            self.assertEqual((len(l)-len(l.lstrip())) % indent, 0)
        self.assertEqual(test, reference_template)


    def test_template_default(self):
        reference_template = """# Basic configuration for Flushing models
network:
  epanet file: Net3.inp     # EPANET network inp file
scenario:                   # Single scenario block
  scenario file: Net3.tsg   # Scenario generation file, see the TEVASIM
                            #   documentation
  merlion: false            # Water quality model
  detection: [1, 2, 3]      # Sensor placement list, epanetID
scenarios: []               # List of scenario blocks
nodes: []                   # List of node IDs
impact:
  metric: MC                # Population or network based impact metric
flushing:
  flush nodes:
    feasible nodes: ALL     # ALL, NZD, NONE, list or filename
    infeasible nodes: NONE  # ALL, NZD, NONE, list or filename
    max nodes: 2            # Maximum number of nodes to flush
    rate: 600.0             # Flushing rate [gallons/min]
    response time: 60.0     # Time [min] between detection and flushing
    duration: 600.0         # Time [min] for flushing
  close valves:
    feasible pipes: ALL     # ALL, DIAM min max [inch], NONE, list or filename
    infeasible pipes: NONE  # ALL, DIAM min max [inch], NONE, list or filename
    max pipes: 2            # Maximum number of pipes to close
    response time: 60.0     # Time [min] between detection and closing valves
"""
        self._validateTemplate(reference_template)

    def test_template_3space(self):
        reference_template = """# Basic configuration for Flushing models
network:
   epanet file: Net3.inp      # EPANET network inp file
scenario:                     # Single scenario block
   scenario file: Net3.tsg    # Scenario generation file, see the TEVASIM
                              #   documentation
   merlion: false             # Water quality model
   detection: [1, 2, 3]       # Sensor placement list, epanetID
scenarios: []                 # List of scenario blocks
nodes: []                     # List of node IDs
impact:
   metric: MC                 # Population or network based impact metric
flushing:
   flush nodes:
      feasible nodes: ALL     # ALL, NZD, NONE, list or filename
      infeasible nodes: NONE  # ALL, NZD, NONE, list or filename
      max nodes: 2            # Maximum number of nodes to flush
      rate: 600.0             # Flushing rate [gallons/min]
      response time: 60.0     # Time [min] between detection and flushing
      duration: 600.0         # Time [min] for flushing
   close valves:
      feasible pipes: ALL     # ALL, DIAM min max [inch], NONE, list or
                              #   filename
      infeasible pipes: NONE  # ALL, DIAM min max [inch], NONE, list or
                              #   filename
      max pipes: 2            # Maximum number of pipes to close
      response time: 60.0     # Time [min] between detection and closing
                              #   valves
"""
        self._validateTemplate(reference_template, indent_spacing=3)

    def test_template_4space(self):
        reference_template = """# Basic configuration for Flushing models
network:
    epanet file: Net3.inp       # EPANET network inp file
scenario:                       # Single scenario block
    scenario file: Net3.tsg     # Scenario generation file, see the TEVASIM
                                #   documentation
    merlion: false              # Water quality model
    detection: [1, 2, 3]        # Sensor placement list, epanetID
scenarios: []                   # List of scenario blocks
nodes: []                       # List of node IDs
impact:
    metric: MC                  # Population or network based impact metric
flushing:
    flush nodes:
        feasible nodes: ALL     # ALL, NZD, NONE, list or filename
        infeasible nodes: NONE  # ALL, NZD, NONE, list or filename
        max nodes: 2            # Maximum number of nodes to flush
        rate: 600.0             # Flushing rate [gallons/min]
        response time: 60.0     # Time [min] between detection and flushing
        duration: 600.0         # Time [min] for flushing
    close valves:
        feasible pipes: ALL     # ALL, DIAM min max [inch], NONE, list or
                                #   filename
        infeasible pipes: NONE  # ALL, DIAM min max [inch], NONE, list or
                                #   filename
        max pipes: 2            # Maximum number of pipes to close
        response time: 60.0     # Time [min] between detection and closing
                                #   valves
"""
        self._validateTemplate(reference_template, indent_spacing=4)

    def test_template_3space_narrow(self):
        reference_template = """# Basic configuration for Flushing models
network:
   epanet file: Net3.inp    # EPANET network inp file
scenario:                   # Single scenario block
   scenario file: Net3.tsg  # Scenario generation file, see the TEVASIM
                            #   documentation
   merlion: false           # Water quality model
   detection: [1, 2, 3]     # Sensor placement list, epanetID
scenarios: []               # List of scenario blocks
nodes: []                   # List of node IDs
impact:
   metric: MC               # Population or network based impact metric
flushing:
   flush nodes:
      feasible nodes: ALL     # ALL, NZD, NONE, list or filename
      infeasible nodes: NONE  # ALL, NZD, NONE, list or filename
      max nodes: 2            # Maximum number of nodes to flush
      rate: 600.0             # Flushing rate [gallons/min]
      response time: 60.0     # Time [min] between detection and
                              #   flushing
      duration: 600.0         # Time [min] for flushing
   close valves:
      feasible pipes: ALL     # ALL, DIAM min max [inch], NONE, list or
                              #   filename
      infeasible pipes: NONE  # ALL, DIAM min max [inch], NONE, list or
                              #   filename
      max pipes: 2            # Maximum number of pipes to close
      response time: 60.0     # Time [min] between detection and closing
                              #   valves
"""
        self._validateTemplate(reference_template, indent_spacing=3, width=72)


    def test_display_default(self):
        reference = """network:
  epanet file: Net3.inp
scenario:
  scenario file: Net3.tsg
  merlion: false
  detection: [1, 2, 3]
scenarios: []
nodes: []
impact:
  metric: MC
flushing:
  flush nodes:
    feasible nodes: ALL
    infeasible nodes: NONE
    max nodes: 2
    rate: 600.0
    response time: 60.0
    duration: 600.0
  close valves:
    feasible pipes: ALL
    infeasible pipes: NONE
    max pipes: 2
    response time: 60.0
"""
        test = self.config.display()
        sys.stdout.write(test)
        self.assertEqual(test, reference)

    def test_display_list(self):
        reference = """network:
  epanet file: Net3.inp
scenario:
  scenario file: Net3.tsg
  merlion: false
  detection: [1, 2, 3]
scenarios:
  -
    scenario file: Net3.tsg
    merlion: false
    detection: [1, 2, 3]
  -
    scenario file: Net3.tsg
    merlion: true
    detection: []
nodes: []
impact:
  metric: MC
flushing:
  flush nodes:
    feasible nodes: ALL
    infeasible nodes: NONE
    max nodes: 2
    rate: 600.0
    response time: 60.0
    duration: 600.0
  close valves:
    feasible pipes: ALL
    infeasible pipes: NONE
    max pipes: 2
    response time: 60.0
"""
        self.config['scenarios'].add()
        self.config['scenarios'].add({'merlion':True, 'detection':[]})
        test = self.config.display()
        sys.stdout.write(test)
        self.assertEqual(test, reference)

    def test_display_userdata_default(self):
        test = self.config.display('userdata')
        sys.stdout.write(test)
        self.assertEqual(test, "")

    def test_display_userdata_list(self):
        self.config['scenarios'].add()
        test = self.config.display('userdata')
        sys.stdout.write(test)
        self.assertEqual(test, """scenarios:
  -
""")

    def test_display_userdata_list_nonDefault(self):
        self.config['scenarios'].add()
        self.config['scenarios'].add({'merlion':True, 'detection':[]})
        test = self.config.display('userdata')
        sys.stdout.write(test)
        self.assertEqual(test, """scenarios:
  -
  -
    merlion: true
    detection: []
""")

    def test_display_userdata_block(self):
        self.config.add("foo", ConfigValue(0, int,None,None))
        self.config.add("bar", ConfigBlock())
        test = self.config.display('userdata')
        sys.stdout.write(test)
        self.assertEqual(test, "")

    def test_display_userdata_block_nonDefault(self):
        self.config.add("foo", ConfigValue(0, int,None,None))
        self.config.add("bar", ConfigBlock()).add("baz", ConfigBlock())
        test = self.config.display('userdata')
        sys.stdout.write(test)
        self.assertEqual(test, "bar:\n")


    def test_unusedUserValues_default(self):
        test = '\n'.join(x.name(True) for x in self.config.unused_user_values())
        sys.stdout.write(test)
        self.assertEqual(test, "")

    def test_unusedUserValues_scalar(self):
        self.config['scenario']['merlion'] = True
        test = '\n'.join(x.name(True) for x in self.config.unused_user_values())
        sys.stdout.write(test)
        self.assertEqual(test, "scenario.merlion")

    def test_unusedUserValues_list(self):
        self.config['scenarios'].add()
        test = '\n'.join(x.name(True) for x in self.config.unused_user_values())
        sys.stdout.write(test)
        self.assertEqual(test, """scenarios
scenarios[0]""")

    def test_unusedUserValues_list_nonDefault(self):
        self.config['scenarios'].add()
        self.config['scenarios'].add({'merlion':True, 'detection':[]})
        test = '\n'.join(x.name(True) for x in self.config.unused_user_values())
        sys.stdout.write(test)
        self.assertEqual(test, """scenarios
scenarios[0]
scenarios[1]
scenarios[1].merlion
scenarios[1].detection""")

    def test_unusedUserValues_list_nonDefault_listAccessed(self):
        self.config['scenarios'].add()
        self.config['scenarios'].add({'merlion':True, 'detection':[]})
        for x in self.config['scenarios']:
            pass
        test = '\n'.join(x.name(True) for x in self.config.unused_user_values())
        sys.stdout.write(test)
        self.assertEqual(test, """scenarios[0]
scenarios[1]
scenarios[1].merlion
scenarios[1].detection""")

    def test_unusedUserValues_list_nonDefault_itemAccessed(self):
        self.config['scenarios'].add()
        self.config['scenarios'].add({'merlion':True, 'detection':[]})
        self.config['scenarios'][1]['merlion'].value()
        test = '\n'.join(x.name(True) for x in self.config.unused_user_values())
        sys.stdout.write(test)
        self.assertEqual(test, """scenarios[0]
scenarios[1].detection""")

    def test_unusedUserValues_topBlock(self):
        self.config.add('foo', ConfigBlock())
        test = '\n'.join(x.name(True) for x in self.config.unused_user_values())
        sys.stdout.write(test)
        self.assertEqual(test, "")

    def test_unusedUserValues_subBlock(self):
        self.config['scenario'].add('foo', ConfigBlock())
        test = '\n'.join(x.name(True) for x in self.config.unused_user_values())
        sys.stdout.write(test)
        self.assertEqual(test, "scenario")


    def test_parseDisplayAndValue_default(self):
        if not using_yaml:
            self.skipTest("Cannot execute test because PyYAML is not available")
        test = self.config.display()
        sys.stdout.write(test)
        self.assertEqual(yaml.load(test), self.config.value())

    def test_parseDisplayAndValue_list(self):
        if not using_yaml:
            self.skipTest("Cannot execute test because PyYAML is not available")
        self.config['scenarios'].add()
        self.config['scenarios'].add({'merlion':True, 'detection':[]})
        test = self.config.display()
        sys.stdout.write(test)
        self.assertEqual(yaml.load(test), self.config.value())

    def test_parseDisplay_userdata_default(self):
        if not using_yaml:
            self.skipTest("Cannot execute test because PyYAML is not available")
        test = self.config.display('userdata')
        sys.stdout.write(test)
        self.assertEqual(yaml.load(test), None)

    def test_parseDisplay_userdata_list(self):
        if not using_yaml:
            self.skipTest("Cannot execute test because PyYAML is not available")
        self.config['scenarios'].add()
        test = self.config.display('userdata')
        sys.stdout.write(test)
        self.assertEqual(yaml.load(test), {'scenarios': [None]})

    def test_parseDisplay_userdata_list_nonDefault(self):
        if not using_yaml:
            self.skipTest("Cannot execute test because PyYAML is not available")
        self.config['scenarios'].add()
        self.config['scenarios'].add({'merlion':True, 'detection':[]})
        test = self.config.display('userdata')
        sys.stdout.write(test)
        self.assertEqual( yaml.load(test), 
                          { 'scenarios': 
                            [ None, 
                              {'merlion':True,'detection':[]}
                              ] } )

    def test_parseDisplay_userdata_block(self):
        if not using_yaml:
            self.skipTest("Cannot execute test because PyYAML is not available")
        self.config.add("foo", ConfigValue(0, int,None,None))
        self.config.add("bar", ConfigBlock())
        test = self.config.display('userdata')
        sys.stdout.write(test)
        self.assertEqual(yaml.load(test), None)

    def test_parseDisplay_userdata_block_nonDefault(self):
        if not using_yaml:
            self.skipTest("Cannot execute test because PyYAML is not available")
        self.config.add("foo", ConfigValue(0, int,None,None))
        self.config.add("bar", ConfigBlock()).add("baz", ConfigBlock())
        test = self.config.display('userdata')
        sys.stdout.write(test)
        self.assertEqual(yaml.load(test), {'bar': None})

    def test_value_ConfigValue(self):
        val = self.config['flushing']['flush nodes']['rate'].value()
        self.assertIs(type(val), float)
        self.assertEqual(val, 600.0)

    def test_value_ConfigList_empty(self):
        val = self.config['nodes'].value()
        self.assertIs(type(val), list)
        self.assertEqual(val, [])

    def test_value_ConfigList_simplePopulated(self):
        self.config['nodes'].add('1')
        self.config['nodes'].add(3)
        self.config['nodes'].add()
        val = self.config['nodes'].value()
        self.assertIs(type(val), list)
        self.assertEqual(len(val), 3)
        self.assertEqual(val, [1, 3, 0])

    def test_value_ConfigList_complexPopulated(self):
        self.config['scenarios'].add()
        val = self.config['scenarios'].value()
        self.assertIs(type(val), list)
        self.assertEqual(len(val), 1)
        self.assertEqual(val, [{'detection': [1, 2, 3], 
                                'merlion': False, 
                                'scenario file': 'Net3.tsg'}])

    def test_name(self):
        self.config['scenarios'].add()
        self.assertEqual(self.config.name(), "")
        self.assertEqual(self.config['scenarios'].name(), "scenarios")
        self.assertEqual(self.config['scenarios'][0].name(), "[0]")
        self.assertEqual(self.config['scenarios'][0]['merlion'].name(), 
                         "merlion")

    def test_name_fullyQualified(self):
        self.config['scenarios'].add()
        self.assertEqual(self.config.name(True), "")
        self.assertEqual(self.config['scenarios'].name(True), "scenarios")
        self.assertEqual(self.config['scenarios'][0].name(True), 
                         "scenarios[0]")
        self.assertEqual(self.config['scenarios'][0]['merlion'].name(True), 
                         "scenarios[0].merlion")

    
    def test_setValue_scalar(self):
        self.config['flushing']['flush nodes']['rate'] = 50
        val = self.config['flushing']['flush nodes']['rate'].value()
        self.assertIs(type(val), float)
        self.assertEqual( val, 50.0 )

    def test_setValue_scalar_badDomain(self):
        try:
            self.config['flushing']['flush nodes']['rate'] = 'a'
        except ValueError:
            pass
        else:
            self.fail('expected test to raise ValueError')
        val = self.config['flushing']['flush nodes']['rate'].value()
        self.assertIs(type(val), float)
        self.assertEqual( val, 600.0 )

    def test_setValue_scalarList(self):
        self.config['scenario']['detection'] = []
        val = self.config['scenario']['detection'].value()
        self.assertIs(type(val), list)
        self.assertEqual( val, [] )

    def test_setValue_scalarList_badDomain(self):
        try:
            self.config['scenario']['detection'] = 50
        except ValueError:
            pass
        else:
            self.fail('expected test to raise ValueError')
        val = self.config['scenario']['detection'].value()
        self.assertIs(type(val), list)
        self.assertEqual( val, [1,2,3] )

    def test_setValue_scalarList_badSubDomain(self):
        try:
            self.config['scenario']['detection'] = [5.5, 'a']
        except ValueError:
            pass
        else:
            self.fail('expected test to raise ValueError')
        val = self.config['scenario']['detection'].value()
        self.assertIs(type(val), list)
        self.assertEqual( val, [1,2,3] )

    def test_getItem_setItem(self):
        self.assertFalse(self.config._userAccessed)
        self.assertFalse(self.config._data['scenario']._userAccessed)
        self.assertFalse(self.config._data['scenario']._data['detection']\
                             ._userAccessed)

        self.assertFalse(self.config['scenario']['detection']._userAccessed)

        self.assertTrue(self.config._userAccessed)
        self.assertTrue(self.config._data['scenario']._userAccessed)
        self.assertFalse(self.config._data['scenario']._data['detection']\
                             ._userAccessed)

        self.assertFalse(self.config._userSet)
        self.assertFalse(self.config._data['scenario']._userSet)
        self.assertFalse(self.config['scenario']['detection']._userSet)

        self.assertEqual(self.config['scenario']['detection'].value(), [1,2,3])
        self.config['scenario']['detection'] = [ 42.5 ]
        self.assertEqual(self.config['scenario']['detection'].value(), [42])

        self.assertFalse(self.config._userSet)
        self.assertFalse(self.config._data['scenario']._userSet)
        self.assertTrue(self.config['scenario']['detection']._userSet)

    def test_generate_documentation(self):
        oFile = os.path.join(currdir,'test_reference.out')
        OUTPUT = open(oFile,'w')
        test = self.config.generate_documentation()
        OUTPUT.write(test)
        OUTPUT.close()
        self.assertFalse(pyutilib.misc.comparison.compare_file(oFile, oFile[:-4]+'.txt')[0])
        os.remove(oFile)

    def test_block_get(self):
        self.assertTrue('scenario' in self.config)
        self.assertNotEquals(self.config.get('scenario', 'bogus'), 'bogus')
        self.assertFalse('fubar' in self.config)
        self.assertEquals(self.config.get('fubar', 'bogus'), 'bogus')

    def test_block_keys(self):
        ref = ['scenario file','merlion','detection']

        # list of keys
        keys = self.config['scenario'].keys()
        self.assertIs( type(keys), list )
        self.assertEqual( keys, ref )
        # lists are independent
        self.assertFalse( keys is self.config['scenario'].keys() )

        # keys iterator
        keyiter = self.config['scenario'].iterkeys()
        self.assertIsNot( type(keyiter), list )
        self.assertEqual( list(keyiter), ref )
        # iterators are independent
        self.assertFalse( keyiter is self.config['scenario'].iterkeys() )

        # default iterator
        keyiter = self.config['scenario'].__iter__()
        self.assertIsNot( type(keyiter), list )
        self.assertEqual( list(keyiter), ref )
        # iterators are independent
        self.assertFalse( keyiter is self.config['scenario'].__iter__() )
        
    def test_block_values(self):
        ref = ['Net3.tsg', False, [1,2,3]]

        # list of values
        values = self.config['scenario'].values()
        self.assertIs( type(values), list )
        self.assertEqual( [x.value() for x in values], ref )
        # lists are independent
        self.assertFalse( values is self.config['scenario'].values() )

        # values iterator
        valueiter = self.config['scenario'].itervalues()
        self.assertIsNot( type(valueiter), list )
        self.assertEqual( [x.value() for x in valueiter], ref )
        # iterators are independent
        self.assertFalse( valueiter is self.config['scenario'].itervalues() )
        
    def test_block_items(self):
        ref = [ ('scenario file', 'Net3.tsg'), 
                ('merlion',False), 
                ('detection',[1,2,3]) ]

        # list of items
        items = self.config['scenario'].items()
        self.assertIs( type(items), list )
        self.assertEqual( [ (x[0],x[1].value()) for x in items ], ref )
        # lists are independent
        self.assertFalse( items is self.config['scenario'].items() )

        # items iterator
        itemiter = self.config['scenario'].iteritems()
        self.assertIsNot( type(itemiter), list )
        self.assertEqual( [ (x[0],x[1].value()) for x in itemiter ], ref )
        # iterators are independent
        self.assertFalse( itemiter is self.config['scenario'].iteritems() )

    def test_list_manipulation(self):
        self.assertEqual(len(self.config['scenarios']), 0)
        self.config['scenarios'].add()
        self.assertEqual(len(self.config['scenarios']), 1)
        self.config['scenarios'].add({'merlion':True, 'detection':[]})
        self.assertEqual(len(self.config['scenarios']), 2)
        test = self.config.display('userdata')
        sys.stdout.write(test)
        self.assertEqual(test, """scenarios:
  -
  -
    merlion: true
    detection: []
""")
        self.config['scenarios'][0] = {'merlion':True, 'detection':[]}
        self.assertEqual(len(self.config['scenarios']), 2)
        test = self.config.display('userdata')
        sys.stdout.write(test)
        self.assertEqual(test, """scenarios:
  -
    merlion: true
    detection: []
  -
    merlion: true
    detection: []
""")
        test = self.config['scenarios'].display()
        sys.stdout.write(test)
        self.assertEqual(test, """-
  scenario file: Net3.tsg
  merlion: true
  detection: []
-
  scenario file: Net3.tsg
  merlion: true
  detection: []
""")
       

if __name__ == "__main__":
    unittest.main()

 
