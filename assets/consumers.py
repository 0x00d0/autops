from channels.generic.websocket import WebsocketConsumer

import json
import paramiko
from . import models
from django.db.models import Q
from asgiref.sync import async_to_sync
import threading
from channels.layers import get_channel_layer
import datetime
import time
from autops.settings import MEDIA_ROOT
import random
import string
import os
import traceback

import logging
logger = logging.getLogger('log')




channel_layer = get_channel_layer()

# 把一次会话，用户输入的命令
CMD_CONTENT = list()
# 用户输入的字符串
CMD_STR = list()



def random_str():

    str = string.ascii_lowercase + string.digits
    result = ''.join(random.sample(str,30))
    return result



class TermLogRecorder():
    def __init__(self,log):
        self.log = log
        self.Recorder_log = {}
        self.StartTime = time.time()
        self.rowslog = []
        self.logname = ''.join(random_str())
        self.time_path = time.strftime("%Y_%m_%d_%H",time.localtime())
        self.logpath = '{}/{}/{}.cast'.format(MEDIA_ROOT,self.time_path,self.logname)

    def write(self,logtype,msg):

        self.rowslog.append([str(time.time() - self.StartTime),logtype,msg])

    def save(self):

        header = {
            "version": 2,
            "width": 80,
            "height": 24,
            "timestamp": round(self.StartTime),
            "title": "Demo",
            "env": {
                "TERM": 'TERM',
                "SHELL":  '/bin/bash'
            },
        }


        path = os.path.join(MEDIA_ROOT,self.time_path)
        if not os.path.exists(path):
            os.mkdir(path)

        with open(self.logpath,mode='w') as f:
            f.write(json.dumps(header) + '\n')
            for row in self.rowslog:
                f.write(json.dumps(row) + '\n')

        self.rowslog.insert(0,header)

        models.RecorderLog(log=self.log,logpath=self.time_path +'/'+self.logname + '.cast').save()



class WebSSHThread(threading.Thread):
    def __init__(self,chan,channel_name,recorderlog):
        threading.Thread.__init__(self)
        self.chan = chan
        self.channel_name = channel_name
        self.recorderlog = recorderlog


    def run(self):

        while not self.chan.shell.exit_status_ready():
            try:
                data = self.chan.shell.recv(1024)

                # 官方文档说明https://channels.readthedocs.io/en/latest/topics/channel_layers.html
                async_to_sync(self.chan.channel_layer.send)(self.channel_name,{"type": "ssh.message","text": data.decode()},)
                self.recorderlog.write("o",data.decode())

            except Exception as e:
                logger.error(e)
                logger.error(traceback.format_exc())


        self.chan.sshclient.close()
        return False



class WebSSHConsumer(WebsocketConsumer):

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)


    def connect(self):
        try:
            remote_ip = self.scope['client'][0]
            self.opsuser = self.scope['user']       # 堡垒机用户
            hostid = self.scope['url_route']['args'][0]         # ssh连接主机id
            hostobj = models.HostBindRemoteUser.objects.filter(Q(host__id=hostid),
                                                               Q(userprofile__username=self.opsuser)|Q(hostgroup__userprofile__username=self.opsuser)).distinct().first()


            if hostobj:
                self.host = hostobj.host.mgaddress
                port = hostobj.host.port
                user = hostobj.remote_user.username
                auth_type = hostobj.remote_user.auth_type
                self.sshclient = paramiko.SSHClient()
                self.sshclient.set_missing_host_key_policy(paramiko.AutoAddPolicy())

                if auth_type == 0:

                    pwd = hostobj.remote_user.password
                    self.sshclient.load_system_host_keys()
                    self.sshclient.connect(hostname=self.host, port=port, username=user, password=pwd)

                elif auth_type == 1:
                    self.sshclient.connect(hostname=self.host,port=port,username=user)

                self.shell = self.sshclient.invoke_shell()
                self.log = models.Log(user=self.opsuser, host=self.host, remote_ip=remote_ip, login_type='web')
                self.log.save()
                self.recorderlog = TermLogRecorder(log=self.log)

                chan = WebSSHThread(self, self.channel_name,self.recorderlog)
                chan.setDaemon(True)
                chan.start()


            else:

                logger.info('来源IP：{} 用户: {} 尝试连接服务器id为:{}'.format(remote_ip,self.opsuser,hostid))
                async_to_sync(self.channel_layer.send)(
                    self.channel_name,
                    {
                        'type':'ssh.message',
                        'text':'无权限连接.....'
                    }
                )

        except paramiko.AuthenticationException:
            async_to_sync(self.channel_layer.send)(
                self.channel_name,
                {
                    'type': 'ssh.message',
                    'text': '账号密码错误......'
                }
            )


        except Exception as e:
            logger.error(e)
            logger.error(traceback.format_exc())

            async_to_sync(self.channel_layer.send)(
                self.channel_name,
                {
                    'type': 'ssh.message',
                    'text': '连接失败请联系管理员...'
                }
            )

        self.accept()



    def ssh_message(self, event):
        self.send(text_data=event["text"])


    def receive(self, text_data=None, bytes_data=None):

        try:

            if text_data in ['\r','\n','\r\n']:
                CMD_CONTENT.append(''.join(CMD_STR))
                CMD_STR.clear()
                if len(CMD_CONTENT[0]) > 1:     # 不为空，忽略 enter
                    models.TtyLog(log=self.log,datetime=datetime.datetime.now(),cmd=(''.join(CMD_CONTENT))).save()
                    self.recorderlog.write("i",''.join(CMD_CONTENT))
                CMD_CONTENT.clear()
            else:

                CMD_STR.append(text_data)

            self.shell.send(text_data)

        except Exception as e:
            logger.error(e)
            logger.error(traceback.format_exc())


    def disconnect(self, close_code):

        try:
            models.Log.objects.filter(id=self.log.id).update(end_time=datetime.datetime.now())
            logobj = models.Log.objects.filter(id=self.log.id).first()
            if logobj.end_time and self.log.start_time:
                models.Log.objects.filter(id=self.log.id).update(hour_longtime = logobj.end_time - self.log.start_time)
                self.recorderlog.save()

        except Exception as e:
            logger.error(e)
            logger.error(traceback.format_exc())


