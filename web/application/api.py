from flask          import request
from application    import app
from data.repo      import Repository
from data           import auth
from flask          import jsonify

# API RESOURCE PATTERN

# GET         /data/get/<id>    get data data by id
# GET         /data/get/all     get data list
# POST        /data/upsert/     upsert data
# POST        /data/delete/     delete data

R = Repository()
cm_util = R.get_common_util()

@auth.verify_password
def authenticate(username, password):
    if username and password:
        if username == 'hifi' and password == 'hifi':
            return True
        else:
            return False
            
# Routes for CRUD Operations
models = {
    "user":         (cm_util.User,          ["name", "email", "phone", "password", "role"]),
    "vehicle":      (cm_util.Vehicle,       ["user_id", "plate_number", "model", "type"]),
    "appointment":  (cm_util.Appointment,   ["user_id", "vehicle_id", "service_type", "appointment_date"]),
    "payment":      (cm_util.Payment,       ["appointment_id", "amount", "payment_method", "transaction_date"]),
    "notification": (cm_util.Notification,  ["user_id", "message", "created_at"]),
    "loyalty":      (cm_util.Loyalty,       ["user_id", "points", "reward_status"]),
    "service":      (cm_util.Service,       ["name", "description", "price", "duration"]),
    "queue":        (cm_util.Queue,         ["appointment_id", "position"]),
    "staff":        (cm_util.Staff,         ["name", "role", "phone", "email"]),
    "feedback":     (cm_util.Feedback,      ["user_id", "appointment_id", "rating", "created_at"])
}

def register_routes(model_name, model, required_fields):

    @app.route(f'/api/{model_name}', methods=['POST'], endpoint=f'create_{model_name}')
    # @login_required
    def create(model=model):
        return cm_util.create_record(model, request.json, required_fields)

    @app.route(f'/api/{model_name}', methods=['GET'], endpoint=f'readall_{model_name}')
    # @login_required
    def readall(model=model):
        return cm_util.read_records(model)

    @app.route(f'/api/{model_name}/<int:id>', methods=['GET'], endpoint=f'read_{model_name}')
    # @login_required
    def read(id, model=model):
        return cm_util.read_record(model, id)

    @app.route(f'/api/{model_name}/<int:id>', methods=['PUT'], endpoint=f'update_{model_name}')
    # @login_required
    def update(id, model=model):
        return cm_util.update_record(model, id, request.json)

    @app.route(f'/api/{model_name}/<int:id>', methods=['DELETE'], endpoint=f'delete_{model_name}')
    # @login_required
    def delete(id, model=model):
        return cm_util.delete_record(model, id)

for model_name, (model, required_fields) in models.items():
    register_routes(model_name, model, required_fields)

# ==================================================================================
# FACTORY

# Call functions to generate data
@app.route(f'/api/factory', methods=['GET'], endpoint=f'factory')
def factory():
    R.start_factory()
    return jsonify({"message": "Dummy Data Created."})
