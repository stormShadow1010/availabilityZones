from pprint import pprint
from collections import OrderedDict
from time import strftime
from time import time
from time import sleep
import copy
import socket
    
####Measurement request/result
header = {
    'tg_id':        11,
    'tg_version':   1,
    'tg_uniq_id':   20_150_674,
    'tg_sender':    0,
    'tg_receiver':  0,
    'tg_size':      80,
    'tg_counter':   0, ##Incrementional
    'tg_time':      0,
    'tg_reserved':     0,
    }

measurement_request = {
    'commands':     'Start Measurement',
    'type':         'Empty Measurement',
    'order':        'Incoming Measurement',
    'customer_id':  11,
    'client_id':    0,
    'truck_id':     'T999XX199',
    'reserved':     0,
    }

header_coded = copy.deepcopy(header)
##Body code
measurement_request_coded = copy.deepcopy(measurement_request)
mask = 0
##Measurement Commands
switch = {
    'Start Measurement':       0b1000_0000_0000_0000,
    'Abort Measurement':       0b0100_0000_0000_0000,
    }
mask = switch[measurement_request['commands']]
measurement_request_coded['commands'] = 0 | mask

##Menagement Type
switch = {
    'Empty Measurement':        0b1000_0000_0000_0000,
    'Full Measurement':         0b0100_0000_0000_0000,
    'Reference Measurement':    0b0010_0000_0000_0000,
    'Calibration Measurement':  0b0001_0000_0000_0000,
    }
mask = switch[measurement_request['type']]
measurement_request_coded['type'] = 0 | mask

#Measurement Order
switch = {
    'Incoming Measurement':       0b1000_0000_0000_0000,
    'Outgoing Measurement':       0b0100_0000_0000_0000,
    }
mask = switch[measurement_request['order']]
measurement_request_coded['order'] = 0 | mask

def incode():
    ##Head
    res = []
    res = byte_append(header_coded['tg_id'], 2, res)
    res = byte_append(header_coded['tg_version'], 1, res)
    res = byte_append(header_coded['tg_uniq_id'], 4, res)
    res = byte_append(header_coded['tg_sender'], 2, res)
    res = byte_append(header_coded['tg_receiver'], 2, res)
    res = byte_append(header_coded['tg_size'], 2, res)
    res = byte_append(header_coded['tg_counter'], 2, res)
    ##Current time include
    time_vals = strftime('%y.%m.%d.%H.%M.%S').split('.')
    for i in range(0, len(time_vals)):
        res.append(int(time_vals[i]))
    res.append(int(time()%1*100))
    res.append(0)
    res = byte_append(header_coded['tg_reserved'], 7, res)
    ##END Head

    ##Body
    res = byte_append(measurement_request_coded['commands'], 2, res)
    res = byte_append(measurement_request_coded['type'], 1, res)
    res = byte_append(measurement_request_coded['order'], 1, res)

    res = byte_append(0, 4, res)
    res = byte_append(0, 4, res)
    res = byte_append(0, 4, res)
    
    ##Truck ID include (16 bytes)
    truck_id = str((measurement_request['truck_id'])).upper()
    print('TRLEN: ', len(truck_id))
    remainig_bytes = 30 - len(truck_id) - 1
    for i in truck_id:
        res.append(ord(i))
    res.append(0)
    res = byte_append(0, remainig_bytes, res)
    
    res = byte_append(0, 4, res)

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


##SOCKET
sock = socket.socket()
sock.connect(('172.16.153.237', 50000))

req = bytes(a)
print(req)

while True:
    sock.send(req)
    sleep(1)
    data = sock.recv(130)
    print(data)
    sleep(0)
    break

print(data)
with open("bin_reply.bin", "wb") as reply:
    reply.write(data)

sock.close()
