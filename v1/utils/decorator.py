#*- coding: utf-8 -*-


import redis 

def queue_warpper(request.data):
	def queue_control(request.data):
		pool = redis.ConnectionPool(host='192.168.121.210', port=6379,db=3)
		r = redis.Redis(connection_pool=pool)

