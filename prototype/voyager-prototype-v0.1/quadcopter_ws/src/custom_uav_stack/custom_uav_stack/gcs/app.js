// --- Global State ---
let isConnected = false;
let isArmed = false;
let latestData = null;

// Telemetry history for rolling charts
const maxHistoryPoints = 100;
const historyZ = [];
const historyZSetpoint = [];
const historyTime = [];

// PID Tab Switching
function switchPidTab(tabName) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.add('hidden'));
    
    // Find the clicked tab button and active content
    event.currentTarget.classList.add('active');
    document.getElementById(`pid-${tabName}`).classList.remove('hidden');
}

// Update slider labels on input
function setupSliderListeners() {
    const sliders = [
        { id: 'kp-xy', labelId: 'val-kp-xy', precision: 2 },
        { id: 'kd-xy', labelId: 'val-kd-xy', precision: 2 },
        { id: 'kp-z', labelId: 'val-kp-z', precision: 2 },
        { id: 'kd-z', labelId: 'val-kd-z', precision: 2 },
        { id: 'kp-att-rp', labelId: 'val-kp-att-rp', precision: 2 },
        { id: 'kp-att-y', labelId: 'val-kp-att-y', precision: 2 },
        { id: 'kp-rate-rp', labelId: 'val-kp-rate-rp', precision: 2 },
        { id: 'kd-rate-rp', labelId: 'val-kd-rate-rp', precision: 2 },
        { id: 'ki-rate-rp', labelId: 'val-ki-rate-rp', precision: 2 },
        { id: 'kp-rate-y', labelId: 'val-kp-rate-y', precision: 2 },
        { id: 'wind-x', labelId: 'val-wind-x', precision: 1 },
        { id: 'wind-y', labelId: 'val-wind-y', precision: 1 }
    ];
    
    sliders.forEach(slider => {
        const el = document.getElementById(slider.id);
        const label = document.getElementById(slider.labelId);
        if (el && label) {
            el.addEventListener('input', (e) => {
                label.innerText = parseFloat(e.target.value).toFixed(slider.precision);
            });
        }
    });
}

// --- SSE Telemetry Stream ---
function connectTelemetryStream() {
    const connBadge = document.getElementById('conn-status');
    const connLabel = connBadge.querySelector('.label');
    const connDot = connBadge.querySelector('.dot');
    
    const eventSource = new EventSource('/stream');
    
    eventSource.onopen = () => {
        isConnected = true;
        connLabel.innerText = "CONNECTED";
        connDot.className = "dot green";
        console.log("Telemetry stream connected.");
    };
    
    eventSource.onerror = (err) => {
        isConnected = false;
        connLabel.innerText = "DISCONNECTED";
        connDot.className = "dot red";
        console.error("Telemetry stream connection error:", err);
    };
    
    eventSource.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            latestData = data;
            updateTelemetryUI(data);
        } catch (e) {
            console.error("Error parsing telemetry stream message:", e);
        }
    };
}

// Update the numerical values, badges, and motor bar charts
function updateTelemetryUI(data) {
    // 1. Arm Status
    const armBadge = document.getElementById('arm-status');
    const armLabel = armBadge.querySelector('.label');
    const armDot = armBadge.querySelector('.dot');
    const btnArm = document.getElementById('btn-arm');
    
    isArmed = data.armed;
    if (isArmed) {
        armLabel.innerText = "ARMED";
        armDot.className = "dot green";
        btnArm.innerText = "DISARM VEHICLE";
        btnArm.className = "btn-danger armed";
    } else {
        armLabel.innerText = "DISARMED";
        armDot.className = "dot red";
        btnArm.innerText = "ARM VEHICLE";
        btnArm.className = "btn-danger";
    }
    
    // 2. Numerical Values
    document.getElementById('val-x').innerText = data.pos[0].toFixed(2) + " m";
    document.getElementById('val-y').innerText = data.pos[1].toFixed(2) + " m";
    document.getElementById('val-z').innerText = data.pos[2].toFixed(2) + " m";
    
    document.getElementById('val-roll').innerText = data.euler[0].toFixed(1) + "°";
    document.getElementById('val-pitch').innerText = data.euler[1].toFixed(1) + "°";
    document.getElementById('val-yaw').innerText = data.euler[2].toFixed(1) + "°";
    
    // 3. Motor Fill Bars
    const maxRpm = 800.0;
    for (let i = 0; i < 4; i++) {
        const speed = data.motors[i];
        const pct = Math.min((speed / maxRpm) * 100, 100);
        document.getElementById(`fill-m${i+1}`).style.height = pct + "%";
        document.getElementById(`txt-m${i+1}`).innerText = Math.round(speed);
    }
    
    // 4. Update History for charts
    historyZ.push(data.pos[2]);
    historyZSetpoint.push(data.target_pos[2]);
    if (historyZ.length > maxHistoryPoints) {
        historyZ.shift();
        historyZSetpoint.shift();
    }
    
    // 5. Update 3D Drone Model
    if (droneGroup) {
        // Translation
        droneGroup.position.set(data.pos[0], data.pos[2], -data.pos[1]); // Swap Y and Z for Three.js coordinates (Y is UP, Z is depth)
        
        // Rotation (roll, pitch, yaw)
        // Convert to radians (they are sent in degrees from telemetry)
        const rollRad = data.euler[0] * Math.PI / 180;
        const pitchRad = data.euler[1] * Math.PI / 180;
        const yawRad = data.euler[2] * Math.PI / 180;
        
        // Pitch rotates around X axis, Roll around Z axis, Yaw around Y axis (in Three.js coordinates)
        droneGroup.rotation.set(pitchRad, -yawRad, rollRad, 'YXZ');
        
        // Spin propellers in 3D
        if (data.armed) {
            propellers.forEach((prop, idx) => {
                const speed = data.motors[idx];
                const direction = (idx === 0 || idx === 1) ? 1 : -1; // CW / CCW directions
                prop.rotation.y += direction * (speed / maxRpm) * 0.8;
            });
        }
        
        // Add path trail point
        updateTrail(data.pos[0], data.pos[2], -data.pos[1]);
    }
}

