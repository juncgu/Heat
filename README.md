Heat
====

Renewable Power (solar) Management for cluster @ IDEAL from ECE-UF


It has four components:
1. top_selector.py  / top_selector2.py   
    It collects all other components, and provides the top-layer mechanism for policy-selection.

2. policy
    It contains policy files, global variable definations.

3. datacollector
    It is in charge of collecting data from all kinds of devices and OpenStack. It contains some basic drivers for outback, ipdu, and HMI. 

4. commit
    All the operations such as IPDU switch, VM live-migration, and DVFS. The feedback information are also send back to HMI through this part.
