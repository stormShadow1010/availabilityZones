from pprint import pprint
from collections import OrderedDict
from time import strftime
from time import time
from time import sleep
import copy
import socket

##if  outgoing_command_input['command']['value'] == 'Start incoming measurement':
##    mask = mask | 0b1000_0000_0000_0000
##elif  outgoing_command_input['command']['value'] == 'Start outgoing measurement':
##    mask = mask | 0b0100_0000_0000_0000
##elif  outgoing_command_input['command']['value'] == 'Truck is full':
##    mask = mask | 0b0010_0000_0000_0000
##elif  outgoing_command_input['command']['value'] == 'Start callibration':
##    mask = mask | 0b0001_0000_0000_0000
##elif  outgoing_command_input['command']['value'] == 'Abort measurement/callibration':
##    mask = mask | 0b0000_1000_0000_0000
##elif  outgoing_command_input['command']['value'] == 'Get result by measure ID':
##    mask = mask | 0b0000_0100_0000_0000


##Dictionaries:
##Variables length - (bytes)
vartypes = {
    'char': 1,
    'byte': 1,
    'short': 2,
    'word': 2,
    'dword': 3,
    'time': 8,
    'float': 4,
    }
    
####Header
header_input = {
    'tg_size':          {'vartype': 'word', 'value': 80},
    'tg_uid':           {'vartype': 'dword', 'value': 0x01_33_79_92},
    'tg_id':            {'vartype': 'word', 'value': 'Command'},
    'tg_seq_num':       {'vartype': 'word', 'value': 0},
    'tg_time':          {'vartype': 'time'},
    'tg_tms_flag':      {'vartype': 'byte', 'value': 'Request Toggle Bit'},
    'tg_reserve':       {'vartype': 'byte', 'value': 0},
    }

####Bodies
######Outgoing
########Get Status
outgoing_status = {
        ##No data part##
    }

########Outgoing command
outgoing_command_input = {
        'command':      {'vartype': 'word', 'value': 'Start incoming measurement'},
        'measure_id':   {'vartype': 'dword', 'value': 5},
        'truck_id':     {'vartype': 'byte', 'value': 'T888HM199'},
        'reserve':      {'vartype': 'byte', 'value': 0x0},
    }

########Outgoing ioData
outgoing_ioData_input = {
        'digital_in':   {'vartype': 'word', 'value': 'Fault enclosure heater'},
        'digital_out':  {'vartype': 'word', 'value': 'Aux relais scanner motor'},
        'analog_in':    {'vartype': 'word', 'value': 5},
        'reserve':      {'vartype': 'byte', 'value': 0x0},
    }

##Header code
header = copy.deepcopy(header_input)

##ID
if header_input['tg_id']['value'] == 'Get status':
    header['tg_id']['value'] = 300
elif header_input['tg_id']['value'] == 'Command':
    header['tg_id']['value'] = 301
elif header_input['tg_id']['value'] == 'IO Data':
    header['tg_id']['value'] = 302

##Transmission flag
mask = 0
if header_input['tg_tms_flag']['value'] == 'Request Toggle Bit':
    mask = mask|0b1000_0000
elif header_input['tg_tms_flag']['value'] == 'Toggle Bit':
    mask = mask|0b0100_0000
header['tg_tms_flag']['value'] = 0 | mask


##Outgoing code
####Command code
outgoing_command = copy.deepcopy(outgoing_command_input)
mask = 0

switch = {
    'Start incoming measurement':       0b1000_0000_0000_0000,
    'Start outgoing measurement':       0b0100_0000_0000_0000,
    'Truck is full':                    0b0010_0000_0000_0000,
    'Start callibration':               0b0001_0000_0000_0000,
    'Abort measurement/callibration':   0b0000_1000_0000_0000,
    'Get result by measure ID':         0b0000_0100_0000_0000,
    }

mask = switch[outgoing_command_input['command']['value']]
outgoing_command['command']['value'] = 0 | mask

####IO data code
outgoing_ioData = copy.deepcopy(outgoing_ioData_input)

