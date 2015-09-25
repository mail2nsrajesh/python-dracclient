#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import requests_mock

import dracclient.client
from dracclient import exceptions
from dracclient.resources import uris
from dracclient.tests import base
from dracclient.tests import utils as test_utils


@requests_mock.Mocker()
class ClientPowerManagementTestCase(base.BaseTest):

    def setUp(self):
        super(ClientPowerManagementTestCase, self).setUp()
        self.drac_client = dracclient.client.DRACClient(
            **test_utils.FAKE_ENDPOINT)

    def test_get_power_state(self, mock_requests):
        mock_requests.post(
            'https://1.2.3.4:443/wsman',
            text=test_utils.BIOSEnumerations[uris.DCIM_ComputerSystem]['ok'])

        self.assertEqual('POWER_ON', self.drac_client.get_power_state())

    def test_set_power_state(self, mock_requests):
        mock_requests.post(
            'https://1.2.3.4:443/wsman',
            text=test_utils.BIOSInvocations[
                uris.DCIM_ComputerSystem]['RequestStateChange']['ok'])

        self.assertIsNone(self.drac_client.set_power_state('POWER_ON'))

    def test_set_power_state_fail(self, mock_requests):
        mock_requests.post(
            'https://1.2.3.4:443/wsman',
            text=test_utils.BIOSInvocations[
                uris.DCIM_ComputerSystem]['RequestStateChange']['error'])

        self.assertRaises(exceptions.DRACOperationFailed,
                          self.drac_client.set_power_state, 'POWER_ON')

    def test_set_power_state_invalid_target_state(self, mock_requests):
        self.assertRaises(exceptions.InvalidParameterValue,
                          self.drac_client.set_power_state, 'foo')


@requests_mock.Mocker()
class WSManClientTestCase(base.BaseTest):

    def test_enumerate(self, mock_requests):
        mock_requests.post('https://1.2.3.4:443/wsman',
                           text='<result>yay!</result>')

        client = dracclient.client.WSManClient(**test_utils.FAKE_ENDPOINT)
        resp = client.enumerate('http://resource')
        self.assertEqual('yay!', resp.text)

    def test_invoke(self, mock_requests):
        xml = """
<response xmlns:n1="http://resource">
    <n1:ReturnValue>42</n1:ReturnValue>
    <result>yay!</result>
</response>
"""  # noqa
        mock_requests.post('https://1.2.3.4:443/wsman', text=xml)

        client = dracclient.client.WSManClient(**test_utils.FAKE_ENDPOINT)
        resp = client.invoke('http://resource', 'Foo')
        self.assertEqual('yay!', resp.find('result').text)

    def test_invoke_with_expected_return_value(self, mock_requests):
        xml = """
<response xmlns:n1="http://resource">
    <n1:ReturnValue>42</n1:ReturnValue>
    <result>yay!</result>
</response>
"""  # noqa
        mock_requests.post('https://1.2.3.4:443/wsman', text=xml)

        client = dracclient.client.WSManClient(**test_utils.FAKE_ENDPOINT)
        resp = client.invoke('http://resource', 'Foo',
                             expected_return_value='42')
        self.assertEqual('yay!', resp.find('result').text)

    def test_invoke_with_error_return_value(self, mock_requests):
        xml = """
<response xmlns:n1="http://resource">
    <n1:ReturnValue>2</n1:ReturnValue>
    <result>yay!</result>
</response>
"""  # noqa
        mock_requests.post('https://1.2.3.4:443/wsman', text=xml)

        client = dracclient.client.WSManClient(**test_utils.FAKE_ENDPOINT)
        self.assertRaises(exceptions.DRACOperationFailed, client.invoke,
                          'http://resource', 'Foo')

    def test_invoke_with_unexpected_return_value(self, mock_requests):
        xml = """
<response xmlns:n1="http://resource">
    <n1:ReturnValue>42</n1:ReturnValue>
    <result>yay!</result>
</response>
"""  # noqa
        mock_requests.post('https://1.2.3.4:443/wsman', text=xml)

        client = dracclient.client.WSManClient(**test_utils.FAKE_ENDPOINT)
        self.assertRaises(exceptions.DRACUnexpectedReturnValue, client.invoke,
                          'http://resource', 'Foo',
                          expected_return_value='4242')
