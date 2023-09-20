from flask import Flask, render_template, request, redirect, url_for,session, flash
from pymysql import connections
import os
import boto3
from botocore.exceptions import NoCredentialsError, ClientError  
from config import *
from werkzeug.utils import secure_filename
import random
import string

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

# Function to generate a random unique company ID
def generate_company_id():
    # Generate a random alphanumeric string, e.g., 'C001'
    prefix = 'C'
    unique_id = ''.join(random.choices(string.digits, k=3))
    company_id = f'{prefix}{unique_id}'
    # Check if the generated ID is already in use
    while db_id_exists(company_id):
        unique_id = ''.join(random.choices(string.digits, k=3))
        company_id = f'{prefix}{unique_id}'
    return company_id

# Function to check if the generated company ID already exists in the database
def db_id_exists(company_id):
    cursor = db_conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM Company WHERE Company_ID = %s", (company_id,))
    count = cursor.fetchone()[0]
    cursor.close()
    return count > 0

@app.route("/company_signup", methods=['GET', 'POST'])
def company_signup():
    if request.method == 'POST':
        # Get form data from the POST request
        company_name = request.form['company_name']
        industry = request.form['industry']
        total_staff = request.form['total_staff']
        product_service = request.form['product_service']
        company_website = request.form['company_website']
        nature_of_job = request.form['job-possition']
        ot_claim = request.form['ot_claim']
        company_address = request.form['company_address']
        state = request.form['state']
        remarks = request.form['remarks']
        person_in_charge = request.form['person_in_charge']
        contact_number = request.form['contact_number']
        email = request.form['email']

        certificate_upload = request.files['certificate_upload']
        logo_upload = request.files['logo_upload']

        try:
            # Generate a unique company ID
            company_id = generate_company_id()
            
            # Insert company data into the database
            insert_sql = "INSERT INTO Company (Company_ID, Comp_name, Comp_website, State, Contact_number, Person_in_charge, EmailAddress, Comp_industry, Comp_address, Total_staff, Product_or_service, Job_offer, OT_claim, Remarks, Status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cursor = db_conn.cursor()

            status = "Pending"
            
            cursor.execute(insert_sql, (
                company_id, company_name, company_website, state, contact_number, person_in_charge, email, industry, company_address, total_staff, product_service, nature_of_job, ot_claim, remarks,status))
            db_conn.commit()

            # Upload company documents to S3
            if certificate_upload.filename != "":
                certificate_s3 = f"company-{company_id}-SSM_certificate"
                s3.Bucket(bucket).put_object(Key=certificate_s3, Body=certificate_upload)

            if logo_upload.filename != "":
                company_logo_s3 = f"company-{company_id}-logo"
                s3.Bucket(bucket).put_object(Key=company_logo_s3, Body=logo_upload)

            return render_template('signup_success.html', name=company_name)
        except Exception as e:
            return str(e)
        finally:
            cursor.close()

    return render_template('company_signup.html')

@app.route('/login', methods=['POST'], endpoint='login_role')
def login():
    if request.method == 'POST':
        # Get the entered role, username, and password from the form
        role = request.form['role']
        username = request.form['username']
        password = request.form['password']

        # Query the database to check if the username and password match for the selected role
        cursor = db_conn.cursor()

        if role == 'student':
            # Check if it's a student login
            cursor.execute("SELECT * FROM Student WHERE Stud_ID = %s AND NRIC_Number = %s", (username, password))
            student = cursor.fetchone()

            if student:
                # Student credentials are valid, redirect to the student dashboard
                session['student_id'] = username
                session['role'] = 'student'
                return redirect(url_for('student_dashboard'))
        
        elif role == 'lecturer':
            # Check if it's a lecturer login
            cursor.execute("SELECT * FROM Lecturer WHERE Lect_ID = %s AND Lect_IC = %s", (username, password))
            lecturer = cursor.fetchone()

            if lecturer:
                # Lecturer credentials are valid, redirect to the lecturer dashboard
                session['lecturer_id'] = username
                session['role'] = 'lecturer'
                return redirect(url_for('lecturer_dashboard'))
            
        elif role == 'company':
            # Check if it's a company login
            cursor.execute("SELECT * FROM Company WHERE Company_ID = %s AND Contact_number = %s", (username, password))
            company = cursor.fetchone()

            if company:
                session['company_id'] = username
                session['role'] = 'company'
                return redirect(url_for('company_dashboard'))

        cursor.close()

        # Invalid credentials or role, display an error message
        flash('Invalid username, password, or role', 'error')

    return render_template('login.html')

