import get_token, path
import pycurl, sys, copy, simplejson
from sys import argv
import os
#upper_path = os.getcwd()[0:-14]
sys.path.append(path.upper_path())
#sys.path.append('/root/solar/Heat')
from policy import globalValue, emergency

class data:
    def __init__(self):
        self.head = ''
        self.body = []
    def body_write(self, buf):
#        print buf
        re_dict = simplejson.loads(buf)
#        re_dict = eval(buf)
#        print re_dict
        self.body = copy.copy(re_dict)
    def head_write(self, buf):
        self.head = self.head + buf 

def get_vm(host):
    token = get_token.get_token() 
    head = ["X-Authr-Project-Id: admin", "Accept: application/json"]
    header = "X-Auth-Token: " + token
    head.append(header)
#    url = 'http://controller:5001/v1/probes/'
    url = globalValue.data_vm_url()
    url = url + host + '/servers'
    d = data()
    c = pycurl.Curl()
    c.setopt(c.HTTPHEADER, head)
#    c.setopt(c.HTTPHEADER, [header])
    c.setopt(c.CUSTOMREQUEST, "GET")
    c.setopt(pycurl.VERBOSE, 1)
    c.setopt(pycurl.FOLLOWLOCATION, 1)
    c.setopt(pycurl.MAXREDIRS, 5)
    c.setopt(c.URL, url)
    c.setopt(c.HEADERFUNCTION, d.head_write)
    c.setopt(c.WRITEFUNCTION, d.body_write)
    try:
        c.perform()
    except:
        print 'Error: get_vm: c.perform()'
      
    c.close()
    print d.body
    if d.body['hypervisors'][0].has_key('servers') == True:
        return d.body['hypervisors'][0]['servers']
    else:
        return {}

if __name__ == '__main__':
    print "GET probes"
    print get_vm('compute6')

