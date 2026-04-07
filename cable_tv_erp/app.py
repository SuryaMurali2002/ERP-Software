import os
import sys

# Ensure imports work from this directory
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, render_template, redirect, url_for, session
from flask_bcrypt import Bcrypt
from config import SECRET_KEY

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['SESSION_PERMANENT'] = False

bcrypt = Bcrypt(app)

# Register blueprints
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.customers import customers_bp
from routes.employees import employees_bp
from routes.packages import packages_bp
from routes.subscriptions import subscriptions_bp
from routes.billing import billing_bp
from routes.inventory import inventory_bp
from routes.tickets import tickets_bp
from routes.permissions import permissions_bp
from routes.reports import reports_bp

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(customers_bp)
app.register_blueprint(employees_bp)
app.register_blueprint(packages_bp)
app.register_blueprint(subscriptions_bp)
app.register_blueprint(billing_bp)
app.register_blueprint(inventory_bp)
app.register_blueprint(tickets_bp)
app.register_blueprint(permissions_bp)
app.register_blueprint(reports_bp)


@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))
    return redirect(url_for('auth.login'))


@app.errorhandler(403)
def forbidden(e):
    return render_template('errors/403.html'), 403


@app.errorhandler(404)
def not_found(e):
    return render_template('errors/404.html'), 404


@app.context_processor
def inject_session():
    return {
        'current_user_id': session.get('user_id'),
        'current_user_name': session.get('user_name'),
        'current_role': session.get('role'),
    }


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
