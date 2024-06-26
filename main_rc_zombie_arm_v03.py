module_name = 'main_rc_zombie_arm_v03'
print (module_name, 'starting')

print ('Expects  main_rc_with_arm or main_a_s_a_d  to be running on the Pico')
print ('Needs DIP switches 5 and 6 UP')
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
js4_min = 181
js4_max = 1810
js4_mid = 994
wrist_interpolator = ColObjects.Interpolator('Wrist Servo Interpolator',
                                            [js4_min, js4_mid, js4_max],
                                            [100,      0,        -100])

loops = 100
no_joysticks = 6
joysticks = [0] * no_joysticks
number_length = 4
delay = 0.1
serial_no = 0
servo_speed = 90
print_interval = 1000
i = 0
exiting = False
finished = False

print ('Main Loop')

while not finished:
    i += 1
    if my_pico.valid:
        if exiting:
            command = 'EXIT'
            finished = True
        else:
            command = 'SBUS'
        serial_no += 1
        if serial_no > 9999:
            serial_no = 1
        serial_no_string = '{:04.0f}'.format(serial_no)
        try:
            serial_no_back, feedback, data = my_pico.send_command(serial_no_string, command)
            if feedback == 'EXIT':
                exiting = True
                continue
            elif feedback == 'OKOK':            
                for j in range(no_joysticks):
                    start = number_length * j
                    end = start + number_length
                    jvalue = data[start:end]
                    #print (jvalue)
                    joysticks[j] = int(jvalue)
                if i % print_interval == 0:
                    print (joysticks)
                knob_value = joysticks[5]
                #  TEMPORARY   ########################
                #base_target = knob_value
                base_target = 30
                #print ('base_target', base_target)
                base_servo.move_to(base_target, servo_speed)
                js4_value = joysticks[2]
                if js4_value > 25:
                    wrist_target = 72
                elif js4_value < -25:
                    wrist_target = 0
                else:
                    wrist_target = 52
                wrist_servo.move_to(wrist_target, servo_speed)
        except Exception as err:
            print ('**** bad interaction ****', err)
            print (serial_no_back, feedback, data)
            break
        time.sleep(delay)
    else:
        print ('*** No Pico ***')
        break

my_pico.close()

print (module_name, 'finished')
