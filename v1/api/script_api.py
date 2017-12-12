#!/usr/bin/env  python
# -*- coding: utf-8 -*-
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import list_route
from rest_framework.decorators import APIView

from models import API
from serializers import APISerializer
import os
import commands
import json

from time import sleep

from v1.utils.ExecuteScript import ScriptExecution
from v1.utils.ExecuteApp import AppExecution

home_dir = os.path.abspath('.') + '/'

class ToolExecute(APIView):
	def post(self,request):

		#j_data = request.POST
		#data = json.loads(j_data)
		data = request.data
		#task = ScriptExecution.ScriptExecute_bg.s(data)
		#res = task.delay()
		output= ScriptExecution(data).ScriptExecute()
		print output
		#result = res.get('output')
		#output = res.result
		status = str(output.get('status'))
		log = output.get('log')
		#content = output['content']
		#return Response({'task_id':res.task_id,'output':output})
		# script_urls = data.get('script_urls')
		#return Response({'task_id': res.task_id,'log':log,'status':status,'content':content})
		return Response({'log':log,'status':status})

	def get(self,request):
		pass

class ReturnLog(APIView):
	"""
	method of return log
	"""
	def get(self,request):
		data = request.GET
		log_file = data.get('log_file')
		start_row = int(data.get('start_row'))
		read_row = int(data.get('read_row'))
		finish_row = start_row + read_row
		log_file_path = '/tmp/'+ log_file

		if os.path.exists(log_file_path)== False:
			return Response({'code':4040,'message':'has no such file'})
		else:
			#with open(log_file_path, 'r') as f:
			#	file_list = f.readlines()
			#	logs = file_list[start_row - 1:finish_row -2]
			#	if logs != []:
			#		return Response({'code':200 ,'message':'success','logs':logs })
			#	else:
			#		return Response({'code':4040,'message':'logs has not generated'})
			count = 0
			logs = []
			#f = open(log_file_path, 'r')
			with open(log_file_path, 'r') as f:
				for i in f.xreadlines():  
					count += 1
					print count
					if count>=start_row and count<=(start_row+read_row):
						logs.append(i)
						print i
					if count == (start_row+read_row):
						break
				f.close()
				if logs != []:
					return Response({'code':200 ,'message':'success','logs':logs })
				else:
					return Response({'code':4040,'message':'logs has not generated'})	
			

class AppExecuteApi (APIView):
	def post(self,request):
		
		#j_data = request.POST
		#p_data = json.dumps(j_data)
		#data = json.loads(p_data)
		data = request.data
		output= AppExecution(data).AppExecute()
		
		#status = str(output.get('status',default=None))
		#log = output.get('log',default=None)
		
		return Response(output)
	def get ():
		pass

class TaskExecute (APIView):
	def post (self,request):
		pass 

class DownloadApi(APIView):
	def post (self,request):
		data = request.data
		output = ScriptExecution(data).DownloadFile()
		status = str(output['status'])
		msg = output['msg']
		return Response({'status':status,'msg':msg})

class ExecuteToolApi(APIView):
	def post (self,request):
		data = request.data
		output = ScriptExecution(data).ScriptExecute()
		status = str(output['status'])
		log = output['log']
		return Response({'status':status,'log':log})


