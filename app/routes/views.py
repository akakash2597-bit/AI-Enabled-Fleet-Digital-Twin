"""
View routes and controllers for Fleet Digital Twin web application.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, abort
from app.models.db import (
    get_all_vehicles,
    get_vehicle_by_id,
    get_recent_telemetry,
    get_fleet_summary,
    get_all_predictions,
    get_maintenance_tickets,
    add_vehicle,
    delete_vehicle,
    add_maintenance_ticket,
    resolve_maintenance_ticket
)
from app.services.digital_twin import get_digital_twin

views_bp = Blueprint('views', __name__)

# Authentication Helper
def is_admin():
    return session.get('is_admin', False)

@views_bp.route('/')
def index():
    """Project Overview and Architecture Landing Page."""
    summary = get_fleet_summary()
    return render_template('index.html', summary=summary, is_admin=is_admin())

@views_bp.route('/dashboard')
def dashboard():
    """Main Fleet Digital Twin Dashboard with KPI cards and charts."""
    summary = get_fleet_summary()
    vehicles = get_all_vehicles()
    recent_alerts = get_all_predictions(limit=5)
    return render_template(
        'dashboard.html', 
        summary=summary, 
        vehicles=vehicles, 
        recent_alerts=recent_alerts,
        is_admin=is_admin()
    )

@views_bp.route('/vehicles')
def vehicle_list():
    """List of all fleet vehicles with filter, status, and health scores."""
    vehicles = get_all_vehicles()
    return render_template('vehicles.html', vehicles=vehicles, is_admin=is_admin())

@views_bp.route('/vehicles/<vehicle_id>')
def vehicle_detail(vehicle_id):
    """
    Vehicle Detail & Digital Twin view.
    Includes interactive subsystem virtualization and real-time simulator.
    """
    vehicle = get_vehicle_by_id(vehicle_id)
    if not vehicle:
        abort(404, description=f"Vehicle {vehicle_id} not found.")

    telemetry_history = get_recent_telemetry(vehicle_id, limit=20)
    tickets = get_maintenance_tickets(vehicle_id)
    
    # Get initial digital twin state
    twin = get_digital_twin(vehicle_id)
    latest_telemetry = telemetry_history[-1] if telemetry_history else {
        'Engine rpm': 750,
        'Lub oil pressure': 3.2,
        'Fuel pressure': 6.5,
        'Coolant pressure': 2.3,
        'lub oil temp': 77.0,
        'Coolant temp': 78.0
    }
    twin_state = twin.compute_twin_state(latest_telemetry)

    return render_template(
        'vehicle_detail.html',
        vehicle=vehicle,
        telemetry_history=telemetry_history,
        tickets=tickets,
        twin_state=twin_state,
        is_admin=is_admin()
    )

@views_bp.route('/predictions')
def predictions():
    """Predictive Maintenance Alerts & Failure Risk Logs."""
    all_predictions = get_all_predictions(limit=50)
    tickets = get_maintenance_tickets()
    return render_template(
        'predictions.html', 
        predictions=all_predictions, 
        tickets=tickets,
        is_admin=is_admin()
    )

# -------------------------------------------------------------
# Admin Authentication Routes
# -------------------------------------------------------------
@views_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin Login Page."""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        # Demo Credentials: admin / admin123
        if username == 'admin' and password == 'admin123':
            session['is_admin'] = True
            session['admin_user'] = username
            flash('Successfully logged in as Fleet Administrator.', 'success')
            return redirect(url_for('views.dashboard'))
        else:
            flash('Invalid username or password. (Hint: admin / admin123)', 'danger')

    return render_template('login.html', is_admin=is_admin())

@views_bp.route('/logout')
def logout():
    """Admin Logout."""
    session.pop('is_admin', None)
    session.pop('admin_user', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('views.dashboard'))

# -------------------------------------------------------------
# Admin Protected Operations
# -------------------------------------------------------------
@views_bp.route('/admin/add-vehicle', methods=['POST'])
def admin_add_vehicle():
    """Register a new vehicle into the fleet."""
    if not is_admin():
        flash('Admin login required to add vehicles.', 'danger')
        return redirect(url_for('views.login'))

    v_id = request.form.get('vehicle_id', '').strip()
    model = request.form.get('vehicle_model', '').strip()
    year = int(request.form.get('manufacture_year', 2024))
    plate = request.form.get('license_plate', '').strip()
    status = request.form.get('current_status', 'Operational')
    mileage = float(request.form.get('total_mileage_km', 0.0))

    if v_id and model:
        try:
            add_vehicle(v_id, model, year, plate, status, mileage)
            flash(f"Vehicle {v_id} ({model}) added to fleet successfully.", 'success')
        except Exception as e:
            flash(f"Error adding vehicle: {e}", 'danger')
    return redirect(url_for('views.vehicle_list'))

@views_bp.route('/admin/delete-vehicle/<vehicle_id>', methods=['POST'])
def admin_delete_vehicle(vehicle_id):
    """Remove a vehicle from the fleet."""
    if not is_admin():
        flash('Admin login required to delete vehicles.', 'danger')
        return redirect(url_for('views.login'))

    try:
        delete_vehicle(vehicle_id)
        flash(f"Vehicle {vehicle_id} removed from fleet.", 'success')
    except Exception as e:
        flash(f"Error removing vehicle: {e}", 'danger')
    return redirect(url_for('views.vehicle_list'))

@views_bp.route('/admin/schedule-maintenance', methods=['POST'])
def admin_schedule_maintenance():
    """Create a new maintenance order."""
    if not is_admin():
        flash('Admin login required.', 'danger')
        return redirect(url_for('views.login'))

    v_id = request.form.get('vehicle_id')
    service_type = request.form.get('service_type', 'Predictive Alert')
    scheduled_date = request.form.get('scheduled_date')
    notes = request.form.get('notes', '')

    if v_id and scheduled_date:
        add_maintenance_ticket(v_id, service_type, scheduled_date, notes)
        flash(f"Maintenance ticket scheduled for vehicle {v_id}.", 'success')
    return redirect(request.referrer or url_for('views.predictions'))

@views_bp.route('/admin/resolve-ticket/<int:ticket_id>', methods=['POST'])
def admin_resolve_ticket(ticket_id):
    """Mark a maintenance ticket as resolved."""
    if not is_admin():
        flash('Admin login required.', 'danger')
        return redirect(url_for('views.login'))

    resolve_maintenance_ticket(ticket_id)
    flash(f"Maintenance ticket #{ticket_id} marked as Completed.", 'success')
    return redirect(request.referrer or url_for('views.predictions'))
