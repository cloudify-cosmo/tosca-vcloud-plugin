# Copyright (c) 2015-2020 Cloudify Platform Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from cosmo_tester.test_suites.test_blueprints import nodecellar_test


class VcloudNodeCellarTest(nodecellar_test.NodecellarAppTest):

    def test_vcloud_nodecellar(self):
        self._test_nodecellar_impl('vcloud-blueprint.yaml')

    def get_inputs(self):
        return {
            'catalog': self.env.public_catalog,
            'template': self.env.ubuntu_precise_template,
            'edge_gateway': self.env.edge_gateway,
            'management_network_name': self.env.management_network_name,
            'agent_public_key': self.env.agent_public_key
        }

    @property
    def entrypoint_property_name(self):
        return 'public_ip'

    @property
    def expected_nodes_count(self):
        return 9
