/**
 * Funciones utilitarias para la aplicación de Biblioteca
 * Compartidas entre todas las páginas del frontend
 */

// ============================================
// UTILIDADES DE FECHA
// ============================================

/**
 * Formatea una fecha en formato legible para España
 * @param {string|Date} fecha - Fecha a formatear
 * @returns {string} Fecha formateada (ej: "27/04/2026")
 */
function formatearFecha(fecha) {
    if (!fecha) return '-';
    const d = new Date(fecha);
    return d.toLocaleDateString('es-ES');
}

/**
 * Formatea una fecha con hora
 * @param {string|Date} fecha - Fecha a formatear
 * @returns {string} Fecha y hora formateada
 */
function formatearFechaHora(fecha) {
    if (!fecha) return '-';
    const d = new Date(fecha);
    return d.toLocaleString('es-ES');
}

/**
 * Obtiene la fecha actual en formato YYYY-MM-DD para inputs date
 * @returns {string} Fecha actual
 */
function getFechaActual() {
    return new Date().toISOString().split('T')[0];
}

/**
 * Calcula los días entre dos fechas
 * @param {string|Date} fechaInicio - Fecha de inicio
 * @param {string|Date} fechaFin - Fecha de fin
 * @returns {number} Número de días
 */
function diasEntre(fechaInicio, fechaFin) {
    const inicio = new Date(fechaInicio);
    const fin = new Date(fechaFin);
    const diffTime = Math.abs(fin - inicio);
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
}

/**
 * Verifica si una fecha está vencida
 * @param {string|Date} fecha - Fecha a verificar
 * @returns {boolean} True si está vencida
 */
function estaVencida(fecha) {
    if (!fecha) return false;
    return new Date(fecha) < new Date();
}

// ============================================
// UTILIDADES DE VALIDACIÓN
// ============================================

/**
 * Valida que una cadena no esté vacía
 * @param {string} valor - Valor a validar
 * @returns {boolean} True si es válido
 */
function noVacio(valor) {
    return valor !== null && valor !== undefined && valor.toString().trim() !== '';
}

/**
 * Valida formato de email
 * @param {string} email - Email a validar
 * @returns {boolean} True si es válido
 */
function esEmailValido(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}

/**
 * Valida que un número sea positivo
 * @param {number} numero - Número a validar
 * @returns {boolean} True si es positivo
 */
function esPositivo(numero) {
    return !isNaN(numero) && numero > 0;
}

/**
 * Valida longitud de cadena
 * @param {string} valor - Valor a validar
 * @param {number} min - Longitud mínima
 * @param {number} max - Longitud máxima
 * @returns {boolean} True si está en rango
 */
function validarLongitud(valor, min, max) {
    const len = valor ? valor.toString().length : 0;
    return len >= min && len <= max;
}

// ============================================
// UTILIDADES DE UI
// ============================================

/**
 * Muestra un mensaje de alerta simple
 * @param {string} mensaje - Mensaje a mostrar
 * @param {string} tipo - Tipo: 'success', 'error', 'warning', 'info'
 */
function mostrarAlerta(mensaje, tipo = 'info') {
    const colores = {
        success: 'bg-green-100 border-green-500 text-green-700',
        error: 'bg-red-100 border-red-500 text-red-700',
        warning: 'bg-yellow-100 border-yellow-500 text-yellow-700',
        info: 'bg-blue-100 border-blue-500 text-blue-700'
    };
    
    const alerta = document.createElement('div');
    alerta.className = `fixed top-4 right-4 ${colores[tipo]} border-l-4 p-4 rounded shadow-lg z-50 max-w-md`;
    alerta.textContent = mensaje;
    
    document.body.appendChild(alerta);
    
    // Auto-remover después de 5 segundos
    setTimeout(() => {
        alerta.remove();
    }, 5000);
}

/**
 * Detecta el tipo de mensaje según el texto
 * @param {string} mensaje - Mensaje a analizar
 * @returns {string} Tipo: success, error, warning, info
 */
