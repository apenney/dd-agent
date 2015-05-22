# 3p
from nose.plugins.attrib import attr

# project
from tests.checks.common import AgentCheckTest


@attr(requires='network')
class TestCheckDisk(AgentCheckTest):
    CHECK_NAME = 'network'

    NETSTAT_GAUGES = [
        'system.net.udp4.connections',
        'system.net.udp6.connections',
        'system.net.tcp4.established',
        'system.net.tcp4.opening',
        'system.net.tcp4.closing',
        'system.net.tcp4.listening',
        'system.net.tcp4.time_wait',
        'system.net.tcp6.established',
        'system.net.tcp6.opening',
        'system.net.tcp6.closing',
        'system.net.tcp6.listening',
        'system.net.tcp6.time_wait',
    ]
    # Really a basic check to see if all metrics are there
    def test_check(self):
        self.run_check({})

        # Assert metrics
        for metric in self.NETSTAT_GAUGES:
            self.assertMetric(metric, tags=[])

        self.coverage_report()

    # Test two instances
    def test_bad_config(self):
        self.assertRaises(Exception,
                          lambda: self.run_check({'instances': [{}, {}]}))
