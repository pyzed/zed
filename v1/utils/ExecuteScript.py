#!/usr/bin/env  python
# -*- coding: utf-8 -*-
import commands
import os
import urllib
from django.core.cache import cache
import sys
import json
from v1.utils.Config import USER_ANSIBLE_DIR
from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
from ansible.inventory import Inventory
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from callback import AdHocResultCallback
from ansible.plugins.callback import CallbackBase
import ansible.constants as C
from ansible.utils.vars import load_extra_vars
from ansible.utils.vars import load_options_vars

C.HOST_KEY_CHECKING = False
reload(sys) 	
sys.setdefaultencoding('utf8')   

results_callback_class = AdHocResultCallback

class ScriptExecution(object):
	def __init__(self,data):
		self.log_file = data.get('log_file')
		self.host = str(data.get('host'))
		self.exec_type = data.get('exec_type')
		self.remote_user = data.get('remote_user')
		self.m_filename = data.get('m_filename')
		self.script_urls = data.get('script_urls')
		self.tool_id = str(data.get('tool_id'))
		self.app_type = data.get('app_type')
		if self.app_type == 'tool':
			self.d_homedir = '/home/admin/tool'
		else: 
			self.d_homedir = '/home/admin'
		self.version = data.get('version')
		self.scripts_name_list =data.get('scripts_name_list')

		self.results_callback = results_callback_class()
		self.Options = namedtuple('Options', ['listtags', 'listtasks', 'listhosts', 'syntax', 'connection','module_path', 'forks', 'private_key_file', 'ssh_common_args', 'ssh_extra_args','sftp_extra_args', 'scp_extra_args', 'become', 'become_method', 'become_user', 'verbosity', 'check'])
		
		self.options = self.Options(
				listtags=False, 
				listtasks=False, 
				listhosts=False, 
				syntax=False, 
				connection='ssh',
				module_path=None, 
				forks=100, 
				private_key_file=None,
				ssh_common_args=None, 
				ssh_extra_args=None, 
				sftp_extra_args=None, 
				scp_extra_args=None, 
				become=False, 
				become_method=None, 
				become_user=None, 
				verbosity=None, 
				check=False)
		self.passwords = {}
		self.variable_manager = VariableManager()
		self.loader = DataLoader()
		user_host_path = os.path.join(USER_ANSIBLE_DIR, self.remote_user + '.hosts')
		self.inventory = Inventory(loader=self.loader, variable_manager=self.variable_manager,host_list=user_host_path)
		self.variable_manager.set_inventory(self.inventory)


	def GetKey(self):
		return 'tool'+self.tool_id
	def SetCache(self,value):
		key = self.GetKey()

		time = 24*60*60
		cache.set(key,value,time,version=self.version)
	
	def GetCache(self):
		key = self.GetKey()
		value = cache.get(key,version=self.version)
		return value

	def IsexistCache(self):
		key = self.GetKey()
		value = cache.get(key,version=self.version)
		if not value:
			return 0	#为0，不存在
		else:
			return 1	#为1，存在
	
	def DownloadFile(self):
		"""
		根据文件的git地址将文件下载至本地
		"""

		tool_path = self.d_homedir  +  '/ansible_file/' + 'tool'+self.tool_id + '/'
		rm_mk_dir = "rm -rf {0} && mkdir -p {1}".format(tool_path,tool_path)

		(mkdir_status,mkdir_output)=commands.getstatusoutput('bash -c "{0}"'.format(rm_mk_dir))
		#print mkdir_output
		
		d_headers = 'PRIVATE-TOKEN:4k-seAEmXzKCkLFzAeZ7'
		download_path = self.d_homedir + '/ansible_file/tool{0}/'.format(self.tool_id) #多个脚本重名
		#print download_path
		if self.script_urls:
			i = 0
			for script_url in self.script_urls:
				print script_url
				#s_download_file = "ansible localhost -u admin  -m get_url  -a 'url={0} dest={1} headers='{2}' mode=755' -become ".format(script_url,download_path,d_headers)
				#print 'ScriptExecution:DownloadFile:'+s_download_file
				
				#(download_status,download_output) = commands.getstatusoutput('bash -c "{0}"'.format(s_download_file))
	
				#print results_callback
				play_source = dict(
								name = "download url",
								hosts = 'localhost',
								remote_user='admin',
								gather_facts = 'no',
								tasks = [
									dict(action=dict(module='get_url',args='url=http://192.168.121.215/odmc-tools/tool-61/raw/develop/test.sh  dest={}  headers=PRIVATE-TOKEN:4k-seAEmXzKCkLFzAeZ7 mode=755'.format(download_path)))
								]
				)
				play = Play().load(play_source, variable_manager=self.variable_manager, loader=self.loader)
				qm = None
				try:
					tqm = TaskQueueManager(
								inventory=self.inventory,
								variable_manager=self.variable_manager,
								loader=self.loader,
								options=self.options,
								passwords=self.passwords,
								stdout_callback=self.results_callback,
					)
					result = tqm.run(play)
				finally:	
					if tqm is not None:
						tqm.cleanup()

				print self.results_callback.result_q
				
				if not self.results_callback.result_q.get('contacted') :
					return {'status':1,'msg':'fail to download the url'}
				i+=1
				if i == len(self.script_urls):
					return {'status':0,'msg':'scripts_urls download sucess'}	
		else:
			return {'status':1,'msg':'error:scripts_urls is null'}

	def ScriptExecute(self):
		"""
		脚本执行
		"""
		
		ansible_playbook = self.d_homedir + '/ansible_file/tool{0}/{1}'.format(self.tool_id,self.m_filename)
		log_file_path = '/tmp/' + self.log_file
		shell_path = '/tmp/tool{0}/'.format(self.tool_id)
		shell_exec_path = self.d_homedir +'/ansible_file/'+'tool'+self.tool_id
		user_host_path = os.path.join(USER_ANSIBLE_DIR, self.remote_user + '.hosts') 
		#shell_param = shell_path
		print ansible_playbook
		print self.script_urls
		print self.host
		
		status = 1 #文件下载标记，初始化未下载
		#判断是否已经下载过tool_id的工具
		
		if self.IsexistCache()==1:	#a、缓存中存在则已经下载过
			print '----------tool_id exist------------'
			print self.tool_id
			print '在堡垒机中已经有资源，不再下载了'

			status = 0
		else:
			#b、不存在，则进行下载
			run = self.DownloadFile()
			print 'ScriptExecution:ScriptExecute:'
			print run
			status =run.get('status')
			if status== 0:
				self.SetCache( 'already exist in pythonBLJ')#时间可以设置为1天

		#command = 'export APP_BASE_PATH =-'/home/admin/app_file''
	#	for script_name in self.scripts_name_list:
			

		#完成文件下载
		if status == 0 :
			#生成shell脚本执行语句
			if self.exec_type == 'shell':
				#mkdir_sh = "ansible {0} -m file -u {1} -a 'path=/tmp/ansible_file/  state=directory mode=0755' -become".format(self.host,self.remote_user)
				#(r_mkdir_sh,mkdir_log)=commands.getstatusoutput('bash -c "{0}"'.format(mkdir_sh))
				#print mkdir_log

				copy_sh ='sudo scp -r {0} {1}@{2}:/tmp/'.format(shell_exec_path,self.remote_user,self.host)
				print 'copy:::::::'+ copy_sh
				(status_sh,log_sh)= commands.getstatusoutput('bash -c "{0}"'.format(copy_sh))
				print status_sh,log_sh
				bits = "set -o pipefail;ansible -i {0} {1}   -u {2}  -a 'nohup sh {3} & chdir='{4}'' -become |tee -a {5}".format(user_host_path,self.host,self.remote_user,self.m_filename,shell_path,log_file_path)
			#生成yaml脚本执行语句
			elif self.exec_type == 'yaml':
				print 'is yaml enter'
				if len(self.host) > 15 :
					bits = "set -o pipefail;ansible-playbook  -i {0} {1}  --limit -{2} -f 20 -u {3} -b |tee -a {4}".format(user_host_path,ansible_playbook,self.host,self.remote_user,self.log_file)
				else:
					bits = "set -o pipefail;ansible-playbook  -i {0} {1}  --limit {1} -f 20 -u {2} -b |tee -a {3}".format(user_host_path,ansible_playbook,self.host,self.remote_user,self.log_file)
			#脚本执行并返回结果
			print bits
			(status,log) = commands.getstatusoutput('bash -c "{0}"'.format(bits))
			print log
			print status
			return {'log':log,'status':status}
		else:
			print 'imposible'
			return {'log':'file down fault','status':1}


