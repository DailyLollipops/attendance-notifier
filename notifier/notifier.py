import cv2
import numpy
import sqlite3
import datetime

import RPi.GPIO as GPIO

from pyzbar.pyzbar import decode
from .database import NotifierDatabase
from .sim808 import Sim808

class Notifier:
    '''
    Initialize a notifier object

    Parameters:
    database (str) : Database path
    port (str) : Serial port of SIM808 module
    rgb_pins (tuple) : RGB pin (R, G, B), follows BCM pinout
    '''

    def __init__(self, database: str, port: str, rgb_pins: tuple):
        '''
        Initialize a notifier object

        Parameters:
        database (str) : Database path
        port (str) : Serial port of SIM808 module
        rgb_pins (tuple) : RGB pin (R, G, B), follows BCM pinout
        '''
        self.qrcode_scanner = cv2.VideoCapture(0)
        self.database = NotifierDatabase(database)
        self.gsm = Sim808(port)
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        self.rgb_pins = rgb_pins
        for pin in rgb_pins:
            GPIO.setup(pin, GPIO.OUT)

    def __decodeframe(self, image):
        '''
        Returns the decoded QR Code message
        '''
        trans_img = cv2.cvtColor(image,0)
        qrcode = decode(trans_img)
        for obj in qrcode:
            points = obj.polygon
            (x,y,w,h) = obj.rect
            pts = numpy.array(points, numpy.int32)
            pts = pts.reshape((-1, 1, 2))
            thickness = 2
            isClosed = True
            line_color = (0, 0, 255)
            cv2.polylines(image, [pts], isClosed, line_color, thickness)
            data = obj.data.decode("utf-8")
            return data
        
    def scan_qrcode(self):
        '''
        Opens an OpenCV window and scans QR Code   
        '''
        data = ''
        while True:
            ret, frame = self.qrcode_scanner.read()
            data = self.__decodeframe(frame)
            cv2.imshow('Image', frame)
            cv2.waitKey(1)
            if(data != None):
                break
        cv2.destroyAllWindows()
        return data
    
    def send_sms(self, number: str, message: str):
        '''
        Send a SMS message

        Parameters:
        number (str) : Number to send message to. Should contain country code
        message (str) : Message to send
        '''
        return self.gsm.send_sms(number, message)

    def change_led_color(self, color: str):
        '''
        Change LED color

        Parameters:
        color (str) : Color. Can be `white`, `blue`, `yellow`, `green`, `red`. Defaults to white.
        '''
        if color == 'blue':
            GPIO.output(self.rgb_pins[0], GPIO.HIGH)
            GPIO.output(self.rgb_pins[1], GPIO.HIGH)
            GPIO.output(self.rgb_pins[2], GPIO.LOW)
        elif color == 'yellow':
            GPIO.output(self.rgb_pins[0], GPIO.LOW)
            GPIO.output(self.rgb_pins[1], GPIO.LOW)
            GPIO.output(self.rgb_pins[2], GPIO.HIGH)
        elif color == 'green':
            GPIO.output(self.rgb_pins[0], GPIO.HIGH)
            GPIO.output(self.rgb_pins[1], GPIO.LOW)
            GPIO.output(self.rgb_pins[2], GPIO.HIGH)
        elif color == 'red':
            GPIO.output(self.rgb_pins[0], GPIO.LOW)
            GPIO.output(self.rgb_pins[1], GPIO.HIGH)
            GPIO.output(self.rgb_pins[2], GPIO.HIGH)
        else:
            GPIO.output(self.rgb_pins[0], GPIO.LOW)
            GPIO.output(self.rgb_pins[1], GPIO.LOW)
            GPIO.output(self.rgb_pins[2], GPIO.LOW)

    def turn_off_led(self):
        '''
        Turn off RGB LED
        '''
        GPIO.output(self.rgb_pins[0], GPIO.HIGH)
        GPIO.output(self.rgb_pins[1], GPIO.HIGH)
        GPIO.output(self.rgb_pins[2], GPIO.HIGH)
    
    
    #####################################
    #                                   #
    #         Database Functions        #
    #                                   #
    #####################################

    def lrn_exists(self, lrn: str):
        '''
        Check if student with given LRN exists

        Parameters:
        lrn (str) : LRN of student

        Returns:
        bool : Exists
        '''
        return self.database.lrn_exists(lrn)

    def get_current_schedule(self):
        '''
        Get schedule based on current date and time

        Returns:
        tupple : (id, subject, start, end, teacher_id)
        '''
        return self.database.get_current_schedule()
    
    def get_current_previous_schedule(self):
        '''
        Get previous schedule based on current date and time

        Returns:
        tupple : (id, id, subject, start, end, teacher_id)
        '''
        return self.database.get_current_previous_schedule()
    
    def get_schedule(self, day: int, time: datetime.time):
        '''
        Get schedule based on the given day and time

        Parameters:
        day (int) : Day of the week (1 = Monday, 7 = Sunday)
        time (datetime.time) : Time to check

        Returns:
        tupple : (id, subject, start, end, teacher_id)
        '''
        return self.database.get_schedule(day, time)
    
    def get_previous_schedule(self, day: int, time: datetime.time):
        '''
        Get previous schedule based on the given day and time

        Parameters:
        day (int) : Day of the week (1 = Monday, 7 = Sunday)
        time (datetime.time) : Time to check

        Returns:
        tupple : (id, subject, start, end, teacher_id)
        '''
        return self.database.get_previous_schedule(day, time)
    
    def get_attendance(self, date: datetime.date, schedule_id: str|int):
        '''
        Get list of students who attend a subject on specific date

        Parameters:
        date (datetime.date) : Date
        schedule_id : Schedule ID

        Returns:
        tupple : (student_name, lrn, time_in)
        '''
        return self.database.get_attendance(date, schedule_id)

    def get_absents(self, date : datetime.date, schedule_id: str|int):
        '''
        Get list of students who are absent in a subject on specific date

        Parameters:
        date (datetime.date) : Date
        schedule_id : Schedule ID

        Returns:
        tupple : (student_name, lrn, guardian_phone_number)
        '''
        return self.database.get_absents(date, schedule_id)
    
    def attendance_exists(self, student_id: str|int, schedule_id: str|int, date: datetime.date):
        '''
        Check if an attendance by student exists

        Parameters:
        student_id: Student ID
        schedule_id : Schedule ID
        date (datetime.date) : Date

        Returns:
        bool : Exists
        '''
        return self.database.attendance_exists(student_id, schedule_id, date)
    
    def add_attendance(self, student_id: str|int, schedule_id: str|int, date: datetime.date, time_in: datetime.time):
        '''
        Add attendance to database

        Parameters:
        student_id: Student ID
        schedule_id : Schedule ID
        date (datetime.date) : Date

        Returns:
        bool : Success
        '''
        return self.database.add_attendance(student_id, schedule_id, date, time_in)
    
    def get_student(self, student_id: str|int):
        '''
        Get a student by primary key

        Returns:
        tupple : (id, first_name, last_name, guardian_phone_number, LRN)
        '''
        return self.database.get_student(student_id)

    def get_student_by_lrn(self, lrn: str):
        '''
        Get a student by lrn

        Returns:
        tupple : (id, first_name, last_name, guardian_phone_number, LRN)
        '''
        return self.database.get_student_by_lrn(lrn)

    def get_teacher(self, teacher_id: str|int):
        '''
        Get a teacher by primary key

        Returns:
        tupple : (id, first_name, last_name, phone_number)
        '''
        return self.database.get_teacher(teacher_id)
    