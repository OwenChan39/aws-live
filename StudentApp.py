from flask import Flask, render_template, request, redirect, url_for,session, flash, jsonify
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
                student_image_file_name_in_s3 = "student-" + str(student_id) + "-profile_pic"
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

def generate_company_id():
    prefix = 'C'
    unique_id = ''.join(random.choices(string.digits, k=5))
    company_id = f'{prefix}{unique_id}'
    while db_id_exists(company_id):
        unique_id = ''.join(random.choices(string.digits, k=5))
        company_id = f'{prefix}{unique_id}'
    return company_id

def generate_job_id():
    prefix = 'J'
    unique_id = ''.join(random.choices(string.digits, k=5))
    job_id = f'{prefix}{unique_id}'
    while db_id_exists(job_id):
        unique_id = ''.join(random.choices(string.digits, k=5))
        job_id = f'{prefix}{unique_id}'
    return job_id

def db_id_exists(company_id):
    cursor = db_conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM Company WHERE Company_ID = %s", (company_id,))
    count = cursor.fetchone()[0]
    cursor.close()
    return count > 0

@app.route("/company_signup", methods=['GET', 'POST'])
def company_signup():
    if request.method == 'POST':
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

def encrypt(text, key):
    encrypted_text = ""
    for char in text:
        encrypted_char = chr(ord(char) ^ key)
        encrypted_text += encrypted_char
    return encrypted_text

def decrypt(encrypted_text, key):
    decrypted_text = ""
    for char in encrypted_text:
        decrypted_char = chr(ord(char) ^ key)
        decrypted_text += decrypted_char
    return decrypted_text

@app.route("/admin_signup", methods=["GET", "POST"])
def admin_signup():
    if request.method == "POST":
        cursor = db_conn.cursor()
        encrypt_key = 42
        admin_name = request.form["admin_name"]
        admin_username = request.form["admin_username"]
        admin_password = encrypt(request.form["admin_password"], encrypt_key)

        cursor.execute("SELECT * FROM Admin WHERE admin_username = %s", (admin_username))
        check_admin = cursor.fetchall()
        num_of_admin = len(check_admin)
        if num_of_admin == 0:

            insert_sql = "INSERT INTO Admin (admin_name, admin_username, admin_password) VALUES (%s, %s, %s)"

            try:
                cursor.execute(insert_sql, (admin_name, admin_username, admin_password))
                db_conn.commit()

                return render_template("signup_success.html", name=admin_name)

            finally:
                cursor.close()
    
    return render_template("adminSignup.html")

@app.route('/login', methods=['POST'], endpoint='login_role')
def login():
    if request.method == 'POST':
        role = request.form['role']
        username = request.form['username']
        password = request.form['password']

        cursor = db_conn.cursor()

        if role == 'student':
            # Check if it's a student login
            cursor.execute("SELECT * FROM Student WHERE Stud_ID = %s AND NRIC_Number = %s", (username, password))
            student = cursor.fetchone()

            if student:
                session['student_id'] = username
                session['role'] = 'student'
                return redirect(url_for('student_dashboard'))
        
        elif role == 'lecturer':
            cursor.execute("SELECT * FROM Lecturer WHERE Lect_ID = %s AND Lect_IC = %s", (username, password))
            lecturer = cursor.fetchone()

            if lecturer:
                session['lecturer_id'] = username
                session['role'] = 'lecturer'
                return redirect(url_for('lecturer_dashboard'))
            
        elif role == 'company':
            cursor.execute("SELECT * FROM Company WHERE Company_ID = %s AND Contact_number = %s", (username, password))
            company = cursor.fetchone()

            if company:
                session['company_id'] = username
                session['role'] = 'company'
                return redirect(url_for('company_dashboard'))

        elif role == "admin":
            encryption_key = 42
            cursor.execute(
                "SELECT admin_username, admin_password FROM Admin WHERE admin_username = %s",
                (username)
            )
            result = cursor.fetchone()

            if result:
                stored_encrypted_password = result[1]

                stored_password = decrypt(stored_encrypted_password, encryption_key)

                if stored_password == password:
                    session["admin_username"] = username
                    session["role"] = "admin"
                    return redirect(url_for("adminLanding"))

        cursor.close()

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
                                   status=status
                                   )
        else:
            return "Company not found"
        
    else:
        return "Unauthorized"

