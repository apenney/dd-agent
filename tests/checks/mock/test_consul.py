import random
from checks import AgentCheck
from tests.checks.common import AgentCheckTest, load_check

MOCK_CONFIG = {
    'init_config': {},
    'instances' : [{
        'url': 'http://localhost:8500',
        'catalog_checks': True,
    }]
}

MOCK_CONFIG_LEADER_CHECK = {
    'init_config': {},
    'instances' : [{
        'url': 'http://localhost:8500',
        'catalog_checks': True,
        'new_leader_checks': True
    }]
}


class TestCheckConsul(AgentCheckTest):
    CHECK_NAME = 'consul'

    def mock_get_services_in_cluster(self, instance):
        return {
            "service-1": [
                "az-us-east-1a"
            ],
            "service-2": [
                "az-us-east-1a"
            ],
            "service-3": [
                "az-us-east-1a"
            ],
            "service-4": [
                "az-us-east-1a"
            ],
            "service-5": [
                "az-us-east-1a"
            ],
            "service-6": [
                "az-us-east-1a"
            ]
        }

    def mock_get_local_config(self, instance):
        return {
            "Config": {
                "AdvertiseAddr": "10.0.2.15",
                "Datacenter": "dc1",
                "Ports": {
                    "DNS": 8600,
                    "HTTP": 8500,
                    "HTTPS": -1,
                    "RPC": 8400,
                    "SerfLan": 8301,
                    "SerfWan": 8302,
                    "Server": 8300
                },
            }
        }

    def mock_get_nodes_in_cluster(self, instance):
        return [
            {
                "Address": "10.0.2.15",
                "Node": "node-1"
            },
            {
                "Address": "10.0.2.25",
                "Node": "node-2"
            },
            {
                "Address": "10.0.2.35",
                "Node": "node-2"
            },
        ]


    def mock_get_nodes_with_service(self, instance, service):
        def _get_random_ip():
            rand_int = int(15 * random.random()) + 10
            return "10.0.2.{0}".format(rand_int)

        return [
            {
                "Address": _get_random_ip(),
                "Node": "node-1",
                "ServiceAddress": "",
                "ServiceID": service,
                "ServiceName": service,
                "ServicePort": 80,
                "ServiceTags": [
                    "az-us-east-1a"
                ]
            }
        ]

    def mock_should_check(self, instance):
        return True

    def mock_get_cluster_leader(self, instance):
        return 'My New Leader'

    def _get_consul_mocks(self):
        return {
            'get_services_in_cluster': self.mock_get_services_in_cluster,
            'get_nodes_in_cluster': self.mock_get_nodes_in_cluster,
            'get_nodes_with_service': self.mock_get_nodes_with_service,
            'should_check': self.mock_should_check,
            '_get_local_config': self.mock_get_local_config
        }

    def test_get_nodes_in_cluster(self):
        self.run_check(MOCK_CONFIG, mocks=self._get_consul_mocks())
        self.assertMetric('consul.catalog.nodes_up', value=3, tags=['consul_datacenter:dc1'])

    def test_get_services_in_cluster(self):
        self.run_check(MOCK_CONFIG, mocks=self._get_consul_mocks())
        self.assertMetric('consul.catalog.services_up', value=6, tags=['consul_datacenter:dc1'])

    def test_get_nodes_with_service(self):
        self.run_check(MOCK_CONFIG, mocks=self._get_consul_mocks())
        self.assertMetric('consul.catalog.nodes_up', value=1, tags=['consul_service_id:service-1'])

    def test_get_services_on_node(self):
        self.run_check(MOCK_CONFIG, mocks=self._get_consul_mocks())
        self.assertMetric('consul.catalog.services_up', value=6, tags=['consul_node_id:node-1'])

    def test_new_leader_event(self):
        self.check = load_check(self.CHECK_NAME, MOCK_CONFIG_LEADER_CHECK, self.DEFAULT_AGENT_CONFIG)
        self.check._last_known_leader = 'My Old Leader'

        mocks = self._get_consul_mocks()
        mocks['_get_cluster_leader'] = self.mock_get_cluster_leader

        self.run_check(MOCK_CONFIG_LEADER_CHECK, mocks=mocks)
        self.assertEqual(len(self.events), 1)

        event = self.events[0]
        self.assertEqual(event['event_type'], 'consul.new_leader')
        self.assertIn('prev_consul_leader:My Old Leader', event['tags'])
        self.assertIn('curr_consul_leader:My New Leader', event['tags'])
