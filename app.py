from flask import Flask, render_template, session
from flask import request, redirect, url_for, Response, flash
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
import os
import cv2
from datetime import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from detection.face_matching import detect_faces, align_face
from detection.face_matching import extract_features, match_face
from utils.configuration import load_yaml

config_file_path = load_yaml("configs/database.yaml")

TEACHER_PASSWORD_HASH = config_file_path["teacher"]["password_hash"]
# print(TEACHER_PASSWORD_HASH)

# Initialize Firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(
    cred,
    {
        "databaseURL": "https://enduring-stage-369514-default-rtdb.firebaseio.com",
        "storageBucket": "enduring-stage-369514.appspot.com",
    },
)


import os

def upload_database(filename):
    """
    Checks if a file with the given filename already exists in the
    database storage, and if not, uploads the file to the database.
    """
    error = None

    # Check if the file already exists in the database
    if storage.bucket().get_blob(filename):
        error = f"<h1>{filename} already exists in the database</h1>"
        return False, error

    # Check if the filename is a number
    if not filename[:-4].isdigit():
        error = f"<h1>Please make sure that the name of the {filename} is a number</h1>"
        return False, error

    # Proceed with the upload
    try:
        # Assuming 'storage' and 'app' are already defined
        filename = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        bucket = storage.bucket()
        blob = bucket.blob(filename)
        blob.upload_from_filename(filename)
    except Exception as e:
        error = f"<h1>Error uploading {filename}: {str(e)}</h1>"
        return False, error

    return True, error


def match_with_database(img, database):
    '''The function "match_with_database" takes an image and a database as input, detects faces in the
    image, aligns and extracts features from each face, and matches the face to a face in the database.
    '''
    global match
    # Detect faces in the frame
    faces = detect_faces(img)

    # Draw the rectangle around each face
    for x, y, w, h in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 4)

    # save the image
    cv2.imwrite("static/recognized/recognized.png", img)

    for face in faces:
        try:
            # Align the face
            aligned_face = align_face(img, face)

            # Extract features from the face
            embedding = extract_features(aligned_face)

            embedding = embedding[0]["embedding"]

            # Match the face to a face in the database
            match = match_face(embedding, database)

            if match is not None:
                return f"Match found: {match}"
            else:
                return "No match found"
        except:
            return "No face detected"
      


app = Flask(__name__, template_folder="template")
app.secret_key = "123456" 


UPLOAD_FOLDER = "static/images"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/")
def mainmet():
    return render_template("index.html")

@app.route("/videoregister",methods=["GET", "POST"])
def videoregisters():
    return render_template("videoregister.html")

@app.route('/logout')
def logout():
    # Clear the session
    session.clear()
    flash('You have been logged out successfully.')
    return redirect(url_for('login'))


@app.route("/logins",methods=["GET", "POST"])
def login():
    flag = 0
    if request.method == "POST":
        emails = request.form.get("loginmail")
        passwords = request.form.get("loginpass")
        ref = db.reference("Students")
        number_student = len(ref.get())
        for i in range(1, number_student):
            studentInfo = db.reference(f"Students/{i}").get()
            if studentInfo["email"] == emails and studentInfo["password"] == passwords:
                session["email"] = emails
                return redirect(url_for("stuhome"))
            else:
                flag = 1
        if flag == 1:
            flash("Invalid email or password")
    return render_template("login.html")
   

@app.route('/stuhome', methods=['GET', 'POST'])
def stuhome():
    if 'email' not in session:
        return redirect(url_for('login'))
    email = session['email']
    ref = db.reference('Students')
    number_student = len(ref.get())
    for i in range(1, number_student):
        studentInfo = db.reference(f"Students/{i}").get()
        if studentInfo["email"] == email:
            imagename = studentInfo['filename'] + '.png'
            url = url_for('static', filename=f'images/{imagename}')
            student_details = {
                'name': studentInfo['name'],
                'email': studentInfo['email'],
                'age': studentInfo['age'],
                'dob': studentInfo['dob'],
                'address': studentInfo['address'],
                'phone': studentInfo['phone'],
                'city': studentInfo['city'],
                'state': studentInfo['state'],
                'country': studentInfo['country'],
                'classes': studentInfo['classes'],
                'course': studentInfo['course']
                
                }
            break
    if not student_details:
        return "Student not found"
    
    return render_template('stuhome.html', student=student_details,url = url)
         
@app.route("/attendances")
def home():
    return render_template("home.html")

@app.route("/takeattendance")
def takeattendance():

    return render_template("takeattendance.html")

@app.route("/add_info")
def add_info():
    return render_template("add_info.html")


@app.route("/teacher_login", methods=["GET", "POST"])
def teacher_login():
    if request.method == "POST":
        password = request.form.get("password")
        if check_password_hash(TEACHER_PASSWORD_HASH, password):
            return redirect(url_for("attendance"))
        else:
            flash("Incorrect password")
    return render_template("teacher_login.html")


@app.route("/attendance")
def attendance():
    ref = db.reference("Students")
    number_student = len(ref.get())
    # attandence
    students = {}
    for i in range(1, number_student):
        studentInfo = db.reference(f"Students/{i}").get()
        students[i] = [
            studentInfo["name"],
            studentInfo["email"],
            studentInfo["classes"],
        ]
    return render_template("attendance.html", students=students)




