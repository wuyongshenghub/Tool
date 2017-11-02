#!/bin/bash
# 升级Python版本2.6->2.7+

# install wget
upgrade_python_version(){
num_wget=$(rpm -qa|grep wget | wc -l)
if [ $num_wget -ne 1 ];then
    yum -y install wget
else
    cd /tmp
    wget http://python.org/ftp/python/2.7/Python-2.7.tar.bz2 --no-check-certificate
    if [ ! -d "/usr/local/python" ];then
        mkdir -p /usr/local/python
    else
        tar -xf Python-2.7.tar.bz2 -C /usr/local/python
        cd /usr/local/python/Python-2.7
        ./configure && make install >> /tmp/install.log &  
    fi 
fi
}

# platform version
sv=$(cat /etc/redhat-release|awk '{print $3}')
if [ `expr "$sv" \< "7.0"` -gt 0 ];then
    echo "Centos Version:" $sv
    # Python version
    pv=$(/usr/bin/python -c 'import sys;print sys.version'|grep -v 'GCC'|awk '{print $1}')
    echo "Python Version:" $pv
    echo "Do you want to upgrade python version?"
    read -p "input yes or no : " var
    if [ "$var" == "yes" ];then
        echo "start upgrade ..." 
        upgrade_python_version
    else
        echo "退出升级"
        exit
    fi
fi
