


class ArgvHandler(object):
    '''
    接受用户参数，并调用相应的功能
    '''

    def __init__(self,sys_args):
        self.sys_args = sys_args


    def run(self):
        '''
        启动用户交互程序
        :return:
        '''

        from backend.ssh_interactive import SshHandler
        obj = SshHandler(self)
        obj.interactive()



















