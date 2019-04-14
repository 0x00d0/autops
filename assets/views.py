from django.shortcuts import render,redirect,HttpResponse
from assets import models
from django.db.models import Q
from django.utils.safestring import mark_safe
import json
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .asset_handler import UpdateAsset,UpdateDockerAsset

import traceback

import logging
logger = logging.getLogger('log')

# Create your views here.


@login_required
def index(request):
    '''

    :param request:
    :return:
    '''

    return render(request,'index.html')



def opslogin(request):

    resdata = {'result_code': 0}
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        userobj = authenticate(username=username,password=password)
        if userobj:
            login(request,userobj)
            return redirect(request.GET.get('next') or '/')
        else:
            resdata['message']= '用户名或密码错误'

    return render(request,'login.html',{'resdata':resdata})



@login_required
def hostmt(request):

    hostlist = models.HostBindRemoteUser.objects.filter(Q(userprofile=request.user)|
                                                        Q(hostgroup__userprofile__username=request.user)).distinct()

    return render(request,'hostmt.html',locals())



@login_required
def auditlog(request):


    logs = models.Log.objects.all()


    return render(request,'auditlog.html',locals())



@login_required
def terminal(request,hostid):


    return render(request,'terminal.html',{
        'hostid':mark_safe(json.dumps(hostid))
    })




@login_required
def asset(request,hostid):


    assets = models.HostBindRemoteUser.objects.filter(Q(host__id=hostid),
                                                               Q(userprofile__username=request.user)|Q(hostgroup__userprofile__username=request.user)).distinct().first()



    return render(request,'asset.html',locals())



@csrf_exempt
def report(request):

    if request.method == 'POST':
        data = request.POST.get('asset_data')
        data_json = json.loads(data)
        try:
            sn = data_json.get('os_info').get('sn').split('\n')
            if sn:
                assetobj = models.Asset.objects.filter(sn=sn[0]).first()
                if assetobj:
                    assets = UpdateAsset(assetobj,data_json)
                    assets.update_asset()
                    dockerasset = UpdateDockerAsset(assetobj,data_json.get('docker_info').get('containers_list'))
                    dockerasset.updateasset()


        except Exception as e:
            logger.error(e)
            logger.error(traceback.format_exc())



        return  HttpResponse('ok')



