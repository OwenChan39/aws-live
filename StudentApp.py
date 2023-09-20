<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <meta name="description" content="">
    <meta name="author" content="">
    <link rel="preconnect" href="https://fonts.gstatic.com">
    <link href="https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;600;700;800&display=swap"
        rel="stylesheet">

    <title>Company info update - SEO Dream</title>

    <!-- Bootstrap core CSS -->
    <link href="{{ url_for('static', filename='vendor/bootstrap/css/bootstrap.min.css') }}" rel="stylesheet">

    <!-- Additional CSS Files -->
    <link href="{{ url_for('static', filename='assets/css/fontawesome.css') }}" rel="stylesheet">
    <link href="{{ url_for('static', filename='assets/css/templatemo-seo-dream.css') }}" rel="stylesheet">
    <link href="{{ url_for('static', filename='assets/css/animated.css') }}" rel="stylesheet">
    <link href="{{ url_for('static', filename='assets/css/owl.css') }}" rel="stylesheet">
    <!-- Your head content -->

    <style>
        /* Header styles */
        .header {
            background-color: #33ccc5;
            /* Change this color to match your index.html */
            color: #fff;
            padding: 10px 0;
            text-align: center;
        }

        .header h1 {
            margin: 0;
        }

        .sidebar {
            width: 250px;
            background-color: #333;
            /* Change this color to match your index.html */
            color: #fff;
            position: fixed;
            height: 100%;
            overflow: visible;
        }

        .sidebar a {
            padding: 15px;
            text-decoration: none;
            font-size: 18px;
            color: #fff;
            display: block;
        }

        .sidebar a:hover {
            background-color: #555;
        }

        .content {
            margin-left: 250px;
            padding: 20px;
        }

        .container {
            background-color: #f2f2f2;
            /* Grey background color */
            padding: 20px;
            border-radius: 10px;
            margin-top: 10px;
        }

        .job-offer {
            margin-top: 50px;
        }

        .job-offer ul li {
            margin-right: 10px;
            /* Add space between job name and delete button */
        }

        /* Additional styles for job position input fields */
        .job-inputs {
            margin-top: 20px;
        }

        .job-inputs .form-group {
            margin-bottom: 20px;
        }
    </style>
</head>

<body>

    <!-- ***** Header Start ***** -->
    <div class="header">
        <h1>Company Information Update</h1>
    </div>
    <!-- ***** Header End ***** -->
    <div class="sidebar">
        <a href="#company-info">Company Information</a>
        <a href="#job-offer">Job Offered</a>
        <!-- Add more navigation links as needed -->
        <!-- <a href="#">Link 2</a> -->
        <!-- <a href="#">Link 3</a> -->
    </div>
    <!-- ***** Company Information Form Start ***** -->

    <div class="content">
        <div class="company-info" id="company-info">

            <h3>Update <strong>[Company name]</strong> Information</h3>

            <div class="container">
                <form action="/company_profile_edit" method="POST">
                    <br>
                    <!-- Total Staff -->
                    <div class="form-group">
                        <label for="total_staff">Total Staff:</label>
                        <input type="number" class="form-control" id="total_staff" name="total_staff" required>
                    </div>

                    <br>
                    <!-- Product or Service -->
                    <div class="form-group">
                        <label for="product_service">Product or Service:</label>
                        <textarea class="form-control" id="product_service" name="product_service" rows="4"
                            required></textarea>
                    </div>

                    <br>
                    <!-- Company Website -->
                    <div class="form-group">
                        <label for="company_website">Company Website:</label>
                        <input type="url" class="form-control" id="company_website" name="company_website" required>
                    </div>

                    <br>
                    <!-- OT Claim (YES/NO) -->
                    <div class="form-group">
                        <label for="ot_claim">OT Claim (YES/NO):</label>
                        <select class="form-control" id="ot_claim" name="ot_claim" required>
                            <option value="YES">YES</option>
                            <option value="NO">NO</option>
                        </select>
                    </div>

                    <br>
                    <!-- Remarks -->
                    <div class="form-group">
                        <label for="remarks">Remarks:</label>
                        <textarea class="form-control" id="remarks" name="remarks" rows="4"></textarea>
                    </div>

                    <br>
                    <!-- Person in Charge -->
                    <div class="form-group">
                        <label for="person_in_charge">Person in Charge Name:</label>
                        <input type="text" class="form-control" id="person_in_charge" name="person_in_charge" required>
                    </div>

                    <br>
                    <!-- Contact Number -->
                    <div class="form-group">
                        <label for="contact_number">Contact Number:</label>
                        <input type="tel" class="form-control" id="contact_number" name="contact_number" required>
                    </div>

                    <br>
                    <!-- Email -->
                    <div class="form-group">
                        <label for="email">Email:</label>
                        <input type="email" class="form-control" id="email" name="email" required>
                    </div>

                    <br>
                    <!-- Upload SSM/Company Registration Certificate -->
                    <div class="form-group">
                        <label for="certificate_upload">Upload SSM/Company Registration Certificate:</label>
                        <input type="file" class="form-control-file" id="certificate_upload" name="certificate_upload"
                            required>
                    </div>

                    <br>
                    <!-- Upload Company Logo -->
                    <div class="form-group">
                        <label for="logo_upload">Upload Company Logo:</label>
                        <input type="file" class="form-control-file" id="logo_upload" name="logo_upload" required>
                    </div>

                    <div class="update-button">
                        <div class="form-group">
                            <button type="submit">Update</button>
                        </div>
                    </div>
                </form>
            </div>
        </div>

        <div class="job-offer" id='job-offer'>
            <h3>Job Positions Offered</h3>

            <!-- Additional input fields for job positions -->
            <div class="job-inputs">
                <h4>Add Job Position</h4>
                <div class="container">
                    <form action="/save_job_details" method="POST">
                        <div class="form-group">
                            <label for="job_position">Job Position:</label>
                            <input type="text" class="form-control" id="job_position" name="job_position">
                        </div>
                        <div class="form-group">
                            <label for="job_description">Job Description:</label>
                            <textarea class="form-control" id="job_description" name="job_description" rows="4"></textarea>
                        </div>
                        <div class="form-group">
                            <label for="job_requirements">Job Requirements:</label>
                            <textarea class="form-control" id="job_requirements" name="job_requirements" rows="4"></textarea>
                        </div>
                        <div class="form-group">
                            <label for="career_level">Career Level:</label>
                            <input type="text" class="form-control" id="career_level" name="career_level">
                        </div>
                        <div class="form-group">
                            <label for="qualification">Qualification:</label>
                            <input type="text" class="form-control" id="qualification" name="qualification">
                        </div>
                        <div class="form-group">
                            <label for="job_type">Job Type:</label>
                            <input type="text" class="form-control" id="job_type" name="job_type">
                        </div>
                        <div class="form-group">
                            <label for="years_experience">Years of Experience:</label>
                            <input type="number" class="form-control" id="years_experience" name="years_experience">
                        </div>
                        <div class="form-group">
                            <label for="salary">Salary:</label>
                            <input type="text" class="form-control" id="salary" name="salary">
                        </div>
                        <div class="form-group">
                            <button type="submit" class="main-green-button">Add</button>
                        </div>
                        <!-- ... (other form fields for additional job positions can be added here) ... -->
                    </form>
                </div>
            </div>

            <!-- Button to add another job position -->
        </div>

    </div>

    <!-- ***** Company Information Form End ***** -->

    <!-- ***** Footer Start ***** -->
    <footer>
        <!-- Add your footer content here, such as copyright information or links -->
    </footer>
    <!-- ***** Footer End ***** -->


</html>
