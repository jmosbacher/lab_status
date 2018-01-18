import logging
from utils import ThreadSafeObject
import collections
import json
import itertools
import sockets
import time
import pmt_templates
DEBUG = False

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

IP = '132.77.44.111'
PORT= 4451
READ_EVERY = 1 #seconds
ROWS = 4
RED = 0.05
YELLOW = 0.01
fields = []
dstore = {'latest_values':{}, 'kill':False, 'live':False, 'connected': False}

def read_data():
    sock = sockets.Socket(IP,PORT)
    while True:
        if dstore['kill']:
            return
        try:
            sock.connect()
            raw = sock.receive()
            rdata = json.loads(raw.decode())
            dstore['connected'] = True
        except:
            dstore['connected'] = False
            dstore['live'] = False
            rdata = pmt_templates.all_off
        #log.info(type(rdata))

        data = {}
        nchan = rdata.get('Nch',-1)
        if nchan>0 and dstore['connected']:
            dstore['live']=True
        else:
            rdata = pmt_templates.all_off
            nchan = rdata.get('Nch',24)
            dstore['live']=False
        cols = nchan//ROWS
        rcs = list(itertools.product(range(ROWS),range(cols)))
        data['row'] = [t[0]+1 for t in rcs]
        data['column'] = [t[1]+1 for t in rcs]
        data['channel'] = list(range(nchan))
        for name, arr in rdata.items():
            if isinstance(arr, collections.Sequence) and len(arr)==nchan:
                data[name] = arr
            elif name=='time':
                data[name] = [arr]*nchan
        data['voltage'] = ['V: {:.2e} ({:.2e})'.format(m,s) if dstore['live'] else 'V: NA' for m,s in zip(data['Vmeas'], data['Vset'])]
        data['current'] = ['I: {:.2e} ({:.2e})'.format(m,s) if dstore['live'] else 'I: NA' for m,s in zip(data['Cmeas'], data['Cset'])]
        data['vdiff'] = [abs((m-s)/s) if s else 0. for m,s in zip(data['Vmeas'], data['Vset'])]
        data['idiff'] = [abs((m-s)/s) if s else 0. for m,s in zip(data['Cmeas'], data['Cset'])]
        data['vcolor'] = ['green' if d<YELLOW else 'yellow' if d<RED else 'red' for d in data['vdiff']]
        data['icolor'] = ['green' if d<YELLOW else 'yellow' if d<RED else 'red' for d in data['idiff']]
        data['boxcolor'] = ['red' if s=='sos' else 'yello' if s=='trip' else 'grey' for s in data['chStat']]
        data['scolor'] = ['red' if s=='sos' else 'yello' if s=='trip' else 'green' if s=='on' else 'black' for s in data['chStat']]
        data['ccolor'] = ['green' if c else 'red' for c in data['chControl']]
        data['status'] = ['Status: {}'.format(x) for x in data['chStat']]
        dstore['latest_values'] = data
        time.sleep(READ_EVERY)
        #log.info(str(data))
        #except:
            #pass
