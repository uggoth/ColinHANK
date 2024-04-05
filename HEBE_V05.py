module_name = 'HEBE_V05.py'
module_description = 'Objects for Raspberry Pi HEBE'
module_last_modified = '20240313'

from importlib.machinery import SourceFileLoader
data_module = SourceFileLoader('Colin', '/home/pi/ColinThisPi/ColinData.py').load_module()
data_object = data_module.ColinData()
data_values = data_object.params
ColObjectsVersion = data_values['ColObjects']
ColObjects = SourceFileLoader('ColObjects', '/home/pi/ColinPiClasses/' + ColObjectsVersion + '.py').load_module()
GPIOVersion = data_values['GPIO']
GPIO = SourceFileLoader('GPIO', '/home/pi/ColinPiClasses/' + GPIOVersion + '.py').load_module()
CommandStreamVersion = data_values['CommandStream']
CommandStream = SourceFileLoader('CommandStream', '/home/pi/ColinPiClasses/' + CommandStreamVersion + '.py').load_module()
AX12ServoVersion = data_values['AX12Servo']
AX12Servo = SourceFileLoader('AX12Servo', '/home/pi/ColinPiClasses/' + AX12ServoVersion + '.py').load_module()
pico_name = data_values['PICO_NAME']

class ZombieArm(ColObjects.ColObj):
    def __init__(self):
        global data_values
        super().__init__('Zombie Arm','2 servo arm for Nerf gun')
        ax12_path = data_values['AX12_PATH']
        ax12_speed = data_values['AX12_SPEED']
        self.ax12_connection = AX12Servo.Connection(port=ax12_path, baudrate=ax12_speed)
        self.base_servo = AX12Servo.AX12Servo('Base Servo', self.ax12_connection, 20)
        self.wrist_servo = AX12Servo.AX12Servo('Wrist Servo', self.ax12_connection, 21)
        self.wrist_servo.clockwise_label = 'UP'
        self.wrist_servo.anticlockwise_label = 'DOWN'
        self.servo_list = [self.base_servo,self.wrist_servo]
    def close(self):
        self.base_servo.close()
        self.wrist_servo.close()
        super().close()

class DIPS(ColObjects.ColObj):
    def __init__(self):
        super().__init__('DIP Switches','Collected for convenience')
        self.DIP_list = []

        self.DIP_4 = GPIO.Switch('DIP_4', 6)
        self.DIP_4.description = 'Suppress startup'
        self.DIP_list.append(self.DIP_4)

        self.DIP_5 = GPIO.Switch('DIP_5', 10)
        self.DIP_5.description = 'Not Used'
        self.DIP_list.append(self.DIP_5)

        self.DIP_6 = GPIO.Switch('DIP_6', 26)
        self.DIP_6.description = 'Not Used'
        self.DIP_list.append(self.DIP_6)

        self.DIP_7 = GPIO.Switch('DIP_7', 9)
        self.DIP_7.description = 'Not Used'
        self.DIP_list.append(self.DIP_7)

        self.DIP_8 = GPIO.Switch('DIP_8', 13)
        self.DIP_8.description = 'Not Used'
        self.DIP_list.append(self.DIP_8)

class Ultrasonics(ColObjects.ColObj):
    def __init__(self, gpio):
        super().__init__('Ultrasonics','Collected for convenience')
        self.ultrasonic_list = []
        trigger_pin_no = 22
        echo_pin_no = 27
        self.front_ultrasonic = GPIO.HCSR04('Front US', gpio, trigger_pin_no, echo_pin_no)
        self.ultrasonic_list.append(self.front_ultrasonic)
    def close(self):
        for ultrasonic in self.ultrasonic_list:
            ultrasonic.close()

if __name__ == "__main__":
    print (module_name)
    print (module_description)
