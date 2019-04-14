from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


class IDC(models.Model):
    '''
    机房
    '''
    name = models.CharField(max_length=128,null=True,blank=True,verbose_name='机房名称')
    region = models.CharField(max_length=16, blank=True, null=True, verbose_name='可用区')
    remarks = models.TextField(blank=True, null=True, verbose_name='备注')

    def __str__(self):
        return self.name


class Asset(models.Model):
    '''
    所有资产共有数据
    '''

    asset_idc_choices = (
        ('ucloud','Ucloud'),
        ('qcloud','腾讯云'),
        ('aws','aws'),
        ('aliyun','阿里云')
    )

    network_type_choices = (
        ('专有网络', '专有网络'),
        ('经典网络', '经典网络'),
        ('other', 'other')
    )

    name = models.CharField(unique=True,max_length=128,verbose_name='名称')
    mgaddress = models.GenericIPAddressField(unique=True,verbose_name='远程管理地址')
    lanip = models.GenericIPAddressField(unique=True,null=True,blank=True,verbose_name='内网IP')
    wanip = models.GenericIPAddressField(unique=True,null=True,blank=True,verbose_name='外网IP')
    port = models.IntegerField(default=22,verbose_name='ssh端口')
    idc = models.ForeignKey('IDC',null=True,blank=True,verbose_name='所在机房')
    sn = models.CharField(max_length=265,unique=True,verbose_name='sn')
    cpu_count = models.CharField(max_length=16,blank=True,null=True,verbose_name='逻辑CPU个数')
    cpu_core_count = models.CharField(max_length=16,blank=True,null=True,verbose_name='物理CPU个数')
    memory = models.CharField(max_length=16,blank=True,null=True,verbose_name='内存')
    disk = models.TextField(blank=True,null=True,verbose_name='磁盘')
    network = models.CharField(max_length=16,blank=True,null=True,choices=network_type_choices,default='other')
    create_time = models.DateTimeField(blank=True,null=True,verbose_name='主机购买时间')
    update_time = models.DateTimeField(blank=True,auto_now=True,verbose_name='更新时间')
    sys_images = models.CharField(max_length=128,blank=True,null=True,verbose_name='系统镜像')
    kernel_version = models.CharField(max_length=64,blank=True,null=True,verbose_name='内核版本')
    os_release = models.CharField(max_length=256, default='Ubuntu 14.04.3 LTS', verbose_name='系统发行版本')
    architecture = models.CharField(max_length=64, blank=True, null=True, verbose_name='系统架构')
    systemtime = models.CharField(max_length=128,blank=True,null=True,verbose_name='系统时间')
    admin = models.CharField(max_length=128,blank=True,null=True,verbose_name='资产管理人员')
    docker_version = models.CharField(max_length=32,blank=True,null=True,verbose_name='docker版本')
    storage_driver = models.CharField(max_length=128,blank=True,null=True,verbose_name='存储驱动')
    containers_count = models.CharField(max_length=16,blank=True,null=True,verbose_name='容器数量')
    containers_running = models.CharField(max_length=16,blank=True,verbose_name='运行容器数量')
    containers_paused = models.CharField(max_length=16,blank=True,verbose_name='暂停运行的容器数量')
    containers_stopped = models.CharField(max_length=16,blank=True,verbose_name='停止的容器数量')
    containers_images = models.CharField(max_length=16,blank=True,verbose_name='镜像数量')
    asset_env_type = (
            (1, '生产环境'),
            (2, '测试环境')
        )
    asset_env = models.SmallIntegerField(choices=asset_env_type,default=1)
    asset_project = models.CharField(max_length=128,null=True,blank=True,verbose_name='资产所属项目')
    remarks = models.TextField(blank=True, null=True, verbose_name='备注')

    def __str__(self):
        return self.name



class DockerPort(models.Model):

    local_port = models.CharField(max_length=16,null=True,blank=True,verbose_name='映射本机端口')
    container_port = models.CharField(max_length=16,null=True,blank=True,verbose_name='容器端口')


    def __str__(self):
        return 'local_port:{} -- container_port: {}'.format(self.local_port,self.container_port)


class DockerStorage(models.Model):
    source = models.CharField(max_length=128,null=True,blank=True,verbose_name='本地挂载目录')
    destination = models.CharField(max_length=128,null=True,blank=True,verbose_name='容器目录')


    def __str__(self):
        return 'Source: {} -- Destination: {}'.format(self.destination,self.source)


class container_user(models.Model):

    username = models.CharField(max_length=128,null=True,blank=True,verbose_name='用户名')
    password = models.CharField(max_length=128,null=True,blank=True,verbose_name='密码')


    class Meta:
        unique_together = ('username','password')


    def __str__(self):
        return "%s:%s" %(self.username,self.password)


