function escapeCsv(value) {
    const text = String(value ?? "");
    return `"${text.replace(/"/g, '""')}"`;
}

function sanitizarNombreArchivo(nombre) {
    return String(nombre || "ruta")
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .replace(/[^a-zA-Z0-9_-]+/g, "_")
        .replace(/^_+|_+$/g, "")
        .toLowerCase() || "ruta";
}

function formatearMoneda(valor) {
    const numero = Number(valor || 0);
    return new Intl.NumberFormat("es-GT", {
        style: "currency",
        currency: "USD",
        minimumFractionDigits: 2,
    }).format(numero);
}

function abrirModal() {
    if (!rutaModal) {
        return;
    }
    rutaModal.classList.add("mostrar");
    rutaModal.setAttribute("aria-hidden", "false");
}

function cerrarModal() {
    if (!rutaModal) {
        return;
    }
    rutaModal.classList.remove("mostrar");
    rutaModal.setAttribute("aria-hidden", "true");
}

async function verDetalles(idRuta) {
    try {
        const response = await fetch(`/rutas/detalles/${idRuta}`);
        const data = await response.json();

        if (!data.success) {
            alert(data.error || "No se pudieron cargar los detalles de la ruta.");
            return;
        }

        const ruta = data.ruta;
        const paquetes = data.paquetes || [];

        modalTitulo.textContent = ruta.nombre_ruta;
        cantidadPaquetesModal.textContent = `${paquetes.length} paquetes`;
        detalleRuta.innerHTML = `
            <p><strong>ID</strong>Ruta #${ruta.id_ruta}</p>
            <p><strong>Departamento</strong>${ruta.departamento || "Sin departamento"}</p>
            <p><strong>Municipio</strong>${ruta.municipio || "Sin municipio"}</p>
            <p><strong>Tienda</strong>${ruta.tienda || "Sin tienda"}</p>
            <p><strong>Creación</strong>${ruta.fecha_creacion || "Sin fecha"}</p>
        `;

        cuerpoPaquetes.innerHTML = paquetes.length
            ? paquetes.map((paquete) => `
        <tr>
            <td>${paquete.posicion}</td>
            <td>${paquete.codigo_barras}</td>
            <td>${paquete.nombre_cliente}</td>
            <td>${paquete.telefono || "-"}</td>
            <td>${paquete.email || "-"}</td>
            <td>${paquete.departamento || "-"}</td>
            <td>${paquete.municipio || "-"}</td>
            <td>${paquete.tienda || "-"}</td>
            <td>${formatearMoneda(paquete.precio)}</td>
        </tr>
        `).join("")
                : `
            <tr>
                <td colspan="9">Esta ruta todavía no tiene paquetes registrados.</td>
            </tr>
        `;

        abrirModal();
    } catch (error) {
        console.error("Error al cargar detalles:", error);
        alert("Ocurrió un problema al cargar los detalles de la ruta.");
    }
}

async function descargarRuta(idRuta) {
    try {
        const response = await fetch(`/rutas/detalles/${idRuta}`);
        const data = await response.json();

        if (!data.success) {
            alert(data.error || "No se pudo descargar la ruta.");
            return;
        }

        const ruta = data.ruta;
        const paquetes = data.paquetes || [];
        const lineas = [
            ["Ruta", ruta.nombre_ruta],
            ["Departamento", ruta.departamento || ""],
            ["Tienda", ruta.tienda || ""],
            ["Fecha", ruta.fecha_creacion || ""],
            [],
            ["Posicion", "Codigo barras", "Cliente", "Telefono", "Email", "Precio"],
            ...paquetes.map((paquete) => [
                paquete.posicion,
                paquete.codigo_barras,
                paquete.nombre_cliente,
                paquete.telefono || "",
                paquete.email || "",
                paquete.precio || "$",
            ]),
        ];

        const csv = lineas
            .map((fila) => fila.map(escapeCsv).join(";"))
            .join("\n");

        const blob = new Blob(["\ufeff", csv], { type: "text/csv;charset=utf-8;" });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");

        link.href = url;
        link.download = `${sanitizarNombreArchivo(ruta.nombre_ruta)}.csv`;
        document.body.appendChild(link);
        link.click();
        link.remove();
        URL.revokeObjectURL(url);
    } catch (error) {
        console.error("Error al descargar ruta:", error);
        alert("No se pudo generar la descarga.");
    }
}