// --- Custom Canvas-based Telemetry Charts ---
const canvasZ = document.getElementById('chart-z');
const ctxZ = canvasZ.getContext('2d');
const canvasXY = document.getElementById('chart-xy');
const ctxXY = canvasXY.getContext('2d');

function drawZChart() {
    ctxZ.clearRect(0, 0, canvasZ.width, canvasZ.height);
    
    // Background Grid
    ctxZ.strokeStyle = 'rgba(255, 255, 255, 0.05)';
    ctxZ.lineWidth = 1;
    for (let i = 0; i < canvasZ.width; i += 40) {
        ctxZ.beginPath();
        ctxZ.moveTo(i, 0);
        ctxZ.lineTo(i, canvasZ.height);
        ctxZ.stroke();
    }
    for (let i = 0; i < canvasZ.height; i += 25) {
        ctxZ.beginPath();
        ctxZ.moveTo(0, i);
        ctxZ.lineTo(canvasZ.width, i);
        ctxZ.stroke();
    }
    
    if (historyZ.length < 2) {
        requestAnimationFrame(drawZChart);
        return;
    }
    
    // Scale mapping
    const minVal = 0.0;
    const maxVal = Math.max(5.0, ...historyZ, ...historyZSetpoint) + 0.5;
    
    const getX = (idx) => (idx / (maxHistoryPoints - 1)) * canvasZ.width;
    const getY = (val) => canvasZ.height - ((val - minVal) / (maxVal - minVal)) * (canvasZ.height - 20) - 10;
    
    // Draw Target Setpoint (dashed blue line)
    ctxZ.strokeStyle = '#3b82f6';
    ctxZ.lineWidth = 2;
    ctxZ.setLineDash([5, 5]);
    ctxZ.beginPath();
    ctxZ.moveTo(getX(0), getY(historyZSetpoint[0]));
    for (let i = 1; i < historyZSetpoint.length; i++) {
        ctxZ.lineTo(getX(i), getY(historyZSetpoint[i]));
    }
    ctxZ.stroke();
    ctxZ.setLineDash([]); // Reset
    
    // Draw Actual Altitude (solid green line)
    ctxZ.strokeStyle = '#10b981';
    ctxZ.lineWidth = 2.5;
    ctxZ.shadowColor = 'rgba(16, 185, 129, 0.3)';
    ctxZ.shadowBlur = 6;
    ctxZ.beginPath();
    ctxZ.moveTo(getX(0), getY(historyZ[0]));
    for (let i = 1; i < historyZ.length; i++) {
        ctxZ.lineTo(getX(i), getY(historyZ[i]));
    }
    ctxZ.stroke();
    ctxZ.shadowBlur = 0; // Reset
    
    // Draw text labels
    ctxZ.fillStyle = '#94a3b8';
    ctxZ.font = '9px monospace';
    ctxZ.fillText(`Max: ${maxVal.toFixed(1)}m`, 5, 12);
    ctxZ.fillText(`0.0m`, 5, canvasZ.height - 5);
    if (latestData) {
        ctxZ.fillStyle = '#10b981';
        ctxZ.fillText(`Z: ${latestData.pos[2].toFixed(2)}m`, canvasZ.width - 65, 12);
        ctxZ.fillStyle = '#3b82f6';
        ctxZ.fillText(`Set: ${latestData.target_pos[2].toFixed(2)}m`, canvasZ.width - 65, 24);
    }
    
    requestAnimationFrame(drawZChart);
}

