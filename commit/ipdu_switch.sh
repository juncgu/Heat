#!/bin/sh
echo "---IPDU PORT SWITCH---"

snmpset -v 3 -u ideal123 -l auThNoPriv -a MD5 -A ideal123 10.10.100.200 WTI-MPC-VMR-MIB::systemTables.plugTable.plugEntry.plugAction.1 = $1
snmpget -v 3 -u ideal123 -l auThNoPriv -a MD5 -A ideal123 10.10.100.200 WTI-MPC-VMR-MIB::systemTables.plugTable.plugEntry.plugStatus.1

snmpset -v 3 -u ideal123 -l auThNoPriv -a MD5 -A ideal123 10.10.100.200 WTI-MPC-VMR-MIB::systemTables.plugTable.plugEntry.plugAction.2 = $2
snmpget -v 3 -u ideal123 -l auThNoPriv -a MD5 -A ideal123 10.10.100.200 WTI-MPC-VMR-MIB::systemTables.plugTable.plugEntry.plugStatus.2

snmpset -v 3 -u ideal123 -l auThNoPriv -a MD5 -A ideal123 10.10.100.200 WTI-MPC-VMR-MIB::systemTables.plugTable.plugEntry.plugAction.3 = $3
snmpget -v 3 -u ideal123 -l auThNoPriv -a MD5 -A ideal123 10.10.100.200 WTI-MPC-VMR-MIB::systemTables.plugTable.plugEntry.plugStatus.3

snmpset -v 3 -u ideal123 -l auThNoPriv -a MD5 -A ideal123 10.10.100.200 WTI-MPC-VMR-MIB::systemTables.plugTable.plugEntry.plugAction.4 = $4
snmpget -v 3 -u ideal123 -l auThNoPriv -a MD5 -A ideal123 10.10.100.200 WTI-MPC-VMR-MIB::systemTables.plugTable.plugEntry.plugStatus.4

snmpset -v 3 -u ideal123 -l auThNoPriv -a MD5 -A ideal123 10.10.100.200 WTI-MPC-VMR-MIB::systemTables.plugTable.plugEntry.plugAction.5 = $5
snmpget -v 3 -u ideal123 -l auThNoPriv -a MD5 -A ideal123 10.10.100.200 WTI-MPC-VMR-MIB::systemTables.plugTable.plugEntry.plugStatus.5

snmpset -v 3 -u ideal123 -l auThNoPriv -a MD5 -A ideal123 10.10.100.200 WTI-MPC-VMR-MIB::systemTables.plugTable.plugEntry.plugAction.6 = $6
snmpget -v 3 -u ideal123 -l auThNoPriv -a MD5 -A ideal123 10.10.100.200 WTI-MPC-VMR-MIB::systemTables.plugTable.plugEntry.plugStatus.6

snmpset -v 3 -u ideal123 -l auThNoPriv -a MD5 -A ideal123 10.10.100.200 WTI-MPC-VMR-MIB::systemTables.plugTable.plugEntry.plugAction.7 = $7
snmpget -v 3 -u ideal123 -l auThNoPriv -a MD5 -A ideal123 10.10.100.200 WTI-MPC-VMR-MIB::systemTables.plugTable.plugEntry.plugStatus.7

snmpset -v 3 -u ideal123 -l auThNoPriv -a MD5 -A ideal123 10.10.100.200 WTI-MPC-VMR-MIB::systemTables.plugTable.plugEntry.plugAction.8 = $8
snmpget -v 3 -u ideal123 -l auThNoPriv -a MD5 -A ideal123 10.10.100.200 WTI-MPC-VMR-MIB::systemTables.plugTable.plugEntry.plugStatus.8
exit 1
