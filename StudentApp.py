from flask import Flask, render_template, request, redirect, url_for,session, flash
from pymysql import connections
import os
import boto3
from botocore.exceptions import NoCredentialsError
from config import *
from werkzeug.utils import secure_filename

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

@app.route("/lecturer_sign_up", methods=['GET', 'POST'])
def lecturer_sign_up():
    if request.method == 'POST':
        # Get form data from the POST request
        full_name = request.form['full_name']
        staff_id = request.form['staff_id']
        email = request.form['email']
        ic = request.form['ic']
        position = request.form['position']

        # Insert lecturer data into the database
        insert_sql = "INSERT INTO Lecturer (Lect_name, Lect_ID, Lect_emailAddress, Lect_IC, Lect_Position) VALUES (%s, %s, %s, %s, %s)"
        cursor = db_conn.cursor()
        
        try:
            cursor.execute(insert_sql, (full_name, staff_id, email, ic, position))
            db_conn.commit()

            return render_template('signup_success.html', name=full_name)
        except Exception as e:
            return str(e)
        finally:
            cursor.close()

    return render_template('lecturer_sign_up.html')

# @app.route('/login', methods=['POST'], endpoint='login_student')
# def login():
#     if request.method == 'POST':
#         # Get the entered student ID and IC number from the form
#         student_id = request.form['username']
#         ic_number = request.form['password']

#         # Query the database to check if the student ID and IC number match
#         cursor = db_conn.cursor()
#         cursor.execute("SELECT * FROM Student WHERE Stud_ID = %s AND NRIC_Number = %s", (student_id, ic_number))
#         student = cursor.fetchone()
#         cursor.close()

#         if student:
#             # Student credentials are valid, redirect to the student dashboard
#             session['student_id'] = student_id
#             return redirect(url_for('student_dashboard'))
#         else:
#             # Invalid credentials, display an error message
#             flash('Invalid username or password', 'error')

#     return render_template('login.html')

@app.route('/login', methods=['POST'], endpoint='login_role')
def login():
    if request.method == 'POST':
        # Get the entered username and password from the form
        username = request.form['username']
        password = request.form['password']

        # Query the database to check if the username and password match for a student
        cursor = db_conn.cursor()
        cursor.execute("SELECT * FROM Student WHERE Stud_ID = %s AND NRIC_Number = %s", (username, password))
        student = cursor.fetchone()

        if student:
            # Student credentials are valid, set session data for student
            session['student_id'] = username
            session['role'] = 'student'
            return redirect(url_for('student_dashboard'))
        
        # If the user is not a student, check if they are a lecturer
        cursor.execute("SELECT * FROM Lecturer WHERE Lect_ID = %s AND Lect_IC = %s", (username, password))
        lecturer = cursor.fetchone()
        cursor.close()

        if lecturer:
            # Lecturer credentials are valid, set session data for lecturer
            session['lecturer_id'] = username
            session['role'] = 'lecturer'
            return redirect(url_for('lecturer_dashboard'))

        # Invalid credentials, display an error message
        flash('Invalid username, password, or role', 'error')

    return render_template('login.html')


@app.route("/lecturer_dashboard")
def lecturer_dashboard():
    return render_template('lecturer_dashboard.html')

@app.route('/student_dashboard', methods=['GET', 'POST'])
def student_dashboard():
    if 'student_id' in session:
        student_id = session['student_id']
        cursor = db_conn.cursor()
        cursor.execute("SELECT * FROM Student WHERE Stud_ID = %s", (student_id,))
        student = cursor.fetchone()
        cursor.close()

        if student:
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
                ExpiresIn=3600
            )

            # Check if a resume file exists in S3
            resume_filename = f"student-{student_id}-resume.pdf"  # Adjust the filename format as needed
            student_resume_url = None

            try:
                s3.Object(bucket, resume_filename).load()
                student_resume_url = s3.meta.client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': bucket, 'Key': resume_filename},
                    ExpiresIn=3600
                )
            except Exception as e:
                pass

            if request.method == 'POST' and 'resume_file' in request.files:
                student_resume_file = request.files['resume_file']

                # Ensure a file was selected for upload
                if student_resume_file and student_resume_file.filename != '':
                    resume_filename = f"student-{student_id}-resume.pdf"  # Adjust the filename format as needed

                    try:
                        s3.Bucket(bucket).put_object(Key=resume_filename, Body=student_resume_file)

                        student_resume_url = s3.meta.client.generate_presigned_url(
                            'get_object',
                            Params={'Bucket': bucket, 'Key': resume_filename},
                            ExpiresIn=3600
                        )

                        flash('Resume uploaded successfully', 'success')
                    except NoCredentialsError:
                        flash('S3 credentials are missing or incorrect. Unable to upload resume.', 'error')
                    except Exception as e:
                        flash(f'Error uploading resume: {str(e)}', 'error')
                else:
                    flash('No resume file selected for upload', 'error')

            if student_resume_url:
                resume_button_text = "View Resume"
            else:
                resume_button_text = "Upload Resume"

            return render_template('student_dashboard.html', Stud_name=Stud_name, Stud_ID=Stud_ID,
                                   NRIC_Number=NRIC_Number, Gender=Gender, Programme_of_Study=Programme_of_Study,
                                   CGPA=CGPA, TARUMT_emailAddress=TARUMT_emailAddress, Mobile_number=Mobile_number,
                                   Intern_batch=Intern_batch, Home_Address=Home_Address,
                                   Personal_emailAddress=Personal_emailAddress, student_image_url=student_image_url,
                                   student_resume_url=student_resume_url, resume_button_text=resume_button_text)

    # If the student is not logged in, redirect to the login page
    return redirect(url_for('login'))

