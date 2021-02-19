#!/usr/bin/env python

from __future__ import print_function
from __future__ import unicode_literals
import sys
import os
import ctypes
import re

try:
   import numpy
except ImportError:
   print('Unable to import NumPy. Please ensure it is installed.')
   sys.exit(1)

def find_library(basedir, names):
    for name in names:
        path = os.path.join(basedir, name)
        if os.path.isfile(path):
            return path

def wrap(name):
    # Determine potential names of dynamic library.
    if os.name == 'nt':
       names = ('%s.dll' % name, 'lib%s.dll' % name)
    elif os.name == 'posix' and sys.platform == 'darwin':
       names = ('lib%s.dylib' % name,)
    else:
       names = ('lib%s.so' % name,)

    # Find FABM dynamic library.
    # Look first in pyfabm directory, then in Python path.
    path = find_library(os.path.dirname(os.path.abspath(__file__)), names)
    if not path:
        for basedir in sys.path:
            path = find_library(basedir, names)
            if path:
                break
        else:
            print('Unable to locate dynamic library %s (tried %s).' % (name, ', '.join(names),))
            return

    # Load FABM library.
    lib = ctypes.CDLL(str(path))

    # Driver settings (number of spatial dimensions, depth index)
    lib.get_driver_settings.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
    lib.get_driver_settings.restype = ctypes.c_void_p

    ndim_c = ctypes.c_int()
    idepthdim_c = ctypes.c_int()
    lib.get_driver_settings(ctypes.byref(ndim_c), ctypes.byref(idepthdim_c))
    assert idepthdim_c.value == -1, 'pyfabm currently only handles spatial domains without deph dimension'
    ndim_int = ndim_hz = ndim_c.value
    lib.ndim_int = ndim_int

    CONTIGUOUS = str('CONTIGUOUS')
    arrtype0D = numpy.ctypeslib.ndpointer(dtype=ctypes.c_double, ndim=0, flags=CONTIGUOUS)
    arrtype1D = numpy.ctypeslib.ndpointer(dtype=ctypes.c_double, ndim=1, flags=CONTIGUOUS)
    arrtypeInterior = numpy.ctypeslib.ndpointer(dtype=ctypes.c_double, ndim=ndim_int, flags=CONTIGUOUS)
    arrtypeHorizontal = numpy.ctypeslib.ndpointer(dtype=ctypes.c_double, ndim=ndim_hz, flags=CONTIGUOUS)
    arrtypeInteriorExt = numpy.ctypeslib.ndpointer(dtype=ctypes.c_double, ndim=ndim_int + 1, flags=CONTIGUOUS)
    arrtypeHorizontalExt = numpy.ctypeslib.ndpointer(dtype=ctypes.c_double, ndim=ndim_hz + 1, flags=CONTIGUOUS)
    arrtypeInteriorExt2 = numpy.ctypeslib.ndpointer(dtype=ctypes.c_double, ndim=ndim_int + 2, flags=CONTIGUOUS)
    arrtypeHorizontalExt2 = numpy.ctypeslib.ndpointer(dtype=ctypes.c_double, ndim=ndim_hz + 2, flags=CONTIGUOUS)

    # Initialization
    lib.create_model.argtypes = [ctypes.c_char_p] + [ctypes.c_int] * ndim_int
    lib.create_model.restype = ctypes.c_void_p

    # Access to model objects (variables, parameters, dependencies, couplings, model instances)
    lib.get_counts.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
    lib.get_counts.restype = None
    lib.get_variable_metadata.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
    lib.get_variable_metadata.restype = None
    lib.get_variable.argtypes = [ctypes.c_void_p, ctypes.c_int,ctypes.c_int]
    lib.get_variable.restype = ctypes.c_void_p
    lib.get_parameter_metadata.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
    lib.get_parameter_metadata.restype = None
    lib.get_model_metadata.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.POINTER(ctypes.c_int)]
    lib.get_model_metadata.restype = None
    lib.get_coupling.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(ctypes.c_void_p)]
    lib.get_coupling.restype = None
    lib.get_error_state.argtypes = []
    lib.get_error_state.restype = ctypes.c_int
    lib.get_error.argtypes = [ctypes.c_int, ctypes.c_char_p]
    lib.get_error.restype = None
    lib.reset_error_state.argtypes = []
    lib.reset_error_state.restype = None

    # Read access to variable attributes
    lib.variable_get_metadata.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p]
    lib.variable_get_metadata.restype = None
    lib.variable_get_background_value.argtypes = [ctypes.c_void_p]
    lib.variable_get_background_value.restype = ctypes.c_double
    lib.variable_get_long_path.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_char_p]
    lib.variable_get_long_path.restype = None
    lib.variable_get_output_name.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_char_p]
    lib.variable_get_output_name.restype = None
    lib.variable_get_suitable_masters.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    lib.variable_get_suitable_masters.restype = ctypes.c_void_p
    lib.variable_get_output.argtypes = [ctypes.c_void_p]
    lib.variable_get_output.restype = ctypes.c_int
    lib.variable_is_required.argtypes = [ctypes.c_void_p]
    lib.variable_is_required.restype = ctypes.c_int
    lib.variable_get_real_property.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_double]
    lib.variable_get_real_property.restype = ctypes.c_double

    # Read/write/reset access to parameters.
    lib.get_real_parameter.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
    lib.get_real_parameter.restype = ctypes.c_double
    lib.get_integer_parameter.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
    lib.get_integer_parameter.restype = ctypes.c_int
    lib.get_logical_parameter.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
    lib.get_logical_parameter.restype = ctypes.c_int
    lib.get_string_parameter.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_char_p]
    lib.get_string_parameter.restype = None
    lib.reset_parameter.argtypes = [ctypes.c_void_p, ctypes.c_int]
    lib.reset_parameter.restype = None
    lib.set_real_parameter.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_double]
    lib.set_real_parameter.restype = None
    lib.set_integer_parameter.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int]
    lib.set_integer_parameter.restype = None
    lib.set_logical_parameter.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int]
    lib.set_logical_parameter.restype = None
    lib.set_string_parameter.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p]
    lib.set_string_parameter.restype = None

    # Read access to lists of variables (e.g., suitable coupling targets).
    lib.link_list_count.argtypes = [ctypes.c_void_p]
    lib.link_list_count.restype = ctypes.c_int
    lib.link_list_index.argtypes = [ctypes.c_void_p, ctypes.c_int]
    lib.link_list_index.restype = ctypes.c_void_p
    lib.link_list_finalize.argtypes = [ctypes.c_void_p]
    lib.link_list_finalize.restype = None

    # Routines for sending pointers to state and dependency data.
    lib.link_interior_state_data.argtypes = [ctypes.c_void_p, ctypes.c_int, arrtypeInterior]
    lib.link_interior_state_data.restype = None
    lib.link_surface_state_data.argtypes = [ctypes.c_void_p, ctypes.c_int, arrtypeHorizontal]
    lib.link_surface_state_data.restype = None
    lib.link_bottom_state_data.argtypes = [ctypes.c_void_p, ctypes.c_int, arrtypeHorizontal]
    lib.link_bottom_state_data.restype = None
    lib.link_interior_data.argtypes = [ctypes.c_void_p, ctypes.c_void_p, arrtypeInterior]
    lib.link_interior_data.restype = None
    lib.link_horizontal_data.argtypes = [ctypes.c_void_p, ctypes.c_void_p, arrtypeHorizontal]
    lib.link_horizontal_data.restype = None
    lib.link_scalar.argtypes = [ctypes.c_void_p, ctypes.c_void_p, arrtype0D]
    lib.link_scalar.restype = None

    # Read access to diagnostic data.
    lib.get_interior_diagnostic_data.argtypes = [ctypes.c_void_p, ctypes.c_int]
    lib.get_interior_diagnostic_data.restype = ctypes.POINTER(ctypes.c_double)
    lib.get_horizontal_diagnostic_data.argtypes = [ctypes.c_void_p, ctypes.c_int]
    lib.get_horizontal_diagnostic_data.restype = ctypes.POINTER(ctypes.c_double)

    lib.start.argtypes = [ctypes.c_void_p]
    lib.start.restype = None

    # Routine for retrieving source-sink terms for the interior domain.
    lib.get_sources.argtypes = [ctypes.c_void_p, ctypes.c_double, arrtypeInteriorExt, arrtypeHorizontalExt, arrtypeHorizontalExt, ctypes.c_int, ctypes.c_int, arrtypeInterior]
    lib.get_sources.restype = None
    lib.check_state.argtypes = [ctypes.c_void_p, ctypes.c_int]
    lib.check_state.restype = ctypes.c_int

    # Routine for getting git repository version information.
    lib.get_version.argtypes = (ctypes.c_int, ctypes.c_char_p)
    lib.get_version.restype = None

    if ndim_int == 0:
        lib.integrate.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, arrtype1D, arrtypeInteriorExt, arrtypeInteriorExt2, ctypes.c_double, ctypes.c_int, ctypes.c_int, arrtypeInterior]
        lib.integrate.restype = None

    return lib

