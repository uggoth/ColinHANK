module_name = 'main_test_command_stream_B_v01'
print (module_name, 'starting')

#### Expects  main_test_command_stream_B  to be running on the Pico

import CommandStreamPi_v03 as CommandStream
import time
import pigpio

gpio = pigpio.pi()
handshake = CommandStream.Handshake(4, gpio)
#handshake = None
pico_id = 'PICOR'
my_pico = CommandStream.Pico(pico_id, gpio, handshake)

stream = [['HREV','2000'],
          ['HFWD','2000'],
          ['HOFF','1000'],
          ['DRIV005000000000','2000'],
          ['DRIV000000000000','0001'],
          ['EXIT','0001']]

serial_no = 0

for line in stream:
    command = line[0]
    duration_ms = line[1]
    serial_no += 1
    if my_pico.valid:
        serial_no_string = '{:04.0f}'.format(serial_no)
        message = serial_no_string + command
        print ('do_command: ' + message)
        result = my_pico.do_command(message)
        if result[4:8] != 'OKOK':
            print (result)
        time.sleep(int(duration_ms)/1000)
    else:
        print ('*** No Pico ***')
        break

my_pico.close()

print (module_name, 'finished')
