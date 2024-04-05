module_name = 'main_test_command_stream_A_v01'
print (module_name, 'starting')

#### Expects  main_test_command_stream_A  to be running on the Pico

import CommandStreamPi_v03 as CommandStream
import time
import pigpio

gpio = pigpio.pi()
handshake = CommandStream.Handshake(4, gpio)
#handshake = None
pico_id = 'PICOR'
my_pico = CommandStream.Pico(pico_id, gpio, handshake)

stream = ['WHOU','HREV','Garbage','HFWD','Garbij','HOFF','EXIT']

serial_no = 0

for command in stream:
    time.sleep(1)
    serial_no += 1
    if my_pico.valid:
        serial_no_string = '{:04.0f}'.format(serial_no)
        message = serial_no_string + command
        print ('do_command: ' + message)
        print (my_pico.do_command(message))
    else:
        print ('*** No Pico ***')
        break

my_pico.close()

print (module_name, 'finished')
