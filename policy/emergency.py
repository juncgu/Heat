#policy: emergency.py
#        include all the handler for emergency 
#        such as data_collect error------- switch to utility (no policy decision can be made)

import globalValue
import sys, copy
sys.path.append(globalValue.top_path())
from commit import commit_analysis

# switch to utility, when serious errors happen
def turn_on_utility():
    open_port = copy.copy(globalValue.ipdu_utility_port())
    close_port = copy.copy(globalValue.ipdu_green_port())
    commit_analysis.ipdu_open_analysis(open_port)
    commit_analysis.ipdu_close_analysis(close_port)
    exit(0)
