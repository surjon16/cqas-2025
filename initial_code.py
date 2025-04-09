import datetime
import os
from functools import wraps
from faker import Faker
from flask import Flask, request, jsonify, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_session import Session
from flask_uploads import UploadSet, IMAGES, configure_uploads
from random import randint, choice
from werkzeug.utils import secure_filename

fake = Faker()
app = Flask(__name__)

# Database Configuration
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://username:password@localhost/carwash_db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@localhost/carwash_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SESSION_TYPE'] = 'filesystem'

# Set the path to save images
app.config['UPLOADED_IMAGES_DEST'] = 'uploads/receipts'  # Directory where images will be stored
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Setup Flask-Uploads
images = UploadSet('images', IMAGES)
configure_uploads(app, images)

Session(app)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='customer')
    loyalty_points = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)
 
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "role": self.role,
            "loyalty_points": self.loyalty_points
        }

class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    plate_number = db.Column(db.String(20), unique=True, nullable=False)
    model = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "plate_number": self.plate_number,
            "model": self.model,
            "type": self.type
        }

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'), nullable=False)
    service_type = db.Column(db.String(100), nullable=False)
    appointment_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), default='Pending')
    payment_status = db.Column(db.String(50), default='Unpaid')
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "vehicle_id": self.vehicle_id,
            "service_type": self.service_type,
            "appointment_date": self.appointment_date.isoformat(),
            "status": self.status,
            "payment_status": self.payment_status
        }

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    payment_status = db.Column(db.String(50), default='Pending')
    transaction_date = db.Column(db.DateTime, nullable=False)
    receipt_filename = db.Column(db.String(255), nullable=True)  # New column for storing the filename of the receipt image
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "appointment_id": self.appointment_id,
            "amount": self.amount,
            "payment_method": self.payment_method,
            "payment_status": self.payment_status,
            "transaction_date": self.transaction_date.isoformat(),
            "receipt_filename": self.receipt_filename,
            "receipt_url": f"/uploads/receipts/{self.receipt_filename}" if self.receipt_filename else None
        }

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), default='Unread')
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)

    user = db.relationship('User', backref=db.backref('notifications', lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "message": self.message,
            "status": self.status,
            "created_at": self.created_at.isoformat()
        }

class Loyalty(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    points_earned = db.Column(db.Integer, default=0)
    points_spent = db.Column(db.Integer, default=0)
    reward_status = db.Column(db.String(50), default='Available')
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)

    user = db.relationship('User', backref=db.backref('loyalties', lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "points_earned": self.points_earned,
            "points_spent": self.points_spent,
            "reward_status": self.reward_status,
            "updated_at": self.updated_at.isoformat()
        }

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # Duration in minutes
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "duration": self.duration
        }

class Queue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'), nullable=False)
    position = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), default='Waiting') 
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "appointment_id": self.appointment_id,
            "position": self.position,
            "status": self.status
        }

class Staff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    assigned_service = db.Column(db.Integer, db.ForeignKey('service.id'))
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "email": self.email,
            "phone": self.phone
        }

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)

    user = db.relationship('User', backref=db.backref('feedback', lazy=True))
    appointment = db.relationship('Appointment', backref=db.backref('feedback', lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "appointment_id": self.appointment_id,
            "rating": self.rating,
            "comment": self.comment
        }

# Authentication Middleware 
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"error": "Unauthorized access, please log in"}), 401
        return f(*args, **kwargs)
    return decorated_function

# Validation Helper
def validate_fields(data, required_fields):
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return {"error": f"Missing fields: {', '.join(missing_fields)}"}, 400
    return None

# CRUD Helpers
def create_record(model, data, required_fields):
    validation_error = validate_fields(data, required_fields)
    if validation_error:
        return validation_error
    record = model(**data)
    db.session.add(record)
    db.session.commit()
    return jsonify({"message": f"{model.__name__} created successfully"})

def read_records(model):
    records = model.query.all()
    return jsonify([record.to_dict() for record in records])

def read_record(model, id):
    record = model.query.get_or_404(id)
    return jsonify(record.to_dict())

