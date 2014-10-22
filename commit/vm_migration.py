#!/usr/bin/env python
import os
from sys import argv

def vm_migration_commit(vm_id, host):
#cmd = 'nova --os-username admin --os-password ADMIN_PASS --os-tenant-name admin --os-auth-url http://controller:35357/v2.0 live-migration 48eda90d-0115-4d91-abc8-a3bb4a700e5d compute3'
    vm_cmd = 'nova --os-username admin --os-password ADMIN_PASS --os-tenant-name admin --os-auth-url http://controller:35357/v2.0 live-migration '
    vm_cmd = vm_cmd + vm_id + ' ' + host
    os.system(vm_cmd)


if __name__ == "__main__":
    if len(argv) != 3:
        print 'usage: %s <vm_id> <new_computer_node>' % argv[0]
        exit(1)
    vm_migration_commit(argv[1], argv[2])
