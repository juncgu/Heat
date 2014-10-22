#!/bin/sh
echo "---IPDU PORT SWITCH---"

snmpset -v 3 -u ideal123 -l auThNoPriv -a MD5 -A ideal123 10.10.100.200 WTI-MPC-VMR-MIB::systemTables.plugTable.plugEntry.plugAction.$1 = $2
snmpget -v 3 -u ideal123 -l auThNoPriv -a MD5 -A ideal123 10.10.100.200 WTI-MPC-VMR-MIB::systemTables.plugTable.plugEntry.plugStatus.$1
sleep 1
exit 1
