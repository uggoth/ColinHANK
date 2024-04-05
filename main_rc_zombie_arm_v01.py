module_name = 'main_rc_with_arm_v01'
print (module_name, 'starting')

#### Expects  main_rc_with_arm  to be running on the Pico

from importlib.machinery import SourceFileLoader
data_module = SourceFileLoader('Colin', '/home/pi/ColinThisPi/ColinData.py').load_module()
data_object = data_module.ColinData()
data_values = data_object.params
ThisPiVersion = data_values['ThisPi']
ThisPi = SourceFileLoader('ThisPi', '/home/pi/ColinThisPi/' + ThisPiVersion + '.py').load_module()
CommandStream = ThisPi.CommandStream
AX12Servo = ThisPi.AX12Servo
ColObjects = ThisPi.ColObjects
pico_name = data_values['PICO_NAME']
import time
import pigpio

gpio = pigpio.pi()
handshake = CommandStream.Handshake(4, gpio)
#handshake = None
my_pico = CommandStream.Pico(pico_name, gpio, handshake)
if my_pico.name != pico_name:
    print ('**** Expected Pico:', pico_name, 'Got:', my_pico.name,'****')
else:
    print ('Connected to Pico OK')
zombie_arm = ThisPi.ZombieArm()

base_servo = zombie_arm.base_servo
base_min = base_servo.min_angle_value
base_max = base_servo.max_angle_value
base_mid = (base_min + base_max) / 2
knob_min = 172
knob_max = 1811
knob_mid = 967
base_interpolator = ColObjects.Interpolator('Base Servo Interpolator',
                                            [knob_min, knob_mid, knob_max],
                                            [100,      0,        -100])
wrist_servo = zombie_arm.wrist_servo
wrist_min = wrist_servo.min_angle_value
wrist_max = wrist_servo.max_angle_value
wrist_mid = (wrist_min + wrist_max) / 2
js1_min = 181
js1_max = 1810
js1_mid = 994
wrist_interpolator = ColObjects.Interpolator('Wrist Servo Interpolator',
                                            [js1_min, js1_mid, js1_max],
                                            [100,      0,        -100])

loops = 100
no_joysticks = 6
joysticks = [0] * no_joysticks
number_length = 4
delay = 0.1
serial_no = 0
servo_speed = 90
interval = 10

for i in range(loops):
    if my_pico.valid:
        command = 'SBUS'
        serial_no += 1
        if serial_no > 9999:
            serial_no = 1
        serial_no_string = '{:04.0f}'.format(serial_no)
        message = serial_no_string + command
        result = my_pico.do_command(message)
        if result:
            try:
                if result[4:8] != 'OKOK':            
                    for j in range(no_joysticks):
                        start = 8 + (number_length * j)
                        end = start + number_length
                        joysticks[j] = int(result[start:end])
                    if i % interval == 0:
                        print (joysticks)
                    knob_value = joysticks[5]
                    base_target = base_interpolator.interpolate(knob_value)
                    base_servo.move_to(base_target, servo_speed)
                    js1_value = joysticks[0]
                    wrist_target = wrist_interpolator.interpolate(js1_value)
                    wrist_servo.move_to(wrist_target, servo_speed)
            except:
                print ('** bad result ** ' + result)
                continue
        time.sleep(delay)
    else:
        print ('*** No Pico ***')
        break

my_pico.close()

print (module_name, 'finished')
