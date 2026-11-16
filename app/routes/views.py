from flask import Blueprint, render_template

views_bp = Blueprint('views', __name__)

@views_bp.route('/')
def index():
    """Home / Project Overview page."""
    return render_template('index.html')

@views_bp.route('/dashboard')
def dashboard():
    """Fleet Digital Twin Main Dashboard."""
    return render_template('dashboard.html')

@views_bp.route('/vehicles/<vehicle_id>')
def vehicle_detail(vehicle_id):
    """Digital Twin View for a specific vehicle."""
    return render_template('vehicle_detail.html', vehicle_id=vehicle_id)

@views_bp.route('/predictions')
def predictions():
    """Predictive Maintenance Alerts & Failure Risk Log."""
    return render_template('predictions.html')