class DockerAsset(models.Model):

    '''
    容器属性
    '''

    asset = models.ForeignKey(Asset,related_name='asset',related_query_name='asset')
    container_name = models.CharField(max_length=32,null=True,blank=True,verbose_name='容器名')
    container_id = models.CharField(max_length=256,unique=True,verbose_name='容器id')
    images = models.CharField(max_length=64,null=True,blank=True,verbose_name='镜像')
    network = models.CharField(max_length=64,blank=True,null=True,verbose_name='容器网络类型')
    platform = models.CharField(max_length=128,blank=True,null=True,verbose_name='容器基于系统平台')
    created = models.CharField(max_length=128,blank=True,null=True,verbose_name='容器创建时间')
    startedat = models.CharField(max_length=128,blank=True,null=True,verbose_name='容器启动时间')
    status = models.CharField(max_length=64, null=True, blank=True, verbose_name='容器状态')
    workingdir = models.CharField(max_length=128,null=True,blank=True,verbose_name='指定工作目录')
    container_port = models.ManyToManyField(DockerPort,blank=True,verbose_name='容器端口映射')
    container_storage = models.ManyToManyField(DockerStorage,blank=True,verbose_name='容器目录映射')
    container_user = models.ManyToManyField(container_user,blank=True,verbose_name='容器服务管理用户')
    env = models.TextField(blank=True,null=True,verbose_name='容器环境变量')
    run = models.TextField(null=True,blank=True,verbose_name='容器启动命令')
    remarks = models.TextField(blank=True, null=True, verbose_name='备注')


    def __str__(self):
        return  '{}'.format(self.container_id)



class HostGroup(models.Model):
    '''
    主机组表
    '''

    name = models.CharField(max_length=64,unique=True,verbose_name='主机组名称')
    hostbindremoteusers = models.ManyToManyField("HostBindRemoteUser")

    def __str__(self):
        return self.name



class HostBindRemoteUser(models.Model):
    '''
    绑定主机和远程用户对应关系
    '''

    host = models.ForeignKey("Asset")
    remote_user = models.ForeignKey("RemoteUser")


    class Meta:
        unique_together = ("host","remote_user")


    def __str__(self):
        return "%s-%s" %(self.host,self.remote_user)


class RemoteUser(models.Model):
    '''存储远程要管理的主机的账号信息'''
    auth_type_choices = ((0,'ssh-password'),(1,'ssh-key'))
    auth_type = models.SmallIntegerField(choices=auth_type_choices,default=0)
    username = models.CharField(max_length=32)
    password = models.CharField(max_length=64,blank=True,null=True)

    class Meta:
        unique_together = ('auth_type','username','password')


    def __str__(self):
        return "%s:%s" %(self.username,self.password)



class UserProfile(AbstractUser):
    '''
    堡垒机账号
    '''

    user_type_choices = (
        (0, '普通用户'),
        (1, '管理员'),
        (2, '超级管理员')
    )
    user_type = models.CharField(max_length=128, default=0, verbose_name='用户类型')
    remote_user_bind_hosts = models.ManyToManyField('HostBindRemoteUser', blank=True, verbose_name='堡垒机用户管理主机用户')
    host_groups = models.ManyToManyField('HostGroup', blank=True, verbose_name='所属堡垒机用户组')
    enabled = models.BooleanField(default=True, verbose_name='是否运行登录堡垒机')
    login_count = models.IntegerField(default=0, verbose_name='登录认证失败次数')





class Log(models.Model):
    LOGIN_CHOICES = (
        ('web', 'web'),
        ('ssh', 'ssh')
    )
    user = models.CharField(max_length=16, null=True,verbose_name='登录用户')
    host = models.CharField(max_length=128, null=True,verbose_name='登录主机')
    remote_ip = models.CharField(max_length=16,verbose_name='来源IP')
    login_type = models.CharField(max_length=8, choices=LOGIN_CHOICES, default='web',verbose_name='登录方式')
    start_time = models.DateTimeField(blank=True, auto_now_add=True,verbose_name='登录时间')
    end_time = models.DateTimeField(null=True,verbose_name='结束时间')
    hour_longtime = models.CharField(max_length=256,null=True,blank=True,verbose_name='登录时长')

    def __str__(self):
        return '{0.host}:[{0.login_type}]'.format(self)

    class Meta:
        verbose_name = '登录日志'
        verbose_name_plural = '登录日志'
        ordering = ['-id']



class TtyLog(models.Model):
    log = models.ForeignKey(Log,null=True,blank=True,on_delete=models.SET_NULL)
    datetime = models.DateTimeField(auto_now_add=True,verbose_name='命令执行时间')
    cmd = models.CharField(max_length=200)
    def __str__(self):
        return self.cmd
    class Meta:
        verbose_name = '操作日志'
        verbose_name_plural = '操作日志'



class RecorderLog(models.Model):
    '''
    存储审计回放
    '''
    log = models.ForeignKey(Log,null=True,blank=True,on_delete=models.SET_NULL)
    logpath = models.TextField(null=True,blank=True,verbose_name='回放日志存储路径')
    class Meta:
        verbose_name = '回放日志'
        verbose_name_plural = '回放日志'


class AssetRecord(models.Model):
    '''
    资产变更记录
    '''

    asset = models.ForeignKey('Asset')
    content = models.TextField(null=True,blank=True,verbose_name='资产变更详情')
    creator = models.ForeignKey('UserProfile',null=True,blank=True,verbose_name='资产手动更新人')
    create_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.asset.name



class ErrorLog(models.Model):
    """
    错误日志
    """
    asset_obj = models.ForeignKey('Asset', null=True, blank=True)
    title = models.CharField(max_length=512)
    content = models.TextField()
    create_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "错误日志表"

    def __str__(self):
        return self.title

