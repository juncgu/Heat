#datacollector: data_collect.py
#      ipdu: status, power, current
#      outback: solar power, batt voltage, batt current, charger status ...
#      vm info: vm id, mapping ..., vm power factor
#      dvfs info: resource utilization, dvfs factor
import get_token, get_probes, get_vm, hmi_filter, filterBuffer, path
import time
import sys, os
#upper_path = os.getcwd()[0:-14]
sys.path.append(path.upper_path())
#sys.path.append('/root/solar/Heat')
from policy import globalValue

class DataCollection:
    '''
    stores all the information needed during the process    
    '''
    #attribute
    # 1. ipdu 
    ipdu = {'status' :[0,1,0,0,1,0,1,1],
            'power'  :[150,150,0,0,150,150,350,400],
            'current':[0,0,0,0,0,0,0,0],
            'port'   :{'compute1':{'g':[0,1], 'u':[4,1], 'status':'g', 'average':0.0, 'var':0.0},    #[port, status]
                       'compute2':{'g':[1,1], 'u':[5,1], 'status':'u', 'average':0.0, 'var':0.0},
                       'compute3':{'g':[2,1], 'u':[6,0], 'status':'g', 'average':0.0, 'var':0.0},
                       'compute4':{'g':[3,0], 'u':[7,0], 'status':'m', 'average':0.0, 'var':0.0}
                      }
           }
    # 2. outback
    outback = {'solarPower': 0,
               'solarEnergy':0,
               'mpptStatus': 0,
               'mpptStatus_str': '',
               'batteryCurrent': 0,
               'batteryVoltage': 0,
               'batteryVoltage_average': 0,
               'batterySoc': 0,
               'shuntCurrent': 0,
               'inverterPower': 0,
               'solarPower_average': 0,
               'solarPower_var': 0,
               'last_solarPower': 0,
               'last_mpptStatus': ''
              }
    # 3. vm

    # 4. host
    server = {'hostname':['compute1', 'compute2', 'compute3', 'compute4'],
              'dvfs':{'compute1':{'max':3, 'current':2, 'min':1, 'scale':[0,0], 'cur_scale':0, 'power':[0,0]},
                      'compute2':{'max':0, 'current':0, 'min':0, 'scale':[0,0], 'cur_scale':0, 'power':[0,0]},
                      'compute3':{'max':30, 'current':20, 'min':10, 'scale':[10,20,30], 'cur_scale':1, 'power':[30,40]},
                      'compute4':{'max':3000, 'current':3000, 'min':3000, 'scale':[3000,3000,3000], 'cur_scale':1, 'power':[0,0]} 
                     },
              'vm':{'compute1':{'count':4, 'left':4, 'vm':[]},    #count=max_constant, left is dynamic
                    'compute2':{'count':4, 'left':4, 'vm':[]},    #'vm':[{'id':xxx, 'power':xxx}]
                    'compute3':{'count':4, 'left':4, 'vm':[]},
                    'compute4':{'count':4, 'left':4, 'vm':[]}
                   }
             }
    
    #5. Domain
    domain = {'dvfsPool':['compute4'],
              'vmmigrationPool':['compute2', 'compute3'],
              'greenPool':['compute1'] 
             }
 
    #6. token
    token = ''

    #7. hmi
    hmi = {'battery_a':{'current':0.0, 'voltage':0.0},
           'battery_b':{'current':0.0, 'voltage':0.0},
           'battery_c':{'current':0.0, 'voltage':0.0} 
          }

    #8. energy
    energy = {'solar_energy': 0,
              'green_port_energy': 0,
              'compute1': 0,
              'compute2': 0,
              'compute3': 0,
              'compute4': 0,
              'brown_port_energy': 0,
              'solar_ratio': 0,
              'solar_efficiency': 0,
              'roi': 0,
              'economic_benefit': 0
             }

    #9. filter
    hmi_filter = {'current1': 0,
                  'current2': 0
                 }


    #function
    def __init__(self):
        self.ipdu['status'][0] = 0; 

    #retrieve info
    def get_token(self):   
        self.token = get_token.get_token()

    # vm info
    def get_vm_info(self):
        for i in self.server['hostname']:
            vm_list = get_vm.get_vm(i)
            #'left'
            vm_count = len(vm_list)
            self.server['vm'][i]['left'] = self.server['vm'][i]['count'] - vm_count
            #'vm'
            if vm_count != 0:
                for j in vm_list:
                    vmid = j['uuid']
                    vmpower = 40
                    self.server['vm'][i]['vm'].append({'id':vmid, 'power':vmpower})
        print self.server['vm']

    # host info
