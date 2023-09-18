from django.contrib import admin
from .models import Student,Teacher, Schedule, Attendance

admin.site.register(Student)
admin.site.register(Teacher)
admin.site.register(Schedule)
admin.site.register(Attendance)
