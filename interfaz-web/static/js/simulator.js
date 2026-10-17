/**
 * Controlador de simulación concurrente y renderizado en vivo para el laboratorio web.
 */

let enrollmentChart = null;
let timeChart = null;

document.addEventListener("DOMContentLoaded", function () {
    const simForm = document.getElementById("simulationForm");
    const btnComparative = document.getElementById("btnRunComparative");
    const btnReset = document.getElementById("btnResetSimulation");

    if (simForm) {
        simForm.addEventListener("submit", function (e) {
            e.preventDefault();
            runSingleSimulation();
        });
    }

    if (btnComparative) {
        btnComparative.addEventListener("click", runComparativeSimulation);
    }

    if (btnReset) {
        btnReset.addEventListener("click", resetSimulatorState);
    }
});

function updateDelayLabel(val) {
    document.getElementById("delayValueLabel").textContent = parseFloat(val).toFixed(3) + " s";
}

function setStudentsPreset(n) {
    document.getElementById("simStudents").value = n;
}

function clearTerminal() {
    const term = document.getElementById("logTerminal");
    term.innerHTML = '<div class="log-entry event-info">Consola limpiada. Lista para nueva prueba.</div>';
}

function appendLog(eventType, message) {
    const term = document.getElementById("logTerminal");
    const div = document.createElement("div");
    div.className = `log-entry event-${eventType}`;
    div.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
    term.appendChild(div);
    term.scrollTop = term.scrollHeight;
}

function updateMetricCards(m) {
    document.getElementById("metricInitialQuota").textContent = m.initial_quota;
    document.getElementById("metricNumStudents").textContent = m.num_students;
    document.getElementById("metricSuccessful").textContent = m.successful_enrollments;
    document.getElementById("metricRejected").textContent = m.rejected_enrollments;
    document.getElementById("metricFinalQuota").textContent = m.final_quota;
    document.getElementById("metricOversubscriptions").textContent = m.oversubscriptions;
    document.getElementById("metricInconsistencies").textContent = m.inconsistencies;
    document.getElementById("metricTotalTime").textContent = `${m.total_time} s`;
    document.getElementById("metricAvgWait").textContent = `${m.avg_wait_time} s`;
    document.getElementById("metricMaxWait").textContent = `${m.max_wait_time} s`;

    const statusBadge = document.getElementById("metricStatusLabel");
    statusBadge.textContent = m.status_label;

    const boxOver = document.getElementById("boxOversubscription");
    if (m.oversubscriptions > 0 || m.final_quota < 0) {
        statusBadge.className = "badge bg-danger";
        boxOver.classList.add("border-danger", "bg-danger-subtle");
    } else {
        statusBadge.className = "badge bg-success";
        boxOver.classList.remove("border-danger", "bg-danger-subtle");
    }
}

async function runSingleSimulation() {
    const quota = parseInt(document.getElementById("simQuota").value);
    const students = parseInt(document.getElementById("simStudents").value);
    const delay = parseFloat(document.getElementById("simDelay").value);
    const mode = document.getElementById("simMode").value;

    const badge = document.getElementById("terminalStatusBadge");
    badge.className = "badge bg-warning text-dark";
    badge.textContent = "Ejecutando...";

    appendLog("info", `>>> Iniciando prueba individual: Modo=${mode.toUpperCase()}, Cupos=${quota}, Estudiantes=${students}, Pausa=${delay}s`);

    try {
        const response = await fetch("/api/simulate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                total_quota: quota,
                num_students: students,
                artificial_delay: delay,
                mode: mode,
                course_code: "IS100"
            })
        });

        const data = await response.json();
        if (!data.success) {
            alert("Error: " + data.message);
            badge.className = "badge bg-danger";
            badge.textContent = "Error";
            return;
        }

        const m = data.metrics;

        // Renderizar eventos en consola
        if (m.events && m.events.length > 0) {
            m.events.forEach(ev => {
                appendLog(ev.event_type, ev.message);
            });
        }

        appendLog("info", `=== Simulación completada: ${m.status_label}. Tiempo: ${m.total_time}s ===`);
        updateMetricCards(m);

        badge.className = "badge bg-success";
        badge.textContent = "Finalizado";

    } catch (err) {
        appendLog("inconsistent", "Error de red o ejecución: " + err.message);
        badge.className = "badge bg-danger";
        badge.textContent = "Fallo";
    }
}