@app.route('/company_dashboard', methods=['GET', 'POST'])
def company_dashboard():
    if 'company_id' in session:
        company_id = session['company_id']
        cursor = db_conn.cursor()
        cursor.execute("SELECT * FROM Company WHERE Company_ID = %s", (company_id,))
        company = cursor.fetchone()
        cursor.close()
        
        if company:
            company_id = company[0]
            company_name = company[1]
            company_website = company[2]
            state = company[3]
            contact_number = company[4]
            person_in_charge = company[5]
            email = company[6]
            industry = company[7]
            company_address = company[8]
            total_staff = company[9]
            product_service = company[10]
            nature_of_job = company[11]
            ot_claim = company[12]
            remarks = company[13]
            status = company[14]
            
            
            company_logo = "company-" + str(company_id) + "-logo"
            company_image_url = s3.meta.client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket, 'Key': company_logo},
                ExpiresIn=3600
            )

            cursor = db_conn.cursor()
            cursor.execute("SELECT * FROM Job_Details WHERE Company_ID = %s", (company_id,))
            companyjobs = cursor.fetchall()  # Fetch all job listings
            cursor.close()

            return render_template('company_dashboard.html',
                                   company_name=company_name,
                                   industry=industry,
                                   total_staff=total_staff,
                                   product_service=product_service,
                                   company_website=company_website,
                                   nature_of_job=nature_of_job,
                                   ot_claim=ot_claim,
                                   company_address=company_address,
                                   state=state,
                                   remarks=remarks,
                                   person_in_charge=person_in_charge,
                                   contact_number=contact_number,
                                   email=email,
                                   company_image_url=company_image_url,
                                   status=status,
                                   companyjobs=companyjobs,
                                   )
        else:
            return "Company not found"
        
    else:
        return "Unauthorized"

@app.route("/addjobpage")
def addjobpage():
    return render_template('company_info_edit.html')

