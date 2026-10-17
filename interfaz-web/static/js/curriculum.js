/**
 * Lógica para la Malla Curricular Universitaria y Trazado de Prerrequisitos en SVG.
 */

document.addEventListener("DOMContentLoaded", function () {
    const wrapper = document.getElementById("curriculumWrapper");
    const svg = document.getElementById("prereq-svg");
    const togglePrereq = document.getElementById("togglePrereqLines");

    // Trazar líneas de prerrequisitos al cargar
    setTimeout(drawPrerequisiteLines, 100);

    // Redibujar en scroll y redimensionamiento
    if (wrapper) {
        wrapper.addEventListener("scroll", drawPrerequisiteLines);
    }
    window.addEventListener("resize", drawPrerequisiteLines);

    if (togglePrereq) {
        togglePrereq.addEventListener("change", function () {
            svg.style.display = this.checked ? "block" : "none";
        });
    }

    // Efecto de iluminación al pasar el cursor sobre una materia
    setupCardHoverHighlight();
});

function drawPrerequisiteLines() {
    const wrapper = document.getElementById("curriculumWrapper");
    const svg = document.getElementById("prereq-svg");
    if (!wrapper || !svg) return;

    // Ajustar dimensiones del SVG al contenedor total de la cuadrícula
    const grid = document.getElementById("curriculumGrid");
    if (!grid) return;

    svg.setAttribute("width", grid.scrollWidth);
    svg.setAttribute("height", grid.scrollHeight);
    svg.style.width = grid.scrollWidth + "px";
    svg.style.height = grid.scrollHeight + "px";

    // Limpiar trazados anteriores
    svg.innerHTML = `
        <defs>
            <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 1 L 10 5 L 0 9 z" fill="#94a3b8" />
            </marker>
            <marker id="arrow-highlight" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                <path d="M 0 1 L 10 5 L 0 9 z" fill="#0d6efd" />
            </marker>
        </defs>
    `;

    const cards = document.querySelectorAll(".course-card");
    const wrapperRect = grid.getBoundingClientRect();

    cards.forEach(card => {
        const prereqsRaw = card.getAttribute("data-prerequisites");
        if (!prereqsRaw) return;

        let prereqs = [];
        try {
            prereqs = JSON.parse(prereqsRaw);
        } catch (e) {
            return;
        }

        const toCode = card.getAttribute("data-code");
        const toRect = card.getBoundingClientRect();

        // Punto de destino: centro del lado izquierdo de la tarjeta actual
        const toX = toRect.left - wrapperRect.left;
        const toY = toRect.top - wrapperRect.top + toRect.height / 2;

        prereqs.forEach(fromCode => {
            const fromCard = document.getElementById(`course-${fromCode}`);
            if (!fromCard) return;

            const fromRect = fromCard.getBoundingClientRect();
            // Punto de origen: centro del lado derecho de la tarjeta prerrequisito
            const fromX = fromRect.right - wrapperRect.left;
            const fromY = fromRect.top - wrapperRect.top + fromRect.height / 2;

            // Curva Bézier suave entre ambas tarjetas
            const deltaX = Math.abs(toX - fromX) * 0.5;
            const cp1X = fromX + deltaX;
            const cp1Y = fromY;
            const cp2X = toX - deltaX;
            const cp2Y = toY;

            const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
            path.setAttribute("d", `M ${fromX} ${fromY} C ${cp1X} ${cp1Y}, ${cp2X} ${cp2Y}, ${toX} ${toY}`);
            path.setAttribute("class", "prereq-line");
            path.setAttribute("marker-end", "url(#arrow)");
            path.setAttribute("data-from", fromCode);
            path.setAttribute("data-to", toCode);

            svg.appendChild(path);
        });
    });
}

function setupCardHoverHighlight() {
    const cards = document.querySelectorAll(".course-card");
    cards.forEach(card => {
        card.addEventListener("mouseenter", function () {
            const code = this.getAttribute("data-code");
            const lines = document.querySelectorAll(".prereq-line");
            lines.forEach(l => {
                if (l.getAttribute("data-from") === code || l.getAttribute("data-to") === code) {
                    l.classList.add("highlight");
                    l.setAttribute("marker-end", "url(#arrow-highlight)");
                } else {
                    l.style.opacity = "0.2";
                }
            });
        });

        card.addEventListener("mouseleave", function () {
            const lines = document.querySelectorAll(".prereq-line");
            lines.forEach(l => {
                l.classList.remove("highlight");
                l.setAttribute("marker-end", "url(#arrow)");
                l.style.opacity = "1";
            });
        });
    });
}

function centerCurriculumView() {
    const wrapper = document.getElementById("curriculumWrapper");
    if (wrapper) {
        // Desplazar suavemente hacia el 5to semestre
        const sem5 = document.querySelector('.semester-column[data-semester="5"]');
        if (sem5) {
            sem5.scrollIntoView({ behavior: "smooth", inline: "center", block: "nearest" });
        }
    }
}

/**
 * Abrir Modal de Asignatura e interactuar con la API
 */
