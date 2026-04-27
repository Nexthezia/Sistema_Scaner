// Clase para manejar la gestión de rutas
class GestorRutas {
    constructor() {
        this.paquetes = [];
        this.rutaData = {
            nombre_ruta: '',
            id_departamento: '',
            id_tienda: ''
        };
        
        this.init();
    }

    init() {
        this.elementos = {
            nombreRuta: document.getElementById('nombreRuta'),
            departamento: document.getElementById('departamento'),
            tienda: document.getElementById('tienda'),
            codigoBarras: document.getElementById('codigoBarras'),
            listaPaquetes: document.getElementById('listaPaquetes'),
            contadorPaquetes: document.getElementById('contadorPaquetes'),
            btnLimpiar: document.getElementById('btnLimpiar'),
            btnGuardar: document.getElementById('btnGuardar')
        };

        this.cargarDelLocalStorage();
        this.configurarEventos();
        this.actualizarVista();
        
        // Mantener el foco en el input de escaneo
        this.elementos.codigoBarras.focus();
    }

    configurarEventos() {
        // Cambio de departamento
        this.elementos.departamento.addEventListener('change', (e) => {
            this.rutaData.id_departamento = e.target.value;
            this.rutaData.id_tienda = '';
            this.elementos.tienda.value = '';
            this.guardarEnLocalStorage();
            
            if (e.target.value) {
                this.cargarTiendas(e.target.value);
            } else {
                this.elementos.tienda.disabled = true;
                this.elementos.tienda.innerHTML = '<option value="">Seleccionar tienda...</option>';
            }
        });

        // Cambio de tienda
        this.elementos.tienda.addEventListener('change', (e) => {
            this.rutaData.id_tienda = e.target.value;
            this.guardarEnLocalStorage();
            this.actualizarBotonesGuardar();
        });

        // Cambio de nombre de ruta
        this.elementos.nombreRuta.addEventListener('input', (e) => {
            this.rutaData.nombre_ruta = e.target.value;
            this.guardarEnLocalStorage();
            this.actualizarBotonesGuardar();
        });

        // Escaneo de código de barra
        this.elementos.codigoBarras.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.procesarEscaneo();
            }
        });

        // Botones
        this.elementos.btnLimpiar.addEventListener('click', () => this.limpiarTodo());
        this.elementos.btnGuardar.addEventListener('click', () => this.guardarRuta());

        // Devolver foco al input de escaneo cuando el usuario termine de escribir en otro campo
        this.elementos.nombreRuta.addEventListener('blur', () => {
            this.elementos.codigoBarras.focus();
        });

        this.elementos.departamento.addEventListener('blur', () => {
            this.elementos.codigoBarras.focus();
        });

        this.elementos.tienda.addEventListener('blur', () => {
            this.elementos.codigoBarras.focus();
        });
    }

    async procesarEscaneo() {
        const codigo = this.elementos.codigoBarras.value.trim();

        if (!codigo) {
            this.mostrarAlerta('Por favor escanea un código', 'advertencia');
            return;
        }

        // Verificar si ya existe
        if (this.paquetes.some(p => p.codigo_barras === codigo)) {
            this.mostrarAlerta('Este código ya fue escaneado', 'advertencia');
            this.elementos.codigoBarras.value = '';
            return;
        }

        try {
            const response = await fetch(`/rutas/validar_codigo/${codigo}`);
            const data = await response.json();

            if (data.success) {
                this.agregarPaquete(data.id_paquete, data.nombre_cliente, data.codigo_barras);
                this.elementos.codigoBarras.value = '';
                this.mostrarAlerta(`Paquete de ${data.nombre_cliente} agregado ✓`, 'exito');
            } else {
                this.mostrarAlerta(`Código no encontrado: ${codigo}`, 'error');
                this.elementos.codigoBarras.value = '';
            }
        } catch (error) {
            console.error('Error:', error);
            this.mostrarAlerta('Error al validar el código', 'error');
            this.elementos.codigoBarras.value = '';
        }
    }

    agregarPaquete(id_paquete, nombre_cliente, codigo_barras) {
        this.paquetes.push({
            id_paquete,
            nombre_cliente,
            codigo_barras
        });

        this.guardarEnLocalStorage();
        this.actualizarVista();
    }

    removerPaquete(id_paquete) {
        this.paquetes = this.paquetes.filter(p => p.id_paquete !== id_paquete);
        this.guardarEnLocalStorage();
        this.actualizarVista();
    }

    actualizarVista() {
        // Actualizar contador
        this.elementos.contadorPaquetes.textContent = this.paquetes.length;

        // Actualizar lista
        if (this.paquetes.length === 0) {
            this.elementos.listaPaquetes.innerHTML = '<p class="mensaje-vacio">No hay paquetes agregados aún</p>';
        } else {
            this.elementos.listaPaquetes.innerHTML = this.paquetes.map((paq, index) => `
                <div class="ItemPaquete">
                    <div class="DatosPaquete">
                        <span class="NumeroPaquete">${index + 1}</span>
                        <span class="CodigoBarras">${paq.codigo_barras}</span>
                        <span class="NombreCliente">${paq.nombre_cliente}</span>
                    </div>
                    <button class="BtnRemover" onclick="gestor.removerPaquete(${paq.id_paquete})">
                        Remover
                    </button>
                </div>
            `).join('');
        }

        this.actualizarBotonesGuardar();
    }

    actualizarBotonesGuardar() {
        const tieneNombre = this.rutaData.nombre_ruta.trim() !== '';
        const tieneDepartamento = this.rutaData.id_departamento !== '';
        const tieneTienda = this.rutaData.id_tienda !== '';
        const tienePaquetes = this.paquetes.length > 0;

        this.elementos.btnGuardar.disabled = !(tieneNombre && tieneDepartamento && tieneTienda && tienePaquetes);
    }

    async cargarTiendas(id_departamento) {
        try {
            const response = await fetch(`/rutas/get_tiendas/${id_departamento}`);
            const data = await response.json();

            if (data.success) {
                const tiendas = data.tiendas;
                this.elementos.tienda.innerHTML = '<option value="">Seleccionar tienda...</option>' +
                    tiendas.map(t => `<option value="${t.id_tienda}">${t.nombre}</option>`).join('');
                this.elementos.tienda.disabled = false;
            } else {
                this.mostrarAlerta('Error al cargar tiendas', 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            this.mostrarAlerta('Error al cargar tiendas', 'error');
        }
    }

    async guardarRuta() {
        if (!this.validarDatos()) {
            return;
        }

        try {
            const response = await fetch('/rutas/guardar_ruta', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    nombre_ruta: this.rutaData.nombre_ruta,
                    id_departamento: this.rutaData.id_departamento,
                    id_tienda: this.rutaData.id_tienda,
                    paquetes: this.paquetes.map(p => p.id_paquete)
                })
            });

            const data = await response.json();

            if (data.success) {
                this.mostrarAlerta(data.mensaje + ' ✓', 'exito');
                this.limpiarTodo();
            } else {
                this.mostrarAlerta(data.error || 'Error al guardar la ruta', 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            this.mostrarAlerta('Error al guardar la ruta', 'error');
        }
    }

    validarDatos() {
        if (!this.rutaData.nombre_ruta.trim()) {
            this.mostrarAlerta('Por favor ingresa un nombre para la ruta', 'advertencia');
            return false;
        }

        if (!this.rutaData.id_departamento) {
            this.mostrarAlerta('Por favor selecciona un departamento', 'advertencia');
            return false;
        }

        if (!this.rutaData.id_tienda) {
            this.mostrarAlerta('Por favor selecciona una tienda', 'advertencia');
            return false;
        }

        if (this.paquetes.length === 0) {
            this.mostrarAlerta('Por favor escanea al menos un paquete', 'advertencia');
            return false;
        }

        return true;
    }

    limpiarTodo() {
        if (confirm('¿Estás seguro de que deseas limpiar todo? Los cambios no guardados se perderán.')) {
            this.paquetes = [];
            this.rutaData = {
                nombre_ruta: '',
                id_departamento: '',
                id_tienda: ''
            };

            this.elementos.nombreRuta.value = '';
            this.elementos.departamento.value = '';
            this.elementos.tienda.value = '';
            this.elementos.tienda.disabled = true;
            this.elementos.codigoBarras.value = '';

            localStorage.removeItem('gestorRutas');
            this.actualizarVista();
            this.elementos.codigoBarras.focus();
            this.mostrarAlerta('Todo ha sido limpiado', 'advertencia');
        }
    }

    guardarEnLocalStorage() {
        localStorage.setItem('gestorRutas', JSON.stringify({
            paquetes: this.paquetes,
            rutaData: this.rutaData
        }));
    }

    cargarDelLocalStorage() {
        const datos = localStorage.getItem('gestorRutas');
        if (datos) {
            try {
                const parsed = JSON.parse(datos);
                this.paquetes = parsed.paquetes || [];
                this.rutaData = parsed.rutaData || {
                    nombre_ruta: '',
                    id_departamento: '',
                    id_tienda: ''
                };

                // Restaurar valores en el formulario
                this.elementos.nombreRuta.value = this.rutaData.nombre_ruta;
                this.elementos.departamento.value = this.rutaData.id_departamento;

                // Si hay departamento guardado, cargar sus tiendas
                if (this.rutaData.id_departamento) {
                    this.cargarTiendas(this.rutaData.id_departamento).then(() => {
                        this.elementos.tienda.value = this.rutaData.id_tienda;
                    });
                }
            } catch (error) {
                console.error('Error al cargar del localStorage:', error);
            }
        }
    }

    mostrarAlerta(mensaje, tipo = 'info') {
        const alerta = document.createElement('div');
        alerta.className = `Alerta ${tipo}`;
        alerta.textContent = mensaje;

        const container = document.querySelector('.SeccionLista');
        container.insertBefore(alerta, container.firstChild);

        // Remover alerta después de 3 segundos
        setTimeout(() => {
            alerta.style.animation = 'slideIn 0.3s ease-out reverse';
            setTimeout(() => alerta.remove(), 300);
        }, 3000);
    }
}

// Instanciar gestor cuando el DOM esté listo
let gestor;
document.addEventListener('DOMContentLoaded', () => {
    gestor = new GestorRutas();
});
