from django.db import models
from django.core.exceptions import ValidationError
import re

class Student(models.Model):
    lrn = models.CharField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    guardian_phone_number = models.CharField(max_length=255)

    def validate_philippine_phone_number(self, value):
        phone_number_pattern = r'^\+?63?[0-9]{10}$'

        if not re.match(phone_number_pattern, value):
            raise ValidationError("Please enter a valid Philippine phone number.")

    def clean(self):
        super().clean()
        self.validate_philippine_phone_number(self.guardian_phone_number)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

class Teacher(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255)

    def validate_philippine_phone_number(self, value):
        phone_number_pattern = r'^\+?63?[0-9]{10}$'

        if not re.match(phone_number_pattern, value):
            raise ValidationError("Please enter a valid Philippine phone number.")

    def clean(self):
        super().clean()
        self.validate_philippine_phone_number(self.phone_number)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

class Schedule(models.Model):
    days = (
        (1,'Monday'),
        (2,'Tuesday'),
        (3,'Wednesday'),
        (4,'Thursday'),
        (5,'Friday'),
        (6,'Saturday'),
        (7,'Sunday'),
    )

    subject = models.CharField(max_length=255)
    day = models.IntegerField(choices=days, default=1)
    start = models.TimeField()
    end = models.TimeField()
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)

    def check_for_conflict(self):
        conflicts = Schedule.objects.filter(
            day=self.day,
            start__lte=self.end,
            end__gte=self.start,
        ).exclude(pk=self.pk)  # Exclude the current instance from the query

        if conflicts.exists():
            raise ValidationError("This schedule conflicts with an existing schedule.")
    
    def clean(self):
        super().clean()
        self.check_for_conflict()

    def __str__(self):
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        return f'{self.subject} ({days[self.day - 1]} {str(self.start.hour).rjust(2, "0")}:{str(self.start.minute).rjust(2, "0")} - {str(self.end.hour).rjust(2, "0")}:{str(self.end.minute).rjust(2, "0")})'

    class Meta:
        ordering = ['day','start']

class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    date = models.DateField()
    time_in = models.TimeField(null=True)

    def __str__(self):
        return f'{self.pk}'