switch = {
    'Switch test lamp':                 0b1000_0000_0000_0000,
    'Fault enclosure heater':           0b0100_0000_0000_0000,
    'Fault 3D-Unit 1':                  0b0010_0000_0000_0000,
    'Fault 3D-Unit 2':                  0b0001_0000_0000_0000,
    'Switch,Start measurement Col1':    0b0000_1000_0000_0000,
    'Switch,Start measurement Col2':    0b0000_0100_0000_0000,
    'Reserve': None
    }
mask = switch[outgoing_ioData_input['digital_in']['value']]
outgoing_ioData['digital_in']['value'] = 0 | mask

switch = {
    'Fault Enclosure':                  0b1000_0000_0000_0000,
    'Status, measurement active Col1':  0b0100_0000_0000_0000,
    'Fault Col1':                       0b0010_0000_0000_0000,
    'Status, measurement active Col2':  0b0001_0000_0000_0000,
    'Fault Col2':                       0b0000_1000_0000_0000,
    'Aux relais reset 3D-Unit 1':       0b0000_0100_0000_0000,
    'Aux relais reset 3D-Unit 2':       0b0000_0010_0000_0000,
    'Aux relais scanner heater':        0b0000_0001_0000_0000,
    'Aux relais scanner motor':         0b0000_0000_1000_0000,
    'Aux relais reserve 1':             0b0000_0000_0100_0000,
    'Reserve': None
    }
mask = switch[outgoing_ioData_input['digital_out']['value']]
outgoing_ioData['digital_out']['value'] = 0 | mask

######Incoming
###TBD

####Telegram constructor

def incode():
    ##Header
    res = []
    res = byte_append(header['tg_size']['value'], 2, res)
    res = byte_append(header['tg_uid']['value'], 4, res)
    res = byte_append(header['tg_id']['value'], 2, res)
    res = byte_append(header['tg_seq_num']['value'], 2, res)

    ##Current time include
    time_vals = strftime('%y.%m.%d.%H.%M.%S').split('.')
    for i in range(0, len(time_vals)):
        res.append(int(time_vals[i]))
    res.append(int(time()%1*100))
    res.append(0)
    
    res = byte_append(header['tg_tms_flag']['value'], 1, res)
    res = byte_append(header['tg_reserve']['value'], 1, res)
    
    ##Body
    if header['tg_id']['value'] == 300:
        res = byte_append(0, 60, res)

##  Command
    elif header['tg_id']['value'] == 301:
        res = byte_append(outgoing_command['command']['value'], 2, res)
        res = byte_append(outgoing_command['measure_id']['value'], 4, res)

    ##Truck ID include (16 bytes)
        truck_id = str((outgoing_command['truck_id']['value'])).upper()
        remainig_bytes = 16 - len(truck_id) - 1
        for i in truck_id:
            res.append(ord(i))
        res.append(0)
        res = byte_append(0, remainig_bytes, res)
        
        res = byte_append(outgoing_command['reserve']['value'], 38, res)

##  IO Data
    elif header['tg_id']['value'] == 302:
        res = byte_append(outgoing_ioData['digital_in']['value'], 2, res)
        res = byte_append(outgoing_ioData['digital_out']['value'], 2, res)
        res = byte_append(outgoing_ioData['analog_in']['value'], 2, res)
        res = byte_append(outgoing_ioData['reserve']['value'], 54, res)
    else:
        print('Error: Illigal Outgoing staus code')
    
    return res


## n - number to append, length - size in bytes
def byte_append(n, length, arr):
    if n >= 2**(8*length):
        print('Error: number doesn\'t fit magnitude')
    for i in range((length-1)*8, -1, -8):
        arr.append((n&(0xFF<<i))>>i)
    return arr
        

a = incode()
if len(a) != 80:
    print('Error: byte array length is %2d, 80 expected' % len(a))

for i in range(len(a)):
    print('%2d:%3d,| ' % (i, a[i]), end='')
    if (i+1)%8 == 0 and i>0:
        print()
print()
##print(a)

b = bytes(a)
with open("bin_request.bin", "wb") as bf:
    bf.write(b)
    
print(bin(a[20]))


##SOCKET
sock = socket.socket()
sock.connect(('172.16.153.237', 50000))

req = bytes(a)
print(req)

while True:
    sock.send(req)
    sleep(1)
    data = sock.recv(80)
    print(data)
    sleep(0)
    break

print(data)
with open("bin_reply.bin", "wb") as reply:
    reply.write(data)

sock.close()