fabm_0d = wrap('fabm_0d')
fabm_1d = wrap('fabm_1d')
if fabm_0d is None or fabm_1d is None:
    sys.exit(1)

INTERIOR_STATE_VARIABLE        = 1
SURFACE_STATE_VARIABLE         = 2
BOTTOM_STATE_VARIABLE          = 3
INTERIOR_DIAGNOSTIC_VARIABLE   = 4
HORIZONTAL_DIAGNOSTIC_VARIABLE = 5
CONSERVED_QUANTITY             = 6
INTERIOR_DEPENDENCY            = 7
HORIZONTAL_DEPENDENCY          = 8
SCALAR_DEPENDENCY              = 9
ATTRIBUTE_LENGTH               = 256

unicodesuperscript = {'1':'\u00B9','2':'\u00B2','3':'\u00B3',
                      '4':'\u2074','5':'\u2075','6':'\u2076',
                      '7':'\u2077','8':'\u2078','9':'\u2079',
                      '0':'\u2070','-':'\u207B'}
unicodesubscript = {'1':'\u2081','2':'\u2082','3':'\u2083',
                    '4':'\u2084','5':'\u2085','6':'\u2086',
                    '7':'\u2087','8':'\u2088','9':'\u2089',
                    '0':'\u2080'}
supnumber = re.compile(r'(?<=\w)(-?\d+)(?=[ \*+\-/]|$)')
supenumber = re.compile(r'(?<=\d)e(-?\d+)(?=[ \*+\-/]|$)')
oldsupminus = re.compile(r'/(\w+)(?:\*\*|\^)(\d+)(?=[ \*+\-/]|$)')
oldsup = re.compile(r'(?<=\w)(?:\*\*|\^)(-?\d+)(?=[ \*+\-/]|$)')
oldsub = re.compile(r'(?<=\w)_(-?\d+)(?=[ \*+\-/]|$)')
def createPrettyUnit(unit):
    def replace_superscript(m):
        return ''.join([unicodesuperscript[n] for n in m.group(1)])
    def replace_subscript(m):
        return ''.join([unicodesubscript[n] for n in m.group(1)])
    def reple(m):
        return '\u00D710%s' % ''.join([unicodesuperscript[n] for n in m.group(1)])
    def reploldminus(m):
        return ' %s\u207B%s' % (m.group(1),''.join([unicodesuperscript[n] for n in m.group(2)]))
    #def replold(m):
    #    return u'%s%s' % (m.group(1),u''.join([unicodesuperscript[n] for n in m.group(2)]))
    unit = oldsup.sub(replace_superscript,unit)
    unit = oldsub.sub(replace_subscript,unit)
    unit = supenumber.sub(reple,unit)
    unit = supnumber.sub(replace_superscript,unit)
    #unit = oldsupminus.sub(reploldminus,unit)
    return unit

