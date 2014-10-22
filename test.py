from commit.ipdu_switch import ipdu_switch_commit
from commit.vm_migration import vm_migration_commit
from commit.cpufreq_dvfs import cpufreq_dvfs_commit

if __name__ == "__main__":
    ipdu_switch_commit([1,0,2,0,0,0,0,1])
    print "success import commit.ipdu_switch"
