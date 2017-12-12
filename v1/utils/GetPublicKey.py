# -*- coding: utf-8 -*-

from subprocess import STDOUT, check_output
import subprocess
import platform
import os
import json
import commands
from Config import *
from Crypto.Cipher import AES
from binascii import b2a_hex,a2b_hex
import base64
import commands
import urllib2
import netifaces
import time
import json



class ReturnHostsResult(object):
    def __init__(self, data):
        print data
        self.ssh_host = data.get('ssh_host')
        self.ssh_port = data.get('ssh_port')
        self.ssh_user = data.get('ssh_user')
        self.ssh_pass = data.get('ssh_pass', 22)
        # self.ssh_host = '192.168.121.216'
        # self.ssh_port = 22
        # self.ssh_user = 'admin'
        # self.ssh_pass = 'Wsad#adm'
        
    def ensure_pub(self):
        """
        确保本地有id_rsa.pub，如果没有创建
        :return:
        """

        sys = platform.system()
        if sys in ['Darwin', 'Linux']:
            s = subprocess.Popen('ls {0}'.format(SSH_KEY_PUB_PATH), shell=True, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, close_fds=True)
            result = s.communicate()
            if 'id_rsa.pub' not in result[0]:
                subprocess.Popen('ssh-keygen -t rsa -f {0} -P ""'.format(SSH_KEY_PUB_PATH), shell=True,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
            print '------'
            return {'code': 200, "message": "Success"}
        else:
            return {'code': 4040, "message": "Unsupported system"}


    def push_key(self):
        """
        上传id_rsa.pub到远程主机
        :return:
        """
        self.ssh_pass = self.ssh_pass.replace(' ','+')
        self.ssh_pass = base64.decodestring(self.ssh_pass)
        cryptor = AES.new(KEY, AES.MODE_CBC,KEY)
        self.ssh_pass= cryptor.decrypt(self.ssh_pass)
        self.ssh_pass= self.ssh_pass.split('+')[0]
        print self.ssh_pass

        command = 'sshpass -p {0} ssh-copy-id -o StrictHostKeyChecking=no {1}@{2} -p {3}'.format(self.ssh_pass,
                                                                                                 self.ssh_user,
                                                                                                 self.ssh_host,
                                                                                                 self.ssh_port)
        s = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
        result = s.communicate()[0]
        print result
        local_ip = netifaces.ifaddresses('ens160')[2][0]['addr']
        n=1
        for other_hosts in SERVER_HOSTS_LIST:
            if other_hosts == local_ip:
                pass
            else:
                BS = AES.block_size
                pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
                cipher = AES.new(KEY, AES.MODE_CBC,KEY)
                self.ssh_pass = self.ssh_pass +'+'+str(int(time.time()))
                print self.ssh_pass
                self.ssh_pass = cipher.encrypt(pad(self.ssh_pass))
                print self.ssh_pass
                self.ssh_pass = base64.encodestring(self.ssh_pass)
                print self.ssh_pass
                print other_hosts
                payload = {
                    "ssh_pass" :self.ssh_pass,
                    "ssh_user":self.ssh_user,
                    "ssh_host":self.ssh_host,
                    "ssh_port":self.ssh_port,
                    }
                data_json =json.dumps(payload)
                url = 'http://{}:8001/v1/machines/add'.format(other_hosts)
                print url
                headers = {
                    "Content-Type":"application/json; charset=UTF-8",
                }
                r = urllib2.Request(url,data_json,headers=headers)
                response = urllib2.urlopen(r)
                r_result =json.loads(response.read())
                print  '+++++++++++++++++++++++++'
                print r_result
                
        if 'the key(s) you wanted were added' in result or 'All keys were skipped because they already exist on the remote system' in result:
            print '11111111111111111111111111'
            return {'code': 200, "message": "success"}
        else:
            #print '222222'
            return {'code': 4040, "message": result}

    def save_hosts(self):
        
        if not self.ssh_user or not self.ssh_port or not self.ssh_user or not self.ssh_pass:
            return {'code': 4040, "message": "No data available"}
        path = os.path.join(USER_ANSIBLE_DIR, self.ssh_user+'.hosts')
        with open(path, 'a') as f:
            f.write('\n'+self.ssh_host)
        path2= os.path.join(USER_ANSIBLE_DIR, self.ssh_user + '.backup')
        print path2
        uniq_command = "sort {0} |uniq > {1} && cat  {2} > {3}".format(path,path2,path2,path)
        (uniq_status,uniq_log)=commands.getstatusoutput(uniq_command)

        return path

    def get_config(self):
        """
        测试主机能不能登录，如果操作成功，返回配置信息
        :return:
        """
        path = self.save_hosts()
        print path
        s = subprocess.Popen('ansible -i {0} {1} -m setup -u {2} '.format(path, self.ssh_host,self.ssh_user),
                             shell=True,
        
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
        print 'ansible -i {0} {1} -m setup -u {2} '.format(path, self.ssh_host,self.ssh_user)
        query_data = s.communicate()[0]
		# print query_data
        if '{0} | SUCCESS '.format(self.ssh_host) in query_data:

            result = json.loads(query_data.split('=> ')[1]).get('ansible_facts')
            # print result
            hosts_config = {"cpu_model": result.get('ansible_processor'),
                            "cpu_cores": result.get('ansible_processor_cores'),
                            "cpu_threads": int(result.get('ansible_processor_cores')) * int(
                                                    result.get('ansible_processor_threads_per_core')),
                            'memory_size': result.get('ansible_memtotal_mb'),
                            "disk_size": result.get('ansible_devices').get('sda').get('size'),
                            "system_distribution": result.get('ansible_distribution'),
                            "system_release": result.get('ansible_distribution'),
                            "system_type": result.get('ansible_machine'),
                            "system_version": result.get('ansible_distribution_version'),
                            "system_install_command": result.get('ansible_pkg_mgr'),
                            "ip_address": result.get('ansible_default_ipv4').get('address'),
                            "mac_address": result.get('ansible_default_ipv4').get('macaddress')
                            }

            return {'code': 200, "message": "Success", "data": hosts_config}
        else:
            return {'code': 4040, "message": 'Can\'t login in the hosts'}

            # 如果主机处于关闭状态，会有10秒左右的等待，可以修改config里的timeout

    def main(self):
        """
        执行
        :return:
		"""
        if self.ensure_pub()['code'] == 200:
            if self.push_key()['code'] == 200:
                return self.get_config()
            else:
                return {"code":"4040","message":"Operation Failed"}
        else:
            return self.ensure_pub()

if __name__ == '__main__':
    data = {"ssh_host": "172.16.228.134", "ssh_port": "22", "ssh_user": "root",
            "ssh_pass": "admin"}
    r = ReturnHostsResult(data)
    a = r.main()
    print a
