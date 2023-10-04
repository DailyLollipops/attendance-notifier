import sqlite3
import datetime

class NotifierDatabase:
    '''
    Initialize a database for notifier class
        
    Parameters:
    database (str): Path of sqlite database
    '''

    def __init__(self, database):
        '''
        Initialize a database for notifier class
            
        Parameters:
        database (str) : Path of sqlite database
        '''
        self.database = sqlite3.connect(database)
        self.cursor = self.database.cursor()

    def lrn_exists(self, lrn: str):
        '''
        Check if student with given LRN exists

        Parameters:
        lrn (str) : LRN of student

        Returns:
        bool : Exists
        '''
        query = 'SELECT * FROM core_student WHERE lrn = ?'
        values = (lrn, )
        self.cursor.execute(query, values)
        result = self.cursor.fetchone()
        if result:
            return True
        else:
            return False
        
    def get_all_schedules(self):
        '''
        Get all existing schedules

        Returns:
        list of tupple : (id, subject, start, end, teacher_id)
        '''
        query = 'SELECT id, subject, start, end, teacher_id FROM core_schedule'
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        return results
        
    def get_current_schedule(self):
        '''
        Get schedule based on current date and time

        Returns:
        tupple : (id, subject, start, end, teacher_id)
        '''
        now = datetime.datetime.now()
        query = 'SELECT id, subject, start, end, teacher_id FROM core_schedule WHERE day = ? AND ? BETWEEN start and end'
        values = (now.date().weekday() + 1, now.time().strftime('%H:%M:%S'))
        self.cursor.execute(query, values)
        result = self.cursor.fetchone()
        return result
    
    def get_current_previous_schedule(self):
        '''
        Get previous schedule based on current date and time

        Returns:
        tupple : (id, id, subject, start, end, teacher_id)
        '''
        now = datetime.datetime.now()
        query = 'SELECT id, subject, start, end, teacher_id FROM core_schedule WHERE day = ? AND end < ? ORDER BY end DESC'
        values = (now.date().weekday() + 1, now.time().strftime('%H:%M:%S'))
        self.cursor.execute(query, values)
        result = self.cursor.fetchone()
        return result

    def get_schedule(self, day: int, time: datetime.time):
        '''
        Get schedule based on the given day and time

        Parameters:
        day (int) : Day of the week (1 = Monday, 7 = Sunday)
        time (datetime.time) : Time to check

        Returns:
        tupple : (id, subject, start, end, teacher_id)
        '''
        query = 'SELECT id, subject, start, end, teacher_id FROM core_schedule WHERE day = ? AND ? BETWEEN start and end'
        values = (day, str(time))
        self.cursor.execute(query, values)
        result = self.cursor.fetchone()
        return result
    
    def get_previous_schedule(self, day: int, time: datetime.time):
        '''
        Get previous schedule based on the given day and time

        Parameters:
        day (int) : Day of the week (1 = Monday, 7 = Sunday)
        time (datetime.time) : Time to check

        Returns:
        tupple : (id, subject, start, end, teacher_id)
        '''
        query = 'SELECT id, subject, start, end, teacher_id FROM core_schedule WHERE day = ? AND end < ? ORDER BY end DESC'
        values = (day, str(time))
        self.cursor.execute(query, values)
        result = self.cursor.fetchone()
        return result

    def get_attendance(self, date: datetime.date, schedule_id):
        '''
        Get list of students who attend a subject on specific date

        Parameters:
        date (datetime.date) : Date
        schedule_id : Schedule ID

        Returns:
        tupple : (student_name, lrn, time_in)
        '''
        query = '''
            SELECT s.first_name || ' ' || s.last_name AS student_name, s.LRN, a.time_in
            FROM core_student s
            JOIN core_attendance a ON s.id = a.student_id
            JOIN core_schedule sch ON a.schedule_id = sch.id
            AND a.date = ?
            AND a.schedule_id = ?
        '''
        values = (date, schedule_id)
        self.cursor.execute(query, values)
        results = self.cursor.fetchall()
        return results
    
    def get_absents(self, date : datetime.date, schedule_id):
        '''
        Get list of students who are absent in a subject on specific date

        Parameters:
        date (datetime.date) : Date
        schedule_id : Schedule ID

        Returns:
        tupple : (student_name, lrn, guardian_phone_number)
        '''
        attendance_query = '''
            SELECT DISTINCT s.id
            FROM core_student s
            JOIN core_attendance a ON s.id = a.student_id
            WHERE a.date = ? AND a.schedule_id = ?;
        '''
        self.cursor.execute(attendance_query, (date, schedule_id))
        attended_students = {row[0] for row in self.cursor.fetchall()}

        all_students_query = '''
            SELECT id
            FROM core_student;
        '''
        self.cursor.execute(all_students_query)
        all_students = {row[0] for row in self.cursor.fetchall()}
        absent_students = all_students - attended_students
        absent_students_query = '''
            SELECT first_name || ' ' || last_name AS student_name, LRN, guardian_phone_number
            FROM core_student
            WHERE id IN ({});
        '''.format(', '.join('?' for _ in absent_students))
        self.cursor.execute(absent_students_query, tuple(absent_students))
        results = self.cursor.fetchall()
        return results
    
    def attendance_exists(self, student_id, schedule_id, date: datetime.date):
        '''
        Check if an attendance by student exists

        Parameters:
        student_id: Student ID
        schedule_id : Schedule ID
        date (datetime.date) : Date

        Returns:
        bool : Exists
        '''
        query = '''
            SELECT id
            FROM core_attendance
            WHERE student_id = ?
            AND schedule_id = ?
            AND date = ?
        '''
        values = (student_id, schedule_id, date)
        self.cursor.execute(query, values)
        result = self.cursor.fetchone()
        if result:
            return True
        else:
            return False
        
    def add_attendance(self, student_id, schedule_id, date: datetime.date, time_in: datetime.time):
        '''
        Add attendance to database

        Parameters:
        student_id: Student ID
        schedule_id : Schedule ID
        date (datetime.date) : Date

        Returns:
        bool : Success
        '''
        query = 'INSERT INTO core_attendance(student_id, schedule_id, date, time_in) VALUES (?, ?, ?, ?)'
        values = (student_id, schedule_id, date, str(time_in))
        if self.attendance_exists(student_id, schedule_id, date):
            return False
        self.cursor.execute(query, values)
        self.database.commit()
        return True
    
    def get_student(self, student_id):
        '''
        Get a student by primary key

        Returns:
        tupple : (id, first_name, last_name, guardian_phone_number, LRN)
        '''
        query = 'SELECT id, first_name, last_name, guardian_phone_number, lrn FROM core_student WHERE id = ?'
        values = (student_id,)
        self.cursor.execute(query, values)
        result = self.cursor.fetchone()
        return result
    
    def get_student_by_lrn(self, lrn: str):
        '''
        Get a student by lrn

        Returns:
        tupple : (id, first_name, last_name, guardian_phone_number, LRN)
        '''
        query = 'SELECT id, first_name, last_name, guardian_phone_number, lrn FROM core_student WHERE lrn = ?'
        values = (lrn,)
        self.cursor.execute(query, values)
        result = self.cursor.fetchone()
        return result
    
    def get_teacher(self, teacher_id):
        '''
        Get a teacher by primary key

        Returns:
        tupple : (id, first_name, last_name, phone_number)
        '''
        query = 'SELECT id, first_name, last_name, phone_number FROM core_teacher WHERE id = ?'
        values = (teacher_id,)
        self.cursor.execute(query, values)
        result = self.cursor.fetchone()
        return result
    
    def get_all_attendance(self):
        '''
        Return all attendances in attendance table
        '''
        query = 'SELECT * FROM core_attendance'
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        return results
    
    def truncate_attendances(self):
        '''
        Delete all records on attendance table
        '''
        query = 'DELETE FROM core_attendance'
        self.cursor.execute(query)