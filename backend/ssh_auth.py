#!/usr/bin/env python

# Copyright (C) 2003-2007  Robey Pointer <robeypointer@gmail.com>
#
# This file is part of paramiko.
#
# Paramiko is free software; you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 2.1 of the License, or (at your option)
# any later version.
#
# Paramiko is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Paramiko; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA.

from assets import models
import datetime
import base64
from binascii import hexlify
import getpass
import os
import select
import socket
import sys
import time
import traceback
from paramiko.py3compat import input

import paramiko

try:
    import interactive
except ImportError:
    from . import interactive


# def agent_auth(transport, username):
#     """
#     Attempt to authenticate to the given transport using any of the private
#     keys available from an SSH agent.
#     """
#
#     agent = paramiko.Agent()
#     agent_keys = agent.get_keys()
#     if len(agent_keys) == 0:
#         return
#
#     for key in agent_keys:
#         print("Trying ssh-agent key %s" % hexlify(key.get_fingerprint()))
#         try:
#             transport.auth_publickey(username, key)
#             print("... success!")
#             return
#         except paramiko.SSHException:
#             print("... nope.")


def manual_auth(t,username,hostname,password):
    default_auth = "p"
    # auth = input(
    #     "Auth by (p)assword, (r)sa key, or (d)ss key? [%s] " % default_auth
    # )

    # if len(auth) == 0:
    #     auth = default_auth
    auth = default_auth
    if auth == "r":
        default_path = os.path.join(os.environ["HOME"], ".ssh", "id_rsa")
        path = input("RSA key [%s]: " % default_path)
        if len(path) == 0:
            path = default_path
        try:
            key = paramiko.RSAKey.from_private_key_file(path)
        except paramiko.PasswordRequiredException:
            password = getpass.getpass("RSA key password: ")
            key = paramiko.RSAKey.from_private_key_file(path, password)
        t.auth_publickey(username, key)
    elif auth == "d":
        default_path = os.path.join(os.environ["HOME"], ".ssh", "id_dsa")
        path = input("DSS key [%s]: " % default_path)
        if len(path) == 0:
            path = default_path
        try:
            key = paramiko.DSSKey.from_private_key_file(path)
        except paramiko.PasswordRequiredException:
            password = getpass.getpass("DSS key password: ")
            key = paramiko.DSSKey.from_private_key_file(path, password)
        t.auth_publickey(username, key)
    else:
        # pw = getpass.getpass("Password for %s@%s: " % (username, hostname))
        # t.auth_password(username, pw)
        t.auth_password(username, password)


# def ssh_connection(hostname,port,username,password):
def ssh_connection(ssh_handler_innstance,ssh_host_obj):

    hostname = ssh_host_obj.host.mgaddress
    port = ssh_host_obj.host.port
    username = ssh_host_obj.remote_user.username
    password = ssh_host_obj.remote_user.password

    # now connect
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((hostname, port))
    except Exception as e:
        print("*** Connect failed: " + str(e))
        traceback.print_exc()
        sys.exit(1)

    try:
        t = paramiko.Transport(sock)
        try:
            t.start_client()
        except paramiko.SSHException:
            print("*** SSH negotiation failed.")
            sys.exit(1)

        try:
            keys = paramiko.util.load_host_keys(
                os.path.expanduser("~/.ssh/known_hosts")
            )
        except IOError:
            try:
                keys = paramiko.util.load_host_keys(
                    os.path.expanduser("~/ssh/known_hosts")
                )
            except IOError:
                print("*** Unable to open host keys file")
                keys = {}

        # check server's host key -- this is important.
        key = t.get_remote_server_key()
        if hostname not in keys:
            print("*** WARNING: Unknown host key!")
        elif key.get_name() not in keys[hostname]:
            print("*** WARNING: Unknown host key!")
        elif keys[hostname][key.get_name()] != key:
            print("*** WARNING: Host key has changed!!!")
            sys.exit(1)
        else:
            print("*** Host key OK.")



        # agent_auth(t, username)
        if not t.is_authenticated():
            manual_auth(t,username, hostname,password)
        if not t.is_authenticated():
            print("*** Authentication failed. :(")
            t.close()
            sys.exit(1)

        chan = t.open_session()
        chan.get_pty()
        chan.invoke_shell()


        chan.audit_account = ssh_handler_innstance.user
        chan.ssh_host_obj = ssh_host_obj
        chan.models = ssh_handler_innstance.models
        chan.log = ssh_handler_innstance.models.Log.objects.create(user=ssh_handler_innstance.user, host=hostname, remote_ip='', login_type='ssh')

        #print("*** Here we go!\n")
        interactive.interactive_shell(chan)
        chan.close()
        t.close()

        models.Log.objects.filter(id=chan.log.id).update(end_time=datetime.datetime.now())
        logobj = models.Log.objects.filter(id=chan.log.id).first()
        if logobj.end_time and logobj.start_time:
            models.Log.objects.filter(id=chan.log.id).update(hour_longtime=logobj.end_time - logobj.start_time)




    except Exception as e:
        print("*** Caught exception: " + str(e.__class__) + ": " + str(e))
        traceback.print_exc()
        try:
            t.close()
        except:
            pass
        sys.exit(1)