# -*- coding: utf-8 -*-
import sys
import os
from Crypto.Cipher import AES
from binascii import b2a_hex,a2b_hex
import base64
import subprocess
from v1.utils.Config import USER_ANSIBLE_DIR,KEY,SERVER_HOSTS_LIST
from passlib.hash import sha512_crypt
from v1.utils.GetPublicKey import ReturnHostsResult
import commands
import urllib2
import netifaces
import json
import time
reload(sys)
sys.setdefaultencoding('utf8')



class ExistsUser(object):

    def __init__(self, data):
        self.data = data
        self.new_user = data.get('new_user')
    def ensure_data(self):
        """
        验证传入的数据是不是dict， 需要json
        :return:
        """
        if not isinstance(self.data, dict):
            return {'code': 4040, "msg": "Please check the data"}
        ip = self.data.get('ip')
        user = self.data.get('user')
        return ip, user

    def save_hosts(self):
        """
        保存到hosts文件
        :return:
        """
        ip, user = self.ensure_data()
        path = os.path.join(USER_ANSIBLE_DIR, user + '.hosts')
        with open(path, 'a') as f:
            f.write('\n'+ip)
        path2= os.path.join(USER_ANSIBLE_DIR, user + '.backup')
        uniq_command = "sort {0} |uniq > {1} && cat  {2} > {3}".format(path,path2,path2,path)
        (uniq_status,uniq_log)=commands.getstatusoutput(uniq_command)
        print self.new_user
        new_user_path = os.path.join(USER_ANSIBLE_DIR,self.new_user+'.hosts')
        print new_user_path
        new_user_path2 = os.path.join(USER_ANSIBLE_DIR,self.new_user+'.backup')
        with open(new_user_path,'a') as f_new:
            f_new.write('\n'+ip)
        uniq_commands = "sort {0} |uniq > {1} && cat {2} > {3}".format(new_user_path,new_user_path2,new_user_path2,new_user_path)
        (uniq_status_new,uniq_log_new) =commands.getstatusoutput(uniq_commands)
	
        return path

    def get_users(self):
        """
        获取用户列表， 无root
        :return:
        """
        #print SERVER_HOSTS_LIST
        ip, user = self.ensure_data()
        #new_user =self.data.get('new_user')
        new_pass =self.data.get('new_pass')
        ssh_port =self.data.get('ssh_port','22')
        #print new_pass
        new_pass = new_pass.replace(' ','+')
        new_pass = base64.decodestring(new_pass)
        cryptor = AES.new(KEY, AES.MODE_CBC,KEY)
		
        #print new_pass
        new_pass = cryptor.decrypt(new_pass)
        #new_pass = new_pass.rstrip('\0')

        new_pass = new_pass.split('+')[0]

        print new_pass
        print type(new_pass)
        print len(new_pass)
        path = self.save_hosts()
        print path
        #s = subprocess.Popen("ansible -i {0} all -m shell -a 'cat /etc/passwd |cut -f 1 -d : ' -u {1}".format(path, user), shell=True,
                            # stdout=subprocess.PIPE,
                            # stderr=subprocess.STDOUT, close_fds=True)
        s="ansible -i {0} {1} -m shell -a 'cat /etc/passwd |cut -f 1 -d : ' -u {2}".format(path,ip, user)
        (status,sc)= commands.getstatusoutput(s)
        print sc
        if '{0} | SUCCESS '.format(ip) in sc:
            user_data = sc.split('>>')[1].split('\n')[1:]
            print user_data
            if self.new_user in user_data:
                r = ReturnHostsResult(self.data).ensure_pub()
                if r['code'] == 200:
                    ssh_command =  "sshpass -p '{0}' ssh-copy-id -o StrictHostKeyChecking=no {1}@{2} -p {3}".format(new_pass,self.new_user,ip,ssh_port)              
                    
                    (ssh_status,ssh_log)= commands.getstatusoutput(ssh_command)
                    #print ssh_log
                    #print SERVER_HOSTS_LIST
                    local_ip = netifaces.ifaddresses('ens160')[2][0]['addr']
                    #print local_ip
                    #print type(local_ip)
                    #a=SERVER_HOSTS_LIST
                    #print a
                    #all_of_hosts = a.replace(local_ip)
                    #print all_of_hosts
                    for other_hosts in SERVER_HOSTS_LIST:
                        if other_hosts == local_ip:
                            pass
                        else:
                            BS = AES.block_size
                            pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
                            cipher = AES.new(KEY, AES.MODE_CBC,KEY)
                            new_pass = new_pass +'+'+str(int(time.time()))
                            print new_pass
                            new_pass = cipher.encrypt(pad(new_pass))
                            print new_pass
                            new_pass = base64.encodestring(new_pass)
                            print new_pass
				
                            print other_hosts
                            payload = {
                                "new_pass" :new_pass,
                                "new_user":self.new_user,
                                "ip":ip,
                                "ssh_port":ssh_port,
                                "user":user,
                            }
                            data_json =json.dumps(payload)
                            url = 'http://{}:8001/v1/users/ssh'.format(other_hosts)
                            print url
                            headers = {
                                "Content-Type":"application/json; charset=UTF-8",
                            }
                            r = urllib2.Request(url,data_json,headers=headers)
                            response = urllib2.urlopen(r)
                            result =json.loads(response.read())
                            print  '+++++++++++++++++++++++++'
                            print new_pass
                            print result
                            print '+++++++++++++++++++++++++++++'


                    if 'the key(s) you wanted were added' in ssh_log or 'All keys were skipped because they already exist on the remote system' in ssh_log:
                        return {'code': 200, 'message': 'Success', 'data': user_data}
                    else:
                        return {'code': 4040, "message": ssh_log}
                else:
                    return{'code':4040,'message':'There is not exist publickey'}
            else:
                return {'code':4040,'message':'There is not exist this user'}
        else:
            return {'code': 4040, 'message': 'False'}
    

    def get_users_list(self):
        """
        """
        new_user =self.data.get('new_user')
        ip, user = self.ensure_data()
        path = self.save_hosts()
        s="ansible -i {0} {1} -m shell -a 'cat /etc/passwd |cut -f 1 -d : ' -u {2}".format(path,ip, user)
        (status,sc)= commands.getstatusoutput(s)
        print sc
        if '{0} | SUCCESS '.format(ip) in sc:
            user_data = sc.split('>>')[1].split('\n')[1:]
            print user_data
            if new_user in user_data:
                return{'code':200,'message':'Success','data':user_data}
            return {'code':4040,'message':'There is not exist this user'}





