# from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
# from werkzeug.security import generate_password_hash, check_password_hash
# from models import db, User, Camera
# import os
# import time
# import base64
# from threading import Lock

# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///camera_app.db'
# app.config['SECRET_KEY'] = 'your_secret_key'
# db.init_app(app)

# # Constants for Image Processing
# STATIC_IMAGE_FOLDER = 'static/images'
# client_states = {}
# status_lock = Lock()

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         business_name = request.form['business_name']
#         address = request.form['address']
#         username = request.form['username']
#         password = generate_password_hash(request.form['password'], method='sha256')

#         user = User.query.filter_by(username=username).first()
#         if user:
#             flash('Username already exists!')
#             return redirect(url_for('register'))

#         new_user = User(business_name=business_name, address=address, username=username, password=password)
#         db.session.add(new_user)
#         db.session.commit()
#         flash('Registration successful! Please log in.')
#         return redirect(url_for('login'))
#     return render_template('register.html')

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']

#         user = User.query.filter_by(username=username).first()
#         if user and check_password_hash(user.password, password):
#             session['user_id'] = user.id
#             session['username'] = user.username
#             return redirect(url_for('dashboard'))
#         flash('Invalid username or password!')
#     return render_template('login.html')

# @app.route('/dashboard')
# def dashboard():
#     if 'user_id' not in session:
#         flash('Please log in to access the dashboard!', 'warning')
#         return redirect(url_for('login'))
    
#     user_id = session['user_id']
#     user = User.query.get(user_id)
#     cameras = Camera.query.filter_by(user_id=user_id).all()
#     return render_template('dashboard.html', user=user, cameras=cameras)

# @app.route('/add_camera', methods=['GET', 'POST'])
# def add_camera():
#     if 'user_id' not in session:
#         flash('Please log in to access this page!', 'warning')
#         return redirect(url_for('login'))
    
#     if request.method == 'POST':
#         camera_name = request.form['camera_name']
#         threshold = request.form['threshold']
#         user_id = session['user_id']

#         new_camera = Camera(name=camera_name, threshold=threshold, user_id=user_id)
#         db.session.add(new_camera)
#         db.session.commit()

#         flash('Camera added successfully!', 'success')
#         return redirect(url_for('dashboard'))

#     return render_template('add_camera.html')

# @app.route('/update_camera/<int:camera_id>', methods=['GET', 'POST'])
# def update_camera(camera_id):
#     if 'user_id' not in session:
#         flash('Please log in to access this page!', 'warning')
#         return redirect(url_for('login'))
    
#     camera = Camera.query.get_or_404(camera_id)
#     if camera.user_id != session['user_id']:
#         flash('Unauthorized access!', 'danger')
#         return redirect(url_for('dashboard'))
    
#     if request.method == 'POST':
#         camera.name = request.form['camera_name']
#         camera.threshold = request.form['threshold']
#         db.session.commit()
#         flash('Camera updated successfully!', 'success')
#         return redirect(url_for('dashboard'))

#     return render_template('update_camera.html', camera=camera)

# @app.route('/delete_camera/<int:camera_id>', methods=['POST'])
# def delete_camera(camera_id):
#     if 'user_id' not in session:
#         flash('Please log in to access this page!', 'warning')
#         return redirect(url_for('login'))
    
#     camera = Camera.query.get_or_404(camera_id)
#     if camera.user_id != session['user_id']:
#         flash('Unauthorized access!', 'danger')
#         return redirect(url_for('dashboard'))
    
#     db.session.delete(camera)
#     db.session.commit()
#     flash('Camera deleted successfully!', 'success')
#     return redirect(url_for('dashboard'))

# @app.route('/logout')
# def logout():
#     session.clear()
#     return redirect(url_for('index'))

# # Start and Stop Capture Routes
# @app.route('/start_capture/<client_id>', methods=['POST'])
# def start_capture(client_id):
#     global client_states
#     with status_lock:
#         client_states[client_id] = 'start'
#     return jsonify({'status': f'Capture started for {client_id}'})

# @app.route('/stop_capture/<client_id>', methods=['POST'])
# def stop_capture(client_id):
#     global client_states
#     with status_lock:
#         client_states[client_id] = 'stop'
#     return jsonify({'status': f'Capture stopped for {client_id}'})

# @app.route('/get_capture_status/<client_id>', methods=['GET'])
# def get_capture_status(client_id):
#     global client_states
#     with status_lock:
#         return jsonify({'command': client_states.get(client_id, 'stop')})

# # Image Handling Routes
# @app.route('/receive_alert/<client_id>', methods=['POST'])
# def receive_alert(client_id):
#     data = request.json
#     img_data = base64.b64decode(data['image'])

#     client_folder = os.path.join(STATIC_IMAGE_FOLDER, client_id)
#     os.makedirs(client_folder, exist_ok=True)

#     # Save the image
#     timestamp = int(time.time())
#     image_filename = f"{timestamp}.jpg"
#     image_path = os.path.join(client_folder, image_filename)
#     with open(image_path, "wb") as img_file:
#         img_file.write(img_data)

#     return jsonify({"status": "Image received!"})

# @app.route('/get_images/<client_id>', methods=['GET'])
# def get_images(client_id):
#     client_folder = os.path.join(STATIC_IMAGE_FOLDER, client_id)

#     if not os.path.exists(client_folder):
#         return jsonify([])

#     images = []
#     for img_file in sorted(os.listdir(client_folder)):
#         if img_file.endswith(".jpg"):
#             image_id = img_file.split('.')[0]  # Using timestamp as a unique id
#             image_path = f'/static/images/{client_id}/{img_file}'
#             timestamp = int(image_id)
#             readable_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
#             message = f"Empty space detected! by {client_id}"
#             images.append({
#                 "id": image_id,  # Include the id for deletion
#                 "image": image_path,
#                 "message": message,
#                 "time": readable_time
#             })

