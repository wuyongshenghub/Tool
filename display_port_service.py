# encoding:utf-8
"""
@project = python_training
@file = display_port_service
@author = __Mark__
@qq = 395424820
@mail = "mark5279@163.com"
@create_time = 2017/11/9 13:53
查询远程服务器开启服务及对应的port
"""

import paramiko
# import commands
import sys
# def get_com_str(cmd):
#     try:
#         stat,pro_res = commands.getstatusoutput(cmd)
#     except:
#         print "command:%s execute failed,exit"%cmd
#         sys.exit(1)
#     return pro_res


def exec_remote_com(cmd, *args):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(args[0], int(args[1]), args[2], args[3])
        stdin, stdout, stderr = ssh.exec_command(cmd)
    except:
        print "command:%s execute failed,exit" % (cmd)
        ssh.close()
        sys.exit()
    return stdout.readlines()


def list_port_service(cmd, *args):
    tmp_res = exec_remote_com(cmd, *args)
    # print tmp_res[2::]
    newlist = []
    for e in tmp_res[2::]:
        split_res = e.strip("\n").split()
        port = split_res[3].split(":")[-1]
        # print port.split(":")[-1]
        name = split_res[6].split("/")[1]
        if (port, name) not in newlist:
            newlist.append((port, name))
        # print "port %s ---->%s service"%(port,name)
    return newlist


def help():
    print "python display_port_service.py -h=host -P=port -u=user -p=pwd"
    print '''
           explain:
           python display_port_service.py [option]
          -h=host remote host
          -P=port remote port
          -u=user remote user
          -p=pwd  remote password
          '''


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print help()
        sys.exit(1)
    cmd = "netstat -nltp"
    for val in sys.argv[1:]:
        tmp = val.split("=")
        if tmp[0] == "-h":
            host = tmp[1]
        elif tmp[0] == "-P":
            port = tmp[1]
        elif tmp[0] == "-u":
            user = tmp[1]
        elif tmp[0] == "-p":
            pwd = tmp[1]

    args = (host, port, user, pwd)
    print "host:%s enable port service" % host
    for val in list_port_service(cmd, *args):
        print "%s--->%s" % (val[0], val[1])

执行结果
python display_port_service.py - h = 192.168.137.11 - P = 22 - u = root - p = 123456
host: 192.168.137.11 enable port service
139 - -- > smbd
111 - -- > rpcbind
22 - -- > sshd
631 - -- > cupsd
25 - -- > master
445 - -- > smbd
56769 - -- > rpc.statd
5672 - -- > qpidd
3366 - -- > mysqld
51301 - -- > rpc.statd