function drawXYRadar() {
    ctxXY.clearRect(0, 0, canvasXY.width, canvasXY.height);
    
    const centerX = canvasXY.width / 2;
    const centerY = canvasXY.height / 2;
    const maxRadarRange = 3.0; // max error to render in meters
    const scale = (canvasXY.height - 20) / (2 * maxRadarRange); // px per meter
    
    // Draw Concentric Radar Circles
    ctxXY.strokeStyle = 'rgba(255, 255, 255, 0.05)';
    ctxXY.lineWidth = 1;
    const ranges = [0.5, 1.0, 2.0, 3.0];
    ranges.forEach(r => {
        ctxXY.beginPath();
        ctxXY.arc(centerX, centerY, r * scale, 0, 2 * Math.PI);
        ctxXY.stroke();
        
        ctxXY.fillStyle = 'rgba(148, 163, 184, 0.4)';
        ctxXY.font = '8px monospace';
        ctxXY.fillText(`${r}m`, centerX + r * scale - 12, centerY - 3);
    });
    
    // Draw Axes
    ctxXY.beginPath();
    ctxXY.moveTo(0, centerY);
    ctxXY.lineTo(canvasXY.width, centerY);
    ctxXY.moveTo(centerX, 0);
    ctxXY.lineTo(centerX, canvasXY.height);
    ctxXY.stroke();
    
    if (latestData) {
        const dx = latestData.pos[0] - latestData.target_pos[0];
        const dy = latestData.pos[1] - latestData.target_pos[1];
        
        // Map delta to radar coordinates (invert Y to match canvas coordinates)
        const dotX = centerX + dx * scale;
        const dotY = centerY - dy * scale; // standard math Y is up, canvas Y is down
        
        // Draw path trail on radar (last 10 positions)
        // ...
        
        // Draw Current Position Dot
        ctxXY.fillStyle = '#ff0055';
        ctxXY.shadowColor = 'rgba(255, 0, 85, 0.6)';
        ctxXY.shadowBlur = 8;
        ctxXY.beginPath();
        ctxXY.arc(dotX, dotY, 5, 0, 2 * Math.PI);
        ctxXY.fill();
        ctxXY.shadowBlur = 0; // Reset
        
        // Draw text
        ctxXY.fillStyle = '#94a3b8';
        ctxXY.font = '9px monospace';
        ctxXY.fillText(`Err X: ${dx.toFixed(2)}m`, 5, 12);
        ctxXY.fillText(`Err Y: ${dy.toFixed(2)}m`, 5, 24);
    }
    
    requestAnimationFrame(drawXYRadar);
}

// --- Three.js 3D Visualizer Setup ---
let scene, camera, renderer;
let droneGroup;
const propellers = [];
let trailLine;
const maxTrailPoints = 500;
const trailPoints = [];

