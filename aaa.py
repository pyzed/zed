#!/usr/bin/env python
from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
from ansible.inventory import Inventory
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.plugins.callback import CallbackBase
import json
class ResultCallback(CallbackBase):
	def v2_runner_on_ok(self,result,**kwargs):
		host = result._host
		self.data = json.dumps({host.name: result._result}, indent=4)
results_callback =ResultCallback()
Options = namedtuple('Options', ['listtags', 'listtasks', 'listhosts', 'syntax', 'connection','module_path', 'forks', 'private_key_file', 'ssh_common_args', 'ssh_extra_args','sftp_extra_args', 'scp_extra_args', 'become', 'become_method', 'become_user', 'verbosity', 'check'])

variable_manager = VariableManager()
loader = DataLoader()

options = Options(listtags=False, listtasks=False, listhosts=False, syntax=False, connection='ssh', module_path=None, forks=100, private_key_file=None,ssh_common_args=None, ssh_extra_args=None, sftp_extra_args=None, scp_extra_args=None, become=False, become_method=None, become_user=None, verbosity=None, check=False)
passwords = {}
inventory = Inventory(loader=loader, variable_manager=variable_manager,host_list='/root/.ansible/admin.hosts')
variable_manager.set_inventory(inventory)



play_source =  dict(
	name = "Ansible Play",
	hosts = 'localhost',
	remote_user = 'admin',
	gather_facts = 'no',
	tasks = [
		dict(action=dict(module='get_url', args="url=http://192.168.121.215/odmc-tools/tool-61/raw/develop/test.sh dest=/tmp/  headers=PRIVATE-TOKEN:4k-seAEmXzKCkLFzAeZ7 mode=755")),

	]
																				   )
play = Play().load(play_source, variable_manager=variable_manager, loader=loader)
try:
	tqm = TaskQueueManager(
				            inventory=inventory,
							variable_manager=variable_manager,
							loader=loader,
							options=options,
							passwords=passwords,
							stdout_callback=results_callback,
	)
	result = tqm.run(play)
#	print results_callback.data.get('localhost')
	json_results = json.loads(results_callback.data)
	print results_callback.data
	print json_results.get('localhost').get('rc')
finally:
	if tqm is not None:
		tqm.cleanup()