def update_record(model, id, data):
    record = model.query.get_or_404(id)
    for key, value in data.items():
        setattr(record, key, value)
    db.session.commit()
    return jsonify({"message": f"{model.__name__} updated successfully"})

def delete_record(model, id):
    record = model.query.get_or_404(id)
    db.session.delete(record)
    db.session.commit()
    return jsonify({"message": f"{model.__name__} deleted successfully"})

# Auth Routes
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data.get('email')).first()
    if user and bcrypt.check_password_hash(user.password, data.get('password')):
        session['user_id'] = user.id
        return jsonify({"message": "Login successful"})
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({"message": "Logout successful"})

# Routes for CRUD Operations
models = {
    "user":         (User,          ["name", "email", "phone", "password", "role"]),
    "vehicle":      (Vehicle,       ["user_id", "plate_number", "model", "type"]),
    "appointment":  (Appointment,   ["user_id", "vehicle_id", "service_type", "appointment_date"]),
    "payment":      (Payment,       ["appointment_id", "amount", "payment_method", "transaction_date"]),
    "notification": (Notification,  ["user_id", "message", "created_at"]),
    "loyalty":      (Loyalty,       ["user_id", "points", "reward_status"]),
    "service":      (Service,       ["name", "description", "price", "duration"]),
    "queue":        (Queue,         ["appointment_id", "position"]),
    "staff":        (Staff,         ["name", "role", "phone", "email"]),
    "feedback":     (Feedback,      ["user_id", "appointment_id", "rating", "created_at"])
}

def register_routes(model_name, model, required_fields):

    @app.route(f'/{model_name}', methods=['POST'], endpoint=f'create_{model_name}')
    # @login_required
    def create(model=model):
        return create_record(model, request.json, required_fields)

    @app.route(f'/{model_name}', methods=['GET'], endpoint=f'readall_{model_name}')
    # @login_required
    def readall(model=model):
        return read_records(model)

    @app.route(f'/{model_name}/<int:id>', methods=['GET'], endpoint=f'read_{model_name}')
    # @login_required
    def read(id, model=model):
        return read_record(model, id)

    @app.route(f'/{model_name}/<int:id>', methods=['PUT'], endpoint=f'update_{model_name}')
    # @login_required
    def update(id, model=model):
        return update_record(model, id, request.json)

    @app.route(f'/{model_name}/<int:id>', methods=['DELETE'], endpoint=f'delete_{model_name}')
    # @login_required
    def delete(id, model=model):
        return delete_record(model, id)

for model_name, (model, required_fields) in models.items():
    register_routes(model_name, model, required_fields)

# IMAGE UPLOADS
@app.route('/payments/<int:payment_id>/upload_receipt', methods=['POST'])
@login_required
def upload_receipt(payment_id):
    payment = Payment.query.get(payment_id)
    if not payment:
        return jsonify({"error": "Payment not found"}), 404
    
    # Check if the request contains a file
    if 'receipt' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['receipt']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    # Ensure the file has an allowed extension
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)  # Secure the filename to prevent security risks
        file_path = os.path.join(app.config['UPLOADED_IMAGES_DEST'], filename)
        
        # Save the file to the designated folder
        file.save(file_path)

        # Update the payment record with the filename
        payment.receipt_filename = filename
        db.session.commit()

        return jsonify({"message": "Receipt uploaded successfully", "filename": filename})

    return jsonify({"error": "Invalid file format. Only image files are allowed."}), 400

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/uploads/receipts/<filename>', methods=['GET'])
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOADED_IMAGES_DEST'], filename)

# FACTORY / DUMMY
def create_dummy_users():
    users = []
    for _ in range(10):
        user = User(
            name=fake.name(),
            email=fake.email(),
            phone=fake.phone_number(),
            password=fake.password(),
            role=choice(['customer', 'admin']),
            loyalty_points=randint(0, 100)
        )
        users.append(user)
    db.session.bulk_save_objects(users)
    db.session.commit()

