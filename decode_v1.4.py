import pprint
from collections import OrderedDict
from time import strftime
from time import time
from time import sleep
import copy
import socket
    
####Structure:
header = {
    'tg_id':        None,
    'tg_version':   None,
    'tg_uniq_id':   None,
    'tg_sender':    None,
    'tg_receiver':  None,
    'tg_size':      None,
    'tg_counter':   None,
    'tg_time':      None,
    'tg_reserved':  None,
    }

measurement_result = {
    'Measurement Status':   None,
    'type':                 None,
    'order':                None,
    'customer_id':          None,
    'client_id':            None,
    'truck_id':             None,
    'reserved':             None,
    }


######Body code
####Measurement Results

m_status = {
    0b0000_0000_0000_0000: 'Null',
    0b0000_0000_0000_0001: 'Measurement Abort',
    0b0000_0000_0000_0010: 'Measurement Error',
    0b0000_1000_0000_0000: 'Test01',
    0b0000_0000_1000_0000: 'Test02',
}

m_type = {
    0b0000_0000: 'Null',
    0b0000_0001: 'Empty Measurement',
    0b0000_0010: 'Full Measurement',
    0b0000_0100: 'Reference Measurement',
    0b0000_1000: 'Calibration Measurement',
}

m_order = {
    0b0000_0000: 'Null',
    0b0000_0001: 'Incoming Measurement',
    0b0000_0010: 'Outgoing Measurement',
}

m_direction = {
    0b0000_0000: 'Null',
    0b0000_0001: 'Left to Right',
    0b0000_0010: 'Right to Left',
}

#####
res = b''
result = {}
header = {}
body = {}
#####

with open('bin_reply.bin', 'rb') as f:
    byte = f.read(1)
    while byte != b'':
        res += byte
        byte = f.read(1)
        
def joined_bytes_int(address, size):
    joined = 0
    for i in range(address, address+size, 1):
        joined = joined | res[i] << (8*(address-(i-size)-1))
    return joined

def get_grz():
    TRUCK_ID_MAX_LEN = 30
    terminator = 0x0
    grz = ''
    for i in range(55, 55+TRUCK_ID_MAX_LEN):
        if res[i] == 0:
            return grz
        grz += chr(res[i])
    return grz


####    Header
header['Telegram ID'] =             joined_bytes_int(0, 2)
header['Telegram Version'] =        joined_bytes_int(2, 1)
header['Unique ID'] =               joined_bytes_int(3, 4)
header['Telegram Sender ID'] =      joined_bytes_int(7, 2)
header['Telegram Receiver ID'] =    joined_bytes_int(9, 2)
header['Telegram Size in Bytes'] =  joined_bytes_int(11, 2)
header['Telegram Counter'] =        joined_bytes_int(13, 2)

if True:
    t =  '%d.%d.%d ' %   (res[17], res[16], res[15], )
    t += '%d:%d:%d'  %   (res[18], res[19], res[20], )
    t += '.%d'       %   (joined_bytes_int(21, 2), )
    header['Telegram Timestamp'] =  t


####    Body
body['Measurement Status'] = m_status[joined_bytes_int(30, 2)]
body['Measurement Type'] = m_type[joined_bytes_int(32, 1)]
body['Measurement Order'] = m_order[joined_bytes_int(33, 1)]
body['Direction of Travel'] = m_direction[joined_bytes_int(34, 1)]




body['Truck ID'] = get_grz()


####    Summary
result = {
    'Header': header,
    'Body': body,
}


#### Printing
pp = pprint.PrettyPrinter(sort_dicts=False)
pp.pprint(result)





        