async function imprimirRuta(idRuta) {
    try {
        const response = await fetch(`/rutas/detalles/${idRuta}`);
        const data = await response.json();

        if (!data.success) {
            alert(data.error || "No se pudo cargar la ruta para imprimir.");
            return;
        }

        const ruta = data.ruta;
        const paquetes = data.paquetes || [];

        // Crear una ventana nueva formateada para impresión
        const ventanaImpresion = window.open('', '_blank');
        ventanaImpresion.document.write(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>Imprimir Ruta - ${ruta.nombre_ruta}</title>
                <style>
                    body { font-family: Arial, sans-serif; padding: 20px; color: #000; }
                    table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                    th, td { border: 1px solid #ccc; padding: 10px; text-align: left; font-size: 14px; }
                    th { background-color: #f2f2f2; }
                    .header { margin-bottom: 20px; border-bottom: 2px solid #000; padding-bottom: 10px; }
                    h2, p { margin: 5px 0; }
                </style>
            </head>
            <body>
                <div class="header">
                    <h2>Ruta: ${ruta.nombre_ruta}</h2>
                    <p><strong>Departamento:</strong> ${ruta.departamento || "N/A"}</p>
                    <p><strong>Municipio:</strong> ${ruta.municipio || "N/A"}</p>
                    <p><strong>Tienda:</strong> ${ruta.tienda || "N/A"}</p>
                    <p><strong>Fecha:</strong> ${ruta.fecha_creacion || "N/A"}</p>
                </div>
                <h3>Paquetes en esta ruta (${paquetes.length})</h3>
                <table>
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Código de Barras</th>
                            <th>Departamento</th>
                            <th>Municipio</th>
                            <th>Tienda</th>
                            <th>Cliente</th>
                            <th>Teléfono</th>
                            <th>Precio</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${paquetes.map(p => `
                            <tr>
                                <td>${p.posicion}</td>
                                <td>${p.codigo_barras}</td>
                                <td>${p.nombre_cliente}</td>
                                <td>${p.telefono || "-"}</td>
                                <td>${formatearMoneda(p.precio)}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
                <script>
                    window.onload = function() {
                        window.print();
                        window.onafterprint = function() { window.close(); }
                    }
                </script>
            </body>
            </html>
        `);
        ventanaImpresion.document.close();
    } catch (error) {
        console.error("Error al imprimir ruta:", error);
        alert("No se pudo generar la impresión.");
    }
}

async function cargarTiendasFiltro(idDepartamento) {
    const selectTienda = document.getElementById("filtroTienda");
    if (!selectTienda) {
        return;
    }

    if (!idDepartamento) {
        selectTienda.innerHTML = '<option value="">Todas las tiendas</option>';
        selectTienda.disabled = true;
        return;
    }

    try {
        const response = await fetch(`/rutas/get_tiendas/${idDepartamento}`);
        const data = await response.json();

        if (!data.success) {
            throw new Error(data.error || "Error al cargar las tiendas.");
        }

        const selected = selectTienda.dataset.selected || "";
        selectTienda.innerHTML = ['<option value="">Todas las tiendas</option>']
            .concat(
                data.tiendas.map(
                    (tienda) =>
                        `<option value="${tienda.id_tienda}" ${String(tienda.id_tienda) === String(selected) ? "selected" : ""}>${tienda.nombre}</option>`
                )
            )
            .join("");
        selectTienda.disabled = false;
    } catch (error) {
        console.error("Error al cargar tiendas del filtro:", error);
        selectTienda.innerHTML = '<option value="">Todas las tiendas</option>';
        selectTienda.disabled = true;
    }
}

document.addEventListener("DOMContentLoaded", () => {
    rutaModal = document.getElementById("modalDetalles");
    detalleRuta = document.getElementById("detallesRuta");
    cuerpoPaquetes = document.getElementById("cuerpoPaquetes");
    modalTitulo = document.getElementById("modalTitulo");
    cantidadPaquetesModal = document.getElementById("cantidadPaquetesModal");

    const selectDepartamento = document.getElementById("filtroDepartamento");
    const selectTienda = document.getElementById("filtroTienda");

    if (selectDepartamento && selectTienda) {
        const selectedDepartamento = selectDepartamento.dataset.selected || "";
        if (selectedDepartamento) {
            cargarTiendasFiltro(selectedDepartamento);
        }

        selectDepartamento.addEventListener("change", (event) => {
            const departamentoId = event.target.value;
            selectTienda.dataset.selected = "";
            cargarTiendasFiltro(departamentoId);
        });
    }

    if (rutaModal) {
        rutaModal.addEventListener("click", (event) => {
            if (event.target === rutaModal) {
                cerrarModal();
            }
        });
    }

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
            cerrarModal();
        }
    });
});

window.verDetalles = verDetalles;
window.descargarRuta = descargarRuta;
window.imprimirRuta = imprimirRuta;
window.cerrarModal = cerrarModal;
