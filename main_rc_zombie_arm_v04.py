module_prefix = 'main_rc_zombie_arm'
module_version = '04'
module_name = module_prefix + '_v' + module_version + '.py'
print (module_name, 'starting')

print ('Expects  main_a_s_a_d  to be running on the Pico')
print ('Needs DIP switches 5 and 6 UP for Pico to respond')
print ('Needs Radio  ON !!!!!')
from importlib.machinery import SourceFileLoader
data_module = SourceFileLoader('Colin', '/home/pi/ColinThisPi/ColinData.py').load_module()
data_object = data_module.ColinData()
data_values = data_object.params
GPIO_version = data_values['GPIO']
GPIO = SourceFileLoader('GPIO', '/home/pi/ColinPiClasses/' + GPIO_version + '.py').load_module()
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

relay_pin_no = 21
gpio.set_mode(relay_pin_no, pigpio.OUTPUT)
my_stepper = GPIO.L298NStepperShort('Test Stepper', gpio, 19, 8, 7, 12)
my_stepper.float()
step_ons = 25
pause_microseconds = 2000

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
no_joysticks = 8
joysticks = [0] * no_joysticks
number_length = 4
delay = 0.1
serial_no = 0
servo_speed = 90
print_interval = 1000
i = 0
exiting = False
finished = False
old_switch_state = 'OFF'

print ('Main Loop')
first_time = True

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
                if first_time:
                    first_time = False
                    if ((joysticks[6] == 1) and (joysticks[7] == 1)):
                        print ('DIPS OK')
                        continue
                    else:
                        print ('DIPS 5 and 6 not set. Looks like Pico is not ready. Closing down')
                        exiting = True
                        continue
                knob_value = joysticks[5]
                base_target = knob_value
                #base_target = 30  #  FOR ECO-DISASTER
                base_servo.move_to(base_target, servo_speed)
                switch_value = joysticks[4]
                if switch_value < -10:
                    switch_state = 'FIRE'
                elif switch_value > 10:
                    switch_state = 'OFF'
                else:
                    switch_state = 'SPIN'
                if switch_state != old_switch_state:
                    old_switch_state = switch_state
                    if switch_state == 'FIRE':
                        for i in range(step_ons):
                            my_stepper.step_on('ANTI', pause_microseconds)
                        my_stepper.float()
                    elif switch_state == 'SPIN':
                        gpio.write(relay_pin_no,1)
                    else:
                        gpio.write(relay_pin_no,0)
                    print ('switch', switch_state)
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