async function openCourseModal(courseCode) {
    try {
        const response = await fetch(`/api/course/${courseCode}`);
        const data = await response.json();
        if (!data.success) {
            alert(data.message);
            return;
        }

        const course = data.course;
        const hasPrereqs = data.has_prerequisites;
        const unmet = data.unmet_prerequisites;

        // Título y Badges
        document.getElementById("modalCourseTitle").textContent = course.name;
        document.getElementById("modalCourseCode").textContent = course.code;
        document.getElementById("modalCourseCredits").textContent = `${course.credits} Créditos`;
        document.getElementById("modalCourseDesc").textContent = course.description;

        const statusBadge = document.getElementById("modalCourseStatus");
        statusBadge.className = "badge ms-1";
        if (course.status === "cursada") {
            statusBadge.classList.add("bg-success");
            statusBadge.textContent = "Cursada";
        } else if (course.status === "inscrita") {
            statusBadge.classList.add("bg-warning", "text-dark");
            statusBadge.textContent = `Inscrita (${course.enrolled_group || 'G1'})`;
        } else if (course.status === "disponible") {
            statusBadge.classList.add("bg-danger");
            statusBadge.style.backgroundColor = "#fd7e14";
            statusBadge.textContent = "Disponible";
        } else {
            statusBadge.classList.add("bg-danger");
            statusBadge.textContent = "No Habilitada";
        }

        // Prerrequisitos
        const prereqBox = document.getElementById("modalPrereqContainer");
        prereqBox.innerHTML = "";
        if (!course.prerequisites || course.prerequisites.length === 0) {
            prereqBox.innerHTML = `<span class="badge bg-light text-muted border">Sin prerrequisitos</span>`;
        } else {
            course.prerequisites.forEach(p => {
                const isMet = !unmet.some(u => u.startsWith(p));
                const pBadge = document.createElement("span");
                pBadge.className = `badge ${isMet ? 'bg-success' : 'bg-danger'}`;
                pBadge.textContent = `${p} (${isMet ? 'Aprobada' : 'Pendiente'})`;
                prereqBox.appendChild(pBadge);
            });
        }

        // Alerta
        const alertBox = document.getElementById("modalAlertBox");
        alertBox.className = "alert small mb-3 d-none";
        if (course.status === "no_habilitada") {
            alertBox.classList.remove("d-none");
            alertBox.classList.add("alert-danger");
            alertBox.innerHTML = `<i class="bi bi-exclamation-triangle-fill me-1"></i> <strong>Asignatura bloqueada:</strong> Debe cursar y aprobar primero los prerrequisitos: ${unmet.join(", ")}.`;
        } else if (course.status === "cursada") {
            alertBox.classList.remove("d-none");
            alertBox.classList.add("alert-success");
            alertBox.innerHTML = `<i class="bi bi-check-circle-fill me-1"></i> Esta materia ya fue cursada y aprobada (Calificación: ${course.grade || '4.0'}).`;
        }

        // Grupos y Horarios
        const tbody = document.getElementById("modalGroupsBody");
        tbody.innerHTML = "";

        if (!course.groups || course.groups.length === 0) {
            tbody.innerHTML = `<tr><td colspan="7" class="text-center text-muted">No hay grupos ofertados actualmente.</td></tr>`;
        } else {
            course.groups.forEach(g => {
                const tr = document.createElement("tr");

                // Formatear horarios
                const scheds = g.schedules.map(s => `${s.day} ${s.start_time}-${s.end_time}`).join("<br>");

                // Botón de acción
                let actionBtn = "";
                if (course.status === "cursada") {
                    actionBtn = `<span class="text-muted small">Aprobada</span>`;
                } else if (course.status === "inscrita") {
                    if (course.enrolled_group === g.group_id) {
                        actionBtn = `<button class="btn btn-outline-danger btn-sm" onclick="cancelEnrollment('${course.code}')"><i class="bi bi-x-circle"></i> Cancelar</button>`;
                    } else {
                        actionBtn = `<span class="text-muted small">Inscrita en otro grupo</span>`;
                    }
                } else if (course.status === "disponible") {
                    if (g.available_quota > 0) {
                        actionBtn = `<button class="btn btn-primary btn-sm" onclick="enrollCourse('${course.code}', '${g.group_id}')"><i class="bi bi-plus-circle"></i> Inscribir</button>`;
                    } else {
                        actionBtn = `<span class="badge bg-secondary">Sin cupos</span>`;
                    }
                } else {
                    actionBtn = `<span class="text-muted small">Bloqueada</span>`;
                }

                tr.innerHTML = `
                    <td class="fw-bold">${g.group_id}</td>
                    <td>${g.teacher}</td>
                    <td><span class="badge bg-light text-dark border">${g.room}</span></td>
                    <td class="small">${scheds}</td>
                    <td>${g.total_quota}</td>
                    <td class="fw-bold ${g.available_quota > 0 ? 'text-success' : 'text-danger'}">${g.available_quota}</td>
                    <td>${actionBtn}</td>
                `;
                tbody.appendChild(tr);
            });
        }

        const modal = new bootstrap.Modal(document.getElementById("courseDetailModal"));
        modal.show();

    } catch (err) {
        alert("Error al cargar detalles de la materia: " + err.message);
    }
}

async function enrollCourse(courseCode, groupId) {
    if (!confirm(`¿Desea confirmar la inscripción de ${courseCode} en el Grupo ${groupId}?`)) return;

    try {
        const response = await fetch("/api/enroll", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ course_code: courseCode, group_id: groupId })
        });
        const data = await response.json();
        if (data.success) {
            alert("✓ " + data.message);
            location.reload();
        } else {
            alert("✗ Error de inscripción: " + data.message);
        }
    } catch (err) {
        alert("Error de conexión: " + err.message);
    }
}

async function cancelEnrollment(courseCode) {
    if (!confirm(`¿Está seguro de cancelar la inscripción de la asignatura ${courseCode}?`)) return;

    try {
        const response = await fetch("/api/cancel", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ course_code: courseCode })
        });
        const data = await response.json();
        if (data.success) {
            alert("✓ " + data.message);
            location.reload();
        } else {
            alert("✗ Error al cancelar: " + data.message);
        }
    } catch (err) {
        alert("Error de conexión: " + err.message);
    }
}
