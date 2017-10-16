#encoding:utf-8
# 输入必要参数 自动完成MySQL软件安装
import os
import sys
import argparse
import paramiko
import time
import  psutil

# 首先安装 paramiko psutil
# 1.生成配置文件
    #获取buffer pool/logfile size/server_id
    # mkdir 各种文件或目录
    # basedir:mkdir -p /usr/local/mysql/
    # datadir:mkdir -p /path/mysql/data
# 2.从服务器上下载安装包
    #scp -P port root@remote_ip:/path/mysql.5.6.x/5.7.x.tar.gz .
# 3.创建MySQL组和用户及目录授权
    #groupadd mysql
    #useradd mysql -g mysql
    #chown -R mysql:mysql /path/mysql/data
# 4.初始化MySQL
    #5.6与5.7初始化方法不一样
    #5.6
      #/usr/local/mysql/bin/mysql_install_db --defaults-file=/etc/my.cnf --user=mysql > /tmp/install_log_5.6.log
    #5.7
      #/usr/local/mysql/bin/mysqld --initialize_insecure --defaults-file=/etc/my.cnf --user=mysql > /tmp/install_log_5.7.log

# 5.启动MySQLd
    #/usr/local/mysql/bin/mysqld_safe --defaults-file=/etc/my.cnf --user=mysql&

# 6.脚本演示
# python mysql_auto_install.py --host=192.168.137.11
# --version=5.6/5.7 --buffer_pool_size=xxGB --log_file_size=xxMB
# --server_id = int(xyz) --datadir=path --package=/path/mysql_5.6.29.tar.gz
# --host:需要安装机器ip
# --version:安装包版本
# --buffer_pool_size:缓冲池大小
# --log_file_size:日志文件大小
# --server_id:数据库服务器id
# --datadir:数据文件目录
# --package:安装包目录

def max_disk_paratition():
    # 获取最大的磁盘分区用于存放数据文件目录
    mount_size = {}
    mount_point = psutil.disk_partitions()
    for disk in mount_point:
        try:
            disk_used=psutil.disk_usage(disk[1])
            mount_size[disk[1]] = int(disk_used[2]/1024) # 单位KB
        except Exception as e:
            pass
    # print  mount_size
    max_mount_area = max(mount_size.items(),key=lambda x:x[1])[0] # or max(mount_size,key=mount_size.get)
    return  max_mount_area

#数据文件目录
data_dir = max_disk_paratition() + "/mysql/data"
base_dir = "/usr/local/mysql"
error = "error"
output = "output"

def chk_arguments():
    # 设置必要的参数名称
    global data_dir,base_dir
    parser = argparse.ArgumentParser()
    parser.add_argument("--host",type=str,dest="host",help="MySQL Server host")
    parser.add_argument("--port",type=int,dest="port",help="MySQL Server port",default=3306)
    parser.add_argument("--version",type=str,dest="version",help="MySQL Version",default='5.7')
    parser.add_argument("--data-dir",type=str,dest="data_dir",help="MySQL data dir",default=data_dir)
    parser.add_argument("--base-dir",type=str,dest="base_dir",help="MySQL base dir",default=base_dir)
    parser.add_argument("--package",type=str,dest="package",help="MySQL install package path")
    parser.add_argument("--ssh-port",type=int,dest="ssh_port",help="ssh2 port",default=22)
    parser.add_argument("--ssh-user",type=str,dest="ssh_user",help="ssh2 username",default="root")
    args = parser.parse_args()

    if not args.host or not args.version:
        print "\033[31m[error:] 输入远端host ip.\033[0m"
        sys.exit(1)
    if (args.version != '5.6' and args.version != '5.7'):
        print "\033[31m[error:] 输入MySQL安装版本号[--version='5.6'|--version='5.7']\033[0m"
        sys.exit(1)
    if (args.ssh_port != 22 or args.ssh_user != "root"):
        print "\033[31m[error:] 输入ssh username or port.\033[0m"
        sys.exit(1)
    if not args.package:
        args.package = "/opt/mysql.tar.gz"

    data_dir = args.data_dir
    base_dir = args.base_dir
    args.package_name = os.path.dirname(args.package)

    return  args

def mysql_install(args):
    # 创建ssh
    host_client = paramiko.SSHClient()
    # 容许连接不在know_hosts文件中的主机
    host_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    host_client.connect(args.host,port=args.ssh_port,username=args.ssh_user)



def execute_remote_shell(host_client,cmd_shell):
    result = {}
    try:
        print "\033[31m cmd_shell \033[0m"
        stdin,stdout,stderr = host_client.exec_command(cmd_shell)
        result[error] = stderr.readlines()
        result[output] = stdout.readlines()
        if len(result[error]>0):
            print "\033[32mresult[error][0].replace('\n','') \033[0m"
        else:
            pass
    except:
        host_client.close()
    return result


# chk_arguments()




# paramiko
# http://www.cnblogs.com/gannan/archive/2012/02/06/2339883.html






