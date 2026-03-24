// Verifica autenticación y redirige si no hay token
function checkAuth() {
    const token = localStorage.getItem("token");
    if (!token) {
        window.location.href = "login.html";
        return null;
    }
    return token;
}

// Función centralizada para hacer peticiones autenticadas
async function apiFetch(url, options = {}) {
    const token = localStorage.getItem("token");
    if (!token) {
        window.location.href = "login.html";
        return;
    }

    const res = await fetch(url, {
        ...options,
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json",
            ...options.headers
        }
    });

    if (res.status === 401) {
        alert("Sesión expirada. Vuelve a iniciar sesión.");
        localStorage.clear();
        window.location.href = "login.html";
    }
    return res;
}

// Función para obtener el usuario actual (útil en otras páginas)
async function getCurrentUser() {
    const token = localStorage.getItem("token");
    if (!token) return null;
    const res = await fetch(`${API_URL}/auth/me`, {
        headers: { "Authorization": `Bearer ${token}` }
    });
    if (res.ok) return await res.json();
    return null;
}