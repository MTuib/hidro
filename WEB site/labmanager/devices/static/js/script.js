let chart = null;
let ultimaTaula = 0;
let ultimaGrafica = 0;

function mostrarError(container, message) {
    const paragraph = document.createElement("p");
    paragraph.setAttribute("role", "alert");
    paragraph.textContent = message;
    container.replaceChildren(paragraph);
}

function urlDades(kind, projectId, deviceId, magnitud, dataInici, dataFinal, page) {
    const params = new URLSearchParams();
    if (magnitud) params.set("magnitud", magnitud);
    if (dataInici) params.set("data_inici", dataInici);
    if (dataFinal) params.set("data_final", dataFinal);
    if (page) params.set("page", page);
    return `/project/${projectId}/${deviceId}/${kind}/?${params}`;
}

async function consultar(url, format) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 30000);
    try {
        const response = await fetch(url, {
            signal: controller.signal,
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "Accept": format === "json" ? "application/json" : "text/html",
            },
        });
        const type = response.headers.get("content-type") || "";
        if (!response.ok) {
            let message = "No s'ha pogut completar la consulta. Torna-ho a provar.";
            let data = null;
            if (type.includes("application/json")) {
                data = await response.json().catch(() => null);
                if (typeof data?.error === "string") message = data.error;
            } else if (type.includes("text/plain")) {
                message = (await response.text()) || message;
            }
            if (response.status === 401 && data?.login_url) {
                window.location.assign(data.login_url);
            }
            throw new Error(message);
        }
        if (format === "json") {
            if (!type.includes("application/json")) {
                throw new Error("El web ha retornat un format inesperat.");
            }
            return await response.json();
        }
        if (!type.includes("text/html")) {
            throw new Error("El web ha retornat un format inesperat.");
        }
        return await response.text();
    } catch (error) {
        if (error.name === "AbortError") {
            throw new Error("La consulta tarda massa. Torna-ho a provar.");
        }
        if (error instanceof TypeError) {
            throw new Error("No es pot connectar amb el web. Comprova la connexió.");
        }
        if (error instanceof SyntaxError) {
            throw new Error("El web ha retornat un JSON no vàlid.");
        }
        throw error;
    } finally {
        clearTimeout(timer);
    }
}

async function carregarPagina(pagina, magnitud, projectId, deviceId, dataInici, dataFinal) {
    const container = document.getElementById("taula");
    const peticio = ++ultimaTaula;
    container.innerHTML = '<div class="skeleton skeleton-table"></div>';
    try {
        const html = await consultar(
            urlDades("dades", projectId, deviceId, magnitud, dataInici, dataFinal, pagina), "html",
        );
        if (peticio === ultimaTaula) container.innerHTML = html;
    } catch (error) {
        if (peticio === ultimaTaula) mostrarError(container, error.message);
    }
}

async function carregarGrafica(magnitud, projectId, deviceId, dataInici, dataFinal) {
    const container = document.getElementById("grafica_container");
    const peticio = ++ultimaGrafica;
    if (chart) { chart.destroy(); chart = null; }
    container.innerHTML = '<div class="skeleton skeleton-chart"></div>';
    try {
        const data = await consultar(
            urlDades("grafica", projectId, deviceId, magnitud, dataInici, dataFinal), "json",
        );
        if (peticio !== ultimaGrafica) return;
        if (!data || !Array.isArray(data.labels) || !Array.isArray(data.values)
            || data.labels.length !== data.values.length
            || !data.labels.every(value => typeof value === "string")
            || !data.values.every(value => typeof value === "number" && Number.isFinite(value))) {
            throw new Error("Les dades de la gràfica tenen un format inesperat.");
        }
        if (typeof Chart === "undefined") {
            throw new Error("No s'ha pogut carregar la llibreria de la gràfica.");
        }
        container.innerHTML = '<canvas id="grafica" height="100"></canvas>';
        chart = new Chart(document.getElementById("grafica"), {
            type: "line",
            data: {
                labels: data.labels,
                datasets: [{ label: magnitud, data: data.values, tension: 0.2 }],
            },
        });
    } catch (error) {
        if (peticio === ultimaGrafica) mostrarError(container, error.message);
    }
}

document.addEventListener("click", function (event) {
    const btn = event.target.closest(".btn-pagina");
    if (!btn) return;
    carregarPagina(btn.dataset.pagina, btn.dataset.magnitud, btn.dataset.project,
        btn.dataset.device, btn.dataset.dataInici, btn.dataset.dataFinal);
});

document.addEventListener("DOMContentLoaded", function () {
    const select = document.getElementById("magnitude");
    if (!select) return;
    const inici = document.getElementById("data_inici");
    const final = document.getElementById("data_final");
    function actualitzar() {
        if (!select.value) return;
        const args = [select.value, select.dataset.projectId, select.dataset.deviceId,
            inici.value, final.value];
        carregarPagina(1, ...args);
        carregarGrafica(...args);
    }
    select.addEventListener("change", actualitzar);
    inici.addEventListener("change", actualitzar);
    final.addEventListener("change", actualitzar);
    document.getElementById("btnDescarregarCSV").addEventListener("click", function () {
        window.location.href = urlDades("csv-raw", this.dataset.projectId,
            this.dataset.deviceId, null, inici.value, final.value);
    });
});
