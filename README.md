
# autops介绍

autops是基于Python3开发的一款CMDB+IT审计堡垒机，支持web terminal和终端ssh。

- 项目启动

```
pip3 install -r requirements.txt
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py createsuperuser
python manage.py runserver
```

- 客户端安装

```
yum -y install dmidecode

```

# 截图

- 首页

![asset1](https://github.com/runcc/autops/blob/master/static/img/asset1.png)

- web ssh

![asset2](https://github.com/runcc/autops/blob/master/static/img/asset2.png)

- 终端

![asset3](https://github.com/runcc/autops/blob/master/static/img/asset3.png)

- 行为审计

![asset4](https://github.com/runcc/autops/blob/master/static/img/asset4.png)

- 录像回放

![asset5](https://github.com/runcc/autops/blob/master/static/img/asset5.png)

- 资产详情

![asset6](https://github.com/runcc/autops/blob/master/static/img/asset6.png)




