import notifier
import datetime

machine = notifier.Notifier('attendance_notifier/db.sqlite3', '/dev/ttyS0')

current_schedule = None

while True:
    # Turn LED blue (ready)

    now = datetime.datetime.now()

    if not current_schedule:
        current_schedule = machine.get_current_schedule()

    # Checking if schedule just ended
    if now.time().strftime('%H:%M:%S') > datetime.datetime.strptime(current_schedule[3], '%H:%M:%S').time():
        # Turn LED yellow (busy)

        # Notify teacher and parents
        attended = machine.get_attendance(now.date(), current_schedule[0])
        absents = machine.get_absents(now.date(), current_schedule[0])

        # Send list of attended and absents to teacher
        teacher = machine.get_teacher(current_schedule[4])
        teacher_message = f'Attendance - {now.date().month} {now.date().day}, {now.date().year}\n{current_schedule[1]} ({current_schedule[2]} - {current_schedule[3]})'

        for student in attended:
            teacher_message += f'{student[0]} ({student[1]}) - {student[2]}\n'

        teacher_message += '\nAbsent Students:\n' + '\n'.join(absents)
        # Send message to teacher

        # Send absent to parent
        for student in absents:
            parent_message = f'{student[0]} ({student[1]}) missed the {current_schedule[1]} subject'
            # Send message to guardian (student[2])

        # Turn LED blue (ready)
        current_schedule = None
        continue

    try:
        lrn = machine.scan_qrcode()
        if machine.lrn_exists(lrn):
            student = machine.get_student_by_lrn(lrn)
            machine.add_attendance(student[0], current_schedule[0], now.date(), now.time().strftime('%H:%M:%S'))
            # turn LED green
        else:
            pass
            # turn LED red
    except Exception as e:
        print(f'Exception occured: {e}')
        # turn LED red