def update_student_profile(student_id, updates):
    cursor = db_conn.cursor()
    update_sql = "UPDATE Student SET "
    update_values = []

    for field, value in updates.items():
        if value is not None:
            update_sql += f"{field} = %s, "
            update_values.append(value)

    # Remove the trailing comma and space
    update_sql = update_sql.rstrip(', ')

    update_sql += " WHERE Stud_ID = %s"
    update_values.append(student_id)

    try:
        cursor.execute(update_sql, tuple(update_values))
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
                updates = {}

                if 'cgpa' in updated_fields:
                    new_cgpa = request.form.get('cgpa')
                    updates['CGPA'] = new_cgpa

                if 'mobile' in updated_fields:
                    new_mobile_number = request.form.get('mobileNumber')
                    updates['Mobile_number'] = new_mobile_number

                if 'address' in updated_fields:
                    new_home_address = request.form.get('homeAddress')
                    updates['Home_Address'] = new_home_address

                if 'email' in updated_fields:
                    new_personal_email = request.form.get('personalEmail')
                    updates['Personal_emailAddress'] = new_personal_email

                if update_student_profile(student_id, updates) is True:
                    flash('Profile updated successfully', 'success')
                else:
                    flash('Error updating profile', 'error')

                return redirect(url_for('student_dashboard'))

            return render_template('try_student_update.html', student=student)

    return redirect(url_for('login'))

# Define a route for uploading the resume
@app.route('/upload_resume', methods=['POST'])
def upload_resume():
    if 'student_id' in session:
        student_id = session['student_id']
        student_resume_file = request.files['resume_file']

        # Ensure a file was selected for upload
        if student_resume_file and student_resume_file.filename != '':
            # Generate a unique filename for the resume, e.g., using the student's ID
            resume_filename = f"student-{student_id}-resume.pdf"  # Adjust the filename format as needed

            # Upload the resume file to your S3 bucket
            try:
                s3.Bucket(bucket).put_object(Key=resume_filename, Body=student_resume_file)

                # Update the database to store the resume information
                update_sql = "UPDATE Student SET ResumeFileName = %s WHERE Stud_ID = %s"
                cursor = db_conn.cursor()
                cursor.execute(update_sql, (resume_filename, student_id))
                db_conn.commit()

                flash('Resume uploaded successfully', 'success')
            except NoCredentialsError:
                flash('S3 credentials are missing or incorrect. Unable to upload resume.', 'error')
            except Exception as e:
                flash(f'Error uploading resume: {str(e)}', 'error')
        else:
            flash('No resume file selected for upload', 'error')

    return redirect(url_for('student_dashboard'))

@app.route('/student_upload_documents_page')
def student_upload_documents_page():
    return render_template('Student_Upload_Documents.html')

@app.route('/student_upload_documents', methods=['POST'])
def upload_documents():
    if request.method == 'POST':
        if 'student_id' in session:
            student_id = session['student_id']

        # Handle combined submission (Letter of Indemnity, Company Acceptance Letter, Parent's Acknowledgment Form)
        for field_name in ['letter_of_indemnity', 'company_acceptance_letter', 'parents_acknowledgment_form']:
            if field_name in request.files:
                file = request.files[field_name]
                if file.filename != '':
                    # Construct the S3 object key with the desired naming convention
                    s3_object_key = f"student-{student_id}-{field_name}.pdf"
                    s3.Bucket(bucket).put_object(Key=s3_object_key, Body=file)

        # Redirect to a success page or render a success message
        return redirect(url_for('student_upload_documents_page'))
    

@app.route('/student_upload_documents_progress', methods=['POST'])
def upload_progress_report():
    if request.method == 'POST':
        if 'student_id' in session:
            student_id = session['student_id']

        # Handle progress report submission
        if 'progress_report' in request.files:
            file = request.files['progress_report']
            if file.filename != '':
                # Construct the S3 object key with the desired naming convention
                s3_object_key = f"student-{student_id}-progress-report.pdf"
                s3.Bucket(bucket).put_object(Key=s3_object_key, Body=file)

        # Redirect to a success page or render a success message
        return redirect(url_for('student_upload_documents_page'))

@app.route('/student_upload_documents_final', methods=['POST'])
def upload_final_report():
    if request.method == 'POST':
        if 'student_id' in session:
            student_id = session['student_id']

        # Handle final report submission
        if 'final_report' in request.files:
            file = request.files['final_report']
            if file.filename != '':
                # Construct the S3 object key with the desired naming convention
                s3_object_key = f"student-{student_id}-final-report.pdf"
                s3.Bucket(bucket).put_object(Key=s3_object_key, Body=file)

        # Redirect to a success page or render a success message
        return redirect(url_for('student_upload_documents_page'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
