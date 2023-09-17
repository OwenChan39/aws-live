from flask import Flask, render_template, request, redirect, url_for,session, flash
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__, static_folder='static')
app.secret_key = '123456'

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
            session['student_id'] = student_id
            return redirect(url_for('student_dashboard'))
        else:
            # Invalid credentials, display an error message
            flash('Invalid username or password', 'error')

    return render_template('login.html')

@app.route('/student_dashboard')
def student_dashboard():
    # Check if student is logged in by checking if student_id is in the session
    if 'student_id' in session:
        student_id = session['student_id']
        # Query the database to retrieve the student's information
        cursor = db_conn.cursor()
        cursor.execute("SELECT * FROM Student WHERE Stud_ID = %s", (student_id,))
        student = cursor.fetchone()
        cursor.close()

        if student:
            print("Student data fetched:", student)  # Add this line for debugging
            # Access the elements of the tuple by their indices
            Stud_name = student[0]
            Stud_ID = student[1]
            NRIC_Number = student[2]
            Gender = student[3]
            Programme_of_Study = student[4]
            CGPA = student[5]
            TARUMT_emailAddress = student[6]
            Mobile_number = student[7]
            Intern_batch = student[8]
            Home_Address = student[9]
            Personal_emailAddress = student[10]

            student_image_file_name_in_s3 = "student-id-" + str(student_id) + "_image_file"
            student_image_url = s3.meta.client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket, 'Key': student_image_file_name_in_s3},
                ExpiresIn=3600  # Set an appropriate expiration time
            )
            
            # Render the student dashboard page with the student's information
            return render_template('student_dashboard.html', Stud_name=Stud_name, Stud_ID=Stud_ID, NRIC_Number=NRIC_Number, Gender=Gender, Programme_of_Study=Programme_of_Study, CGPA=CGPA, TARUMT_emailAddress=TARUMT_emailAddress, Mobile_number=Mobile_number, Intern_batch=Intern_batch, Home_Address=Home_Address, Personal_emailAddress=Personal_emailAddress,student_image_url=student_image_url)

    # If the student is not logged in, redirect to the login page
    return redirect(url_for('login'))

def update_student_profile(student_id, cgpa, mobile_number, home_address, personal_email):
    cursor = db_conn.cursor()
    update_sql = "UPDATE Student SET CGPA=%s, Mobile_number=%s, Home_Address=%s, Personal_emailAddress=%s WHERE Stud_ID=%s"
    try:
        cursor.execute(update_sql, (cgpa, mobile_number, home_address, personal_email, student_id))
        db_conn.commit()
        return True  # Profile updated successfully
    except Exception as e:
        db_conn.rollback()
        return str(e)  # Error updating profile
    finally:
        cursor.close()

@app.route('/student_profile_edit', methods=['GET', 'POST'])
def student_profile_edit():
    if 'student_id' in session:
        student_id = session['student_id']
        cursor = db_conn.cursor()
        cursor.execute("SELECT * FROM Student WHERE Stud_ID = %s", (student_id,))
        student = cursor.fetchone()
        cursor.close()

        if student:
            if request.method == 'POST':
                updated_fields = request.form.getlist('update_fields[]')

                if 'cgpa' in updated_fields:
                    new_cgpa = request.form.get('cgpa')
                    if new_cgpa:
                        if update_student_profile(student_id, new_cgpa, None, None, None) is True:
                            flash('CGPA updated successfully', 'success')
                        else:
                            flash('Error updating CGPA', 'error')

                if 'mobile' in updated_fields:
                    new_mobile_number = request.form.get('mobileNumber')
                    if new_mobile_number:
                        if update_student_profile(student_id, None, new_mobile_number, None, None) is True:
                            flash('Mobile Number updated successfully', 'success')
                        else:
                            flash('Error updating Mobile Number', 'error')

                if 'address' in updated_fields:
                    new_home_address = request.form.get('homeAddress')
                    if new_home_address:
                        if update_student_profile(student_id, None, None, new_home_address, None) is True:
                            flash('Home Address updated successfully', 'success')
                        else:
                            flash('Error updating Home Address', 'error')

                if 'email' in updated_fields:
                    new_personal_email = request.form.get('personalEmail')
                    if new_personal_email:
                        if update_student_profile(student_id, None, None, None, new_personal_email) is True:
                            flash('Personal Email updated successfully', 'success')
                        else:
                            flash('Error updating Personal Email', 'error')

                return redirect(url_for('student_dashboard'))

            return render_template('try_student_update.html', student=student)

    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
