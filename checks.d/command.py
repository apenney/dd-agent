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
            self.service_check('command.{}'.format(instance['command']), 1,
                tags=["host:{}".format(self.hostname)],
                hostname=self.hostname,
                message='Command Check output failed: {} not found in {}'.format(instance['output'], instance['command'])
            )


    def _command(self, command):
        listified_command = command.split(' ')
        return subprocess.check_output(listified_command)