class FABMException(Exception):
    pass

def hasError():
   return fabm_0d.get_error_state() != 0 or fabm_1d.get_error_state() != 0

def getError():
    if fabm_0d.get_error_state() != 0:
        strmessage = ctypes.create_string_buffer(1024)
        fabm_0d.get_error(1024, strmessage)
        return strmessage.value.decode('ascii')
    if fabm_1d.get_error_state() != 0:
        strmessage = ctypes.create_string_buffer(1024)
        fabm_1d.get_error(1024, strmessage)
        return strmessage.value.decode('ascii')

def printTree(root, stringmapper, indent=''):
    """Print an indented tree of objects, encoded by dictionaries linking the names of children to
    their subtree, or to their object. Objects are finally printed as string obtained by
    calling the provided stringmapper method."""
    for name, item in root.items():
        if isinstance(item, dict):
            print('%s%s' % (indent, name))
            printTree(item, stringmapper, indent + '   ')
        else:
            print('%s%s = %s' % (indent, name, stringmapper(item)))

class Variable(object):
    def __init__(self, model, name=None, units=None, long_name=None, path=None, variable_pointer=None):
        self.model = model
        self.variable_pointer = variable_pointer
        if variable_pointer:
           strname = ctypes.create_string_buffer(ATTRIBUTE_LENGTH)
           strunits = ctypes.create_string_buffer(ATTRIBUTE_LENGTH)
           strlong_name = ctypes.create_string_buffer(ATTRIBUTE_LENGTH)
           self.model.fabm.variable_get_metadata(variable_pointer, ATTRIBUTE_LENGTH, strname, strunits, strlong_name)
           name = strname.value.decode('ascii')
           units = strunits.value.decode('ascii')
           long_name = strlong_name.value.decode('ascii')

        self.name = name
        self.units = units
        self.units_unicode = None if units is None else createPrettyUnit(units)
        self.long_name = long_name or name
        self.path = path or name

    @property
    def long_path(self):
        if self.variable_pointer is None:
            return self.long_name
        strlong_name = ctypes.create_string_buffer(ATTRIBUTE_LENGTH)
        self.model.fabm.variable_get_long_path(self.variable_pointer, ATTRIBUTE_LENGTH, strlong_name)
        return strlong_name.value.decode('ascii')

    @property
    def output_name(self):
        if self.variable_pointer is None:
            return self.name
        stroutput_name = ctypes.create_string_buffer(ATTRIBUTE_LENGTH)
        self.model.fabm.variable_get_output_name(self.variable_pointer, ATTRIBUTE_LENGTH, stroutput_name)
        return stroutput_name.value.decode('ascii')

    def getOptions(self):
        pass

    def getRealProperty(self, name, default=-1.0):
        return self.model.fabm.variable_get_real_property(self.variable_pointer, name.encode('ascii'), default)

