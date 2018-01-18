import logging
from utils import ThreadSafeObject
import collections
import json
import itertools
import sockets
import time
DEBUG = True

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

IP = '132.77.44.111'
PORT= 4451
READ_EVERY = 1 #seconds
ROWS = 4
RED = 0.05
YELLOW = 0.01
dstore = {'latest_values':{}, 'kill':False}

def read_data():
    if DEBUG:
        Socket = sockets.FakeSocket
    else:
        Socket = sockets.Socket

    sock = Socket(IP,PORT)
    while True:
        if dstore['kill']:
            return
        #try:
        sock.connect()
        raw = sock.receive()
        rdata = json.loads(raw.decode())
        #log.info(type(rdata))

        data = {}
        if 'Vmeas' not in rdata:
            return
        nchan = rdata.get('Nch',0)
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
        data['voltage'] = ['V: {:.2e} ({:.2e})'.format(m,s) for m,s in zip(data['Vmeas'], data['Vset'])]
        data['current'] = ['I: {:.2e} ({:.2e})'.format(m,s) for m,s in zip(data['Cmeas'], data['Cset'])]
        data['vdiff'] = [abs((m-s)/s) if s else 0. for m,s in zip(data['Vmeas'], data['Vset'])]
        data['idiff'] = [abs((m-s)/s) if s else 0. for m,s in zip(data['Cmeas'], data['Cset'])]
        data['vcolor'] = ['green' if d<YELLOW else 'yellow' if d<RED else 'red' for d in data['vdiff']]
        data['icolor'] = ['green' if d<YELLOW else 'yellow' if d<RED else 'red' for d in data['idiff']]
        dstore['latest_values'] = data
        time.sleep(READ_EVERY)
        #log.info(str(data))
        #except:
            #pass