#    def get_dvfs_info(self):


    #retrieve all info
    def get_ipdu_outback(self):
        probes_data = get_probes.get_probes()
        print probes_data
        self.outback['mpptStatus'] = int(probes_data['mpptStatus']['w'])
        self.outback['batteryCurrent'] = probes_data['batteryCurrent']['w']
        self.outback['batterySoc'] = probes_data['batterySoc']['w']
        self.outback['solarPower'] = probes_data['solarPower']['w']
        self.outback['batteryVoltage'] = probes_data['batteryVoltage']['w']
        self.outback['shuntCurrent'] = probes_data['shuntCurrent']['w']
        self.outback['inverterPower'] = probes_data['inverterPower']['w']
        self.hmi['battery_a']['current'] = probes_data['a_current']['w']
        self.hmi['battery_a']['voltage'] = probes_data['a_voltage']['w']
        self.hmi['battery_b']['current'] = probes_data['b_current']['w']
        self.hmi['battery_b']['voltage'] = probes_data['b_voltage']['w']
        self.hmi['battery_c']['current'] = probes_data['c_current']['w']
        self.hmi['battery_c']['voltage'] = probes_data['c_voltage']['w']
        self.outback['solarPower_average'] = probes_data['solar_power_expected']['w']  
        self.outback['solarPower_var'] = probes_data['solar_power_var']['w']
        self.outback['batteryVoltage_average'] = probes_data['battery_expected']['w']
        self.outback['solarEnergy'] = probes_data['solar_energy']['w']
        self.energy['solar_energy'] = probes_data['solar_energy']['w'] 
        self.energy['green_port_energy'] = probes_data['compute_onsolar_energy']['w'] 
        self.energy['compute1'] = probes_data['compute1_energy']['w'] 
        self.energy['compute2'] = probes_data['compute2_energy']['w'] 
        self.energy['compute3'] = probes_data['compute3_energy']['w'] 
        self.energy['compute4'] = probes_data['compute4_energy']['w'] 
        self.energy['roi'] = probes_data['roi']['w']
        self.energy['economic_benefit'] = probes_data['economic_benefit']['w']
        self.energy['brown_port_energy'] = self.energy['compute1'] + self.energy['compute2'] + self.energy['compute3']+ self.energy['compute4'] - self.energy['green_port_energy']        
        if ((self.energy['green_port_energy'] + self.energy['brown_port_energy']) > 0):
            self.energy['solar_ratio'] = self.energy['green_port_energy'] / (self.energy['green_port_energy'] + self.energy['brown_port_energy'])
        else:
            self.energy['solar_ratio'] = 0
        if self.energy['solar_energy'] > 0:
            self.energy['solar_efficiency'] = self.energy['green_port_energy'] / self.energy['solar_energy']
        else:
            self.energy['solar_efficiency'] = 0

        for i in self.server['hostname']:
            var_key = i + '_power_var'
            exp_key = i + '_power_expected'
            self.ipdu['port'][i]['var'] = probes_data[var_key]['w']
            self.ipdu['port'][i]['average'] = probes_data[exp_key]['w']

        if probes_data['ipdu_port_a1']['w'] > 0.0:
            self.ipdu['status'][0] = 1
            self.ipdu['power'][0] = probes_data['ipdu_port_a1']['w']
        else:
            self.ipdu['status'][0] = 0
            self.ipdu['power'][0] = 0
        if probes_data['ipdu_port_a2']['w'] > 0.0:
            self.ipdu['status'][1] = 1
            self.ipdu['power'][1] = probes_data['ipdu_port_a2']['w']
        else:
            self.ipdu['status'][1] = 0
            self.ipdu['power'][1] = 0
        if probes_data['ipdu_port_a3']['w'] > 0.0:
            self.ipdu['status'][2] = 1
            self.ipdu['power'][2] = probes_data['ipdu_port_a3']['w']
        else:
            self.ipdu['status'][2] = 0
            self.ipdu['power'][2] = 0
        if probes_data['ipdu_port_a4']['w'] > 0.0:
            self.ipdu['status'][3] = 1
            self.ipdu['power'][3] = probes_data['ipdu_port_a4']['w']
        else:
            self.ipdu['status'][3] = 0
            self.ipdu['power'][3] = 0
        if probes_data['ipdu_port_b1']['w'] > 0.0:
            self.ipdu['status'][4] = 1
            self.ipdu['power'][4] = probes_data['ipdu_port_b1']['w']
        else:
            self.ipdu['status'][4] = 0
            self.ipdu['power'][4] = 0
        if probes_data['ipdu_port_b2']['w'] > 0.0:
            self.ipdu['status'][5] = 1
            self.ipdu['power'][5] = probes_data['ipdu_port_b2']['w']
        else:
            self.ipdu['status'][5] = 0
            self.ipdu['power'][5] = 0
        if probes_data['ipdu_port_b3']['w'] > 0.0:
            self.ipdu['status'][6] = 1
            self.ipdu['power'][6] = probes_data['ipdu_port_b3']['w']
        else:
            self.ipdu['status'][6] = 0
            self.ipdu['power'][6] = 0
        if probes_data['ipdu_port_b4']['w'] > 0.0:
            self.ipdu['status'][7] = 1
            self.ipdu['power'][7] = probes_data['ipdu_port_b4']['w']
        else:
            self.ipdu['status'][7] = 0
            self.ipdu['power'][7] = 0
        for i in self.server['hostname']:
            self.ipdu['port'][i]['g'][1] = self.ipdu['status'][self.ipdu['port'][i]['g'][0]] 
            self.ipdu['port'][i]['u'][1] = self.ipdu['status'][self.ipdu['port'][i]['u'][0]]
            if (self.ipdu['port'][i]['g'][1] == 1 and self.ipdu['port'][i]['u'][1] == 1):
                self.ipdu['port'][i]['status'] = 'm'  
            elif (self.ipdu['port'][i]['g'][1] == 1 and self.ipdu['port'][i]['u'][1] == 0):
                self.ipdu['port'][i]['status'] = 'g' 
            elif (self.ipdu['port'][i]['g'][1] == 0 and self.ipdu['port'][i]['u'][1] == 1):
                self.ipdu['port'][i]['status'] = 'u' 
        print self.ipdu
        print self.outback
        print self.hmi

    def data_filter(self, filter_buffer):
        load_power = 0
        for i in self.ipdu['power']:
            load_power += i
        
        filter_buffer.insert(self.hmi['battery_a']['current'], self.hmi['battery_b']['current'], self.outback['solarPower'], load_power, self.outback['batteryCurrent']) 
  
        filtered_data = hmi_filter.hmi_data_filter(self, filter_buffer)
        self.hmi_filter['current1'] = filtered_data['current1_PLC']
        self.hmi_filter['current2'] = filtered_data['current2_PLC']
        time_stamp = time.strftime('%Y-%m-%d-%H-%M', time.localtime(time.time()))
        write_str = time_stamp+' '+str(self.hmi['battery_a']['current'])+' '+str(filtered_data['current1_PLC'])+' '+str(self.hmi['battery_b']['current'])+' '+str(filtered_data['current2_PLC'])+' '+str(self.outback['solarPower'])+' '+str(filtered_data['predict_solarPower'])+' '+str(load_power)+' '+str(filtered_data['predict_workload'])+' '+'\n'
        filter_file = open(globalValue.filter_file_name(), 'a')
        filter_file.write(write_str)
        filter_file.close()




