# -*- coding: utf-8 -*-

import multiprocessing

bind = "0.0.0.0:8001"  # 绑定IP和端口
workers = 5  # 最优进程数
backlog = 2048  # 等待连接最大数量
worker_class = 'gevent'  # 异步处理模块
worker_connections = 1000  # 单个worker最大链接数量
threads =  5#multiprocessing.cpu_count() * 2 + 1  # 最优线程数
max_requests = 2048  # 单个worker最大请求数，超过这个数量worker会重启
pidfile = 'gun.pid'  # gunicorn进程ID
proc_name = 'hiss'  # gunicorn进程名，多个gunicorn实例时有用，要安装setproctitle
timeout = 60  # 连接超时时间
debug = False  # debug模式
loglevel = 'info'  # 日志级别
errorlog = 'log/error.log'  # 错误日志文件路径
accesslog = 'log/access.log'  # 正常日志文件路径
