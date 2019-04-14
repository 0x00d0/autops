import traceback
from assets import models
from django.db.models import Q
import logging

logger = logging.getLogger('log')


class UpdateAsset():

    def __init__(self, assetobj, report_data):
        self.assetobj = assetobj
        self.report_data = report_data

    def update_asset(self):
        try:
            log_list = []
            os_release = self.report_data.get('os_info').get('os_release')
            kernel_version = self.report_data.get('os_info').get('kernel_version').split('\n')
            architecture = self.report_data.get('os_info').get('architecture').split('\n')
            systemtime = self.report_data.get('os_info').get('systemtime').split('\n')

            if self.assetobj.cpu_count != str(self.report_data.get('cpu_info').get('cpu_count')):
                log_list.append('逻辑CPU个数由{}变更为{}'.format(self.assetobj.cpu_count,
                                                         self.report_data.get('cpu_info').get('cpu_count')))
                self.assetobj.cpu_count = self.report_data.get('cpu_info').get('cpu_count')

            if self.assetobj.memory != str(self.report_data.get('mem_info')):
                log_list.append('内存容量由{}变更为{}'.format(self.assetobj.memory, self.report_data.get('mem_info')))
                self.assetobj.memory = self.report_data.get('mem_info')

            if self.assetobj.cpu_core_count != str(self.report_data.get('cpu_info').get('cpu_core_count')):
                log_list.append('物理CPU个数由{}变更为{}'.format(self.assetobj.cpu_core_count,
                                                         self.report_data.get('cpu_info').get('cpu_core_count')))
                self.assetobj.cpu_core_count = self.report_data.get('cpu_info').get('cpu_core_count')

            if self.assetobj.os_release != os_release:
                log_list.append('系统发行版本由{}变更为{}'.format(self.assetobj.os_release, os_release))
                self.assetobj.os_release = os_release

            if self.assetobj.architecture != architecture[0]:
                log_list.append('系统架构由{}变更为{}'.format(self.assetobj.architecture, architecture[0]))
                self.assetobj.architecture = architecture[0]

            if self.assetobj.systemtime != systemtime[0]:
                self.assetobj.systemtime = systemtime[0]

            if self.assetobj.kernel_version != kernel_version[0]:
                log_list.append('内核版本由{}变更为{}'.format(self.assetobj.kernel_version, kernel_version[0]))
                self.assetobj.kernel_version = kernel_version[0]

            if self.assetobj.docker_version != self.report_data.get('docker_info').get('docker_version'):
                log_list.append('docker version由{}变更为{}'.format(self.assetobj.docker_version,
                                                                self.report_data.get('docker_info').get(
                                                                    'docker_version')))
                self.assetobj.docker_version = self.report_data.get('docker_info').get('docker_version')

            if self.assetobj.storage_driver != self.report_data.get('docker_info').get('storage_driver'):
                log_list.append('docker存储驱动由{}变更为{}'.format(self.assetobj.storage_driver,
                                                            self.report_data.get('docker_info').get('storage_driver')))
                self.assetobj.storage_driver = self.report_data.get('docker_info').get('storage_driver')

            if self.assetobj.containers_count != str(self.report_data.get('docker_info').get('containers_count')):
                log_list.append('容器数量由{}变更为{}'.format(self.assetobj.containers_count,
                                                      self.report_data.get('docker_info').get('containers_count'), ))
                self.assetobj.containers_count = self.report_data.get('docker_info').get('containers_count')

            if self.assetobj.containers_running != str(self.report_data.get('docker_info').get('containers_running')):
                log_list.append('运行容器数量由{}变更为{}'.format(self.assetobj.containers_running,
                                                        self.report_data.get('docker_info').get('containers_running')))
                self.assetobj.containers_running = self.report_data.get('docker_info').get('containers_running')

            if self.assetobj.containers_paused != str(self.report_data.get('docker_info').get('containers_paused')):
                log_list.append('暂停的容器数量由{}变更为{}'.format(self.assetobj.containers_paused,
                                                         self.report_data.get('docker_info').get('containers_paused')))
                self.assetobj.containers_paused = self.report_data.get('docker_info').get('containers_paused')

            if self.assetobj.containers_stopped != str(self.report_data.get('docker_info').get('containers_stopped')):
                log_list.append('停止的容器数量由{}变更为{}'.format(self.assetobj.containers_stopped,
                                                         self.report_data.get('docker_info').get('containers_stopped')))
                self.assetobj.containers_stopped = self.report_data.get('docker_info').get('containers_stopped')

            if self.assetobj.containers_images != str(self.report_data.get('docker_info').get('containers_images')):
                log_list.append('容器镜像数量由{}变更为{}'.format(self.assetobj.containers_images,
                                                        self.report_data.get('docker_info').get('containers_images')))
                self.assetobj.containers_images = self.report_data.get('docker_info').get('containers_images')

            self.assetobj.save()

            if log_list:
                models.AssetRecord.objects.create(asset=self.assetobj, content='\n'.join(log_list))
                log_list.clear()

        except Exception as e:

            logger.error(e, traceback.format_exc())
            models.ErrorLog.objects.create(asset_obj=self.assetobj, title=e, content=traceback.format_exc())


