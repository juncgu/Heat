#policy: test.py

import max_green
import sys
sys.path.append("../")
from datacollector import data_collect


if __name__ == '__main__':
    testset = data_collect.DataCollection()  
    max_green.solar_excess(testset)
