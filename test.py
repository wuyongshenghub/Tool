#encoding:utf-8


import  psutil

def disk_paration():
    mount_size = {}
    mount_point = psutil.disk_partitions()
    for disk in mount_point:
        try:
            disk_used=psutil.disk_usage(disk[1])
            mount_size[disk[1]] = int(disk_used[2]/1024) # 单位KB
        except Exception as e:
            pass
    print  mount_size
    max_mount_area = max(mount_size.items(),key=lambda x:x[1])[0] # or max(mount_size,key=mount_size.get)
    return  max_mount_area


if __name__=='__main__':
    print disk_paration()