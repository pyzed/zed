# -*- coding: utf-8 -*-

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

USER_PATH = os.environ['HOME']

# ansible 文件路径
USER_ANSIBLE_DIR = os.path.join(USER_PATH, '.ansible/')

# ansible hosts 文件路径
ANSIBLE_HOSTS_PATH = os.path.join(USER_PATH, '.ansible/hosts')

# 本地ssh key
SSH_KEY_PUB_PATH = os.path.join(USER_PATH, '.ssh/id_rsa')

# 超时时间(秒)
TIMEOUT = 3

SERVER_HOSTS_LIST =['192.168.121.217','192.168.121.216']
#key
KEY ='oDM239c!$ocmd339'

#app post url
POSTSTATUS_URL = 'http://192.168.121.210/odmc/applicationCenter/appProject/task-state-chage'