@app.route('/save_job_details', methods=['POST'])
def save_job_details():
    if request.method == 'POST':
        # Get job details from the form
        company_id = session.get('company_id')  # Assuming you store company_id in session after login
        job_position = request.form['job_position']
        job_description = request.form['job_description']
        job_requirements = request.form['job_requirements']
        career_level = request.form['career_level']
        qualification = request.form['qualification']
        job_type = request.form['job_type']
        years_experience = request.form['years_experience']
        salary = request.form['salary']

        try:
            # Insert job details into the database
            insert_sql = """
                INSERT INTO Job_Details (
                    company_id, JobPosition, JobDescription, JobRequirements,
                    CareerLevel, Qualification, JobType, YearsExperience, Salary
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor = db_conn.cursor()
            cursor.execute(insert_sql, (
                company_id, job_position, job_description, job_requirements,
                career_level, qualification, job_type, years_experience, salary
            ))
            db_conn.commit()
            cursor.close()

            # Redirect to a success page or any other appropriate action
            return redirect(url_for('company_dashboard'))

        except Exception as e:
            return str(e)  # Handle database insertion errors here

    # Handle GET requests or other cases
    return render_template('company_info_edit.html')  # Render the form page again if not a POST request



@app.route('/lecturer_dashboard', methods=['GET', 'POST'])
def lecturer_dashboard():
    if 'lecturer_id' in session and 'role' in session and session['role'] == 'lecturer':
        lecturer_id = session['lecturer_id']
        cursor = db_conn.cursor()
        cursor.execute("SELECT * FROM Lecturer WHERE Lect_ID = %s", (lecturer_id,))
        lecturer = cursor.fetchone()

        if lecturer:
            lecturer_name = lecturer[0]
        else:
            lecturer_name = "Unknown Lecturer"  # Default if lecturer not found

        cursor.close()

        # Pass the lecturer_name to the template
        return render_template('lecturer_dashboard.html', lecturer_name=lecturer_name)


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

@app.route('/studentdatabase', methods=['GET'])
def student_database():
    cursor = db_conn.cursor()

    # Get the search query from the URL parameter
    query = request.args.get('query', '')

    # Use the search query to filter the student data
    if query:
        # Execute a SQL query to retrieve matching students
        cursor.execute("SELECT Stud_ID, Stud_name, Gender, Programme_of_Study, Intern_batch, Personal_emailAddress FROM Student WHERE Stud_name LIKE %s OR Stud_ID LIKE %s", ('%' + query + '%', '%' + query + '%'))
    else:
        # If no query provided, retrieve all students
        cursor.execute("SELECT Stud_ID, Stud_name, Gender, Programme_of_Study, Intern_batch, Personal_emailAddress FROM Student")

    students = cursor.fetchall()
    cursor.close()

    return render_template('studentdatabase.html', students=students)


@app.route('/view_student_progress', methods=['GET'])
def view_student_progress():
    if 'lecturer_id' in session and session['role'] == 'lecturer':
        # Retrieve student data and file status from your database
        cursor = db_conn.cursor()
        cursor.execute("SELECT Stud_ID, Stud_name FROM Student")
        students = cursor.fetchall()

        # Dictionary to store file status and presigned URLs
        student_files = {}

        for student in students:
            student_id = student[0]

            # Initialize the file status as 'Completed' (green color)
            status = {'text': 'Completed', 'status': 'completed'}
            all_files_found = True  # Flag to track if all files are found

            # Generate presigned URLs for each file (if they exist)
            for file_name in ['letter_of_indemnity', 'company_acceptance_letter', 'parents_acknowledgment_form', 'progress-report', 'final-report']:
                file_key = f"student-{student_id}-{file_name}.pdf"
                presigned_url = None

                try:
                    s3_client = boto3.client('s3', region_name=region)
                    s3_object = s3_client.head_object(Bucket=bucket, Key=file_key)

                    if 'ContentLength' in s3_object:
                        # File exists, generate a presigned URL
                        presigned_url = s3_client.generate_presigned_url(
                            'get_object',
                            Params={'Bucket': bucket, 'Key': file_key},
                            ExpiresIn=3600
                        )
                    else:
                        # File does not exist, set the flag to False
                        all_files_found = False
                except NoCredentialsError:
                    flash('S3 credentials are missing or incorrect.', 'error')
                except ClientError as e:
                    if e.response['Error']['Code'] == '404':
                        # File does not exist, set the flag to False
                        all_files_found = False

                student_files.setdefault(student_id, {})[file_name] = {'url': presigned_url}

            # Update the status to 'Completed' only if all files are found
            if not all_files_found:
                status['text'] = 'Pending'
                status['status'] = 'pending'

            # Store the status in the student_files dictionary
            student_files[student_id]['Status'] = status

        cursor.close()

        return render_template('view_progress_reports.html', students=students, student_files=student_files)

    return redirect(url_for('login'))

@app.route('/student_company_jobs_posting')
def student_company_jobs_posting():
    cursor = db_conn.cursor()
    cursor.execute("""
        SELECT JD.JobPosition, C.Comp_name, JD.JobDescription, JD.CareerLevel
        FROM Job_Details JD
        JOIN Company C ON JD.Company_ID = C.Company_ID
    """)
    job_company_data = cursor.fetchall()
    cursor.close()

    if job_company_data:
        for row in job_company_data:
            print(row)  # Add this line for debugging
        return render_template('student_company_jobs_posting.html', job_company_data=job_company_data)
    else:
        return "No job postings available"
    
@app.route('/company_profile_edit', methods=['GET', 'POST'])
def company_profile_edit():
    if request.method == 'GET':
        # Retrieve existing company information from the database (replace 'company_id' with the actual company ID)
        company_id = session.get('company_id')  # You may have a different way to identify the company
        cursor = db_conn.cursor()
        cursor.execute("""
            SELECT Total_staff, Product_or_service, Comp_website, OT_claim, Remarks, Person_in_charge,
                   Contact_number, EmailAddress
            FROM Company
            WHERE Company_ID = %s
        """, (company_id,))
        company_info = cursor.fetchone()
        cursor.close()

        if company_info:
            # Pass the existing company information to the template
            return render_template('company_profile_edit.html', company_info=company_info)
        else:
            return "Company not found"

    elif request.method == 'POST':
        # Handle the form submission to update company information
        company_id = session.get('company_id')  # You may have a different way to identify the company
        total_staff = request.form['total_staff']
        product_service = request.form['product_service']
        company_website = request.form['company_website']
        ot_claim = request.form['ot_claim']
        remarks = request.form['remarks']
        person_in_charge = request.form['person_in_charge']
        contact_number = request.form['contact_number']
        email = request.form['email']

        # Update the database with the new information
        cursor = db_conn.cursor()
        cursor.execute("""
            UPDATE Company
            SET Total_staff = %s, Product_or_service = %s, Comp_website = %s, OT_claim = %s,
                Remarks = %s, Person_in_charge = %s, Contact_number = %s, EmailAddress = %s
            WHERE Company_ID = %s
        """, (total_staff, product_service, company_website, ot_claim, remarks,
              person_in_charge, contact_number, email, company_id))
        db_conn.commit()
        cursor.close()

        return "Company information updated successfully"



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)



