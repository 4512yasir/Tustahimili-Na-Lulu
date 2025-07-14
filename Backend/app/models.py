from . import db
from datetime import datetime

# -------------------- Person, Role, User --------------------
class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    emergency_contact = db.Column(db.String(20))
    
    users = db.relationship('User', backref='person', lazy=True, cascade="all, delete-orphan")
    contributions = db.relationship('Contribution', backref='person', lazy=True, cascade="all, delete-orphan")
    loans = db.relationship('Loan', backref='person', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Person {self.full_name}>"


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return f"<Role {self.name}>"


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)

    role = db.relationship('Role')
    notifications = db.relationship('Notification', backref='user', lazy=True, cascade="all, delete-orphan")
    meetings_created = db.relationship('Meeting', backref='creator', lazy=True)
    minutes_written = db.relationship('Minute', backref='writer', lazy=True)

    def __repr__(self):
        return f"<User {self.email} - Role: {self.role.name}>"

# -------------------- Contributions --------------------
class Contribution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, default=datetime.utcnow)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    receipt_code = db.Column(db.String(50), nullable=True)

    def __repr__(self):
        return f"<Contribution {self.amount} by Person ID {self.person_id}>"

# -------------------- Loans --------------------
class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    purpose = db.Column(db.String(100))
    request_date = db.Column(db.DateTime, default=datetime.utcnow)
    approved = db.Column(db.Boolean, default=False)
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    status = db.Column(db.String(30), default="pending")
    due_date = db.Column(db.Date)
    interest = db.Column(db.Float, default=0.0)  # Added for reporting
    repayment_amount = db.Column(db.Float, default=0.0)  # Added for reporting
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)

    def __repr__(self):
        return f"<Loan {self.amount} to Person ID {self.person_id}>"

# -------------------- Meetings --------------------
class Meeting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(150))
    description = db.Column(db.String(300))
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    minutes = db.relationship('Minute', backref='meeting', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Meeting on {self.date} at {self.location}>"


class Minute(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    meeting_id = db.Column(db.Integer, db.ForeignKey('meeting.id'), nullable=False)
    written_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Minute for Meeting ID {self.meeting_id}>"

# -------------------- Notifications --------------------
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Notification to User ID {self.user_id}>"

# -------------------- Property & Rent --------------------
class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)           
    location = db.Column(db.String(200), nullable=True)         
    monthly_rent = db.Column(db.Float, nullable=False)          
    is_occupied = db.Column(db.Boolean, default=True)
    tenant_name = db.Column(db.String(100), nullable=True)
    tenant_phone = db.Column(db.String(20), nullable=True)

    rent_payments = db.relationship('RentPayment', backref='property', lazy=True, cascade="all, delete-orphan")
    maintenance_requests = db.relationship('MaintenanceRequest', backref='property', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Property {self.name} - KES {self.monthly_rent}>"


class RentPayment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.Date, default=datetime.utcnow)
    payment_method = db.Column(db.String(50), nullable=False, default="M-Pesa")
    receipt_code = db.Column(db.String(50), nullable=True)
    notes = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return f"<RentPayment {self.amount} for Property ID {self.property_id}>"

# -------------------- Maintenance Requests --------------------
class MaintenanceRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('property.id'), nullable=False)
    issue_description = db.Column(db.String(255), nullable=False)
    reported_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default="Pending")  # Pending, In Progress, Resolved
    resolved_date = db.Column(db.DateTime, nullable=True)
    resolution_notes = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f"<MaintenanceRequest for Property ID {self.property_id}>"
