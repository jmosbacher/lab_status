from threading import Thread
from functools import partial
import time
import pmt_data

def on_server_loaded(server_context):
    #FIXME: Setup the data readers and queues
    # Add a peridoc callback that updates display periodically from queues
    #server_context.add_next_tick_callback(callback)
    th = Thread(target=pmt_data.read_data, args=())
    th.setDaemon(True)
    th.start()

def on_server_unloaded(server_context):
    ''' If present, this function is called when the server shuts down. '''
    pmt_data.dstore['kill'] = True

def on_session_created(session_context):
    ''' If present, this function is called when a session is created. '''

def on_session_destroyed(session_context):
    ''' If present, this function is called when a session is closed. '''
    pass