function detectarTipoMensaje(mensaje) {
    if (!mensaje) return 'info';
    const texto = mensaje.toString().trim().toLowerCase();
    if (texto.startsWith('✅') || texto.startsWith('exito') || texto.includes('correctamente') || texto.includes('guardado')) {
        return 'success';
    }
    if (texto.startsWith('❌') || texto.startsWith('error') || texto.includes('no se pudo') || texto.includes('algo salió mal')) {
        return 'error';
    }
    if (texto.startsWith('⚠️') || texto.startsWith('advertencia') || texto.startsWith('atención')) {
        return 'warning';
    }
    return 'info';
}

/**
 * Muestra un mensaje centralizado y decorado
 * @param {string} mensaje - Texto del mensaje
 * @param {string} [tipo] - success, error, warning, info
 */
function mostrarMensaje(mensaje, tipo) {
    const mensajeFinal = mensaje?.toString() || '';
    const tipoFinal = tipo || detectarTipoMensaje(mensajeFinal);
    mostrarAlerta(mensajeFinal, tipoFinal);
}

// Reemplaza globalmente alert() para usar el estilo decorado
window.alert = function(mensaje) {
    mostrarMensaje(mensaje);
};

/**
 * Muestra/oculta un elemento
 * @param {string} id - ID del elemento
 * @param {boolean} mostrar - True para mostrar
 */
function toggleElemento(id, mostrar) {
    const el = document.getElementById(id);
    if (el) {
        if (mostrar) {
            el.classList.remove('hidden');
        } else {
            el.classList.add('hidden');
        }
    }
}

/**
 * Crea un spinner de carga
 * @returns {HTMLElement} Elemento spinner
 */
function crearSpinner() {
    const spinner = document.createElement('div');
    spinner.id = 'globalSpinner';
    spinner.className = 'fixed inset-0 bg-black/30 flex items-center justify-center z-50';
    spinner.innerHTML = `
        <div class="bg-white p-6 rounded-xl shadow-xl flex flex-col items-center">
            <div class="animate-spin rounded-full h-12 w-12 border-4 border-amber-500 border-t-transparent"></div>
            <p class="mt-3 text-gray-600">Cargando...</p>
        </div>
    `;
    return spinner;
}

/**
 * Muestra el spinner global
 */
function mostrarSpinner() {
    const existente = document.getElementById('globalSpinner');
    if (!existente) {
        document.body.appendChild(crearSpinner());
    }
}

/**
 * Oculta el spinner global
 */
function ocultarSpinner() {
    const spinner = document.getElementById('globalSpinner');
    if (spinner) {
        spinner.remove();
    }
}

/**
 * Confirma una acción con el usuario
 * @param {string} mensaje - Mensaje de confirmación
 * @returns {Promise<boolean>} True si confirmó
 */
async function confirmar(mensaje) {
    return confirm(mensaje);
}

// ============================================
// UTILIDADES DE DATOS
// ============================================

/**
 * Escapa caracteres HTML para prevenir XSS
 * @param {string} str - Cadena a escapar
 * @returns {string} Cadena escapada
 */
function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/[&<>]/g, function(m) {
        if (m === '&') return '&amp;';
        if (m === '<') return '&lt;';
        if (m === '>') return '&gt;';
        return m;
    });
}

/**
 * Capitaliza la primera letra de cada palabra
 * @param {string} texto - Texto a capitalizar
 * @returns {string} Texto capitalizado
 */
function capitalizar(texto) {
    if (!texto) return '';
    return texto.toLowerCase().split(' ').map(palabra => 
        palabra.charAt(0).toUpperCase() + palabra.slice(1)
    ).join(' ');
}

/**
 * Trunca un texto a una longitud máxima
 * @param {string} texto - Texto a truncar
 * @param {number} maxLength - Longitud máxima
 * @returns {string} Texto truncado
 */
function truncar(texto, maxLength = 50) {
    if (!texto || texto.length <= maxLength) return texto;
    return texto.substring(0, maxLength) + '...';
}

/**
 * Formatea un número como moneda
 * @param {number} numero - Número a formatear
 * @returns {string} Número formateado
 */
