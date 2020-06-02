#!/usr/bin/env python3
#
# Copyright 2017-2020 GridGain Systems.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from .singleton import singleton
from .util import load_yaml
from .tidenfabric import TidenFabric
from .copy import deepcopy
from .tidenexception import TidenException


class Requirement:
    options = {}
    def __init__(self, **kwargs):
        self.options = deepcopy(kwargs)

    def check(self, config):
        pass


class ArtifactRequirement(Requirement):
    def check(self, config):
        if not 'artifacts' in config or not isinstance(config['artifacts'], dict):
            raise TidenException("Required 'artifacts' section missing in config")

        if not 'artifact_name' in self.options:
            raise TidenException("Unknown 'artifact_name'")

        if not self.options['artifact_name'] in config['artifacts'].keys():
            raise TidenException("Required artifact '%s' missing" % self.options['artifact_name'])


class ApplicationRequirement(Requirement):
    def check(self, config):
        pass


@singleton
class ArtifactRepository:

    artifact_templates = {}

    def __init__(self):
        self.artifact_templates = load_yaml("config/artifact-repository.yaml")

    def require_artifact(self, artifact_name, artifact_version=None):
        fabric = TidenFabric()
        config = fabric.getConfigDict()


def require_artifact(cls, artifact_template_name, artifact_version=None, artifact_name=None):
    """
    That decorator for test class adds
    :param cls:
    :param artifact_template_name:
    :param artifact_version:
    :param artifact_name:
    :return:
    """
    def wrapper(cls):
        # if not hasattr(cls, '__requrements__')
        pass

