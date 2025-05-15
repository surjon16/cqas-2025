from data                   import db
from data                   import login_manager
from flask_login            import UserMixin
from werkzeug.security      import generate_password_hash, check_password_hash
 
class User(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    name            = db.Column(db.String(100), nullable=False)
    phone           = db.Column(db.String(20), unique=True, nullable=False)
    email           = db.Column(db.String(100), unique=True, nullable=False)
    password_hash   = db.Column(db.String(255), nullable=False)
    role            = db.Column(db.String(20), nullable=False, default='customer') # customer / guest
    image_profile   = db.Column(db.String(128), default="img/no-photo.jpg")
    created_at      = db.Column(db.DateTime, nullable=False)
    updated_at      = db.Column(db.DateTime, nullable=False)
 
    @property 
    def password(self):
        """
        Prevent pasword from being accessed
        """
        raise AttributeError('password is not a readable attribute.')

    @password.setter
    def password(self, password):
        """
        Set password to a hashed password
        """
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """
        Check if hashed password matches actual password
        """
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id"            : self.id,
            "name"          : self.name,
            "email"         : self.email,
            "phone"         : self.phone,
            "role"          : self.role
        }

class Vehicle(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    user_id         = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    plate_number    = db.Column(db.String(20), unique=True, nullable=False)
    model           = db.Column(db.String(100), nullable=False)
    type            = db.Column(db.String(50), nullable=False)
    created_at      = db.Column(db.DateTime, nullable=False)
    updated_at      = db.Column(db.DateTime, nullable=False)

    def to_dict(self):
        return {
            "id"            : self.id,
            "user_id"       : self.user_id,
            "plate_number"  : self.plate_number,
            "model"         : self.model,
            "type"          : self.type
        }

class Appointment(db.Model):
    id                  = db.Column(db.Integer, primary_key=True)
    user_id             = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    staff_id            = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)
    vehicle_id          = db.Column(db.Integer, db.ForeignKey('vehicle.id'), nullable=False)
    service_type        = db.Column(db.String(100), nullable=False)
    appointment_date    = db.Column(db.DateTime, nullable=False)
    status              = db.Column(db.String(50), default='Pending')
    payment_status      = db.Column(db.String(50), default='Unpaid') # To be confirmed by staff
    created_at          = db.Column(db.DateTime, nullable=False)
    updated_at          = db.Column(db.DateTime, nullable=False)

    def to_dict(self):
        return {
            "id"                : self.id,
            "user_id"           : self.user_id,
            "vehicle_id"        : self.vehicle_id,
            "service_type"      : self.service_type,
            "appointment_date"  : self.appointment_date.isoformat(),
            "status"            : self.status,
            "payment_status"    : self.payment_status
        }

class Payment(db.Model):
    id                  = db.Column(db.Integer, primary_key=True)
    appointment_id      = db.Column(db.Integer, db.ForeignKey('appointment.id'), nullable=False)
    amount              = db.Column(db.Float, nullable=False)
    payment_method      = db.Column(db.String(50), nullable=False)
    payment_status      = db.Column(db.String(50), default='Pending') # To be confirmed by app if actual payment was processed
    transaction_date    = db.Column(db.DateTime, nullable=False)
    receipt_filename    = db.Column(db.String(255), nullable=True)  # New column for storing the filename of the receipt image
    created_at          = db.Column(db.DateTime, nullable=False)
    updated_at          = db.Column(db.DateTime, nullable=False)

    def to_dict(self):
        return {
            "id"                : self.id,
            "appointment_id"    : self.appointment_id,
            "amount"            : self.amount,
            "payment_method"    : self.payment_method,
            "payment_status"    : self.payment_status,
            "transaction_date"  : self.transaction_date.isoformat(),
            "receipt_filename"  : self.receipt_filename,
            "receipt_url"       : f"/uploads/receipts/{self.receipt_filename}" if self.receipt_filename else None
        }

class Notification(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message     = db.Column(db.String(255), nullable=False)
    status      = db.Column(db.String(50), default='Unread')
    created_at  = db.Column(db.DateTime, nullable=False)
    updated_at  = db.Column(db.DateTime, nullable=False)

    user = db.relationship('User', backref=db.backref('notifications', lazy=True))

    def to_dict(self):
        return {
            "id"        : self.id,
            "user_id"   : self.user_id,
            "message"   : self.message,
            "status"    : self.status,
            "created_at": self.created_at.isoformat()
        }

class Loyalty(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    user_id         = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    points_earned   = db.Column(db.Integer, default=0)
    points_spent    = db.Column(db.Integer, default=0)
    reward_status   = db.Column(db.String(50), default='Available')
    created_at      = db.Column(db.DateTime, nullable=False)
    updated_at      = db.Column(db.DateTime, nullable=False)

    user = db.relationship('User', backref=db.backref('loyalties', lazy=True))

    def to_dict(self):
        return {
            "id"            : self.id,
            "user_id"       : self.user_id,
            "points_earned" : self.points_earned,
            "points_spent"  : self.points_spent,
            "reward_status" : self.reward_status,
            "updated_at"    : self.updated_at.isoformat()
        }

class Service(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    price       = db.Column(db.Float, nullable=False)
    duration    = db.Column(db.Integer, nullable=False)  # Duration in minutes
    created_at  = db.Column(db.DateTime, nullable=False)
    updated_at  = db.Column(db.DateTime, nullable=False)

    def to_dict(self):
        return {
            "id"            : self.id,
            "name"          : self.name,
            "description"   : self.description,
            "price"         : self.price,
            "duration"      : self.duration
        }

class Queue(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    appointment_id  = db.Column(db.Integer, db.ForeignKey('appointment.id'), nullable=False)
    position        = db.Column(db.Integer, nullable=False)
    status          = db.Column(db.String(50), default='Waiting') 
    created_at      = db.Column(db.DateTime, nullable=False)
    updated_at      = db.Column(db.DateTime, nullable=False)

    def to_dict(self):
        return {
            "id"            : self.id,
            "appointment_id": self.appointment_id,
            "position"      : self.position,
            "status"        : self.status
        }

class Staff(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(100), nullable=False)
    role        = db.Column(db.String(50), nullable=False) # 'Admin', 'Cashier', 'Manager', 'Washer', 'Cleaner'
    phone       = db.Column(db.String(20), nullable=True)
    email       = db.Column(db.String(100), nullable=True)
    created_at  = db.Column(db.DateTime, nullable=False)
    updated_at  = db.Column(db.DateTime, nullable=False)

    def to_dict(self):
        return {
            "id"    : self.id,
            "name"  : self.name,
            "role"  : self.role,
            "email" : self.email,
            "phone" : self.phone
        }

class Feedback(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    user_id         = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    appointment_id  = db.Column(db.Integer, db.ForeignKey('appointment.id'), nullable=False)
    rating          = db.Column(db.Integer, nullable=False)
    comment         = db.Column(db.String(255))
    created_at      = db.Column(db.DateTime, nullable=False)
    updated_at      = db.Column(db.DateTime, nullable=False)

    user        = db.relationship('User', backref=db.backref('feedback', lazy=True))
    appointment = db.relationship('Appointment', backref=db.backref('feedback', lazy=True))

    def to_dict(self):
        return {
            "id"            : self.id,
            "user_id"       : self.user_id,
            "appointment_id": self.appointment_id,
            "rating"        : self.rating,
            "comment"       : self.comment
        }

# ============================================================================================
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))