def create_dummy_vehicles():
    vehicles = []
    users = User.query.all()  # Get all users from the database
    for _ in range(10):
        vehicle = Vehicle(
            user_id=choice(users).id,
            plate_number=fake.license_plate(),
            model=fake.word(),
            type=choice(['Sedan', 'SUV', 'Truck', 'Van'])
        )
        vehicles.append(vehicle)
    db.session.bulk_save_objects(vehicles)
    db.session.commit()

def create_dummy_appointments():
    appointments = []
    vehicles = Vehicle.query.all()
    users = User.query.all()
    for _ in range(10):
        appointment = Appointment(
            user_id=choice(users).id,
            vehicle_id=choice(vehicles).id,
            service_type=choice(['Full Wash', 'Exterior Wash', 'Interior Clean', 'Detailing']),
            appointment_date=fake.date_time_this_year(),
            status=choice(['Pending', 'Completed', 'Cancelled']),
            payment_status=choice(['Paid', 'Unpaid'])
        )
        appointments.append(appointment)
    db.session.bulk_save_objects(appointments)
    db.session.commit()

def create_dummy_payments():
    payments = []
    appointments = Appointment.query.all()
    for _ in range(10):
        payment = Payment(
            appointment_id=choice(appointments).id,
            amount=randint(50, 150),
            payment_method=choice(['Cash', 'Card', 'Online']),
            payment_status=choice(['Pending', 'Paid']),
            transaction_date=fake.date_time_this_year()
        )
        payments.append(payment)
    db.session.bulk_save_objects(payments)
    db.session.commit()

def create_dummy_notifications():
    notifications = []
    users = User.query.all()
    for _ in range(10):
        notification = Notification(
            user_id=choice(users).id,
            message=fake.sentence(),
            status=choice(["Unread", "Read"]),
            created_at=fake.date_time_this_year()
        )
        notifications.append(notification)
    db.session.bulk_save_objects(notifications)
    db.session.commit()

def create_dummy_loyalties():
    loyalties = []
    users = User.query.all()
    for _ in range(10):
        loyalty = Loyalty(
            user_id=choice(users).id,
            points_earned=randint(10, 50),
            points_spent=randint(0, 20),
            updated_at=fake.date_time_this_year() 
        )
        loyalties.append(loyalty) 
    db.session.bulk_save_objects(loyalties)
    db.session.commit()

def create_dummy_services():
    services = []
    for _ in range(10):
        service = Service(
            name=choice(['Full Wash', 'Exterior Wash', 'Interior Clean', 'Detailing']),
            description=fake.sentence(),
            price=randint(20, 100)
        )
        services.append(service)
    db.session.bulk_save_objects(services)
    db.session.commit()

def create_dummy_queues():
    queues = []
    appointments = Appointment.query.all()
    for _ in range(10):
        queue = Queue(
            appointment_id=choice(appointments).id,
            position=randint(1, 20),
        )
        queues.append(queue)
    db.session.bulk_save_objects(queues)
    db.session.commit()

def create_dummy_staff():
    staff = []
    for _ in range(10):
        staff_member = Staff(
            name=fake.name(),
            role=choice(['Manager', 'Washer', 'Cleaner']),
        ) 
        staff.append(staff_member)
    db.session.bulk_save_objects(staff)
    db.session.commit()

def create_dummy_feedbacks():
    feedbacks = []
    users = User.query.all()
    appointments = Appointment.query.all()
    for _ in range(10):
        feedback = Feedback(
            user_id=choice(users).id,
            appointment_id=choice(appointments).id,
            rating=randint(1, 5),
            comment=fake.sentence(),
            created_at=fake.date_time_this_year()
        )
        feedbacks.append(feedback)
    db.session.bulk_save_objects(feedbacks)
    db.session.commit()

# Call functions to generate data
@app.route(f'/factory', methods=['GET'], endpoint=f'factory')
def factory():
    create_dummy_users()
    create_dummy_vehicles()
    create_dummy_appointments()
    create_dummy_payments()
    create_dummy_notifications()
    create_dummy_loyalties()
    create_dummy_services()
    create_dummy_queues()
    create_dummy_staff()
    create_dummy_feedbacks()

    return jsonify({"message": "Dummy Data Created."})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
