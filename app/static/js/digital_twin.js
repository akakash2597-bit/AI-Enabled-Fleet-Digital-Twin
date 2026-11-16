/**
 * Digital Twin Interactive Simulator & Subsystem Controller.
 * Powers real-time sliders, presets, AJAX ML inference, and DOM updates.
 */

let debounceTimer = null;

function onTelemetryChange() {
    // 1. Update slider value text labels immediately
    const rpm = document.getElementById('input-rpm').value;
    const coolTemp = document.getElementById('input-cooltemp').value;
    const oilPres = document.getElementById('input-oilpres').value;
    const oilTemp = document.getElementById('input-oiltemp').value;
    const fuelPres = document.getElementById('input-fuelpres').value;
    const coolPres = document.getElementById('input-coolpres').value;

    document.getElementById('val-rpm').innerText = `${rpm} RPM`;
    document.getElementById('val-cooltemp').innerText = `${coolTemp} °C`;
    document.getElementById('val-oilpres').innerText = `${oilPres} bar`;
    document.getElementById('val-oiltemp').innerText = `${oilTemp} °C`;
    document.getElementById('val-fuelpres').innerText = `${fuelPres} bar`;
    document.getElementById('val-coolpres').innerText = `${coolPres} bar`;

    // 2. Debounce AJAX prediction request
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
        executePrediction({
            'Engine rpm': parseFloat(rpm),
            'Coolant temp': parseFloat(coolTemp),
            'Lub oil pressure': parseFloat(oilPres),
            'lub oil temp': parseFloat(oilTemp),
            'Fuel pressure': parseFloat(fuelPres),
            'Coolant pressure': parseFloat(coolPres)
        });
    }, 150);
}

/**
 * Sends current telemetry state to Flask /api/predict endpoint
 */
async function executePrediction(telemetryPayload) {
    try {
        const response = await fetch('/api/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(telemetryPayload)
        });

        if (!response.ok) {
            console.error('Prediction API failed:', response.status);
            return;
        }

        const data = await response.json();
        updateDigitalTwinUI(data);
    } catch (err) {
        console.error('Error contacting prediction engine:', err);
    }
}

/**
 * Updates DOM components with returned digital twin and ML risk payload
 */
function updateDigitalTwinUI(data) {
    if (!data || !data.digital_twin || !data.prediction) return;

    const twin = data.digital_twin;
    const pred = data.prediction;

    // 1. Overall Health Score
    const healthEl = document.getElementById('twinHealthScore');
    const healthFill = document.getElementById('twinHealthFill');
    if (healthEl && healthFill) {
        healthEl.innerText = `${twin.overall_health_score}%`;
        healthFill.style.width = `${twin.overall_health_score}%`;

        // Update color
        healthFill.className = 'health-progress-fill';
        if (twin.overall_health_score < 40) {
            healthFill.classList.add('bg-danger');
            healthEl.className = 'gauge-number text-danger';
        } else if (twin.overall_health_score < 75) {
            healthFill.classList.add('bg-warning');
            healthEl.className = 'gauge-number text-warning';
        } else {
            healthFill.classList.add('bg-success');
            healthEl.className = 'gauge-number text-success';
        }
    }

    // 2. Failure Risk Score & Severity Pill
    const riskEl = document.getElementById('twinRiskScore');
    const sevPill = document.getElementById('twinSeverityPill');
    if (riskEl && sevPill) {
        riskEl.innerText = `${twin.failure_risk_percentage}%`;
        sevPill.innerText = `${pred.severity} SEVERITY`;

        sevPill.className = 'risk-pill large';
        if (pred.severity === 'CRITICAL' || pred.severity === 'HIGH') {
            sevPill.classList.add('risk-critical');
        } else if (pred.severity === 'MEDIUM') {
            sevPill.classList.add('risk-warning');
        } else {
            sevPill.classList.add('risk-normal');
        }
    }

    // 3. Subsystem Breakdown
    const subsystems = twin.subsystems;
    updateSubsystemCard('engine', subsystems.engine_assembly);
    updateSubsystemCard('cooling', subsystems.cooling_system);
    updateSubsystemCard('lubrication', subsystems.lubrication_system);
    updateSubsystemCard('fuel', subsystems.fuel_injection);
    updateSubsystemCard('transmission', subsystems.transmission);

    // 4. Recommendation Card
    const recTitle = document.getElementById('recTitle');
    const recAction = document.getElementById('recActionText');
    if (recTitle && recAction) {
        recTitle.innerText = `Diagnosed: ${pred.suspect_component}`;
        recAction.innerText = pred.recommended_maintenance || pred.recommended_action;
    }

    // 5. Estimated Remaining Life (RUL)
    const rulEl = document.getElementById('twinRUL');
    const rulNote = document.getElementById('twinRULNote');
    if (rulEl && pred.estimated_remaining_life) {
        rulEl.innerText = pred.estimated_remaining_life.formatted_display;
        if (rulNote) rulNote.innerText = pred.estimated_remaining_life.urgency_text;
    }

    // 6. Plain-English Explanation
    const explEl = document.getElementById('twinExplanationText');
    if (explEl && pred.explanation) {
        explEl.innerText = pred.explanation.summary_text.replace(/\*\*/g, '');
    }
}

