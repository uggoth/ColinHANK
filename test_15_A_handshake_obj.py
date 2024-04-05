#  Test command stream handshake
#  Run in conjunction with test_15_A... on the Pico

module_name = 'test_15_A_handshake_obj.py'
print (module_name, 'starting')

from importlib.machinery import SourceFileLoader
data_module = SourceFileLoader('Colin', '/home/pi/ColinHEBE/ColinData.py').load_module()
data_object = data_module.ColinData()
data_values = data_object.params
ColObjectsVersion = data_values['ColObjects']
col_objects_name = '/home/pi/ColinPiClasses/' + ColObjectsVersion + '.py'
ColObjects = SourceFileLoader('ColObjects', col_objects_name).load_module()
ThisPiVersion = data_values['ThisPi']
pi_version = '/home/pi/ColinThisPi/' + ThisPiVersion + '.py'
ThisPi = SourceFileLoader('ThisPi', pi_version).load_module()
CommandStream = SourceFileLoader('CommandStream', '/home/pi/ColinPiClasses/' + data_values['CommandStream'] + '.py').load_module()
import time
import pigpio

gpio = pigpio.pi()
my_handshake = CommandStream.Handshake(4, gpio)
previous = my_handshake.get()
for i in range(900):
    new = my_handshake.get()
    if new != previous:
        print (new)
        previous = new
    time.sleep(0.01)

gpio.stop()
print (module_name, 'finished')
