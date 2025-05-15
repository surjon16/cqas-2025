from application import app
from data import db

app.secret_key = 'hifi_brew_2025'
app.WTF_CSRF_ENABLED = True

if __name__ == '__main__':
    db.drop_all()
    db.create_all()
    app.run(debug=True, host='localhost', port='8080')
    # app.run(host='0.0.0.0', port='8080')