function updateSubsystemCard(key, sub) {
    if (!sub) return;

    const statusPill = document.getElementById(`status-${key}`);
    const fillEl = document.getElementById(`fill-${key}`);
    const pctEl = document.getElementById(`pct-${key}`);

    if (statusPill) {
        statusPill.innerText = sub.status;
        statusPill.className = `subsystem-status-pill status-${sub.status.toLowerCase()}`;
    }

    if (fillEl && pctEl) {
        fillEl.style.width = `${sub.health}%`;
        pctEl.innerText = `${sub.health}%`;

        fillEl.className = 'health-progress-fill';
        if (sub.health < 50) {
            fillEl.classList.add('bg-danger');
            pctEl.className = 'health-pct-text text-danger';
        } else if (sub.health < 80) {
            fillEl.classList.add('bg-warning');
            pctEl.className = 'health-pct-text text-warning';
        } else {
            fillEl.classList.add('bg-success');
            pctEl.className = 'health-pct-text text-success';
        }
    }
}

/**
 * Demonstrates presets for viva presentation
 */
function applyPreset(presetType) {
    const inputs = {
        'normal': { rpm: 820, cooltemp: 78.0, oilpres: 3.8, oiltemp: 76.5, fuelpres: 6.2, coolpres: 2.4 },
        'overheating': { rpm: 550, cooltemp: 138.0, oilpres: 1.8, oiltemp: 88.0, fuelpres: 7.2, coolpres: 0.7 },
        'oil_drop': { rpm: 420, cooltemp: 85.0, oilpres: 0.6, oiltemp: 91.0, fuelpres: 5.8, coolpres: 1.8 },
        'fuel_surge': { rpm: 980, cooltemp: 82.0, oilpres: 3.4, oiltemp: 78.0, fuelpres: 19.2, coolpres: 2.2 }
    };

    const target = inputs[presetType];
    if (!target) return;

    document.getElementById('input-rpm').value = target.rpm;
    document.getElementById('input-cooltemp').value = target.cooltemp;
    document.getElementById('input-oilpres').value = target.oilpres;
    document.getElementById('input-oiltemp').value = target.oiltemp;
    document.getElementById('input-fuelpres').value = target.fuelpres;
    document.getElementById('input-coolpres').value = target.coolpres;

    onTelemetryChange();
}

/**
 * Saves current simulated telemetry values directly into SQLite database
 */
async function saveSimulatedReading(vehicleId) {
    const rpm = parseFloat(document.getElementById('input-rpm').value);
    const coolTemp = parseFloat(document.getElementById('input-cooltemp').value);
    const oilPres = parseFloat(document.getElementById('input-oilpres').value);
    const oilTemp = parseFloat(document.getElementById('input-oiltemp').value);
    const fuelPres = parseFloat(document.getElementById('input-fuelpres').value);
    const coolPres = parseFloat(document.getElementById('input-coolpres').value);

    try {
        const res = await fetch(`/api/vehicles/${vehicleId}/telemetry`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                'Engine rpm': rpm,
                'Coolant temp': coolTemp,
                'Lub oil pressure': oilPres,
                'lub oil temp': oilTemp,
                'Fuel pressure': fuelPres,
                'Coolant pressure': coolPres,
                'vibration': coolTemp > 100 ? 0.35 : 0.14,
                'speed': 62.0
            })
        });

        if (res.ok) {
            alert(`Simulated telemetry and ML diagnosis successfully stored in database for ${vehicleId}!`);
            window.location.reload();
        } else {
            alert('Failed to save telemetry reading.');
        }
    } catch (e) {
        console.error(e);
        alert('Error saving telemetry reading.');
    }
}
