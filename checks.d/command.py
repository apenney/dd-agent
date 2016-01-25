import subprocess, time
from checks import AgentCheck

class CommandCheck(AgentCheck):
    def check(self, instance):
        if 'command' not in instance:
            raise Exception('Missing "command" in Command config.')

        if 'output' not in instance:
            raise Exception('Missing "output" in Command config.')

        command_output = self._command(instance['command'])

        if instance['output'] not in command_output:
            event = {
                "timestamp": int(time.time()),
                "event_type": 'command',
                "msg_title": 'Command {} check failed'.format(instance['command']),
                "msg_text": 'Command Check output failed: {} not found in {}'.format(instance['output'], instance['command']),
                "alert_type": 'warning',
                "source_type_name": 'command',
                "host": self.hostname,
                "tags": ["host:{}".format(self.hostname)],
            }
            self.event(event)


    def _command(self, command):
        listified_command = command.split(' ')
        return subprocess.check_output(listified_command)