@app.route('/company_jobs_offers', methods=['GET', 'POST'])
def company_jobs_offers():
    if 'company_id' in session:
        company_id = session['company_id']
        cursor = db_conn.cursor()
        cursor.execute("SELECT * FROM Company WHERE Company_ID = %s", (company_id,))
        company = cursor.fetchone()
        cursor.close()
        
        if company:
            status = company[14]

            cursor = db_conn.cursor()
            cursor.execute("SELECT * FROM Job_Details WHERE Company_ID = %s", (company_id,))
            companyjobs = cursor.fetchall()
            cursor.close()

            return render_template('company_jobs_offers.html',
                                   status=status,
                                   companyjobs=companyjobs
                                   )
        else:
            return "Company not found"
        
    else:
        return "Unauthorized"

@app.route("/companyinfopage")
def companyinfopage():
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
            contact_number = company[4]
            person_in_charge = company[5]
            email = company[6]
            total_staff = company[9]
            product_service = company[10]
            ot_claim = company[12]
            remarks = company[13]
            
            company_logo = "company-" + str(company_id) + "-logo"
            company_image_url = s3.meta.client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket, 'Key': company_logo},
                ExpiresIn=3600
            )
            return render_template('company_info_edit.html', 
                                    company_name=company_name,
                                    total_staff=total_staff,
                                    product_service=product_service,
                                    company_website=company_website,
                                    ot_claim=ot_claim,
                                    remarks=remarks,
                                    person_in_charge=person_in_charge,
                                    contact_number=contact_number,
                                    email=email,
                                    company_image_url=company_image_url,
                                    )

@app.route("/addjobpage")
def addjobpage():
    return render_template('company_add_jobs.html')

@app.route('/company_profile_edit', methods=['GET', 'POST'])
def company_profile_edit():
    if 'company_id' in session:
        if request.method == 'POST':
            company_id = session['company_id']
            cursor = db_conn.cursor()
            total_staff = request.form['total_staff']
            product_service = request.form['product_service']
            company_website = request.form['company_website']
            remarks = request.form['remarks']
            person_in_charge = request.form['person_in_charge']
            contact_number = request.form['contact_number']
            email = request.form['email']
            ot_claim=request.form['ot_claim']

            update_query = """
                UPDATE Company
                SET Total_Staff = %s, Product_or_Service = %s, Comp_Website = %s, Remarks = %s,
                Person_In_Charge = %s, Contact_Number = %s, EmailAddress = %s, ot_claim = %s
                WHERE Company_ID = %s
            """

            cursor.execute(update_query, (
                total_staff, product_service, company_website, remarks,
                person_in_charge, contact_number, email, ot_claim, company_id, 
            ))

            db_conn.commit()

            cursor.execute("SELECT * FROM Company WHERE Company_ID = %s", (company_id,))
            company = cursor.fetchone()
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
            
                cursor.execute("SELECT * FROM Job_Details WHERE Company_ID = %s", (company_id,))
                companyjobs = cursor.fetchall()
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
        
        return redirect(url_for('companyinfopage'))