class Dependency(Variable):
    def __init__(self, model, variable_pointer, data):
        Variable.__init__(self, model, variable_pointer=variable_pointer)
        self.data = data
        self.is_set = False

    def getValue(self):
        return self.data

    def setValue(self, value):
        self.is_set = True
        self.data[...] = value

    value = property(getValue, setValue)

    @property
    def required(self):
        return self.model.fabm.variable_is_required(self.variable_pointer) != 0

class StateVariable(Variable):
    def __init__(self, model, variable_pointer, data):
        Variable.__init__(self, model, variable_pointer=variable_pointer)
        self.data = data

    def getValue(self):
        return self.data

    def setValue(self, value):
        self.data[...] = value

    value = property(getValue, setValue)

    @property
    def background_value(self):
        return self.model.fabm.variable_get_background_value(self.variable_pointer)

    @property
    def output(self):
        return self.model.fabm.variable_get_output(self.variable_pointer) != 0

class DiagnosticVariable(Variable):
    def __init__(self, model, variable_pointer, index, horizontal):
        Variable.__init__(self, model, variable_pointer=variable_pointer)
        self.data = None

    def getValue(self):
        return self.data

    @property
    def output(self):
        return self.model.fabm.variable_get_output(self.variable_pointer) != 0

    value = property(getValue)

class Parameter(Variable):
    def __init__(self, model, name, index, units=None, long_name=None, type=None, has_default=False):
        Variable.__init__(self, model, name, units, long_name)
        self.type = type
        self.index = index + 1
        self.has_default = has_default

    def getValue(self,default=False):
        default = 1 if default else 0
        if self.type == 1:
            return self.model.fabm.get_real_parameter(self.model.pmodel, self.index, default)
        elif self.type == 2:
            return self.model.fabm.get_integer_parameter(self.model.pmodel, self.index, default)
        elif self.type == 3:
            return self.model.fabm.get_logical_parameter(self.model.pmodel, self.index, default) != 0
        elif self.type == 4:
            result = ctypes.create_string_buffer(ATTRIBUTE_LENGTH)
            self.model.fabm.get_string_parameter(self.model.pmodel, self.index, default, ATTRIBUTE_LENGTH, result)
            return result.value.decode('ascii')

    def setValue(self,value):
        settings = self.model.saveSettings()

        if self.type == 1:
            self.model.fabm.set_real_parameter(self.model.pmodel, self.name.encode('ascii'), value)
        elif self.type == 2:
            self.model.fabm.set_integer_parameter(self.model.pmodel, self.name.encode('ascii'), value)
        elif self.type == 3:
            self.model.fabm.set_logical_parameter(self.model.pmodel, self.name.encode('ascii'), value)
        elif self.type == 4:
            self.model.fabm.set_string_parameter(self.model.pmodel, self.name.encode('ascii'), value)

        # Update the model configuration (arrays with variables and parameters have changed)
        self.model.updateConfiguration(settings)

    def getDefault(self):
        if not self.has_default:
            return None
        return self.getValue(True)

    def reset(self):
        settings = self.model.saveSettings()
        self.model.fabm.reset_parameter(self.model.pmodel, self.index)
        self.model.updateConfiguration(settings)

    value = property(getValue, setValue)
    default = property(getDefault)