class AddUser(object):
    def __init__(self, data):
        self.data = data

    def ensure_data(self):
        """
        验证传入的数据是不是dict， 需要json
        :return:
        """
        if not isinstance(self.data, dict):
            return {'code': 4040, "message": "Please check the data"}
        ip = self.data.get('ip')
        root_user = self.data.get('root_user')
        new_user = self.data.get('new_user')
        new_pass = self.data.get('new_pass')
        group = self.data.get('group')
        return ip, root_user, new_user, new_pass, group

    def save_hosts(self):
        """
        保存到hosts文件
        :return:
        """
        ip, root_user, new_user, new_pass, group = self.ensure_data()
        path = os.path.join(USER_ANSIBLE_DIR, root_user + '.hosts')
        with open(path, 'a') as f:
            f.write('\n'+ip)
        path2= os.path.join(USER_ANSIBLE_DIR, root_user + '.backup')
        uniq_command = "sort {0} |uniq > {1} && cat  {2} > {3}".format(path,path2,path2,path)
        (uniq_status,uniq_log)=commands.getstatusoutput(uniq_command)
        return path

    def create_user(self):
        """
        创建用户
        :return:
        """
        ip, root_user, new_user, new_pass, group = self.ensure_data()
        path = self.save_hosts()
        hash_pass = sha512_crypt.using(rounds=5000).hash(new_pass)
        print hash_pass
        s = subprocess.Popen(
            'ansible -i {0} {1} -m user -a "name={2} shell=/bin/bash group={3} password={4}" -u {5} -become'.format(
                path,ip,
                new_user,
                group,
                hash_pass,
                root_user),
            shell=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
        sc = s.communicate()
        if '{0} | SUCCESS '.format(ip) in sc[0]:
            return {'code': 200, 'message': 'Success'}
        return {'code': 4040, 'message': 'Create User Failure'}



class DeleteUser(object):
    def __init__(self, data):
        self.data = data

    def ensure_data(self):
        """
        验证传入的数据是不是dict， 需要json
        :return:
        """
        if not isinstance(self.data, dict):
            return {'code': 4040, "message": "Please check the data"}
        ip = self.data.get('ip')
        root_user = self.data.get('root_user')
        del_user = self.data.get('del_user')
        return ip, root_user, del_user

    def save_hosts(self):
        """
        保存到hosts文件
        :return:
        """
        ip, root_user, del_user = self.ensure_data()
        path = os.path.join(USER_ANSIBLE_DIR, root_user + '.hosts')
        with open(path, 'a') as f:
            f.write('\n'+ip)
        path2= os.path.join(USER_ANSIBLE_DIR,root_user + '.backup')
        uniq_command = "sort {0} |uniq > {1} && cat  {2} > {3}".format(path,path2,path2,path)
        (uniq_status,uniq_log)=commands.getstatusoutput(uniq_command)

        return path

    def del_user(self):
        """
        删除用户
        :return:
        """
        ip, root_user, del_user = self.ensure_data()
        path = self.save_hosts()

        s = subprocess.Popen(
            'ansible -i {0} {1} -m shell -a "userdel -rf {2}  && rm -rf /home/{3}" -u {4} -become'.format(path,ip,
                                                                                                del_user,
                                                                                                del_user,
                                                                                                root_user),
            shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
        sc = s.communicate()
        if '{0} | SUCCESS '.format(ip) in sc[0]:
            return {'code': 200, 'message': 'Success'}
        return {'code': 4040, 'message': 'There is not exist this user'}


if __name__ == '__main__':
    a = ExistsUser({"ip": "172.16.228.134", 'user': 'root'})
    b = a.get_users()
    print b
    # c = AddUser({"ip": "172.16.228.134", 'new_user': 'test', 'new_pass': 'admin', 'group': 0, 'root_user': 'root'})
    # d = c.create_user()
    # print d
    # e = DeleteUser({'ip': "172.16.228.134", 'root_user': 'root', 'del_user': 'test'})
    # f = e.del_user()
    # print f
