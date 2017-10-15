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
datadir = max_disk_paratition()
basedir = "/usr/local/mysql"
error = "error"
output = "output"






