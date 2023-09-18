import serial
import time

class Sim808:
    '''
    Initialize a Sim808 object for communicating with a SIM808 module

    Parameters:
    port (str) : Serial port of SIM808 module 
    '''

    def __init__(self, port):
        '''
        Initialize a Sim808 object for communicating with a SIM808 module

        Parameters:
        port (str) : Serial port of SIM808 module 
        '''
        self.sim808 = serial.Serial(port, 115200, timeout=1)
        self.initialize()

    def initialize(self):
        '''
        Check if SIM808 exists and functioning
        '''
        self.send_command('AT\r')
        response = self.read_response()
        if('OK' not in response):
            raise Exception('Error starting sim808')
        self.send_command('AT+CMGF=1\r')
        self.read_response()
 
    def read_response(self):
        '''
        Get the response from SIM808 Serial COM

        Returns:
        str : SIM808 response
        '''
        response = ''
        while(self.sim808.inWaiting()):
            bit = self.sim808.read()
            response = response + bit.decode()
        return response
 
    def send_command(self, command: str, timeout: float = 1):
        '''
        Send a command to SIM808 Serial COM

        Parameters:
        command (str) : Command to send
        timeout (float) : Timeout allows module to recieve command in full
        '''
        self.sim808.write(command.encode())
        time.sleep(timeout)
 
    def send_sms(self, number: str, message: str):
        '''
        Send a SMS message

        Parameters:
        number (str) : Number to send message to. Should contain country code
        message (str) : Message to send
        '''
        self.send_command('AT+CMGS="' + number + '"\r')
        time.sleep(0.5)
        self.send_command(message + '\x1A\r\n')
