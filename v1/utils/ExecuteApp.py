#!/usr/bin/env  python2
# -*- coding: utf-8 -*-
import requests
import json
import commands
import os
import urllib,urllib2
from ExecuteScript import ScriptExecution
from django.core.cache import cache
import sys
from v1.utils.Config import USER_ANSIBLE_DIR,POSTSTATUS_URL
reload(sys)  
sys.setdefaultencoding('utf8')   
    

class AppExecution(object):
	def __init__ (self,data):
		self.user = data.get('user')
		self.host = str(data.get('host'))
		self.log_file = data.get('log_file')
		self.remote_user = data.get('remote_user')
		self.app_id = str(data.get('app_id'))
		self.app_package_path =data.get('app_package_path')
		self.script_resources = data.get('script_resources')
		self.task_seq = data.get('task_seq')
		self.app_type = data.get('app_type')
		self.d_homedir = '/home/admin/app_file'
		self.version = data.get('version')
		self.data =data

	def SetCache(self,value):
		key = 'app'+self.app_id
		
		time = 24*60*60
		cache.set(key,value,time,version=self.version)

	def GetCache(self):
		key =  'app'+self.app_id
		value = cache.get(key,version=self.version)
		return value
				
	def IsexistCache(self):
		key ='app'+self.app_id
		value = cache.get(key,version=self.version)
		if not value:
			return 0    #为0，不存在
		else:
			return 1    #为1，存在


	def DownloadApp (self):
		#self.tool_id = self.app_id
		#self.script_urls = self.app_package_path
		#down_app = ScriptExecution()
		#down_result = down_app.DownloadFile()
		#status = down_result['status']
		#if status == 0:
		app_path = self.d_homedir  + '/'+ 'app' + self.app_id + '/'
		print app_path
		rm_mk_app_dir = 'rm -rf {0} && mkdir {1}'.format(app_path,app_path)
		(mkdir_app_status,mkdir_app_output)=commands.getstatusoutput('bash -c "{0}"'.format(rm_mk_app_dir))
		d_headers = 'PRIVATE-TOKEN:4k-seAEmXzKCkLFzAeZ7'
		n=0
		if self.script_resources:
			
			download_app_file = "ansible localhost -u admin  -m get_url  -a 'url={0} dest={1} headers='{2}' mode=755' -become ".format(self.app_package_path,app_path,d_headers)
			print download_app_file
			(download_app_status,download_app_output) = commands.getstatusoutput('bash -c "{0}"'.format(download_app_file))
			
			if download_app_status != 0 :
				return {'status':1,'msg':'fail to download the url'}
			else:
				for j in range(len(self.script_resources)):
					self.task_idx = str(self.script_resources[j]['task_idx'])
					self.task_id  = str(self.script_resources[j]['task_id'])
					self.task_name = self.script_resources[j]['task_name']
					self.tools = self.script_resources[j]['tools']
												    
					for i in range(len(self.tools)):
						
						self.tool_id = str(self.tools[i]['tool_id'])
						self.tool_name = self.tools[i]['tool_name']    
						self.tool_idx = str(self.tools[i]['tool_idx'])
						self.tool_param = self.tools[i]['tool_param']
						self.m_filename =self.tools[i]['m_filename']
						self.exec_type = self.tools[i]['exec_type']
						self.script_urls = self.tools[i]['script_urls']
						tool_path = self.d_homedir + '/'+ 'app'+self.app_id + '/' + self.task_id + '/'+ self.tool_id + '/'
						mk_tool_dir = "mkdir  -p {0}".format(tool_path)
						print "mk_tool_dir:"+mk_tool_dir
						(mkdir_tool_status,mkdir_tool_output)=commands.getstatusoutput('bash -c "{0}"'.format(mk_tool_dir))

					
						d_headers = 'PRIVATE-TOKEN:4k-seAEmXzKCkLFzAeZ7'
						download_path = self.d_homedir + '/app{0}/{1}/{2}/'.format(self.app_id,self.task_id,self.tool_id) #多个脚本重名
																					                
						if self.script_urls:
							m = 0
							
							for script_url in self.script_urls :
								print script_url
								s_download_file = "ansible localhost -u admin  -m get_url -f 20 -a 'url={0} dest={1} headers='{2}' mode=755' -become ".format(script_url,download_path,d_headers)
								(download_status,download_output) = commands.getstatusoutput('bash -c "{0}"'.format(s_download_file))
								if download_status != 0: 
									return {'status':1,'msg':'fail to download the url'}
								m+=1
								if m == len(self.script_urls):
									n+=1
									print n
									if n == len(self.tools)*len(self.script_resources):
										
										return {'status':0,'msg':'scripts_urls download sucess'}    
						else:
						
							return {'status':1,'msg':'error:scripts_urls is null'}

	def PostStatus(self,task_status):
		payload = {
			"app_id" : self.app_id,
			"task_seq":self.task_seq,
			"host":self.host,
			"task_id": self.task_id,
			"task_status":task_status,
		}
		data_json =json.dumps(payload)
		url = POSTSTATUS_URL
		print url
		headers = {
			 "Content-Type":"application/json; charset=UTF-8",	
		}
		r = urllib2.Request(url,data_json,headers=headers)
		response = urllib2.urlopen(r)
		result =json.loads(response.read())
		print result
		#return  {'log':log,'status':status}




	def AppExecute(self):
		#run = self.DownloadApp()
		#status =run.get('status')
		print 'data ::::::::'
		print self.data

		status =1
		if self.IsexistCache()==1:  #a、缓存中存在则已经下载过print 
			print'----------tool_id exist------------'
			print '在堡垒机中已经有资源，不再下载了'
			exchange_status = 0
			status = 0
		else:
		#b、不存在，则进行下载
			run = self.DownloadApp()
			print 'ScriptExecution:ScriptExecute:'
			print run
			status =run.get('status')
			exchange_status = 1
			if status== 0:
				self.SetCache( 'already exist in pythonBLJ')#时间可以设置为1天

		
		if status == 0 :
			sort_script_resources = sorted(self.script_resources,key=lambda x:x['task_idx'])
					
			m = 0	
			for j in range(len(sort_script_resources)):
				
				self.task_idx = str(sort_script_resources[j]['task_idx'])
				self.task_id  = str(sort_script_resources[j]['task_id'])
				self.tools = sort_script_resources[j]['tools']
				self.task_name = sort_script_resources[j]['task_name']
				
				sort_tools = sorted(self.tools,key=lambda x:x['tool_idx'])
				n = 0
				for i in range(len(sort_tools)):

					self.tool_id = str(sort_tools[i]['tool_id'])
					self.tool_name = sort_tools[i]['tool_name']
					self.tool_idx = str(sort_tools[i]['tool_idx'])
					self.tool_param = sort_tools[i]['tool_param']
					self.m_filename =sort_tools[i]['m_filename']
					self.exec_type = sort_tools[i]['exec_type']
					self.script_urls = sort_tools[i]['script_urls']
					
					download_path = self.d_homedir+'/app{0}'.format(self.app_id)
					#{0}/{1}/{2}/.format(self.app_id,self.tas;k_id,self.tool_id) #多个脚本重名
					ansible_playbook = self.d_homedir + '/app{0}/{1}/{2}/{3}'.format(self.app_id,self.task_id,self.tool_id,self.m_filename)
					log_file_path = '/tmp/' + self.log_file
					shell_path = '/tmp/app{0}/{1}/{2}/'.format(self.app_id,self.task_id,self.tool_id)
					app_base_path =  '\/tmp\/app{0}'.format(self.app_id) 
					user_host_path = os.path.join(USER_ANSIBLE_DIR,self.remote_user + '.hosts')

					if exchange_status == 1:
						for script_url in self.script_urls :
							if script_url.split('.')[-1]=='sh'or script_url.split('.')[-1]== 'yml':
								print script_url
								exchange_file = script_url.split('/')[-1]
								##change_file_command = "cat {} |sed 's^${tool}/'"
								exchange_file_path = self.d_homedir + '/app{0}/{1}/{2}/{3}'.format(self.app_id,self.task_id,self.tool_id,exchange_file)							
								if '.sh' in exchange_file:
									exchange_shfile_command = "sed -i 's/{0}/{1}/g' {2}".format('${APP_BASE_PATH}',app_base_path,exchange_file_path)
									print exchange_shfile_command
									(exchange_sh_status, exchange_sh_log) = commands.getstatusoutput("{0}".format(exchange_shfile_command))
									print exchange_sh_log
								else:
									exchange_ymlfile_command = "sed -i 's/{0}/{1}/g' {2}".format('{{APP_BASE_PATH}}',app_base_path,exchange_file_path)
									(exchange_yml_status, exchange_yml_log) = commands.getstatusoutput("{0}".format(exchange_ymlfile_command))

								
							    

					if self.exec_type == 'shell':
						#mkdir_sh = "ansible {0} -u {1} -a 'mkdir /tmp/app_file/' -become ".format(self.host,self.remote_user)
						#(r_mkdir_sh,log_mkdir_sh)= commands.getstatusoutput('bash -c "{0}"'.format(mkdir_sh))


						copy_sh = " scp -r {0} {1}@{2}:/tmp/".format(download_path,self.remote_user,self.host)
						print copy_sh
						(status_sh,log_sh)= commands.getstatusoutput('bash -c "{0}"'.format(copy_sh))
						bits = "set -o pipefail;ansible -i {0} {1} -u {2}  -a 'nohup sh {3}  & chdir='{4}' ' -become |tee -a {5}".format(user_host_path,self.host,self.remote_user,self.m_filename,shell_path,log_file_path)
					
					elif self.exec_type == 'yaml':
						if len(self.host) > 15 :
							bits = "set -o pipefail;ansible-playbook  -i {0} {1}  --limit -{2} -u {3} -b |tee -a {4}".format(user_host_path,ansible_playbook,self.host,self.remote_user,log_file_path)
						else:
							bits = "set -o pipefail;ansible-playbook  -i {0} {1}  --limit {2} -u {3} -b |tee -a {4}".format(user_host_path,ansible_playbook,self.host,self.remote_user,log_file_path)
					#脚本执行并返回
					print bits
					(status, log) = commands.getstatusoutput('bash -c "{0}"'.format(bits))					
					print status	
					if status  != 0:
						r=self.PostStatus(task_status=1)
						print {'n,log':log,'status':status}
						return	{'log':log,'status':status}
					n += 1
					print 'n:'
					print n
					if  n  == len(self.tools):
						r = self.PostStatus(task_status=0)
						m += 1
						print '---------------'
						print m
						print len(self.script_resources)
						print '---------------'
						if m== len(self.script_resources):
							#print {'m,log':log,'status':status}
							return {'log':log,'status':0}