async function runComparativeSimulation() {
    const quota = parseInt(document.getElementById("simQuota").value);
    const students = parseInt(document.getElementById("simStudents").value);
    const delay = parseFloat(document.getElementById("simDelay").value);

    const badge = document.getElementById("terminalStatusBadge");
    badge.className = "badge bg-primary";
    badge.textContent = "Ejecutando 3 Versiones...";

    appendLog("info", `========================================================================`);
    appendLog("info", `INICIANDO COMPARATIVA CON PARÁMETROS IDÉNTICOS:`);
    appendLog("info", `Cupos=${quota}, Estudiantes=${students}, Pausa=${delay}s`);
    appendLog("info", `========================================================================`);

    try {
        const response = await fetch("/api/compare", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                total_quota: quota,
                num_students: students,
                artificial_delay: delay,
                course_code: "IS100"
            })
        });

        const data = await response.json();
        if (!data.success) {
            alert("Error en comparativa: " + data.message);
            badge.className = "badge bg-danger";
            badge.textContent = "Error";
            return;
        }

        const comp = data.comparison;

        // Mostrar resumen en consola
        for (const [key, m] of Object.entries(comp)) {
            appendLog("info", `[${m.mode.toUpperCase()}] Inscritos: ${m.successful_enrollments}/${m.initial_quota} | Sobreinscripciones: ${m.oversubscriptions} | Inconsistencias: ${m.inconsistencies} | Tiempo: ${m.total_time}s | ${m.status_label}`);
        }

        // Actualizar tarjetas con la última o mutex
        updateMetricCards(comp.mutex || comp.unsafe);

        // Mostrar gráficos comparativos
        renderComparativeCharts(comp);

        badge.className = "badge bg-success";
        badge.textContent = "Comparativa Lista";

    } catch (err) {
        appendLog("inconsistent", "Error de ejecución: " + err.message);
        badge.className = "badge bg-danger";
        badge.textContent = "Fallo";
    }
}

function renderComparativeCharts(comp) {
    const section = document.getElementById("comparativeChartsSection");
    section.style.display = "flex";

    const labels = ["Sin Protección", "Mutex (Lock)", "Semáforo Binario"];
    const modes = ["unsafe", "mutex", "semaforo"];

    const enrolledData = modes.map(m => comp[m] ? comp[m].successful_enrollments : 0);
    const oversubData = modes.map(m => comp[m] ? comp[m].oversubscriptions : 0);
    const timesData = modes.map(m => comp[m] ? comp[m].total_time : 0);

    // Gráfico 1: Inscritos vs Sobreinscripciones
    const ctx1 = document.getElementById("chartEnrollmentComparison").getContext("2d");
    if (enrollmentChart) enrollmentChart.destroy();

    enrollmentChart = new Chart(ctx1, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [
                {
                    label: "Inscripciones Exitosas",
                    data: enrolledData,
                    backgroundColor: "rgba(13, 110, 253, 0.75)",
                    borderColor: "#0d6efd",
                    borderWidth: 1
                },
                {
                    label: "Sobreinscripciones (Anomalías)",
                    data: oversubData,
                    backgroundColor: "rgba(220, 53, 69, 0.85)",
                    borderColor: "#dc3545",
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: true }
            }
        }
    });

    // Gráfico 2: Tiempos de Ejecución
    const ctx2 = document.getElementById("chartTimeComparison").getContext("2d");
    if (timeChart) timeChart.destroy();

    timeChart = new Chart(ctx2, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [
                {
                    label: "Tiempo Total (segundos)",
                    data: timesData,
                    backgroundColor: [
                        "rgba(255, 193, 7, 0.8)",
                        "rgba(25, 135, 84, 0.8)",
                        "rgba(13, 202, 240, 0.8)"
                    ],
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}

function resetSimulatorState() {
    clearTerminal();
    document.getElementById("metricInitialQuota").textContent = "-";
    document.getElementById("metricNumStudents").textContent = "-";
    document.getElementById("metricSuccessful").textContent = "-";
    document.getElementById("metricRejected").textContent = "-";
    document.getElementById("metricFinalQuota").textContent = "-";
    document.getElementById("metricOversubscriptions").textContent = "-";
    document.getElementById("metricInconsistencies").textContent = "-";
    document.getElementById("metricTotalTime").textContent = "-";
    document.getElementById("metricAvgWait").textContent = "-";
    document.getElementById("metricMaxWait").textContent = "-";
    document.getElementById("metricStatusLabel").textContent = "Reiniciado";
    document.getElementById("metricStatusLabel").className = "badge bg-secondary";
    document.getElementById("comparativeChartsSection").style.display = "none";
}