function init3DVisualizer() {
    const container = document.getElementById('canvas-3d-container');
    const width = container.clientWidth;
    const height = container.clientHeight;
    
    // 1. Scene
    scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x020617, 0.015);
    
    // 2. Camera
    camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.set(0, 5, 10);
    camera.lookAt(0, 0, 0);
    
    // 3. Renderer
    renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);
    
    // 4. Ground Grid
    const gridHelper = new THREE.GridHelper(50, 50, 0x00d2ff, 0x1e293b);
    gridHelper.position.y = -0.01; // Slightly below zero to avoid Z-fighting
    scene.add(gridHelper);
    
    // 5. Lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
    scene.add(ambientLight);
    
    const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
    dirLight.position.set(5, 10, 7);
    scene.add(dirLight);
    
    // 6. Build Quadcopter Model
    droneGroup = new THREE.Group();
    scene.add(droneGroup);
    
    // Central Hub
    const hubGeom = new THREE.CylinderGeometry(0.3, 0.3, 0.15, 16);
    const hubMat = new THREE.MeshPhongMaterial({ color: 0x1e293b, shininess: 100 });
    const hub = new THREE.Mesh(hubGeom, hubMat);
    droneGroup.add(hub);
    
    // Heading Indicator (Arrow on hub)
    const arrowGeom = new THREE.ConeGeometry(0.12, 0.3, 4);
    const arrowMat = new THREE.MeshPhongMaterial({ color: 0xff0055 });
    const arrow = new THREE.Mesh(arrowGeom, arrowMat);
    arrow.position.set(0, 0.08, -0.2);
    arrow.rotation.x = Math.PI / 2;
    droneGroup.add(arrow);
    
    // Arms (X layout)
    const armGeom = new THREE.BoxGeometry(0.06, 0.04, 0.7);
    const armMat = new THREE.MeshPhongMaterial({ color: 0x334155 });
    
    // Arm 1 (diagonal)
    const arm1 = new THREE.Mesh(armGeom, armMat);
    arm1.rotation.y = Math.PI / 4;
    droneGroup.add(arm1);
    
    // Arm 2 (diagonal)
    const arm2 = new THREE.Mesh(armGeom, armMat);
    arm2.rotation.y = -Math.PI / 4;
    droneGroup.add(arm2);
    
    // 4 Rotors / Propellers
    const motorGeom = new THREE.CylinderGeometry(0.05, 0.05, 0.08, 8);
    const motorMat = new THREE.MeshPhongMaterial({ color: 0x0f172a });
    const propGeom = new THREE.BoxGeometry(0.35, 0.005, 0.03);
    
    // Positions relative to center: FR, RL, FL, RR
    // Motor 1 (FR): x > 0, z > 0 (Wait, in our standard body axes, X is forward, Y is left.
    // Three.js: Z is depth (out of page is +Z, in is -Z). Let's represent:
    // Front is -Z, Rear is +Z, Right is +X, Left is -X.
    // Motor positions:
    // FR: x = d, z = -d
    // RL: x = -d, z = d
    // FL: x = -d, z = -d
    // RR: x = d, z = d
    const d = 0.25;
    const motorPositions = [
        { x: d, z: -d, color: 0xff0055 }, // FR (Red heading)
        { x: -d, z: d, color: 0x00d2ff },  // RL (Blue)
        { x: -d, z: -d, color: 0xff0055 }, // FL (Red heading)
        { x: d, z: d, color: 0x00d2ff }   // RR (Blue)
    ];
    
    motorPositions.forEach((pos, idx) => {
        const motor = new THREE.Mesh(motorGeom, motorMat);
        motor.position.set(pos.x, 0.06, pos.z);
        droneGroup.add(motor);
        
        // Propeller
        const propMat = new THREE.MeshPhongMaterial({ 
            color: pos.color, 
            transparent: true, 
            opacity: 0.8 
        });
        const prop = new THREE.Mesh(propGeom, propMat);
        prop.position.set(pos.x, 0.1, pos.z);
        droneGroup.add(prop);
        propellers.push(prop);
    });
    
    // 7. Path Trail Setup
    const trailMat = new THREE.LineBasicMaterial({ color: 0x00d2ff, linewidth: 2 });
    const trailGeom = new THREE.BufferGeometry();
    trailLine = new THREE.Line(trailGeom, trailMat);
    scene.add(trailLine);
    
    // Target Setpoint Marker
    const targetGeom = new THREE.SphereGeometry(0.12, 16, 16);
    const targetMat = new THREE.MeshBasicMaterial({ color: 0x3b82f6, wireframe: true });
    window.targetMarker = new THREE.Mesh(targetGeom, targetMat);
    scene.add(window.targetMarker);
    
    // Animation/Render Loop
    function animate() {
        requestAnimationFrame(animate);
        
        // Spin propellers idle when disarmed
        if (!isArmed) {
            propellers.forEach(prop => {
                prop.rotation.y += 0.02;
            });
        }
        
        // Camera follow
        if (latestData) {
            // Keep camera at offset from drone
            const dx = latestData.pos[0];
            const dy = latestData.pos[2]; // Z is height in ROS, Y in Three.js
            const dz = -latestData.pos[1]; // ROS Y is Three.js -Z
            
            camera.position.x = dx;
            camera.position.y = dy + 4.5;
            camera.position.z = dz + 8.5;
            camera.lookAt(dx, dy, dz);
            
            // Move target marker
            window.targetMarker.position.set(
                latestData.target_pos[0],
                latestData.target_pos[2],
                -latestData.target_pos[1]
            );
        }
        
        renderer.render(scene, camera);
    }
    
    animate();
    
    // Handle Window Resize
    window.addEventListener('resize', () => {
        const w = container.clientWidth;
        const h = container.clientHeight;
        camera.aspect = w / h;
        camera.updateProjectionMatrix();
        renderer.setSize(w, h);
    });
}