#     return jsonify(images)

# @app.route('/delete_images/<client_id>', methods=['POST'])
# def delete_images(client_id):
#     data = request.json
#     deleted_files = []

#     for image_id in data['filenames']:
#         filename = f"{image_id}.jpg"  # Assuming images are named by timestamp
#         image_path = os.path.join(STATIC_IMAGE_FOLDER, client_id, filename)
#         print(image_path)
#         if os.path.exists(image_path):
#             os.remove(image_path)
#             deleted_files.append(filename)

#     return jsonify({"status": "Images deleted successfully", "deleted": deleted_files})

# if __name__ == '__main__':
#     app.run(debug=True)


from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Camera
import os
import time
import base64
from threading import Lock

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///camera_app.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db.init_app(app)

# Constants for Image Processing
STATIC_IMAGE_FOLDER = 'static/images'
client_states = {}
status_lock = Lock()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        business_name = request.form['business_name']
        address = request.form['address']
        username = request.form['username']
        password = generate_password_hash(request.form['password'], method='sha256')

        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists!')
            return redirect(url_for('register'))

        new_user = User(business_name=business_name, address=address, username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('dashboard'))
        flash('Invalid username or password!')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in to access the dashboard!', 'warning')
        return redirect(url_for('login'))

    user_id = session['user_id']
    user = User.query.get(user_id)
    cameras = Camera.query.filter_by(user_id=user_id).all()
    return render_template('dashboard.html', user=user, cameras=cameras)

@app.route('/add_camera', methods=['GET', 'POST'])
def add_camera():
    if 'user_id' not in session:
        flash('Please log in to access this page!', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        camera_name = request.form['camera_name']
        threshold = request.form['threshold']
        user_id = session['user_id']

        new_camera = Camera(name=camera_name, threshold=threshold, user_id=user_id)
        db.session.add(new_camera)
        db.session.commit()

        flash('Camera added successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('add_camera.html')

@app.route('/update_camera/<int:camera_id>', methods=['GET', 'POST'])
def update_camera(camera_id):
    if 'user_id' not in session:
        flash('Please log in to access this page!', 'warning')
        return redirect(url_for('login'))

    camera = Camera.query.get_or_404(camera_id)
    if camera.user_id != session['user_id']:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        camera.name = request.form['camera_name']
        camera.threshold = request.form['threshold']
        db.session.commit()
        flash('Camera updated successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('update_camera.html', camera=camera)

@app.route('/delete_camera/<int:camera_id>', methods=['POST'])
def delete_camera(camera_id):
    if 'user_id' not in session:
        flash('Please log in to access this page!', 'warning')
        return redirect(url_for('login'))

    camera = Camera.query.get_or_404(camera_id)
    if camera.user_id != session['user_id']:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('dashboard'))

    db.session.delete(camera)
    db.session.commit()
    flash('Camera deleted successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# Start and Stop Capture Routes
@app.route('/start_capture/<client_id>', methods=['POST'])
def start_capture(client_id):
    global client_states
    with status_lock:
        client_states[client_id] = 'start'
    return jsonify({'status': f'Capture started for {client_id}'})

@app.route('/stop_capture/<client_id>', methods=['POST'])
def stop_capture(client_id):
    global client_states
    with status_lock:
        client_states[client_id] = 'stop'
    return jsonify({'status': f'Capture stopped for {client_id}'})

@app.route('/get_capture_status/<client_id>', methods=['GET'])
def get_capture_status(client_id):
    global client_states
    with status_lock:
        return jsonify({'command': client_states.get(client_id, 'stop')})

# Image Handling Routes
@app.route('/receive_alert/<client_id>', methods=['POST'])
def receive_alert(client_id):
    data = request.json
    img_data = base64.b64decode(data['image'])

    client_folder = os.path.join(STATIC_IMAGE_FOLDER, client_id)
    os.makedirs(client_folder, exist_ok=True)

    # Save the image
    timestamp = int(time.time())
    image_filename = f"{timestamp}.jpg"
    image_path = os.path.join(client_folder, image_filename)
    with open(image_path, "wb") as img_file:
        img_file.write(img_data)

    return jsonify({"status": "Image received!"})

@app.route('/get_images/<client_id>', methods=['GET'])
def get_images(client_id):
    client_folder = os.path.join(STATIC_IMAGE_FOLDER, client_id)

    if not os.path.exists(client_folder):
        return jsonify([])

    images = []
    for img_file in sorted(os.listdir(client_folder)):
        if img_file.endswith(".jpg"):
            image_id = img_file.split('.')[0]  # Using timestamp as a unique id
            image_path = f'/static/images/{client_id}/{img_file}'
            timestamp = int(image_id)
            readable_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
            message = f"Empty space detected! by {client_id}"
            images.append({
                "cid": client_id, # me taking the client id 
                "id": image_id,  # Include the id for deletion
                "image": image_path,
                "message": message,
                "time": readable_time
            })

    return jsonify(images)

@app.route('/delete_images/<cid>/<image_id>', methods=['GET'])
def delete_images(cid,image_id):
    # data = request.json
    deleted_files = []

    # for image_id in data['filenames']:
    filename = f"{image_id}.jpg"  # Assuming images are named by timestamp
    image_path = os.path.join(STATIC_IMAGE_FOLDER, cid, filename)
    print(image_path)
    if os.path.exists(image_path):
        os.remove(image_path)
        deleted_files.append(filename)

    return jsonify({"status": "Images deleted successfully", "deleted": deleted_files})

if __name__ == '__main__':
    app.run(debug=True)
