#!/usr/bin/env python
"""
Generate rst files for automod documentation of the various libraries in
the reduction tree.
"""
from __future__ import with_statement

import os.path

MODULE_TEMPLATE = """.. Autogenerated by genmods.py

******************************************************************************
%(name)s
******************************************************************************

:mod:`%(package)s.%(module)s`
==============================================================================

.. automodule:: %(package)s.%(module)s
   :members:
   :undoc-members:
   :show-inheritance:

"""

INDEX_TEMPLATE = """.. Autogenerated by genmods.py

.. _%(package)s-api-index:

##############################################################################
   %(package_name)s
##############################################################################

.. only:: html

   :Release: |version|
   :Date: |today|

.. toctree::
   :titlesonly:
   :numbered: 1
   :maxdepth: 2

   %(rsts)s
"""


def genfiles(package, package_name, modules, dir='api'):
    # type: (str, str, Sequence[Tuple[str, str]], str) -> None
    """
    Generate an rst file for the *modules* in *package*.

    *package_name* is the name given to the whole package.

    *dir* is the target directory.  All rst files, including an index file
    are generated in this directory.  Modules is a list of pairs of name
    relative to the package and short description.
    """
    if not os.path.exists(dir):
        os.makedirs(dir)

    for module, name in modules:
        #print "module","name", module,name
        with open(os.path.join(dir, module+'.rst'), 'w') as f:
            f.write(MODULE_TEMPLATE%locals())

    rsts = "\n   ".join(module+'.rst' for module, name in modules)
    with open(os.path.join(dir, 'index.rst'), 'w') as f:
        f.write(INDEX_TEMPLATE%locals())

def dataflow():
    """Generate modules for the dataflow package"""
    modules = [
        ('anno_exc', 'annotate exceptions'),
        ('automod', 'generate module definition from function declarations'),
        ('cache', 'redis/memory cache manager'),
        ('calc', 'template calculator'),
        ('core', 'instrument definition'),
        ('deps', 'graph dependeny resolution'),
        ('fakeredis', 'memory-based cache manager with redis interface'),
        ('fetch', 'fetch data from remote data source, with caching'),
        ('rst2html', 'convert restructured text document to html'),
        ('store', 'template serializer'),
        ('lib.err1d', '1-D error propagation functions'),
        ('lib.errutil', 'extensions to the PyPI uncertainties package'),
        ('lib.formatnum', 'nice formatting of uncertain numbers'),
        ('lib.hzf_readonly_stripped', 'zip NeXus reader'),
        ('lib.iso8601', 'timestamp parsing and printing'),
        ('lib.rebin', 'rebinning support'),
        ('lib.uncertainty', '1-D uncertainty type'),
        ('lib.unit', 'NeXus file units support'),
        ('lib.wsolve', 'linear regression with uncertainty'),
    ]
    package = 'dataflow'
    package_name = 'Dataflow'
    genfiles(package, package_name, modules, dir=package)

def reflred():
    """Generate modules for the reflred package"""
    modules = [
        ('steps', 'reflectometry reduction steps'),
        ('angles', 'angle corrections'),
        ('background', 'background alignment and subtraction'),
        ('bruker', 'Bruker X-ray data format loader'),
        ('deadtime_fit', 'dead time estimation routines'),
        ('deadtime', 'dead time corrections'),
        ('footprint', 'footprint correction'),
        ('intent', 'intent marking'),
        ('joindata', 'data joining'),
        ('load', 'data loader'),
        ('nexusref', 'load reflectometry data from NeXus format'),
        ('polarization', 'polarization correction'),
        ('refldata', 'reflectometry data structure'),
        ('resolution', 'reflectometry resolution calculations'),
        ('scale', 'data scaling'),
        ('smoothslits', 'slit scan smoothing'),
        ('util', 'data correction helper functions'),
        ('xrawref', 'load reflectometry data from Bruker format'),
        # Modules moved to reflred-old
        #('data', 'generic data file support'),
        #('fresnel', 'Fresnel reflectivity calculation'),
        #('h5natural', 'monkeypatch for h5py to support tab completion'),
        #('h5nexus', 'NeXus reader/writer using h5py'),
        #('limits', 'set consistent data ranges across datasets'),
        #('pipeline', 'pipeline processor for reduction steps'),
        #('properties', 'manage instrument properties'),
        #('qxqz', 'Qx-Qz to angle calculations'),
        #('registry', 'data loader registry'),
        #('ticker', 'matplotlib log scale ticker'),
        #('formats.bruker', 'Bruker X-ray data reader'),
        #('formats.icpformat', 'ICP data reader'),
        #('formats.ncnr_ng1', 'NG-1 ICP reader'),
        #('formats.ncnr_ng7', 'NG-7 ICP reader'),
        #('formats.rigaku', 'Rigaku X-ray data reader'),
    ]
    package = 'reflred'
    package_name = 'Reflectometry Reduction'
    genfiles(package, package_name, modules, dir=package)

def ospecred():
    """Generate modules for the off-specular package"""
    modules = [
        ('magik_filters_func', 'Off-specular reduction steps'),
        ('FilterableMetaArray', 'dataflow interchange format'),
        ('MetaArray', 'nd array with metadata'),
        ('asterix_filters', 'annotate exceptions'),
        ('asterix_loaders', 'data loaders for Asterix instrument'),
        ('filters', 'dataflow reduction steps'),
        ('he3analyzer', 'He3 analysis corrections'),
        ('magik_loaders', 'load NeXus data for Magik instrument'),
        ('xray_loaders', 'load UXD data from Bruker X-ray reflectometer'),
    ]
    package = 'ospecred'
    package_name = 'Off-Specular Reduction'
    genfiles(package, package_name, modules, dir=package)

def sansred():
    """Generate modules for the SANS package"""
    modules = [
        ('steps', 'SANS reduction steps'),
        ('attenuation_constants', 'calibration values for SANS attenuators'),
        ('draw_annulus_aa', 'anti-aliased annulus mask'),
        ('loader', 'SANS data loader'),
        ('sansdata', 'SANS data format'),
    ]
    package = 'sansred'
    package_name = 'SANS Reduction'
    genfiles(package, package_name, modules, dir=package)


dataflow()
reflred()
ospecred()
sansred()