class Coupling(Variable):
    def __init__(self, model, index):
        self.model = model
        self.master = ctypes.c_void_p()
        self.slave = ctypes.c_void_p()
        self.model.fabm.get_coupling(self.model.pmodel, index, ctypes.byref(self.slave), ctypes.byref(self.master))
        Variable.__init__(self, model, variable_pointer=self.slave)

    def getValue(self):
        strlong_name = ctypes.create_string_buffer(ATTRIBUTE_LENGTH)
        self.model.fabm.variable_get_long_path(self.master, ATTRIBUTE_LENGTH, strlong_name)
        return strlong_name.value.decode('ascii')

    def setValue(self,value):
        print('New coupling specified: %s' % value)
        pass

    def getOptions(self):
        options = []
        list = self.model.fabm.variable_get_suitable_masters(self.model.pmodel, self.slave)
        strlong_name = ctypes.create_string_buffer(ATTRIBUTE_LENGTH)
        for i in range(self.model.fabm.link_list_count(list)):
            variable = self.model.fabm.link_list_index(list, i + 1)
            self.model.fabm.variable_get_long_path(variable, ATTRIBUTE_LENGTH, strlong_name)
            options.append(strlong_name.value.decode('ascii'))
        self.model.fabm.link_list_finalize(list)
        return options

    @property
    def long_path(self):
        strlong_name = ctypes.create_string_buffer(ATTRIBUTE_LENGTH)
        self.model.fabm.variable_get_long_path(self.slave, ATTRIBUTE_LENGTH, strlong_name)
        return strlong_name.value.decode('ascii')

    value = property(getValue, setValue)

class SubModel(object):
    def __init__(self, model, name):
        strlong_name = ctypes.create_string_buffer(ATTRIBUTE_LENGTH)
        iuser = ctypes.c_int()
        model.fabm.get_model_metadata(model.pmodel, name.encode('ascii'), ATTRIBUTE_LENGTH, strlong_name, iuser)
        self.long_name = strlong_name.value.decode('ascii')
        self.user_created = iuser.value != 0