function updateTrail(x, y, z) {
    trailPoints.push(new THREE.Vector3(x, y, z));
    if (trailPoints.length > maxTrailPoints) {
        trailPoints.shift();
    }
    trailLine.geometry.setFromPoints(trailPoints);
    trailLine.geometry.attributes.position.needsUpdate = true;
}

// --- HTTP POST API Commands ---
function sendCommand(endpoint, bodyData) {
    fetch(endpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(bodyData)
    })
    .then(res => res.json())
    .then(data => {
        console.log(`API response from ${endpoint}:`, data);
    })
    .catch(err => {
        console.error(`API error from ${endpoint}:`, err);
    });
}

function setupButtonListeners() {
    // 1. Arm/Disarm
    document.getElementById('btn-arm').addEventListener('click', () => {
        sendCommand('/api/arm', { arm: !isArmed });
    });
    
    // 2. Send Waypoint
    document.getElementById('btn-send-wp').addEventListener('click', () => {
        const x = parseFloat(document.getElementById('wp-x').value);
        const y = parseFloat(document.getElementById('wp-y').value);
        const z = parseFloat(document.getElementById('wp-z').value);
        const yaw = parseFloat(document.getElementById('wp-yaw').value);
        
        sendCommand('/api/setpoint', { x, y, z, yaw });
    });
    
    // 3. Return Home
    document.getElementById('btn-rth').addEventListener('click', () => {
        document.getElementById('wp-x').value = 0;
        document.getElementById('wp-y').value = 0;
        document.getElementById('wp-z').value = 2.0;
        document.getElementById('wp-yaw').value = 0;
        sendCommand('/api/setpoint', { x: 0, y: 0, z: 2.0, yaw: 0 });
    });
    
    // 4. Apply PID Gains
    document.getElementById('btn-apply-pid').addEventListener('click', () => {
        // Gather gains
        const gains = [
            parseFloat(document.getElementById('kp-xy').value),
            parseFloat(document.getElementById('kd-xy').value),
            0.05, // Ki XY position (hardcoded/small)
            parseFloat(document.getElementById('kp-z').value),
            parseFloat(document.getElementById('kd-z').value),
            0.15, // Ki Z position
            parseFloat(document.getElementById('kp-att-rp').value),
            parseFloat(document.getElementById('kp-att-y').value),
            parseFloat(document.getElementById('kp-rate-rp').value),
            parseFloat(document.getElementById('kd-rate-rp').value),
            parseFloat(document.getElementById('ki-rate-rp').value),
            parseFloat(document.getElementById('kp-rate-y').value),
            0.05  // Ki yaw rate
        ];
        sendCommand('/api/pid', { gains });
    });
    
    // 5. Apply Wind Disturbance
    document.getElementById('btn-apply-wind').addEventListener('click', () => {
        const fx = parseFloat(document.getElementById('wind-x').value);
        const fy = parseFloat(document.getElementById('wind-y').value);
        sendCommand('/api/disturbance', { fx, fy, fz: 0.0, tx: 0.0, ty: 0.0, tz: 0.0 });
    });
    
    // 6. Clear Wind Disturbance
    document.getElementById('btn-clear-wind').addEventListener('click', () => {
        document.getElementById('wind-x').value = 0;
        document.getElementById('wind-x').dispatchEvent(new Event('input'));
        document.getElementById('wind-y').value = 0;
        document.getElementById('wind-y').dispatchEvent(new Event('input'));
        sendCommand('/api/disturbance', { fx: 0.0, fy: 0.0, fz: 0.0, tx: 0.0, ty: 0.0, tz: 0.0 });
    });
    
    // 7. Reset Position Sim
    document.getElementById('btn-reset-sim').addEventListener('click', () => {
        // Reset inputs
        document.getElementById('wp-x').value = 0;
        document.getElementById('wp-y').value = 0;
        document.getElementById('wp-z').value = 2.0;
        document.getElementById('wp-yaw').value = 0;
        
        // Disarm first
        sendCommand('/api/arm', { arm: false });
        
        // Clear trail
        trailPoints.length = 0;
        if (trailLine) {
            trailLine.geometry.setFromPoints([]);
        }
        
        // Wait and then reset target setpoint
        setTimeout(() => {
            sendCommand('/api/setpoint', { x: 0, y: 0, z: 2.0, yaw: 0 });
        }, 100);
    });
}

// --- Initialization ---
window.onload = () => {
    init3DVisualizer();
    setupSliderListeners();
    setupButtonListeners();
    connectTelemetryStream();
    
    // Start drawing loop for custom canvas charts
    drawZChart();
    drawXYRadar();
};
