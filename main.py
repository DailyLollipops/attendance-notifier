import sys

sys.path.append('/home/roboscan/attendance-notifier')

import notifier
import datetime
import logging
import traceback
import subprocess
import time

logging.basicConfig(filename="attendance-notifier.log",
                    format='%(asctime)s [%(levelname)s] - %(message)s',
                    filemode='a', level=logging.DEBUG)

# For RGB LED wiring, follow : https://www.instructables.com/Raspberry-Pi-Tutorial-How-to-Use-a-RGB-LED/

logging.info('Starting process')

machine = notifier.Notifier(
    database='attendance_notifier/db.sqlite3', 
    port='/dev/ttyUSB0', 
    rgby_pins=(18, 23, 24, 17))

# Set machine time
com = subprocess.run(
    ['sudo', 'date', '-s', f'{machine.get_time().strftime("%y-%m-%d %H:%M:%S")}'], 
    capture_output=True,
    text=True,
    check=False)

logging.info(com.stdout)

machine.delete_all_sms()
logging.info('SMS deleted!')

current_schedule = None

while True:
    try:
        if current_schedule:
            # Turn LED blue (ready)
            machine.change_led_color('blue')
        else:
            # Turn LED yellow (not ready)
            machine.change_led_color('yellow')

        # Get current datetime
        now = datetime.datetime.now()

        # Check if current schedule is not yet assigned
        if not current_schedule:
            current_schedule = machine.get_current_schedule()
            if current_schedule:
                logging.info(f'Current Schedule ID: {current_schedule}')
                machine.delete_all_sms()
                logging.info('SMS deleted!')
            else:
                current_schedule = None

        # Checking if schedule just ended
        if current_schedule and now.time() > datetime.datetime.strptime(current_schedule[3], '%H:%M:%S').time():
            # Turn LED yellow (busy)
            machine.change_led_color('yellow')

            # Get list of attendees and absents
            attended = machine.get_attendance(now.date(), current_schedule[0])
            absents = machine.get_absents(now.date(), current_schedule[0])

            logging.info('Schedule just ended')
            logging.info(f'Student attended: {attended}')
            logging.info(f'Absent Students: {absents}')

            # Send list of attended and absents to teacher
            teacher = machine.get_teacher(current_schedule[4])
            teacher_message = f'Attendance - {now.strftime("%B %d, %Y")}\n{current_schedule[1]} ({current_schedule[2]} - {current_schedule[3]})\n\n'

            if attended:
                for student in attended:
                    teacher_message += f'{student[0]} ({student[1]}) - {student[2]}\n'
            else:
                teacher_message += 'No student has attended the class!'

            if absents: 
                teacher_message += '\nAbsent Students:\n'
                for student in absents:
                    teacher_message += f'{student[0]} ({student[1]})\n'
            else:
                teacher_message += 'No student is absent in class!'
            
            teacher_message += '\n\n\nThis is a generated message. Please do not reply!'
            logging.info(f'Sending message to {teacher[3]}')
            machine.send_sms(teacher[3], teacher_message)
            logging.info(f'Sent message to teacher:')
            logging.info(f'Message: {teacher_message}')
            logging.info(f'Number: {teacher[3]}')
            time.sleep(3)

            # Send message to parent of student that attended
            for student in attended:
                parent_message = f'{student[0]} ({student[1]}) attended the {current_schedule[1]} subject'
                parent_message += '\n\n\nThis is a generated message. Please do not reply!'
                logging.info(f'Sending message to {student[0]}')
                machine.send_sms(student[2], parent_message)
                logging.info('Sent message to parent:')
                logging.info(f'Message: {parent_message}')
                logging.info(f'Number: {student[2]}')
                time.sleep(1)

            # Send message to parent of absent students
            for student in absents:
                parent_message = f'{student[0]} ({student[1]}) missed the {current_schedule[1]} subject'
                parent_message += '\n\n\nThis is a generated message. Please do not reply!'
                logging.info(f'Sending message to {student[0]}')
                machine.send_sms(student[2], parent_message)
                logging.info('Sent message to parent:')
                logging.info(f'Message: {parent_message}')
                logging.info(f'Number: {student[2]}')
                time.sleep(1)

            # Turn LED blue (ready)
            machine.change_led_color('blue')

            # Remove assigned current schedule (renew)
            logging.info('Current Schedule ID: None')
            current_schedule = None
            machine.delete_all_sms()
            logging.info('SMS Deleted!')
            continue

        # Scan qrcode
        if current_schedule:
            lrn = machine.scan_qrcode(timeout=1)
            if not lrn:
                continue
            if machine.lrn_exists(lrn):
                student = machine.get_student_by_lrn(lrn)
                if not machine.attendance_exists(student[0], current_schedule[0], now.date()):
                    machine.change_led_color('green')
                    machine.add_attendance(student[0], current_schedule[0], now.date(), now.time().strftime('%H:%M:%S'))
                    logging.info(f'LRN matched: {lrn}')
                    time.sleep(3)
                else:
                    machine.change_led_color('red')
                    time.sleep(1)
            else:
                machine.change_led_color('red')
                logging.warning(f'LRN mismatched: {lrn}')
                time.sleep(1)
    except Exception as e:
        machine.change_led_color('red')
        logging.error(f'Exception occured: {e}')
        logging.error(f'Traceback: {traceback.format_exc()}')
        