@app.route("/video_feed")
def video_feed():
    return Response(gen_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/capture", methods=["POST"])
def capture():
    global filename
    ret, frame = video.read()
    if ret:
        # Information to database
        ref = db.reference("Students")

        try:
           
            studentId = len(ref.get())

        except TypeError:
            studentId = 1

        
        filename = f"{studentId}.png"
       
        cv2.imwrite(os.path.join(app.config["UPLOAD_FOLDER"], filename), frame)

      
        val, err = upload_database(filename)

        if val:
            return err
   
    return redirect(url_for("add_info"))


@app.route("/success/<filename>")
def success(filename):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")  # for browser cache
  
    url = url_for("static", filename="images/" + filename, v=timestamp)
    
    # return f'<h1>{filename} image uploaded successfully to the database</h1><img src="{url}" alt="Uploaded image">'
    return render_template('result.html', filename=filename, url=url)


@app.route("/submit_info", methods=["POST"])
def submit_info():
    # Get the form data
    name = request.form.get("name")
    email = request.form.get("email")
    course = request.form.get("courses")  
    password = request.form.get("password")
    age = request.form.get("age")
    dob = request.form.get("dob")
    address = request.form.get("address")
    phone = request.form.get("phone")
    city = request.form.get("city")
    state = request.form.get("state")
    country = request.form.get("country")
    pincode = request.form.get("pincode")

    if course == "B.Tech":
        classes = ["data structures", "algorithms", "computer networks", "operating systems", "database management systems"]
    elif course == "M.Tech":
        classes = ["introduction to machine learning", "deep learning", "computer vision", "natural language processing", "reinforcement learning"]
    elif course == "BBA":
        classes = ["finance", "marketing", "human resources",]
    elif course == "MBA":
        classes = ["human resources", "marketing", "finance", "operations management", "business analytics"]
    elif course == "BCA":
        classes = ["intro to programming", "data structures", "algorithms", "computer networks", "operating systems", "database management systems"]
    elif course == "MCA":
        classes = ["discrete mathematics", "data structures", "algorithms", "computer networks", "operating systems", "database management systems"]
    elif course == "B.Sc":
        classes = ["mathematics", "physics", "chemistry", "biology", "computer science", "statistics"]
    elif course == "M.Sc":
        classes = ["physics", "chemistry", "biology", "computer science", "statistics", "mathematics"]
    elif course == "B.Com":
        classes = ["accounting", "finance", "economics", "business law", "marketing"]
    
    studentId, _ = os.path.splitext(filename)
    fileName = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    data = cv2.imread(fileName)

    # Detect faces in the image
    faces = detect_faces(data)

    for face in faces:
        # Align the face
        aligned_face = align_face(data, face)

        # Extract features from the face
        embedding = extract_features(aligned_face)
        break

    # Add the information to the database
    #check email already exist or not
    ref = db.reference("Students")
    number_student = len(ref.get())
    if number_student != 0:
        studentInfo = db.reference(f"Students/{1}").get()
        if studentInfo["email"] == email:
            flash("Email already exist")
            return redirect(url_for("add_info"))
  
    base_name, extension = os.path.splitext(filename)

    data = {
        str(studentId): {
            "name": name,
            "email": email,
            "classes": {class_: int("0") for class_ in classes},
            "password": password,
            "embeddings": embedding[0]["embedding"],
            "age": age,
            "dob": dob,
            "address": address,
            "phone": phone,
            "city": city,
            "state": state,
            "country": country,
            "pincode": pincode,
            "filename": base_name,
            "course" :course,

        }
    }

    for key, value in data.items():
        ref.child(key).set(value)

    return redirect(url_for("success", filename=filename))


@app.route("/recognize", methods=["GET", "POST"])
def recognize():
    global detection
    ret, frame = video.read()
    if ret:
        # Information to database
        ref = db.reference("Students")
        # Obtain the last studentId number from the database
        number_student = len(ref.get())
        print("There are", (number_student - 1), "students in the database")

        database = {}
        for i in range(1, number_student):
            studentInfo = db.reference(f"Students/{i}").get()
            studentName = studentInfo["name"]
            studentEmbedding = studentInfo["embeddings"]
            database[studentName] = studentEmbedding

        detection = match_with_database(frame, database)

    # Return a successful response
    return redirect(url_for("select_class"))


@app.route("/select_class", methods=["GET", "POST"])
def select_class():
    if request.method == "POST":
        # Get the selected class from the form data
        selected_class = request.form.get("classes")

        # Generate the URL of the image
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")  # for browser cache
        url = url_for("static", filename="recognized/recognized.png", v=timestamp)

        # Information to database
        ref = db.reference("Students")
        # Obtain the last studentId number from the database
        number_student = len(ref.get())

        for i in range(1, number_student):
            studentInfo = db.reference(f"Students/{i}").get()
            if match == studentInfo["name"]:
                # Check if the selceted class is in the list of studentInfo['classes']
                print(studentInfo["classes"])
                if selected_class in studentInfo["classes"]:
                    # Update the attendance in the database
                    ref.child(f"{i}/classes/{selected_class}").set(
                        int(studentInfo.get("classes", {}).get(selected_class)) + 1
                    )

                    return render_template('selectresult.html', url=url,selected_class=selected_class)
                    
                else:
                    return f'<h2>Student not in class - {detection}</h2><img src="{url}" alt="Recognized face">'
    else:
        # Render the select class page
        if 'email' not in session:
         return redirect(url_for('login'))
        email = session['email']
        ref = db.reference('Students')
        number_student = len(ref.get())
        for i in range(1, number_student):
            studentInfo = db.reference(f"Students/{i}").get()
            if studentInfo["email"] == email:
                student_details = {
                    'classes': studentInfo['classes']
                }
                break
        if not student_details:
            return "Student not found"
        return render_template("select_class.html", student=student_details)
    

def gen_frames():
    global video
    video = cv2.VideoCapture(0)
    while True:
        success, frame = video.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode(".jpg", frame)
            frame = buffer.tobytes()
        yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")


if __name__ == "__main__":
    app.run(debug=True)