@app.route('/save_job_details', methods=['POST'])
def save_job_details():
    if request.method == 'POST':
        company_id = session.get('company_id')  
        job_position = request.form['job_position']
        job_description = request.form['job_description']
        job_requirements = request.form['job_requirements']
        career_level = request.form['career_level']
        qualification = request.form['qualification']
        job_type = request.form['job_type']
        years_experience = request.form['years_experience']
        salary = request.form['salary']

        job_id = generate_job_id()

        try:
            insert_sql = """
                INSERT INTO Job_Details (
                    company_id, JobPosition, JobDescription, JobRequirements,
                    CareerLevel, Qualification, JobType, YearsExperience, Salary, Job_id
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor = db_conn.cursor()
            cursor.execute(insert_sql, (
                company_id, job_position, job_description, job_requirements,
                career_level, qualification, job_type, years_experience, salary, job_id
            ))
            db_conn.commit()
            cursor.close()

            return redirect(url_for('company_jobs_offers'))

        except Exception as e:
            return str(e) 

    return redirect(url_for('company_dashboard'))

@app.route('/delete_job', methods=['POST'])
def delete_job():
    if request.method == 'POST':
        job_id = request.form['job_id']
        
        try:
            delete_sql = "DELETE FROM Job_Details WHERE Job_id = %s"
            cursor = db_conn.cursor()
            cursor.execute(delete_sql, (job_id,))
            db_conn.commit()
            cursor.close()

            return jsonify("success")
            
        except Exception as e:
            return jsonify("error")

    return redirect(url_for('company_dashboard'))


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
            lecturer_name = "Unknown Lecturer" 

        cursor.close()

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

            student_image_file_name_in_s3 = "student-" + str(student_id) + "-profile_pic"
            student_image_url = s3.meta.client.generate_presigned_url(
                'get_object',
                Params={'Bucket': bucket, 'Key': student_image_file_name_in_s3},
                ExpiresIn=3600
            )

            resume_filename = f"student-{student_id}-resume.pdf" 
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

                if student_resume_file and student_resume_file.filename != '':
                    resume_filename = f"student-{student_id}-resume.pdf"  

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

    return redirect(url_for('login'))

@app.route("/adminLanding")
def adminLanding():
    return render_template("adminLanding.html")
    
@app.route("/adminProfile", methods=["GET", "POST"])
def adminProfile():
    if "admin_username" in session and "role" in session and session["role"] == "admin":
        admin_username = session["admin_username"]
        cursor = db_conn.cursor()
        cursor.execute("SELECT * FROM Admin WHERE admin_username = %s", (admin_username,))
        admin = cursor.fetchone()

        if admin:
            admin_name = admin[0]
            admin_username = admin[1]
            admin_password = admin[2]
        else:
            admin_name = "Unknown Admin" 

        cursor.close()

        return render_template("adminProfile.html", admin=admin)

def update_student_profile(student_id, updates):
    cursor = db_conn.cursor()
    update_sql = "UPDATE Student SET "
    update_values = []

    for field, value in updates.items():
        if value is not None:
            update_sql += f"{field} = %s, "
            update_values.append(value)

    update_sql = update_sql.rstrip(', ')

    update_sql += " WHERE Stud_ID = %s"
    update_values.append(student_id)

    try:
        cursor.execute(update_sql, tuple(update_values))
        db_conn.commit()
        return True 
    except Exception as e:
        db_conn.rollback()
        return str(e) 
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

@app.route('/upload_resume', methods=['POST'])
def upload_resume():
    if 'student_id' in session:
        student_id = session['student_id']
        student_resume_file = request.files['resume_file']

        if student_resume_file and student_resume_file.filename != '':
            resume_filename = f"student-{student_id}-resume.pdf" 

            try:
                s3.Bucket(bucket).put_object(Key=resume_filename, Body=student_resume_file)

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

        for field_name in ['letter_of_indemnity', 'company_acceptance_letter', 'parents_acknowledgment_form']:
            if field_name in request.files:
                file = request.files[field_name]
                if file.filename != '':
                    s3_object_key = f"student-{student_id}-{field_name}.pdf"
                    s3.Bucket(bucket).put_object(Key=s3_object_key, Body=file)

        return redirect(url_for('student_upload_documents_page'))
    

@app.route('/student_upload_documents_progress', methods=['POST'])
def upload_progress_report():
    if request.method == 'POST':
        if 'student_id' in session:
            student_id = session['student_id']

        if 'progress_report' in request.files:
            file = request.files['progress_report']
            if file.filename != '':
                s3_object_key = f"student-{student_id}-progress-report.pdf"
                s3.Bucket(bucket).put_object(Key=s3_object_key, Body=file)

        return redirect(url_for('student_upload_documents_page'))

@app.route('/student_upload_documents_final', methods=['POST'])
def upload_final_report():
    if request.method == 'POST':
        if 'student_id' in session:
            student_id = session['student_id']

        if 'final_report' in request.files:
            file = request.files['final_report']
            if file.filename != '':
                s3_object_key = f"student-{student_id}-final-report.pdf"
                s3.Bucket(bucket).put_object(Key=s3_object_key, Body=file)

        return redirect(url_for('student_upload_documents_page'))

@app.route('/studentdatabase', methods=['GET'])
def student_database():
    cursor = db_conn.cursor()

    query = request.args.get('query', '')

    if query:
        cursor.execute("SELECT Stud_ID, Stud_name, Gender, Programme_of_Study, Intern_batch, Personal_emailAddress FROM Student WHERE Stud_name LIKE %s OR Stud_ID LIKE %s", ('%' + query + '%', '%' + query + '%'))
    else:
        cursor.execute("SELECT Stud_ID, Stud_name, Gender, Programme_of_Study, Intern_batch, Personal_emailAddress FROM Student")

    students = cursor.fetchall()
    cursor.close()

    return render_template('studentdatabase.html', students=students)

@app.route("/adminStudent", methods=["GET"])
def adminStudent():
    cursor = db_conn.cursor()

    query = request.args.get("query", "")

    if query:
        cursor.execute(
            "SELECT Stud_ID, Stud_name, Gender, Programme_of_Study, Intern_batch, Personal_emailAddress FROM Student WHERE Stud_name LIKE %s OR Stud_ID LIKE %s",
            ("%" + query + "%", "%" + query + "%"),
        )
    else:
        cursor.execute(
            "SELECT Stud_ID, Stud_name, Gender, Programme_of_Study, Intern_batch, Personal_emailAddress FROM Student ORDER BY Stud_name"
        )

    students = cursor.fetchall()
    number_of_students = len(students)
    enumerated_students = enumerate(students)
    cursor.close()

    return render_template("adminStudent.html", students=enumerated_students, number_of_students=number_of_students)

@app.route('/adminDeleteStudent/<string:student_id>', methods=["GET"])
def admin_delete_student(student_id):
    cursor = db_conn.cursor()

    delete_query = "DELETE FROM Student WHERE Stud_ID = %s"
    cursor.execute(delete_query, (student_id,))
    db_conn.commit()

    cursor.close()
    return redirect(url_for("adminStudent"))

@app.route("/adminLecturer", methods=["GET"])
def adminLecturer():
    cursor = db_conn.cursor()

    query = request.args.get("query", "")

    if query:
        cursor.execute(
            "SELECT Lect_name, Lect_ID, Lect_emailAddress, Lect_IC, Lect_position FROM Lecturer WHERE Lect_name LIKE %s OR Lect_ID LIKE %s",
            ("%" + query + "%", "%" + query + "%"),
        )
    else:
        cursor.execute(
            "SELECT Lect_name, Lect_ID, Lect_emailAddress, Lect_IC, Lect_position FROM Lecturer ORDER BY Lect_name"
        )

    lecturers = cursor.fetchall()
    number_of_lecturers = len(lecturers)
    enumerated_lecturers = enumerate(lecturers)
    cursor.close()

    return render_template("adminLecturer.html", lecturers=enumerated_lecturers, number_of_lecturers=number_of_lecturers)

@app.route('/adminDeleteLecturer/<string:lecturer_id>', methods=["GET"])
def admin_delete_lecturer(lecturer_id):
    cursor = db_conn.cursor()

    delete_query = "DELETE FROM Lecturer WHERE Lect_ID = %s"
    cursor.execute(delete_query, (lecturer_id,))
    db_conn.commit()

    cursor.close()
    return redirect(url_for("adminLecturer"))

@app.route('/view_student_progress', methods=['GET'])
def view_student_progress():
    if 'lecturer_id' in session and session['role'] == 'lecturer':
        cursor = db_conn.cursor()
        cursor.execute("SELECT Stud_ID, Stud_name FROM Student")
        students = cursor.fetchall()

        student_files = {}

        for student in students:
            student_id = student[0]

            status = {'text': 'Completed', 'status': 'completed'}
            all_files_found = True  

            for file_name in ['letter_of_indemnity', 'company_acceptance_letter', 'parents_acknowledgment_form', 'progress-report', 'final-report']:
                file_key = f"student-{student_id}-{file_name}.pdf"
                presigned_url = None

                try:
                    s3_client = boto3.client('s3', region_name=region)
                    s3_object = s3_client.head_object(Bucket=bucket, Key=file_key)

                    if 'ContentLength' in s3_object:
                        presigned_url = s3_client.generate_presigned_url(
                            'get_object',
                            Params={'Bucket': bucket, 'Key': file_key},
                            ExpiresIn=3600
                        )
                    else:
                        all_files_found = False
                except NoCredentialsError:
                    flash('S3 credentials are missing or incorrect.', 'error')
                except ClientError as e:
                    if e.response['Error']['Code'] == '404':
                        all_files_found = False

                student_files.setdefault(student_id, {})[file_name] = {'url': presigned_url}

            if not all_files_found:
                status['text'] = 'Pending'
                status['status'] = 'pending'

            student_files[student_id]['Status'] = status

        cursor.close()

        return render_template('view_progress_reports.html', students=students, student_files=student_files)

    return redirect(url_for('login'))

@app.route('/student_company_jobs_posting')
def student_company_jobs_posting():
    cursor = db_conn.cursor()
    cursor.execute("""
        SELECT JD.JobPosition, C.Comp_name, JD.JobDescription, JD.CareerLevel, JD.JobRequirements, JD.Qualification, JD.Salary
        FROM Job_Details JD
        JOIN Company C ON JD.Company_ID = C.Company_ID
    """)
    job_company_data = cursor.fetchall()
    cursor.close()

    if job_company_data:
        for row in job_company_data:
            print(row) 
        return render_template('student_company_jobs_posting.html', job_company_data=job_company_data)
    else:
        return "No job postings available"

@app.route('/company_database', methods=["GET"])
def company_database():
    cursor = db_conn.cursor()

    cursor.execute(
        "SELECT Comp_name, EmailAddress, Contact_number, Comp_address, Person_in_charge, Status FROM Company WHERE Status = 'Pending' ORDER BY Comp_name"
    )
    new_applications = cursor.fetchall()
    num_of_new = len(new_applications)
    enumerated_new = enumerate(new_applications)

    cursor.execute(
        "SELECT Comp_name, EmailAddress, Contact_number, Comp_address, Person_in_charge, Status FROM Company WHERE Status = 'Approved' ORDER BY Comp_name"
    )
    approved_companies = cursor.fetchall()
    num_of_approved = len(approved_companies)
    enumerated_approved = enumerate(approved_companies)

    cursor.execute(
        "SELECT Comp_name, EmailAddress, Contact_number, Comp_address, Person_in_charge, Status FROM Company WHERE Status = 'Rejected' ORDER BY Comp_name"
    )
    rejected_companies = cursor.fetchall()
    num_of_rejected = len(rejected_companies)
    enumerated_rejected = enumerate(rejected_companies)

    cursor.close()

    return render_template("adminCompany.html",
                           new_applications=enumerated_new,
                           num_of_new=num_of_new,
                           approved_companies=enumerated_approved,
                           num_of_approved=num_of_approved,
                           rejected_companies=enumerated_rejected,
                           num_of_rejected=num_of_rejected)

@app.route('/adminDeleteCompany/<string:company_name>', methods=["GET"])
def admin_delete_company(company_name):
    cursor = db_conn.cursor()

    delete_query = "DELETE FROM Company WHERE Comp_name = %s"
    cursor.execute(delete_query, (company_name,))
    db_conn.commit()

    cursor.close()
    return redirect(url_for("company_database"))

@app.route('/update_company_status', methods=['POST'])
def update_company_status():
    cursor = db_conn.cursor()
    company_name = str(request.form.get('company_name'))
    action = str(request.form.get('action'))

    if action == 'approve':
        cursor.execute("UPDATE Company SET Status = 'Approved' WHERE Comp_name = %s", (company_name,))
    elif action == 'reject':
        cursor.execute("UPDATE Company SET Status = 'Rejected' WHERE Comp_name = %s", (company_name,))
    
    db_conn.commit()
    cursor.close()
    return redirect(url_for("company_database"))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