class Model(object):
    def __init__(self, path='fabm.yaml', shape=()):
        if len(shape) > 1:
            raise FABMException('Invalid domain shape %s. Domain must have 0 or 1 dimensions.' % (shape,))
        self.fabm = fabm_0d if len(shape) == 0 else fabm_1d
        self.fabm.reset_error_state()
        self.lookup_tables = {}
        self._cell_thickness = None
        self.pmodel = self.fabm.create_model(path.encode('ascii'), *shape)
        self.domain_shape = shape
        if hasError():
            raise FABMException('An error occurred while parsing %s:\n%s' % (path, getError()))
        self.updateConfiguration()

    def setCellThickness(self, value):
        if self._cell_thickness is None:
            self._cell_thickness = numpy.empty(self.domain_shape)
        self._cell_thickness[...] = value

    cell_thickness = property(fset=setCellThickness)

    def getSubModel(self,name):
        return SubModel(self, name)

    def saveSettings(self):
        environment = dict([(dependency.name, dependency.value) for dependency in self.dependencies])
        state = dict([(variable.name,variable.value) for variable in self.state_variables])
        return environment,state

    def restoreSettings(self, data):
        environment,state = data
        for dependency in self.dependencies:
            if dependency.name in environment:
                dependency.value = environment[dependency.name]
        for variable in self.state_variables:
            if variable.name in state:
                variable.value = state[variable.name]

    def updateConfiguration(self, settings=None):
        # Get number of model variables per category
        nstate_interior = ctypes.c_int()
        nstate_surface = ctypes.c_int()
        nstate_bottom = ctypes.c_int()
        ndiag_interior = ctypes.c_int()
        ndiag_horizontal = ctypes.c_int()
        ndependencies_interior = ctypes.c_int()
        ndependencies_horizontal = ctypes.c_int()
        ndependencies_scalar = ctypes.c_int()
        nconserved = ctypes.c_int()
        nparameters = ctypes.c_int()
        ncouplings = ctypes.c_int()
        self.fabm.get_counts(self.pmodel,
            ctypes.byref(nstate_interior), ctypes.byref(nstate_surface), ctypes.byref(nstate_bottom),
            ctypes.byref(ndiag_interior), ctypes.byref(ndiag_horizontal),
            ctypes.byref(ndependencies_interior), ctypes.byref(ndependencies_horizontal), ctypes.byref(ndependencies_scalar),
            ctypes.byref(nconserved), ctypes.byref(nparameters), ctypes.byref(ncouplings)
        )

        # Allocate memory for state variable values, and send ctypes.pointer to this memory to FABM.
        self.state = numpy.empty((nstate_interior.value + nstate_surface.value + nstate_bottom.value,) + self.domain_shape, dtype=float)
        self.interior_state = self.state[:nstate_interior.value, ...]
        self.surface_state = self.state[nstate_interior.value:nstate_interior.value + nstate_surface.value, ...]
        self.bottom_state = self.state[nstate_interior.value + nstate_surface.value:, ...]
        for i in range(nstate_interior.value):
            self.fabm.link_interior_state_data(self.pmodel, i + 1, self.interior_state[i, ...])
        for i in range(nstate_surface.value):
            self.fabm.link_surface_state_data(self.pmodel, i + 1, self.surface_state[i, ...])
        for i in range(nstate_bottom.value):
            self.fabm.link_bottom_state_data(self.pmodel, i + 1, self.bottom_state[i, ...])

        self.dependency_data = numpy.zeros((ndependencies_interior.value + ndependencies_horizontal.value + ndependencies_scalar.value,) + self.domain_shape, dtype=float)
        self.interior_dependency_data = self.dependency_data[:ndependencies_interior.value, ...]
        self.horizontal_dependency_data = self.dependency_data[ndependencies_interior.value:ndependencies_interior.value + ndependencies_horizontal.value, ...]
        self.scalar_dependency_data = self.dependency_data[ndependencies_interior.value + ndependencies_horizontal.value:, ...]

        # Retrieve variable metadata
        strname = ctypes.create_string_buffer(ATTRIBUTE_LENGTH)
        strunits = ctypes.create_string_buffer(ATTRIBUTE_LENGTH)
        strlong_name = ctypes.create_string_buffer(ATTRIBUTE_LENGTH)
        strpath = ctypes.create_string_buffer(ATTRIBUTE_LENGTH)
        typecode = ctypes.c_int()
        has_default = ctypes.c_int()
        required = ctypes.c_int()
        self.interior_state_variables = []
        self.surface_state_variables = []
        self.bottom_state_variables = []
        self.interior_diagnostic_variables = []
        self.horizontal_diagnostic_variables = []
        self.conserved_quantities = []
        self.parameters = []
        self.interior_dependencies = []
        self.horizontal_dependencies = []
        self.scalar_dependencies = []
        for i in range(nstate_interior.value):
            ptr = self.fabm.get_variable(self.pmodel, INTERIOR_STATE_VARIABLE, i + 1)
            self.interior_state_variables.append(StateVariable(self, ptr, self.interior_state[i, ...]))
        for i in range(nstate_surface.value):
            ptr = self.fabm.get_variable(self.pmodel, SURFACE_STATE_VARIABLE, i + 1)
            self.surface_state_variables.append(StateVariable(self, ptr, self.surface_state[i, ...]))
        for i in range(nstate_bottom.value):
            ptr = self.fabm.get_variable(self.pmodel, BOTTOM_STATE_VARIABLE, i + 1)
            self.bottom_state_variables.append(StateVariable(self, ptr, self.bottom_state[i, ...]))
        for i in range(ndiag_interior.value):
            ptr = self.fabm.get_variable(self.pmodel, INTERIOR_DIAGNOSTIC_VARIABLE, i + 1)
            self.interior_diagnostic_variables.append(DiagnosticVariable(self, ptr, i, False))
        for i in range(ndiag_horizontal.value):
            ptr = self.fabm.get_variable(self.pmodel, HORIZONTAL_DIAGNOSTIC_VARIABLE, i + 1)
            self.horizontal_diagnostic_variables.append(DiagnosticVariable(self, ptr, i, True))
        for i in range(ndependencies_interior.value):
            ptr = self.fabm.get_variable(self.pmodel, INTERIOR_DEPENDENCY, i + 1)
            self.interior_dependencies.append(Dependency(self, ptr, self.interior_dependency_data[i, ...]))
        for i in range(ndependencies_horizontal.value):
            ptr = self.fabm.get_variable(self.pmodel, HORIZONTAL_DEPENDENCY, i + 1)
            self.horizontal_dependencies.append(Dependency(self, ptr, self.horizontal_dependency_data[i, ...]))
        for i in range(ndependencies_scalar.value):
            ptr = self.fabm.get_variable(self.pmodel, SCALAR_DEPENDENCY, i + 1)
            self.scalar_dependencies.append(Dependency(self, ptr, self.scalar_dependency_data[i, ...]))
        for i in range(nconserved.value):
            self.fabm.get_variable_metadata(self.pmodel, CONSERVED_QUANTITY, i + 1, ATTRIBUTE_LENGTH, strname, strunits, strlong_name, strpath)
            self.conserved_quantities.append(Variable(self, strname.value.decode('ascii'), strunits.value.decode('ascii'), strlong_name.value.decode('ascii'), strpath.value.decode('ascii')))
        for i in range(nparameters.value):
            self.fabm.get_parameter_metadata(self.pmodel, i + 1, ATTRIBUTE_LENGTH, strname, strunits, strlong_name, ctypes.byref(typecode), ctypes.byref(has_default))
            self.parameters.append(Parameter(self, strname.value.decode('ascii'), i, type=typecode.value, units=strunits.value.decode('ascii'), long_name=strlong_name.value.decode('ascii'), has_default=has_default.value != 0))

        self.couplings = [Coupling(self, i + 1) for i in range(ncouplings.value)]

        # Arrays that combine variables from pelagic and boundary domains.
        self.state_variables = self.interior_state_variables + self.surface_state_variables + self.bottom_state_variables
        self.diagnostic_variables = self.interior_diagnostic_variables + self.horizontal_diagnostic_variables
        self.dependencies = self.interior_dependencies + self.horizontal_dependencies + self.scalar_dependencies

        if settings is not None:
            self.restoreSettings(settings)

        # For backward compatibility
        self.bulk_state_variables = self.interior_state_variables
        self.bulk_diagnostic_variables = self.interior_diagnostic_variables

        self.itime = -1.

    def getRates(self, t=None, surface=True, bottom=True):
        """Returns the local rate of change in state variables,
        given the current state and environment.
        """
        if t is None:
            t = self.itime
        sources = numpy.empty_like(self.state)
        sources_interior = sources[:len(self.interior_state_variables), ...]
        sources_surface = sources[len(self.interior_state_variables):len(self.interior_state_variables) + len(self.surface_state_variables), ...]
        sources_bottom = sources[len(self.interior_state_variables) + len(self.surface_state_variables):, ...]
        assert not ((surface or bottom) and self._cell_thickness is None), 'You must assign model.cell_thickness to use getRates'
        self.fabm.get_sources(self.pmodel, t, sources_interior, sources_surface, sources_bottom, surface, bottom, self._cell_thickness)
        if hasError():
            raise FABMException(getError())
        return sources

    def checkState(self, repair=False):
        valid = self.fabm.check_state(self.pmodel, repair) != 0
        if hasError():
            raise FABMException(getError())
        return valid

    def getJacobian(self,pert=None):
        # Define perturbation per state variable.
        y_pert = numpy.empty_like(self.state)
        if pert is None: pert = 1e-6
        y_pert[:] = pert

        # Compute dy for original state (used as reference for finite differences later on)
        dy_ori = self.getRates()

        # Create memory for Jacobian
        Jac = numpy.empty((len(self.state), len(self.state)), dtype=self.state.dtype)

        for i in range(len(self.state)):
            # Save original state variable value, create perturbed one.
            y_ori = self.state[i]
            self.state[i] += y_pert[i]

            # Compute dy for perturbed state, compute Jacobian elements using finite difference.
            dy_pert = self.getRates()
            Jac[:,i] = (dy_pert - dy_ori) / y_pert[i]

            # Restore original state variable value.
            self.state[i] = y_ori

        return Jac

    def findObject(self, name, objecttype, case_insensitive=False):
        tablename = str(objecttype)
        if case_insensitive:
            tablename += '_ci'
        table = self.lookup_tables.get(tablename, None)
        if table is None:
           data = getattr(self, objecttype)
           if case_insensitive:
              table = dict([(obj.name.lower(), obj) for obj in data])
           else:
              table = dict([(obj.name, obj) for obj in data])
           self.lookup_tables[tablename] = table
        if case_insensitive:
            name = name.lower()
        return table[name]

    def findParameter(self,name,case_insensitive=False):
        return self.findObject(name, 'parameters', case_insensitive)

    def findDependency(self,name,case_insensitive=False):
        return self.findObject(name, 'dependencies', case_insensitive)

    def findStateVariable(self,name,case_insensitive=False):
        return self.findObject(name, 'state_variables', case_insensitive)

    def findDiagnosticVariable(self,name,case_insensitive=False):
        return self.findObject(name, 'diagnostic_variables', case_insensitive)

    def findCoupling(self,name,case_insensitive=False):
        return self.findObject(name, 'couplings', case_insensitive)

    def getParameterTree(self):
        root = {}
        for parameter in self.parameters:
            pathcomps = parameter.name.split('/')
            parent = root
            for component in pathcomps[:-1]:
                parent = root.setdefault(component,{})
            parent[pathcomps[-1]] = parameter
        return root

    def start(self, verbose=True, stop=False):
        def process_dependencies(dependencies, link_function):
            ready = True
            for dependency in dependencies:
                if dependency.is_set:
                    link_function(self.pmodel, dependency.variable_pointer, dependency.data)
                elif dependency.required:
                    print('Value for dependency %s is not set.' % dependency.name)
                    ready = False
            return ready

        ready = process_dependencies(self.interior_dependencies, self.fabm.link_interior_data)
        ready = process_dependencies(self.horizontal_dependencies, self.fabm.link_horizontal_data) and ready
        ready = process_dependencies(self.scalar_dependencies, self.fabm.link_scalar) and ready
        assert ready or not stop, 'Not all dependencies have been fulfilled.'

        self.fabm.start(self.pmodel)
        if hasError():
            return False
        for i, variable in enumerate(self.interior_diagnostic_variables):
            pdata = self.fabm.get_interior_diagnostic_data(self.pmodel, i + 1)
            variable.data = None if not pdata else numpy.ctypeslib.as_array(pdata, self.domain_shape)
        for i, variable in enumerate(self.horizontal_diagnostic_variables):
            pdata = self.fabm.get_horizontal_diagnostic_data(self.pmodel, i + 1)
            variable.data = None if not pdata else numpy.ctypeslib.as_array(pdata, self.domain_shape)
        return ready
    checkReady = start

    def updateTime(self, nsec):
       self.itime = nsec

    def printInformation(self):
        """Show information about the model."""
        def printArray(classname, array):
            if not array:
                return
            print(' %i %s:' % (len(array), classname))
            for variable in array:
                print('    %s = %s %s' % (variable.name, variable.value, variable.units))

        print('FABM model contains the following:')
        printArray('interior state variables', self.interior_state_variables)
        printArray('bottom state variables', self.bottom_state_variables)
        printArray('surface state variables', self.surface_state_variables)
        printArray('interior diagnostic variables', self.interior_diagnostic_variables)
        printArray('horizontal diagnostic variables', self.horizontal_diagnostic_variables)
        printArray('external variables', self.dependencies)
        print(' %i parameters:' % len(self.parameters))
        printTree(self.getParameterTree(), lambda x:'%s %s' % (x.value, x.units), '    ')

