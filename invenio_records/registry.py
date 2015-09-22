# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2013, 2014, 2015 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""Define registries for extending *Record* class."""

from flask_registry import PkgResourcesDirDiscoveryRegistry, \
    ModuleAutoDiscoveryRegistry, RegistryProxy

from invenio_ext.registry import ModuleAutoDiscoverySubRegistry
from invenio_utils.datastructures import LazyDict


def jsonext(namespace):
    return RegistryProxy(namespace, ModuleAutoDiscoveryRegistry, namespace)


def function_proxy(namespace):
    return RegistryProxy(
        namespace + '.functions',
        ModuleAutoDiscoverySubRegistry,
        'functions',
        registry_namespace=jsonext(namespace)
    )


def functions(namespace=None):
    funcs = dict((module.__name__.split('.')[-1],
                 getattr(module, module.__name__.split('.')[-1]))
                 for module in function_proxy('jsonext'))
    if namespace is not None:
        funcs.update((module.__name__.split('.')[-1],
                     getattr(module, module.__name__.split('.')[-1]))
                     for module in function_proxy(namespace))
    return funcs