function formatearMoneda(numero) {
    return new Intl.NumberFormat('es-ES', {
        style: 'currency',
        currency: 'EUR'
    }).format(numero);
}

/**
 * Genera un ID único (basado en timestamp + random)
 * @returns {string} ID único
 */
function generarId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
}

// ============================================
// UTILIDADES DE STORAGE
// ============================================

/**
 * Guarda datos en localStorage de forma segura
 * @param {string} key - Clave
 * @param {any} value - Valor a guardar
 */
function guardarStorage(key, value) {
    try {
        localStorage.setItem(key, JSON.stringify(value));
    } catch (e) {
        console.error('Error guardando en localStorage:', e);
    }
}

/**
 * Recupera datos de localStorage
 * @param {string} key - Clave
 * @param {any} defaultValue - Valor por defecto
 * @returns {any} Valor recuperado
 */
function obtenerStorage(key, defaultValue = null) {
    try {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : defaultValue;
    } catch (e) {
        console.error('Error leyendo localStorage:', e);
        return defaultValue;
    }
}

/**
 * Elimina un elemento de localStorage
 * @param {string} key - Clave a eliminar
 */
function eliminarStorage(key) {
    localStorage.removeItem(key);
}

/**
 * Limpia todo el storage relacionado con la sesión
 */
function limpiarSesion() {
    eliminarStorage('token');
    eliminarStorage('user');
    eliminarStorage('role');
}

// ============================================
// UTILIDADES DE API
// ============================================

/**
 * Wrapper para fetch con manejo de errores comunes
 * @param {string} url - URL de la API
 * @param {object} options - Opciones de fetch
 * @returns {Promise<Response>} Respuesta
 */
async function apiFetch(url, options = {}) {
    const token = localStorage.getItem('token');
    const headers = {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` }),
        ...options.headers
    };
    
    const response = await fetch(url, { ...options, headers });
    
    // Manejar errores comunes
    if (response.status === 401) {
        limpiarSesion();
        window.location.href = 'login.html';
        throw new Error('Sesión expirada');
    }
    
    if (response.status === 403) {
        mostrarAlerta('No tienes permisos para realizar esta acción', 'error');
        throw new Error('Sin permisos');
    }
    
    return response;
}

/**
 * Obtiene el usuario actual del storage
 * @returns {object|null} Usuario actual
 */
function getUsuarioActual() {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
}

/**
 * Obtiene el rol del usuario actual
 * @returns {string|null} Rol del usuario
 */
function getRolActual() {
    return localStorage.getItem('role');
}

/**
 * Verifica si el usuario es administrador
 * @returns {boolean} True si es administrador
 */
function esAdministrador() {
    return getRolActual() === 'Administrador';
}

// ============================================
// INICIALIZACIÓN
// ============================================

// Verificar autenticación en páginas protegidas
function verificarAutenticacion() {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'login.html';
        return false;
    }
    return true;
}

// Exportar funciones para uso global
window.formatearFecha = formatearFecha;
window.formatearFechaHora = formatearFechaHora;
window.getFechaActual = getFechaActual;
window.diasEntre = diasEntre;
window.estaVencida = estaVencida;
window.noVacio = noVacio;
window.esEmailValido = esEmailValido;
window.esPositivo = esPositivo;
window.validarLongitud = validarLongitud;
window.mostrarAlerta = mostrarAlerta;
window.toggleElemento = toggleElemento;
window.mostrarSpinner = mostrarSpinner;
window.ocultarSpinner = ocultarSpinner;
window.confirmar = confirmar;
window.escapeHtml = escapeHtml;
window.capitalizar = capitalizar;
window.truncar = truncar;
window.formatearMoneda = formatearMoneda;
window.generarId = generarId;
window.guardarStorage = guardarStorage;
window.obtenerStorage = obtenerStorage;
window.eliminarStorage = eliminarStorage;
window.limpiarSesion = limpiarSesion;
window.apiFetch = apiFetch;
window.getUsuarioActual = getUsuarioActual;
window.getRolActual = getRolActual;
window.esAdministrador = esAdministrador;
window.verificarAutenticacion = verificarAutenticacion;