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

    # 创建目录
    print "create mysql data/base dir."
    execute_remote_shell(host_client,"rm -rf {0}".format(data_dir))
    execute_remote_shell(host_client,"rm -rf {0}".format(base_dir))
    execute_remote_shell(host_client,"mkdir -p {0}".format(data_dir))
    execute_remote_shell(host_client,"mkdir -p {0}".format(base_dir))

    # 创建用户＆赋予权限
    print "create group/user/grant."
    execute_remote_shell(host_client,"groupadd mysql")
    execute_remote_shell(host_client,"useradd mysql -g mysql")
    execute_remote_shell(host_client,"chown -R mysql:mysql {0}".format(data_dir))

    #copy mysql install package and copy remote host
    print "copy mysql install package and copy remote host"
    os.system("scp -P {0} {1} args.ssh_user@{2}:max_disk_paratition()/".format(args.ssh_port,args.package,args.host))
    execute_remote_shell(host_client,"tar -zf max_disk_paratition()/{0} --strip-components=1 -C {1}".format(args.package_name,base_dir))

    # 设置配置文件 同步到远程host
    print "set mysql cnf and sync remote host"
    # get server_id
    server_id = get_server_id(host_client,args)
    # get buffer_size/buffer_pool_instance
    buffer_pool_size,buffer_pool_instance = get_buffer_pool_size(host_client)
    # MySQL config parameter
    config_val = mysql_config.format()
    # my.cnf write to tmpfile
    write_mysql_conf_to_file(args,config_val)

def get_server_id(host_client,args):
    result = execute_remote_shell(host_client,"ip addr | grep inet | grep -v 127.0.0.1 | grep -v inet6 " "| awk \'{ print $2}\' | awk -F \"/\" \'{print $1}\' | awk -F \".\" \'{print $4}\'")

    return args.port + result[output][0].replace("\n","")

def get_buffer_pool_size(host_client):
    result = execute_remote_shell(host_client,"free -g | head -n2 | tail -n1 | awk \'{print $2}\'")
    buffer_pool_instance = 1
    total_memory = int(result[output][0].replace("\n",""))
    buffer_pool_memory = str(int(round(total_memory * 0.75))) + 'G'
    if total_memory == 0:
        buffer_pool_size = "1000M"
        buffer_pool_instance = 1
    elif (total_memory > 0 and total_memory <=2):
        buffer_pool_instance = 2
    elif (total_memory > 2 and total_memory <=8):
        buffer_pool_instance = 3
    elif (total_memory >8 and total_memory <= 16):
        buffer_pool_instance = 4
    elif total_memory > 16:
        buffer_pool_instance = 8
    return  (buffer_pool_size,buffer_pool_instance)

def write_mysql_conf_to_file(args,config_val):
    # 本地生成MySQL临时配置文件 然后传到到远程服务器
    file_path = "/tmp/my.cnf"
    with open(file_path,'w') as f:
        f.write(config_val)
    # scp -P 22 file root@192.168.137.11:/etc/
    os.system("scp -P {0} {1} {2}@{3}:/etc/".format(args.ssh_port,file_path,args.ssh_user,args.host))


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

mysql_config = ("""
[client]
default_character_set = utf8

[mysql]
prompt = "\\u@\\h(\\d) \\\\r:\\\\m:\\\\s>"
default_character_set = utf8

[mysqld]
server_id = {0}
user = mysql
port = {1}
character_set_server = utf8
basedir = {2}
datadir = {3}
socket = mysql.sock
pid_file= mysql.pid
log_error = mysql.err

#innodb
innodb_buffer_pool_size = {4}
innodb_flush_log_at_trx_commit = 2
innodb_flush_log_at_timeout = 1
innodb_flush_method = O_DIRECT
innodb_support_xa = 1
innodb_lock_wait_timeout = 3
innodb_rollback_on_timeout = 1
innodb_file_per_table = 1
transaction_isolation = REPEATABLE-READ
innodb_log_buffer_size = 16M
innodb_log_file_size = 256M
innodb_data_file_path = ibdata1:1G:autoextend
#innodb_log_group_home_dir = ./
innodb_log_files_in_group = 3 
#innodb_force_recovery = 1
#read_only = 1
innodb_sort_buffer_size=2M
innodb_online_alter_log_max_size=1G
innodb_buffer_pool_instances = {5}
innodb_buffer_pool_load_at_startup = 1
innodb_buffer_pool_dump_at_shutdown = 1
innodb_lru_scan_depth = 2000
#innodb_file_format = Barracuda
#innodb_file_format_max = Barracuda
innodb_purge_threads = 8
innodb_large_prefix = 1
innodb_thread_concurrency = 0
innodb_io_capacity = 300
innodb_print_all_deadlocks = 1
innodb_locks_unsafe_for_binlog = 1
innodb_autoinc_lock_mode = 1
innodb_open_files = 6000

#replication
log_bin = {6}/bin_log
log_bin_index = {6}/bin_log_index
binlog_format = ROW
binlog_cache_size = 32M
#max_binlog_cache_size = 50M
max_binlog_size = 1G
expire_logs_days = 7
sync_binlog = 0
skip_slave_start = 1
binlog_rows_query_log_events = 1
relay_log = {6}/relay_log
relay_log_index = {6}/relay_log_index
max_relay_log_size = 1G
#relay_log_purge = 0
master_info_repository = TABLE
relay_log_info_repository = TABLE
relay_log_recovery = 1
log_slave_updates = 1
#gtid
#gtid_mode = ON
#enforce_gtid_consistency = ON

#slow_log
slow_query_log = 1
long_query_time = 2
#log_output = TABLE
slow_query_log_file = slow.log
log_queries_not_using_indexes = 1
log_throttle_queries_not_using_indexes = 30
log_slow_admin_statements = 1
log_slow_slave_statements = 1

#thread buffer size
tmp_table_size = 64M
max_heap_table_size = 64M
sort_buffer_size = 2M
join_buffer_size = 2M
read_buffer_size = 3M
read_rnd_buffer_size = 3M
key_buffer_size = 10M

#other
#sql_safe_updates = 1
skip_name_resolve = 1
open_files_limit = 65535
max_connections = 3000
max_connect_errors = 100000
#max_user_connections = 150
thread_cache_size = 64
lower_case_table_names = 0
query_cache_size = 0
query_cache_type = 0
max_allowed_packet = 1G
#time_zone = SYSTEM
lock_wait_timeout = 30
#performance_schema = OFF
table_open_cache_instances = 2
metadata_locks_hash_instances = 8
table_open_cache = 4000
table_definition_cache = 2048

#timeout
wait_timeout = 300
interactive_timeout = 300
connect_timeout = 20
""")

mysql_install(chk_arguments())
# chk_arguments()




# paramiko
# http://www.cnblogs.com/gannan/archive/2012/02/06/2339883.html






