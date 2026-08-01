// Particles Canvas Background Animation
const canvas = document.getElementById('particles-canvas');
const ctx = canvas.getContext('2d');

let particles = [];
const particleCount = 60;
const connectionDistance = 120;

function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}

window.addEventListener('resize', resizeCanvas);
resizeCanvas();

class Particle {
    constructor() {
        this.x = Math.random() * canvas.width;
        this.y = Math.random() * canvas.height;
        this.vx = (Math.random() - 0.5) * 0.5;
        this.vy = (Math.random() - 0.5) * 0.5;
        this.radius = Math.random() * 2 + 1;
    }

    update() {
        this.x += this.vx;
        this.y += this.vy;

        if (this.x < 0 || this.x > canvas.width) this.vx = -this.vx;
        if (this.y < 0 || this.y > canvas.height) this.vy = -this.vy;
    }

    draw() {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(6, 182, 212, 0.4)';
        ctx.fill();
    }
}

function initParticles() {
    particles = [];
    for (let i = 0; i < particleCount; i++) {
        particles.push(new Particle());
    }
}

function animateParticles() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    for (let i = 0; i < particles.length; i++) {
        const p1 = particles[i];
        p1.update();
        p1.draw();

        for (let j = i + 1; j < particles.length; j++) {
            const p2 = particles[j];
            const dist = Math.hypot(p1.x - p2.x, p1.y - p2.y);

            if (dist < connectionDistance) {
                const alpha = (1 - dist / connectionDistance) * 0.15;
                ctx.beginPath();
                ctx.moveTo(p1.x, p1.y);
                ctx.lineTo(p2.x, p2.y);
                ctx.strokeStyle = `rgba(59, 130, 246, ${alpha})`;
                ctx.lineWidth = 1;
                ctx.stroke();
            }
        }
    }
    requestAnimationFrame(animateParticles);
}

initParticles();
animateParticles();

// Interactive Sizing Calculator Logic
const sliderPayload = document.getElementById('slider-payload');
const sliderProp = document.getElementById('slider-prop');
const sliderDensity = document.getElementById('slider-density');
const sliderRange = document.getElementById('slider-range');

const valPayload = document.getElementById('val-payload');
const valProp = document.getElementById('val-prop');
const valDensity = document.getElementById('val-density');
const valRange = document.getElementById('val-range');

const resTOW = document.getElementById('res-tow');
const resBattery = document.getElementById('res-battery');
const resPower = document.getElementById('res-power');
const resTime = document.getElementById('res-time');

function runSizingCalculation() {
    // Inputs
    const payload = parseFloat(sliderPayload.value);
    const prop_in = parseFloat(sliderProp.value);
    const density = parseFloat(sliderDensity.value);
    const range_km = parseFloat(sliderRange.value);

    // Update Slider text
    valPayload.textContent = payload.toFixed(1);
    valProp.textContent = prop_in.toFixed(0);
    valDensity.textContent = density.toFixed(0);
    valRange.textContent = range_km.toFixed(0);

    // Constants for Sizing Loop
    const prop_r_m = (prop_in * 0.0254) / 2.0; // propeller radius in meters
    const disk_area = Math.PI * Math.pow(prop_r_m, 2);
    const num_rotors = 6;
    const hover_fom = 0.72; // Figure of Merit
    const motor_eff = 0.85; // Brushless motor efficiency
    const esc_eff = 0.95;   // ESC efficiency
    const air_density = 1.225; // kg/m^3
    const cruise_speed = 12.0; // m/s
    const loiter_time = 20.0 * 60.0; // 20 mins loiter in seconds

    // Initial Guess
    let tow = payload + 15.0; // starting guess in kg
    let battery_mass = 5.0;
    let hover_power_elec = 1000.0;
    let flight_time_mins = 60.0;

    // Convergence loop (8 iterations)
    for (let iter = 0; iter < 8; iter++) {
        // Sized dry weight components based on structural load
        // Sized frame structures scales with TOW (carbon tubes, aluminum plate, clamps)
        const frame_mass = 1.5 + 0.11 * tow;
        // Propulsion hardware (6 motors, ESCs, cabling) scales slightly with power (cabling weight)
        const prop_hardware = 3.5 + 0.06 * tow;
        // Avionics & payload mounts
        const avionics = 1.2; 
        
        // Thrust required per rotor at hover (N)
        const hover_thrust_n = (tow * 9.81) / num_rotors;

        // Ideal induced power via actuator disk theory (W)
        const P_ideal = hover_thrust_n * Math.sqrt(hover_thrust_n / (2 * air_density * disk_area));
        
        // Actual rotor aerodynamic hover power
        const hover_power_aero = P_ideal / hover_fom;

        // Total electrical power (6 rotors + motor & ESC efficiencies + 50W avionics base)
        hover_power_elec = num_rotors * (hover_power_aero / (motor_eff * esc_eff)) + 50.0;

        // Energy budget calculation (30 km radius = 60 km round trip + loiter)
        const cruise_time = (range_km * 2 * 1000) / cruise_speed; // in seconds
        const total_time = cruise_time + loiter_time;
        flight_time_mins = total_time / 60.0;

        // SSSS Battery energy consumption (Wh)
        const energy_consumed = hover_power_elec * (total_time / 3600.0);
        
        // Required energy capacity with 20% safety reserve margin (80% DoD)
        const batt_capacity_wh = energy_consumed / 0.8;

        // Battery mass (kg)
        battery_mass = batt_capacity_wh / density;

        // Converged TOW
        tow = payload + frame_mass + prop_hardware + avionics + battery_mass;
    }

    // Update Output display with animation transitions
    animateValue(resTOW, tow, 2, " kg");
    animateValue(resBattery, battery_mass, 2, " kg");
    animateValue(resPower, hover_power_elec, 0, " W");
    animateValue(resTime, flight_time_mins, 1, " min");
}

// Small helper to animate counter changes smoothly
function animateValue(obj, targetValue, decimals, suffix) {
    const startVal = parseFloat(obj.getAttribute('data-value') || 0);
    const duration = 250; // ms
    const startTime = performance.now();

    function update(now) {
        const elapsed = now - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Ease out quadratic
        const easeProgress = progress * (2 - progress);
        const currentVal = startVal + (targetValue - startVal) * easeProgress;
        
        obj.textContent = currentVal.toFixed(decimals) + suffix;
        
        if (progress < 1) {
            requestAnimationFrame(update);
        } else {
            obj.setAttribute('data-value', targetValue);
        }
    }
    
    requestAnimationFrame(update);
}

// Add event listeners to sliders
[sliderPayload, sliderProp, sliderDensity, sliderRange].forEach(slider => {
    slider.addEventListener('input', runSizingCalculation);
});

// Run initial calculation on load
runSizingCalculation();
