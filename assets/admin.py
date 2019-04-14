from django.contrib import admin
from assets import models
# Register your models here.


admin.site.register(models.HostGroup)
admin.site.register(models.UserProfile)
admin.site.register(models.HostBindRemoteUser)
admin.site.register(models.RemoteUser)
admin.site.register(models.Log)
admin.site.register(models.TtyLog)
admin.site.register(models.RecorderLog)
admin.site.register(models.Asset)
admin.site.register(models.DockerAsset)
admin.site.register(models.DockerPort)
admin.site.register(models.DockerStorage)
admin.site.register(models.container_user)
admin.site.register(models.IDC)
admin.site.register(models.AssetRecord)
