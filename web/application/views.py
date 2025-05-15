from flask          import flash, jsonify, render_template, request, redirect, url_for, session, send_file
from flask_login    import login_required, login_user, logout_user, current_user
from application    import app
from data.repo      import Repository
from data.schemas   import RegisterAccountSchema, RegisterStudentAccountSchema, SetStudentAppointmentSchema, SetGuestAppointmentSchema
from datetime       import datetime, timedelta
from functools      import wraps
from io             import BytesIO
from werkzeug.utils import secure_filename
import dateutil.parser as parser


# ===============================================================
# DECORATORS
# ===============================================================

app.jinja_env.filters['zip'] = zip

@app.template_filter('day_of_week')
def _jinja2_filter_datetime(date, fmt=None):
    date = parser.parse(date)
    native = date.replace(tzinfo=None)
    format='%B %d, %Y'
    return native.strftime(format)

@app.template_filter('strfdate')
def _jinja2_filter_datetime(date, fmt=None):
    date = parser.parse(date)
    native = date.replace(tzinfo=None)
    format='%m/%d/%Y'
    return native.strftime(format)

@app.template_filter('strftime')
def _jinja2_filter_datetime(date, fmt=None):
    date = parser.parse(date)
    native = date.replace(tzinfo=None)
    format='%hh:%mm %tt'
    return native.strftime(format)

@app.context_processor
def inject_now():
    return {
        'now'   : datetime.now(),
        'day'   : timedelta(days=1),
        'month' : timedelta(days=30),
        'time_schedules' : [
            {'v': 9,  't':'09:00AM-10:00AM'},
            {'v': 10, 't':'10:00AM-11:00AM'},
            {'v': 11, 't':'11:00AM-12:00NN'},
            {'v': 13, 't':'01:00PM-02:00PM'},
            {'v': 14, 't':'02:00PM-03:00PM'},
            {'v': 15, 't':'03:00PM-04:00PM'},
            {'v': 16, 't':'04:00PM-05:00PM'}
        ]
    }

def admin_login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):

        if current_user.role_id == 2:
            return redirect(url_for('faculty_dashboard'))

        if current_user.role_id == 3:
            return redirect(url_for('student_dashboard'))

        if current_user.role_id == 4 or current_user.role_id is None:
            return redirect(url_for('guest_dashboard'))

        return f(*args, **kwargs)
    return wrapper

# ===============================================================
# COMMON WEB VIEWS
# ===============================================================

@app.route('/')
def faculties():
    response = {
        'faculties'  : Repository.readFaculties()
    }
    return render_template('common/faculties.html', data=response)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        data = Repository.loginAccount(request.form)
        if data is not None and data is not False:
            if data.role_id is not None:
                if data.role_id < 3 :
                    return redirect(url_for('dashboard'))        
            return redirect(url_for('patient_dashboard'))
        else:
            flash('Invalid credentials.')
    return render_template('common/login.html')

@app.route('/logout')
@login_required
def logout():
    Repository.logoutAccount(current_user.id)
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('login'))

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        
        validator = RegisterAccountSchema(unknown='EXCLUDE')
        errors = validator.validate(request.form)

        if errors:
            return render_template('common/register.html', data={'errors': errors, 'input': request.form})

        if Repository.registerAccount(request.form):
            return redirect(url_for('login'))
        
    return render_template('common/register.html', data={'errors':[], 'input': []})

@app.route('/register_non_faculty', methods=['POST', 'GET'])
def register_non_faculty():
    if request.method == 'POST':
        
        validator = RegisterStudentAccountSchema(unknown='EXCLUDE')
        errors = validator.validate(request.form)

        if errors:
            return render_template('common/register_non_faculty.html', data={'errors': errors, 'input': request.form})

        if Repository.registerStudentAccount(request.form):
            return redirect(url_for('faculties'))
        
    return render_template('common/register_non_faculty.html', data={'errors':[], 'input': []})

@app.route('/window')
def window():
    response = {
        'faculties' : Repository.readFaculties(),
        'calls'     : Repository.readCalls(),
        'active'    : Repository.readActive(),
        'declined'  : Repository.readDeclined()
    }
    return render_template('common/window.html', data=response)

@app.route('/common/faculty/<id>')
def faculty(id):
    response = {
        'account'       : Repository.readAccount(id),
    }
    return render_template('common/faculty.html', data=response)

@app.route('/common/wave/<id>/<faculty_id>', methods=['POST', 'GET'])
def wave(id, faculty_id):
       
    response = {
        'purpose'   : Repository.readAllPurpose(),
        'students'  : Repository.readStudents(),
        'faculty'   : Repository.readAccount(faculty_id),
    }

    if request.method == 'POST':

        if id == "1":
            
            validator = SetStudentAppointmentSchema(unknown='EXCLUDE')
            errors = validator.validate(request.form)

            if errors:
                return render_template('common/wave_student.html', data={'errors': errors, 'input': request.form, 'id': id, 'faculty_id': faculty_id, 'repo': response})

        if id == "2":
            
            validator = SetStudentAppointmentSchema(unknown='EXCLUDE')
            errors = validator.validate(request.form)

            if errors:
                return render_template('common/wave_group.html', data={'errors': errors, 'input': request.form, 'id': id, 'faculty_id': faculty_id, 'repo': response})

        if id == "3":

            validator = SetGuestAppointmentSchema(unknown='EXCLUDE')
            errors = validator.validate(request.form)

            if errors:
                return render_template('common/wave_guest.html', data={'errors': errors, 'input': request.form, 'id': id, 'faculty_id': faculty_id, 'repo': response})

        _response = Repository.setAppointment(id, faculty_id, request.form.to_dict(flat=False))
        return render_template('common/success.html', data=_response)
         
    Repository.updateInquiries(faculty_id)

    if id == "1":
        return render_template('common/wave_student.html', data={'errors':[], 'input': [], 'id': id, 'faculty_id': faculty_id, 'repo': response})

    if id == "2":
        return render_template('common/wave_group.html', data={'errors':[], 'input': [], 'id': id, 'faculty_id': faculty_id, 'repo': response})

    if id == "3":
        return render_template('common/wave_guest.html', data={'errors':[], 'input': [], 'id': id, 'faculty_id': faculty_id, 'repo': response})
