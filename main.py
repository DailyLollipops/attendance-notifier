import notifier
import datetime
import logging

logging.basicConfig(filename="attendance-notifier.log",
                    format='%(asctime)s [%(levelname)s] - %(message)s',
                    filemode='a')

# For RGB LED wiring, follow : https://www.instructables.com/Raspberry-Pi-Tutorial-How-to-Use-a-RGB-LED/

machine = notifier.Notifier(
    database='attendance_notifier/db.sqlite3', 
    port='/dev/ttyS0', 
    rgb_pins=(12, 19, 13))

current_schedule = None

while True:
    try:
        # Turn LED blue (ready)
        machine.change_led_color('blue')

        # Get current datetime
        now = datetime.datetime.now()

        # Check if current schedule is not yet assigned
        if not current_schedule:
            current_schedule = machine.get_current_schedule()
            logging.info(f'Current Schedule ID: {current_schedule[0]}')

        # Checking if schedule just ended
        if now.time() > datetime.datetime.strptime(current_schedule[3], '%H:%M:%S').time():
            # Turn LED yellow (busy)
            machine.change_led_color('yellow')

            # Get list of attendees and absents
            attended = machine.get_attendance(now.date(), current_schedule[0])
            absents = machine.get_absents(now.date(), current_schedule[0])

            # Send list of attended and absents to teacher
            teacher = machine.get_teacher(current_schedule[4])
            teacher_message = f'Attendance - {now.date().month} {now.date().day}, {now.date().year}\n{current_schedule[1]} ({current_schedule[2]} - {current_schedule[3]})'

            for student in attended:
                teacher_message += f'{student[0]} ({student[1]}) - {student[2]}\n'

            teacher_message += '\nAbsent Students:\n' + '\n'.join(absents)
            machine.send_sms(teacher[3], teacher_message)

            # Send absent to parent
            for student in absents:
                parent_message = f'{student[0]} ({student[1]}) missed the {current_schedule[1]} subject'
                machine.send_sms(student[2], parent_message)

            # Turn LED blue (ready)
            machine.change_led_color('blue')

            # Remove assigned current schedule (renew)
            logging.info('Current Schedule ID: None')
            current_schedule = None
            continue

        # Scan qrcode
        lrn = machine.scan_qrcode()
        if machine.lrn_exists(lrn):
            student = machine.get_student_by_lrn(lrn)
            machine.add_attendance(student[0], current_schedule[0], now.date(), now.time().strftime('%H:%M:%S'))
            machine.change_led_color('green')
            logging.info(f'LRN matched: {lrn}')
        else:
            machine.change_led_color('red')
            logging.warning(f'LRN mismatched: {lrn}')
    except Exception as e:
        machine.change_led_color('red')
        logging.error(f'Exception occured: {e}')
