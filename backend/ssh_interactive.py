from django.contrib.auth import authenticate
from assets import models

import getpass

class SshHandler(object):
    '''
    堡垒机交互脚本
    '''

    def __init__(self,argv_handler_instance):
        self.argv_handler_instance = argv_handler_instance
        self.models = models

    def auth(self):
        '''
        认证
        :return:
        '''

        count = 0
        while count < 3:
            username = input("Please your username: ").strip()
            #password = input("Please your password: ").strip()
            password = getpass.getpass("Please your password: ").strip()
            user = authenticate(username=username,password=password)
            if user:
                self.user = user
                return True
            else:
                count += 1

    def memu(self):

        msg = """
                                    0) 输入 \033[32mQ/q\033[0m 退出.
                                    1) 输入 \033[32mH/h\033[0m 显示您有权限的主机.
                                    2) 输入 \033[32mG/g\033[0m 显示您有权限的主机组.
                                    """
        print(msg)








    def interactive(self):
        '''
        启动交互脚本
        :return:
        '''
        if self.auth():
            import sys
            from backend import ssh_auth

            while True:
                self.memu()
                choice_option = input('Please option or ID: ').strip()
                if choice_option in ['0','Q','q']:
                    sys.exit()
                elif choice_option in ['1','H','h']:
                    if self.user.remote_user_bind_hosts.all():
                        choice_host_list = self.user.remote_user_bind_hosts.all()
                        while True:
                            print('[%-3s] %-12s %-20s  %-5s  %-10s ' % ('ID', '主机名', '内网IP', '环境', '项目'))
                            for hostobj in self.user.remote_user_bind_hosts.all():
                                print('[%-3s] %-10s %-15s  %-15s  %-15s' % (hostobj.host.id,
                                                                            hostobj.host.name,
                                                                            hostobj.host.lanip,
                                                                            hostobj.host.get_asset_env_display(),
                                                                            hostobj.host.asset_project))

                            choice = input('请选择主机：').strip()
                            if choice in ['q','quit']:
                                break
                            if choice.isdigit():
                                ssh_host_obj = self.user.remote_user_bind_hosts.all().get(id=choice)
                                print('ssh_host_obj', ssh_host_obj)
                                ssh_auth.ssh_connection(self, ssh_host_obj)

                    else:
                        print('暂无主机')
                elif choice_option in ['2','G','g']:
                    if self.user.host_groups.all():

                        while True:
                            for host_group_obj in self.user.host_groups.all():
                                print('[%-3s] %-12s' % ('ID', '组名'))
                                print('[%-3s] %-12s ' % (host_group_obj.id, host_group_obj.name))

                            choice = input('请选择主机组：').strip()
                            if choice in ['q','quit']:
                                break

                            if choice.isdigit():
                                choice = int(choice)
                                choice_group_obj = self.user.host_groups.all().get(id=choice)
                                while True:
                                    print('[%-3s] %-12s %-20s  %-5s  %-10s ' % ('ID', '主机名', '内网IP', '环境', '项目'))
                                    for hostobj in choice_group_obj.hostbindremoteusers.all():
                                        print('[%-3s] %-10s %-15s  %-15s  %-15s' % (hostobj.host.id,
                                                                                    hostobj.host.name,
                                                                                    hostobj.host.lanip,
                                                                                    hostobj.host.get_asset_env_display(),
                                                                                    hostobj.host.asset_project))

                                    choice = input('请选择主机：').strip()
                                    if choice in ['q', 'quit']:
                                        break
                                    if choice.isdigit():
                                        ssh_host_obj = choice_group_obj.hostbindremoteusers.all().get(id=choice)
                                        ssh_auth.ssh_connection(self,ssh_host_obj)




                    else:
                        print('暂无主机')

