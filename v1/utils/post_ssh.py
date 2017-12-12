#!/usr/bin/env  python2
# -*- coding: utf-8 -*-

from v1.utils.Config import SERVER_HOSTS_LIST
import urllib2
import netifaces 

def post_ssh_to_hosts(data):

	local_ip = netifaces.ifaddresses('ens160')[2][0]['addr']
	SERVER_HOSTS_LIST.remove(local_ip)
	payload = {
			"app_id" : self.app_id,
			"task_seq":self.task_seq,
			"host":self.host,
			"task_id": self.task_id,
			"task_status":task_status,
	}
	data_json =json.dumps(payload)
	url = POSTSTATUS_URL
	127         print url
	128         headers = {
		129              "Content-Type":"application/json; charset=UTF-8",
		130         }
		131         r = urllib2.Request(url,data_json,headers=headers)
	132         response = urllib2.urlopen(r)
	133         result =json.loads(response.read())
	134         print result
	135         #return  {'log':log,'status':status}


