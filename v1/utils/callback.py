from ansible.plugins.callback import CallbackBase
from collections import defaultdict
import json
class ResultCallback(CallbackBase):
	def __init__(self, result, **kwargs):
		#host = result._host
		self.callback_data = json.dumps({host.name: result._result}, indent=4)
class AdHocResultCallback(CallbackBase):
	def __init__(self,display=None):
		#host =result._host
		self.result_q = dict(contacted={}, dark={})
		super(AdHocResultCallback, self).__init__(display)
	def gather_result(self, n, res):
		if res._host.name in self.result_q[n]:
			self.result_q[n][res._host.name].append(res._result)
		else:
			self.result_q[n][res._host.name] = [res._result]

	def v2_runner_on_ok(self, result):
		self.gather_result("contacted", result)


	def v2_runner_on_failed(self, result, ignore_errors=False):
		self.gather_result("dark", result)																		      
	def v2_runner_on_unreachable(self, result):
		self.gather_result("dark", result)
	def v2_runner_on_skipped(self, result):
		self.gather_result("dark", result)
	def v2_playbook_on_task_start(self, task, is_conditional):
		pass
	def v2_playbook_on_play_start(self, play):																							
		pass

class CommandResultCallback(CallbackBase):
		def __init__(self, display=None):
			self.result_q = dict(contacted={}, dark={})
			super(CommandResultCallback, self).__init__(display)

		def gather_result(self, n, res):
			self.result_q[n][res._host.name] = {}
			self.result_q[n][res._host.name]['cmd'] = res._result.get('cmd')
			self.result_q[n][res._host.name]['stderr'] = res._result.get('stderr')
			self.result_q[n][res._host.name]['stdout'] = res._result.get('stdout')
			self.result_q[n][res._host.name]['rc'] = res._result.get('rc')

		def v2_runner_on_ok(self, result):
			self.gather_result("contacted", result)

		def v2_runner_on_failed(self, result, ignore_errors=False):
			self.gather_result("dark", result)

		def v2_runner_on_unreachable(self, result):
			self.gather_result("dark", result)

		def v2_runner_on_skipped(self, result):
			self.gather_result("dark", result)
