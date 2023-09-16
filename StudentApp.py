from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__, static_folder='static')

# AWS S3 configuration
bucket = custombucket
region = customregion
s3 = boto3.resource('s3')

# Database configuration
db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb
)

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/login")
def login():
    return render_template('login.html')

# Define a route for student sign-up
@app.route("/student_sign_up", methods=['GET', 'POST'])
def student_sign_up():
    if request.method == 'POST':
        # Get form data from the POST request
        student_name = request.form['Stud_name']
        student_id = request.form['Stud_ID']
        nric_no = request.form['NRIC_Number']
        gender = request.form['Gender']
        programme = request.form['Programme_of_Study']
        cgpa = request.form['CGPA']
        student_email = request.form['TARUMT_emailAddress']
        mobile_num = request.form['Mobile_number']
        intern_batch = request.form['Intern_batch']
        home_address = request.form['Home_Address']
        personal_email = request.form['Personal_emailAddress']
        student_image_file = request.files['studentImage']

        # Insert student data into the database
        insert_sql = "INSERT INTO Student (Stud_name, Stud_ID, NRIC_Number, Gender, Programme_of_Study, CGPA, TARUMT_emailAddress, Mobile_number, Intern_batch, Home_Address, Personal_emailAddress) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor = db_conn.cursor()
        
        try:
            cursor.execute(insert_sql, (student_name, student_id, nric_no, gender, programme, cgpa, student_email, mobile_num, intern_batch, home_address, personal_email))
            db_conn.commit()

            # Upload student image to S3
            if student_image_file.filename != "":
                student_image_file_name_in_s3 = "student-id-" + str(student_id) + "_image_file"
                s3.Bucket(bucket).put_object(Key=student_image_file_name_in_s3, Body=student_image_file)

            return render_template('signup_success.html', name=student_name)
        except Exception as e:
            return str(e)
        finally:
            cursor.close()

    return render_template('student_sign_up.html')

@app.route('/login', methods=['POST'], endpoint='login_student')
def login():
    if request.method == 'POST':
        # Get the entered student ID and IC number from the form
        student_id = request.form['username']
        ic_number = request.form['password']

        # Query the database to check if the student ID and IC number match
        cursor = db_conn.cursor()
        cursor.execute("SELECT * FROM Student WHERE Stud_ID = %s AND NRIC_Number = %s", (student_id, ic_number))
        student = cursor.fetchone()
        cursor.close()

        if student:
            # Student credentials are valid, redirect to the student dashboard
            return render_template('student_dashboard', student_id=student_id)
        else:
            # Invalid credentials, display an error message
            return render_template('login.html', error='Invalid username or password')

    return render_template('login.html')

@app.route('/student_dashboard/<student_id>')
def student_dashboard(student_id):
    # Query the database to retrieve the student's information
    cursor = db_conn.cursor()
    cursor.execute("SELECT * FROM Student WHERE Stud_ID = %s", (student_id,))
    student = cursor.fetchone()
    cursor.close()

    if student:
        # Render the student dashboard page with the student's information
        return render_template('student_dashboard.html', student=student)
    else:
        # Handle the case where the student ID is not found
        return render_template('error.html', message='Student not found')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
