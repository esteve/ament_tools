#!/usr/bin/env python3

# Copyright 2014 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This is a place holder script for bootstrapping a workspace.

The actual script which is installed is generated by python-setuptools.
"""

from __future__ import print_function

import importlib
import os
import sys

if sys.version_info < (3, 5):
    print('ament requires Python 3.5 or higher.', file=sys.stderr)
    sys.exit(1)

# add ament_tools to the Python path
ament_tools_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, os.path.abspath(ament_tools_root))

# check if ament_package is in a sibling folder
ament_package_root = os.path.join(ament_tools_root, '..', 'ament_package')
if os.path.exists(ament_package_root):
    # and add it to the Python path
    sys.path.insert(1, os.path.abspath(ament_package_root))
try:
    import ament_package
    ament_package  # silence pyflakes
except ImportError as e:
    raise ImportError(("%s\nTry cloning 'ament_package' into a sibling " +
                       "folder of 'ament_tools'") % e)

# check if osrf_pycommon is in a sibling folder
osrf_pycommon_root = os.path.join(ament_tools_root, '..', 'osrf_pycommon')
if os.path.exists(osrf_pycommon_root):
    # and add it to the Python path
    sys.path.insert(1, os.path.abspath(osrf_pycommon_root))
try:
    import osrf_pycommon
    osrf_pycommon  # silence pyflakes
except ImportError as e:
    raise ImportError(("%s\nTry cloning 'osrf_pycommon' into a sibling " +
                       "folder of 'ament_tools'") % e)

# override verb discovery relying on pkg_resources entry points
from osrf_pycommon.cli_utils import verb_pattern  # noqa


def list_verbs(group):
    assert group == 'ament.verbs'
    verbs = [
        'build',
        'build_pkg',
        'list_dependencies',
        'list_packages',
        'package_name',
        'package_version',
        'test',
        'test_pkg',
        'test_results',
        'uninstall',
        'uninstall_pkg',
    ]
    return verbs

verb_pattern.list_verbs = list_verbs


def load_verb_description(verb_name, group):
    verb_module = importlib.import_module('ament_tools.verbs.%s' % verb_name)
    return verb_module.entry_point_data

verb_pattern.load_verb_description = load_verb_description


# override build type discovery relying on pkg_resources entry points
known_build_types = {
    'ament_cmake': 'AmentCmakeBuildType',
    'ament_python': 'AmentPythonBuildType',
    'cmake': 'CmakeBuildType',
}


def yield_supported_build_types(name=None):
    class Loader(object):
        def __init__(self, build_type, entry_point):
            self.build_type = build_type
            self.entry_point = entry_point

        def load(self):
            build_type_module = importlib.import_module(
                'ament_tools.build_types.%s' % self.build_type)
            return getattr(build_type_module, self.entry_point)

    if name is None:
        return [Loader(build_type, entry_point)
                for build_type, entry_point in known_build_types.items()]

    if name not in known_build_types:
        raise RuntimeError(
            "This script does not support the build type '%s'\n" % name +
            'Only the following build types are supported: %s' %
            ', '.join(known_build_types.keys()))
    return Loader(name, known_build_types[name])


def get_class_for_build_type(build_type):
    loader = yield_supported_build_types(build_type)
    return loader.load()


from ament_tools import build_type_discovery  # noqa

build_type_discovery.yield_supported_build_types = yield_supported_build_types
build_type_discovery.get_class_for_build_type = get_class_for_build_type


# override package type discovery relying on pkg_resources entry points
from ament_tools.package_types.ament import entry_point_data as ament_entry_point_data  # noqa
from ament_tools.package_types.cmake import entry_point_data as cmake_entry_point_data  # noqa
from ament_tools.package_types.python import entry_point_data as python_entry_point_data  # noqa

known_package_types = [
    ament_entry_point_data,
    cmake_entry_point_data,
    python_entry_point_data,
]


def get_package_types():
    return known_package_types

from ament_tools import package_types  # noqa
package_types.get_package_types = get_package_types


from ament_tools.commands.ament import main  # noqa

if __name__ == '__main__':
    sys.exit(main() or 0)
