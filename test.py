import notifier
import datetime

machine = notifier.Notifier('attendance_notifier/db.sqlite3')

print(machine.get_teacher(1))