class Simulator(object):
    def __init__(self, model):
        assert model._cell_thickness is not None, 'You must assign model.cell_thickness to use Simulator'
        self.model = model

    def integrate(self, y0, t, dt, surface=True, bottom=True):
        y = numpy.empty((t.size, self.model.state.size))
        self.model.fabm.integrate(self.model.pmodel, t.size, self.model.state.size, t, y0, y, dt, surface, bottom, ctypes.byref(self.model._cell_thickness))
        if hasError():
            raise FABMException(getError())
        return y

def unload():
    global fabm_0d, fabm_1d

    for lib in (fabm_0d, fabm_1d):
        handle = lib._handle
        if os.name == 'nt':
            import ctypes.wintypes
            ctypes.windll.kernel32.FreeLibrary.argtypes = [ctypes.wintypes.HMODULE]
            ctypes.windll.kernel32.FreeLibrary(handle)
        else:
            dlclose = ctypes.CDLL(None).dlclose
            dlclose.argtypes = [ctypes.c_void_p]
            dlclose.restype = ctypes.c_int
            dlclose(handle)
    fabm_0d, fabm_1d = None, None

def get_version():
    version_length = 256
    strversion = ctypes.create_string_buffer(version_length)
    fabm_0d.get_version(version_length, strversion)
    return strversion.value.decode('ascii')

