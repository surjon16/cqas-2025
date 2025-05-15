from data           import db
from data.models    import User, Vehicle, Appointment, Payment, Notification, Loyalty, Service, Queue, Staff, Feedback
from flask          import jsonify

# class CommonRepo:

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
