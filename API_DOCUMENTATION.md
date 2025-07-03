# Intelligent Face Recognition Attendance System - API Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Setup and Configuration](#setup-and-configuration)
3. [Web API Endpoints](#web-api-endpoints)
4. [Core Modules and Functions](#core-modules-and-functions)
5. [Configuration Utilities](#configuration-utilities)
6. [Frontend Components](#frontend-components)
7. [Usage Examples](#usage-examples)
8. [Database Schema](#database-schema)

## Project Overview

This is a Flask-based web application that implements an intelligent face recognition attendance system. The system allows students to register their faces, login, and mark attendance using facial recognition technology. Teachers can manage the system and view attendance records.

### Key Features
- Face detection and recognition using OpenCV and DeepFace
- Student registration with facial biometric data
- Automated attendance marking through face recognition
- Teacher dashboard for attendance management
- Firebase integration for data storage
- Real-time video processing for face capture

### Dependencies
The system requires Python 3.8+ and key dependencies include:
- Flask 2.1.0
- OpenCV 4.8.0.74
- DeepFace 0.0.92
- Firebase Admin SDK 6.5.0
- dlib (with shape predictor model)

## Setup and Configuration

### Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Configure Firebase credentials
# Place your serviceAccountKey.json in the root directory

# Configure database settings
# Edit configs/database.yaml with your Firebase configuration
```

### Configuration Files

#### `configs/database.yaml`
```yaml
teacher:
  password_hash: "pbkdf2:sha256:260000$HEpPDqDm0nYHv6oG$d7c53e69f9b1168fab28ebc7afc2987b65d87faabd2eb8d04b4aa7393209a972"
firebase:
  databaseURL: 'https://enduring-stage-369514-default-rtdb.firebaseio.com'
  storageBucket: "enduring-stage-369514.appspot.com"
  pathToServiceAccount: "configs/serviceAccountKey.json"
```

## Web API Endpoints

### Public Endpoints

#### `GET /` - Main Index
**Description:** Renders the main landing page of the application.
**Template:** `index.html`
**Authentication:** None required

```python
@app.route("/")
def mainmet():
    return render_template("index.html")
```

#### `GET|POST /logins` - Student Login
**Description:** Handles student authentication using email and password.
**Methods:** GET, POST
**Template:** `login.html`
**Redirects:** `/stuhome` on success

```python
# POST data expected:
{
    "loginmail": "student@example.com",
    "loginpass": "password123"
}
```

#### `GET|POST /videoregister` - Video Registration
**Description:** Renders the video registration interface for new students.
**Template:** `videoregister.html`

#### `GET /logout` - User Logout
**Description:** Clears user session and redirects to login.
**Redirects:** `/logins`

### Student Dashboard Endpoints

#### `GET|POST /stuhome` - Student Home
**Description:** Student dashboard displaying personal information and profile image.
**Authentication:** Requires active session
**Template:** `stuhome.html`

```python
# Returns student data:
{
    'name': 'John Doe',
    'email': 'john@example.com',
    'age': '20',
    'dob': '2003-01-01',
    'address': '123 Main St',
    'phone': '+1234567890',
    'city': 'New York',
    'state': 'NY',
    'country': 'USA',
    'classes': ['data structures', 'algorithms'],
    'course': 'B.Tech'
}
```

### Teacher Management Endpoints

#### `GET|POST /teacher_login` - Teacher Authentication
**Description:** Teacher login using password hash verification.
**Template:** `teacher_login.html`
**Redirects:** `/attendance` on success

```python
# POST data expected:
{
    "password": "teacher_password"
}
```

#### `GET /attendance` - Attendance Management
**Description:** Teacher dashboard for viewing and managing student attendance.
**Authentication:** Requires teacher login
**Template:** `attendance.html`

### Registration and Data Management

#### `GET /add_info` - Student Information Form
**Description:** Renders form for adding student personal information.
**Template:** `add_info.html`

#### `POST /submit_info` - Submit Student Information
**Description:** Processes student registration data and stores in Firebase.

```python
# POST data expected:
{
    "name": "John Doe",
    "email": "john@example.com",
    "courses": "B.Tech",
    "password": "password123",
    "age": "20",
    "dob": "2003-01-01",
    "address": "123 Main St",
    "phone": "+1234567890",
    "city": "New York",
    "state": "NY",
    "country": "USA",
    "pincode": "12345"
}
```

### Face Recognition Endpoints

#### `POST /capture` - Capture Face Image
**Description:** Captures image from video feed and uploads to database.
**Returns:** Redirects to `/add_info` or error message

#### `GET|POST /recognize` - Face Recognition
**Description:** Performs face recognition against stored database.
**Redirects:** `/select_class` after recognition

#### `GET|POST /select_class` - Class Selection
**Description:** Allows students to select class for attendance marking.
**Authentication:** Requires student session
**Template:** `select_class.html`

```python
# POST data expected:
{
    "classes": "data structures"
}
```

### Utility Endpoints

#### `GET /video_feed` - Video Stream
**Description:** Provides real-time video feed for face capture.
**Content-Type:** `multipart/x-mixed-replace; boundary=frame`

#### `GET /success/<filename>` - Upload Success
**Description:** Displays successful image upload confirmation.
**Template:** `result.html`
**Parameters:** `filename` - uploaded image filename

## Core Modules and Functions

### Face Detection and Recognition (`detection/face_matching.py`)

#### `detect_faces(img)`
**Description:** Detects faces in an input image using Haar cascade classifier.

```python
def detect_faces(img):
    """
    Detects faces in an image and returns bounding box coordinates.
    
    Parameters:
    -----------
    img : numpy.ndarray
        Input image in BGR format
        
    Returns:
    --------
    list
        List of tuples containing (x, y, width, height) for each detected face
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
    )
    return faces
```

**Usage Example:**
```python
import cv2
from detection.face_matching import detect_faces

# Load image
image = cv2.imread('path/to/image.jpg')

# Detect faces
faces = detect_faces(image)

# Draw rectangles around detected faces
for (x, y, w, h) in faces:
    cv2.rectangle(image, (x, y), (x+w, y+h), (255, 0, 0), 2)
```

#### `align_face(img, face)`
**Description:** Aligns a detected face based on eye positions for consistent feature extraction.

```python
def align_face(img, face):
    """
    Aligns a face image based on eye landmark positions.
    
    Parameters:
    -----------
    img : numpy.ndarray
        Input image containing the face
    face : tuple
        Face bounding box (x, y, width, height)
        
    Returns:
    --------
    numpy.ndarray
        Aligned face image of size 256x256 pixels
    """
```

**Usage Example:**
```python
# Detect faces first
faces = detect_faces(image)

# Align each detected face
for face in faces:
    aligned_face = align_face(image, face)
    cv2.imshow('Aligned Face', aligned_face)
```

#### `extract_features(face)`
**Description:** Extracts facial features using DeepFace FaceNet model.

```python
def extract_features(face):
    """
    Extracts facial embeddings using DeepFace FaceNet model.
    
    Parameters:
    -----------
    face : numpy.ndarray
        Aligned face image in BGR format
        
    Returns:
    --------
    list
        Face embedding vector representing facial features
    """
```

**Usage Example:**
```python
# Extract features from aligned face
embedding = extract_features(aligned_face)
feature_vector = embedding[0]["embedding"]

# Store or compare this feature vector
print(f"Feature vector length: {len(feature_vector)}")
```

#### `match_face(embedding, database)`
**Description:** Matches a face embedding against a database of known faces.

```python
def match_face(embedding, database):
    """
    Matches input face embedding against database of known faces.
    
    Parameters:
    -----------
    embedding : list
        Face embedding vector to match
    database : dict
        Dictionary with name:embedding pairs
        
    Returns:
    --------
    str or None
        Name of matched person if similarity > threshold, None otherwise
    """
```

**Usage Example:**
```python
# Create database of known faces
database = {
    "John Doe": john_embedding,
    "Jane Smith": jane_embedding
}

# Match new face against database
match_result = match_face(new_embedding, database)
if match_result:
    print(f"Recognized: {match_result}")
else:
    print("No match found")
```

### Application Functions (`app.py`)

#### `upload_database(filename)`
**Description:** Uploads captured images to Firebase storage with validation.

```python
def upload_database(filename):
    """
    Uploads image file to Firebase storage with validation checks.
    
    Parameters:
    -----------
    filename : str
        Name of file to upload
        
    Returns:
    --------
    tuple
        (success_boolean, error_message)
    """
```

**Usage Example:**
```python
# Upload captured image
success, error = upload_database("123.png")
if success:
    print("Upload successful")
else:
    print(f"Upload failed: {error}")
```

#### `match_with_database(img, database)`
**Description:** Complete pipeline for face detection, recognition, and matching.

```python
def match_with_database(img, database):
    """
    Complete face recognition pipeline.
    
    Parameters:
    -----------
    img : numpy.ndarray
        Input image for recognition
    database : dict
        Database of known face embeddings
        
    Returns:
    --------
    str
        Recognition result message
    """
```

**Usage Example:**
```python
# Load student database
database = {
    "Student1": embedding1,
    "Student2": embedding2
}

# Recognize face in image
result = match_with_database(camera_image, database)
print(result)  # "Match found: Student1" or "No match found"
```

#### `gen_frames()`
**Description:** Generator function for video streaming from camera.

```python
def gen_frames():
    """
    Generates video frames for real-time streaming.
    
    Yields:
    -------
    bytes
        Encoded video frame in multipart format
    """
```

## Configuration Utilities

### `utils/configuration.py`

#### `load_yaml(path)`
**Description:** Loads YAML configuration files safely.

```python
def load_yaml(path):
    """
    Loads YAML configuration file.
    
    Parameters:
    -----------
    path : str
        Path to YAML file
        
    Returns:
    --------
    dict
        Parsed YAML data as Python dictionary
    """
```

**Usage Example:**
```python
from utils.configuration import load_yaml

# Load database configuration
config = load_yaml("configs/database.yaml")
teacher_hash = config["teacher"]["password_hash"]
firebase_url = config["firebase"]["databaseURL"]
```

### Password Utilities

#### `generate_password_hash.py`
**Description:** Utility script for generating secure password hashes.

```python
from werkzeug.security import generate_password_hash

# Generate hash for new password
password = "new_teacher_password"
hash_value = generate_password_hash(password)
print(f"Password hash: {hash_value}")
```

## Frontend Components

### HTML Templates

#### Student Interface Templates
- **`login.html`** - Student login form
- **`stuhome.html`** - Student dashboard with personal information
- **`select_class.html`** - Class selection for attendance
- **`selectresult.html`** - Attendance marking confirmation

#### Registration Templates  
- **`videoregister.html`** - Video capture interface for registration
- **`add_info.html`** - Student information form
- **`result.html`** - Registration success confirmation

#### Teacher Interface Templates
- **`teacher_login.html`** - Teacher authentication
- **`attendance.html`** - Attendance management dashboard

#### General Templates
- **`index.html`** - Main landing page
- **`home.html`** - General home interface
- **`takeattendance.html`** - Attendance capture interface

### Static Assets
- **`css/`** - Stylesheet files
- **`js/`** - JavaScript files  
- **`images/`** - Student profile images
- **`recognized/`** - Recognition result images
- **`fonts/`** - Web fonts
- **`webimages/`** - General web assets

## Usage Examples

### Complete Student Registration Flow

```python
# 1. Student accesses video registration
# GET /videoregister

# 2. Capture face image
# POST /capture
# - Captures image from video feed
# - Validates and uploads to Firebase storage

# 3. Add personal information
# GET /add_info
# POST /submit_info with form data:
{
    "name": "John Doe",
    "email": "john@example.com",
    "courses": "B.Tech",
    "password": "secure_password",
    "age": "20",
    "dob": "2003-01-01",
    "address": "123 Main St",
    "phone": "+1234567890",
    "city": "New York", 
    "state": "NY",
    "country": "USA",
    "pincode": "12345"
}

# 4. Face features extracted and stored
# System automatically:
# - Detects face in uploaded image
# - Aligns face for consistency
# - Extracts feature embeddings
# - Stores in Firebase with student data
```

### Attendance Marking Flow

```python
# 1. Student login
# POST /logins with credentials

# 2. Access student dashboard  
# GET /stuhome

# 3. Face recognition for attendance
# POST /recognize
# - Captures current image
# - Matches against database
# - Identifies student

# 4. Select class for attendance
# GET /select_class
# POST /select_class with selected class

# 5. Attendance marked and confirmed
# System updates attendance count in Firebase
```

### Teacher Management Flow

```python
# 1. Teacher authentication
# POST /teacher_login with password

# 2. View attendance dashboard
# GET /attendance
# - Displays all students
# - Shows attendance counts per class
# - Allows attendance management
```

### Programmatic Face Recognition

```python
import cv2
from detection.face_matching import detect_faces, align_face, extract_features, match_face

# Load and process image
image = cv2.imread('student_photo.jpg')

# Complete recognition pipeline
faces = detect_faces(image)
for face in faces:
    # Align face
    aligned = align_face(image, face)
    
    # Extract features
    embedding = extract_features(aligned)
    feature_vector = embedding[0]["embedding"]
    
    # Match against database
    database = load_student_database()
    match_result = match_face(feature_vector, database)
    
    if match_result:
        print(f"Student identified: {match_result}")
        mark_attendance(match_result, selected_class)
    else:
        print("Student not recognized")
```

## Database Schema

### Firebase Realtime Database Structure

```json
{
  "Students": {
    "1": {
      "name": "John Doe",
      "email": "john@example.com", 
      "classes": {
        "data structures": 5,
        "algorithms": 3,
        "computer networks": 7
      },
      "password": "hashed_password",
      "embeddings": [0.1, 0.2, -0.3, ...],
      "age": "20",
      "dob": "2003-01-01",
      "address": "123 Main St",
      "phone": "+1234567890",
      "city": "New York",
      "state": "NY", 
      "country": "USA",
      "pincode": "12345",
      "filename": "1",
      "course": "B.Tech"
    }
  }
}
```

### Firebase Storage Structure
```
gs://bucket-name/
├── static/
│   └── images/
│       ├── 1.png
│       ├── 2.png
│       └── ...
```

### Course-Class Mappings
```python
COURSE_CLASSES = {
    "B.Tech": ["data structures", "algorithms", "computer networks", "operating systems", "database management systems"],
    "M.Tech": ["introduction to machine learning", "deep learning", "computer vision", "natural language processing", "reinforcement learning"],
    "BBA": ["finance", "marketing", "human resources"],
    "MBA": ["human resources", "marketing", "finance", "operations management", "business analytics"],
    "BCA": ["intro to programming", "data structures", "algorithms", "computer networks", "operating systems", "database management systems"],
    "MCA": ["discrete mathematics", "data structures", "algorithms", "computer networks", "operating systems", "database management systems"],
    "B.Sc": ["mathematics", "physics", "chemistry", "biology", "computer science", "statistics"],
    "M.Sc": ["physics", "chemistry", "biology", "computer science", "statistics", "mathematics"],
    "B.Com": ["accounting", "finance", "economics", "business law", "marketing"]
}
```

## Error Handling

### Common Error Scenarios

1. **Face Detection Failures**
```python
try:
    faces = detect_faces(image)
    if len(faces) == 0:
        return "No face detected"
except Exception as e:
    return f"Face detection error: {str(e)}"
```

2. **Database Upload Errors**  
```python
# File already exists
if storage.bucket().get_blob(filename):
    error = f"{filename} already exists in the database"
    
# Invalid filename
if not filename[:-4].isdigit():
    error = f"Filename must be numeric: {filename}"
```

3. **Authentication Failures**
```python
# Invalid credentials
if not check_password_hash(TEACHER_PASSWORD_HASH, password):
    flash("Incorrect password")
    
# Student not found
if 'email' not in session:
    return redirect(url_for('login'))
```

## Security Considerations

1. **Password Security**: Uses Werkzeug's secure password hashing
2. **Session Management**: Flask sessions for user authentication  
3. **File Upload Security**: Validates filenames and checks for duplicates
4. **Firebase Security**: Uses service account authentication
5. **Input Validation**: Form data validation and sanitization

## Performance Optimization

1. **Face Recognition**: Uses efficient FaceNet embeddings for fast matching
2. **Video Streaming**: Optimized frame encoding for real-time video
3. **Database Queries**: Efficient Firebase queries with indexing
4. **Image Processing**: OpenCV optimizations for face detection

This documentation covers all public APIs, functions, and components in the Intelligent Face Recognition Attendance System. Each section includes detailed parameter descriptions, return values, and practical usage examples to help developers understand and integrate with the system effectively.