
# -*- coding: utf-8 -*-

'''A pure Python implementation of geodesy tools for various ellipsoidal
and spherical earth models using trigonometric and vector-based methods
for geodetic (lat-/longitude) and cartesian (x/y/z) coordinates.

Transcribed from JavaScript originals by I{(C) Chris Veness 2005-2016}
and published under the same U{MIT License<https://opensource.org/licenses/MIT>}**.
For more information and further details see:

 - U{https://github.com/chrisveness/geodesy/}
 - U{http://www.movable-type.co.uk/scripts/latlong.html}
 - U{http://www.movable-type.co.uk/scripts/latlong-vincenty.html}
 - U{http://www.movable-type.co.uk/scripts/latlong-vectors.html}

Also included are conversions to and from UTM (Universal Transverse Mercator)
coordinates and MGRS (NATO Military Grid Reference System) and OSGR (British
Ordinance Survery Grid Reference) grid references, see:

 - U{http://www.movable-type.co.uk/scripts/latlong-utm-mgrs.html}
 - U{http://www.movable-type.co.uk/scripts/latlong-os-gridref.html}

An additional module provides Lambert conformal conic projections
and positions, transcribed from:

 - U{https://pubs.er.USGS.gov/djvu/PP/PP_1395.pdf} pp 107-109.

Another module offers several functions to simplify or linearize a path,
including implementations of the original Ramer-Douglas-Peucker (RDP)
and Visvalingam-Wyatt (VW) algorithms and modified versions of both:

 - U{https://en.m.wikipedia.org/wiki/Ramer-Douglas-Peucker_algorithm}
 - U{https://hydra.hull.ac.uk/assets/hull:8338}
 - U{https://bost.ocks.org/mike/simplify/}

All modules have been statically checked* with
U{PyChecker<https://pypi.python.org/pypi/pychecker>},
U{PyFlakes<https://pypi.python.org/pypi/pyflakes>},
U{PyCodeStyle<https://pypi.python.org/pypi/pycodestyle>} (formerly Pep8),
U{McCabe<https://pypi.python.org/pypi/mccabe>} using Python 2.7.10 and 2.7.13
and with U{Flake8<https://pypi.python.org/pypi/flake8>} on Python 3.6.0.
The tests have been run with 64-bit Python 2.6.9, 2.7.10, 2.7.13, 3.5.2, 3.5.3
and 3.6.0, but only on MacOSX 10.10 Yosemite, MacOSX 10.11 El Capitan and/or
macOS 10.12.2, 10.12.3 and 10.12.4 Sierra.

The C{zip} and C{tar} files in directory C{dist} each contain the entire
B{PyGeodesy} distribution for installation with the enclosed C{setup.py} file.

The U{documentation<https://pythonhosted.org/PyGeodesy/>} was generated
by U{Epydoc<https://pypi.python.org/pypi/epydoc>} using command line:
C{epydoc --html --no-private --no-source --name=PyGeodesy --url=... -v pygeodesy}.

Several function and method names differ from the JavaScript version.
Documentation tag B{JS name:} shows the original JavaScript name.

_

*) U{PyChecker postprocessor<http://code.activestate.com/recipes/546532>}

**) U{MIT License<https://opensource.org/licenses/MIT>} text follows:

Copyright (C) 2016-2017 -- I{mrJean1 at Gmail dot com}

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

@newfield example: Example, Examples
@newfield JSname: JS name, JS names

@var EPS:  System's M{epsilon} (float)
@var EPS1: M{1 - EPS} (float)
@var EPS2: M{sqrt(EPS)} (float)

@var F_D:   Format degrees as deg° (string).
@var F_DM:  Format degrees as deg°min′ (string).
@var F_DMS: Format degrees as deg°min′sec″ (string).
@var F_RAD: Converts degrees to radians and format (string).

@var PI:   Constant M{math.pi} (float)
@var PI2:  Two PI, M{math.pi * 2} (float)
@var PI_2: Half PI, M{math.pi / 2} (float)

@var R_KM: Mean, spherical earth radius (kilo meter).
@var R_M:  Mean, spherical earth radius (meter).
@var R_NM: Mean, spherical earth radius (nautical miles).
@var R_SM: Mean, spherical earth radius (statute miles).

@var S_DEG: Degrees symbol '°' (string).
@var S_MIN: Minutes symbol '′' (string).
@var S_SEC: Seconds symbol '″' (string).
@var S_SEP: Separator between deg°, min′ and sec″ (string).

@var Conics:     Registered conics (enum).
@var Datums:     Registered datums (enum).
@var Ellipsoids: Registered ellipsoids (enum).
@var Transforms: Registered transforms (enum).

@var version: Normalized PyGeodesy version (string).

'''

try:
    import bases  # PYCHOK expected
except ImportError:
    # extend sys.path to include this very directory
    # such that all public and private sub-modules can
    # be imported (and checked by PyChecker, etc.)
    import os, sys  # PYCHOK expected
    sys.path.insert(0, os.path.dirname(__file__))  # XXX __path__[0]
    del os, sys

# keep ellipsoidal and spherical modules as modules
import ellipsoidalNvector  # PYCHOK false
import ellipsoidalVincenty  # PYCHOK false
import sphericalNvector  # PYCHOK false
import sphericalTrigonometry  # PYCHOK false
import nvector  # PYCHOK false
import vector3d  # PYCHOK false

VincentyError = ellipsoidalVincenty.VincentyError

# all public contants, classes and functions
__all__ = ('ellipsoidalNvector', 'ellipsoidalVincenty',
           'sphericalNvector', 'sphericalTrigonometry',
           'VincentyError',
           'nvector', 'vector3d', 'version',
           'isclockwise')  # extended below
__version__ = '17.04.08'

# see setup.py for similar logic
version = '.'.join(map(str, map(int, __version__.split('.'))))

# lift all public classes, constants, functions, etc. but
# only from the following sub-modules ... (see also David
# Beazley's <http://dabeaz.com/modulepackage/index.html>)
from bases    import isclockwise  # PYCHOK expected
from datum    import *  # PYCHOK __all__
from dms      import *  # PYCHOK __all__
from lcc      import *  # PYCHOK __all__
from mgrs     import *  # PYCHOK __all__
from osgr     import *  # PYCHOK __all__
from simplify import *  # PYCHOK __all__
from utils    import *  # PYCHOK __all__
from utm      import *  # PYCHOK __all__

import datum     # PYCHOK expected
import dms       # PYCHOK expected
import lcc       # PYCHOK expected
import mgrs      # PYCHOK expected
import osgr      # PYCHOK expected
import simplify  # PYCHOK expected
import utils     # PYCHOK expected
import utm       # PYCHOK expected

# concat __all__ with the public classes, constants,
# functions, etc. from the sub-modules mentioned above
for m in (datum, dms, lcc, mgrs, osgr, simplify, utils, utm):
    __all__ += tuple(m.__all__)
del m

# try:  # remove private, INTERNAL modules
#     del bases, ellipsoidalBase, sphericalBase  # PYCHOK expected
# except NameError:
#     pass