class UpdateDockerAsset():

    def __init__(self, assetobj, docker_info):

        self.assetobj = assetobj
        self.container_list = docker_info

    def updateasset(self):

        try:

            log_list = []

            # 更新
            for container in self.assetobj.asset.all():  # 获取当前主机上所有的容器

                if container.container_id in self.container_list:  # 判决数据库中的容器存在agent采集的数据中，则更新

                    log_list.insert(0, '容器：{}'.format(container.container_id))

                    if container.container_name != self.container_list.get(container.container_id).get('Name'):
                        log_list.append('容器名称由{}变更为{}'.format(container.container_name,
                                                              self.container_list.get(container.container_id).get(
                                                                  'Name')))
                        container.container_name = self.container_list.get(container.container_id).get('Name')

                    if container.images not in self.container_list.get(container.container_id).get('Image'):
                        log_list.append('容器镜像由{}变更为{}'.format(container.images,
                                                              self.container_list.get(container.container_id).get(
                                                                  'Image')))
                        container.images = self.container_list.get(container.container_id).get('Image')

                    if container.network != self.container_list.get(container.container_id).get('Network'):
                        log_list.append('容器网络类型由{}变更为{}'.format(container.network,
                                                                self.container_list.get(container.container_id).get(
                                                                    'Network')))
                        container.network = self.container_list.get(container.container_id).get('Network')

                    if container.platform != self.container_list.get(container.container_id).get('Platform'):
                        log_list.append('容器系统平台由{}变更为{}'.format(container.platform,
                                                                self.container_list.get(container.container_id).get(
                                                                    'Platform')))
                        container.platform = self.container_list.get(container.container_id).get('Platform')

                    if container.created != self.container_list.get(container.container_id).get('Created'):
                        log_list.append('容器创建时间由{}变更为{}'.format(container.created,
                                                                self.container_list.get(container.container_id).get(
                                                                    'Created')))
                        container.created = self.container_list.get(container.container_id).get('Created')

                    if container.startedat != self.container_list.get(container.container_id).get('State').get(
                            'StartedAt'):
                        log_list.append('容器启动时间由{}变更为{}'.format(container.startedat,
                                                                self.container_list.get(container.container_id).get(
                                                                    'State').get('StartedAt')))
                        container.startedat = self.container_list.get(container.container_id).get('State').get(
                            'StartedAt')

                    if container.status != self.container_list.get(container.container_id).get('State').get('Status'):
                        log_list.append('容器状态由{}变更为{}'.format(container.status,
                                                              self.container_list.get(container.container_id).get(
                                                                  'State').get('Status')))
                        container.status = self.container_list.get(container.container_id).get('State').get('Status')

                    if container.env != str(self.container_list.get(container.container_id).get('Env')):
                        log_list.append('容器环境变量由{}变更为{}'.format(container.env,
                                                                self.container_list.get(container.container_id).get(
                                                                    'Env')))
                        container.env = self.container_list.get(container.container_id).get('Env')

                    if container.workingdir != self.container_list.get(container.container_id).get('WorkingDir'):
                        log_list.append('容器工作目录由{}变更为{}'.format(container.workingdir,
                                                                self.container_list.get(container.container_id).get(
                                                                    'WorkingDir')))
                        container.workingdir = self.container_list.get(container.container_id).get('WorkingDir')

                    container.save()

                    for containerportobj in container.container_port.all():

                        if container.container_id in self.container_list:  # self.container_list 从用户发送过来的数据

                            if containerportobj.local_port != self.container_list.get(container.container_id).get(
                                    'Ports').get(containerportobj.container_port):
                                log_list.append('容器{}容器端口{}映射本地端口{}变更为{}'.format(container.container_id,
                                                                                 containerportobj.container_port,
                                                                                 containerportobj.local_port,
                                                                                 self.container_list.get(
                                                                                     container.container_id).get(
                                                                                     'Ports').items().get(
                                                                                     containerportobj.container_port)))
                                containerportobj.local_port = self.container_list.get(container.container_id).get(
                                    'Ports').get(containerportobj.container_port)
                                containerportobj.save()

                            else:
                                pass

                        else:
                            pass

                    if len(log_list) <= 1:
                        log_list.pop(0)

                else:  # 不存在则删除记录
                    log_list.append('容器{}不存在、已删除'.format(container.container_id))
                    models.DockerAsset.objects.filter(container_id=container.container_id).delete()

            # 增加

            db_container_list = []  # 存放当前主机上所有的容器的id

            for containerobj in self.assetobj.asset.all():
                db_container_list.append(containerobj.container_id)

            for container_id in self.container_list:
                if container_id not in db_container_list:  # agent回报的容器不存在数据库中是，新增容器资产信息
                    dockerassetobj = models.DockerAsset.objects.filter(container_id=container_id).first()
                    if not dockerassetobj:
                        dockerassetobj = models.DockerAsset.objects.create(asset=self.assetobj,
                                                                           container_id=container_id,
                                                                           container_name=self.container_list.get(
                                                                               container_id).get('Name'),
                                                                           images=self.container_list.get(
                                                                               container_id).get('Image'),
                                                                           network=self.container_list.get(
                                                                               container_id).get('Network'),
                                                                           platform=self.container_list.get(
                                                                               container_id).get('Platform'),
                                                                           created=self.container_list.get(
                                                                               container_id).get('Created'),
                                                                           startedat=self.container_list.get(
                                                                               container_id).get('State').get(
                                                                               'StartedAt'),
                                                                           status=self.container_list.get(
                                                                               container_id).get('State').get('Status'),
                                                                           workingdir=self.container_list.get(
                                                                               container_id).get('WorkingDir'),
                                                                           env=self.container_list.get(
                                                                               container_id).get('Env'),
                                                                           )

                    if self.container_list.get(container_id).get('Ports'):  # 容器有做端口映射
                        for ports in self.container_list.get(container_id).get('Ports'):
                            for containerport, localport in self.container_list.get(container_id).get('Ports').items():
                                DockerPortobj = models.DockerPort.objects.filter(Q(container_port=containerport),
                                                                                 Q(local_port=localport)).first()
                                if not DockerPortobj:
                                    DockerPortobj = models.DockerPort.objects.create(container_port=containerport,
                                                                                     local_port=localport)
                                if DockerPortobj:
                                    dockerassetobj.container_port.add(DockerPortobj)

                    if self.container_list.get(container_id).get('mounts'):  # 容器有做目录映射
                        for destination, source in self.container_list.get(container_id).get('mounts').items():
                            DockerStorageobj = models.DockerStorage.objects.filter(Q(destination=destination),
                                                                                   Q(source=source)).first()
                            if not DockerStorageobj:
                                DockerStorageobj = models.DockerStorage.objects.create(destination=destination,
                                                                                       source=source)
                            dockerassetobj.container_storage.add(DockerStorageobj)

            if log_list:
                models.AssetRecord.objects.create(asset=self.assetobj, content='\n'.join(log_list))
                log_list.clear()

        except Exception as e:

            logger.error(e, traceback.format_exc())
            models.ErrorLog.objects.create(asset_obj=self.assetobj, title=e, content=traceback.format_exc())
