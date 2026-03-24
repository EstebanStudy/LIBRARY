const API_URL = "http://127.0.0.1:8000";

async function login() {
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;
    const errorMsg = document.getElementById("error");

    if (!email || !password) {
        errorMsg.textContent = "Por favor, completa todos los campos";
        errorMsg.classList.remove("hidden");
        return;
    }

    try {
        const res = await fetch(`${API_URL}/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: new URLSearchParams({ username: email, password: password })
        });

        const data = await res.json();

        if (res.ok) {
            localStorage.setItem("token", data.access_token);
            localStorage.setItem("role", data.role);
            // Guardar userId (necesario para mostrar préstamos personales)
            if (data.user_id) localStorage.setItem("userId", data.user_id);
            window.location.href = "dashboard.html";
        } else {
            errorMsg.textContent = data.detail || "Credenciales incorrectas";
            errorMsg.classList.remove("hidden");
        }
    } catch (err) {
        errorMsg.textContent = "Error: El servidor FastAPI no responde (puerto 8000)";
        errorMsg.classList.remove("hidden");
    }
}

// Función auxiliar para obtener el usuario actual (si el backend tiene endpoint)
async function fetchUsuarioActual(token) {
    try {
        const res = await fetch(`${API_URL}/usuarios/me`, {
            headers: { "Authorization": `Bearer ${token}` }
        });
        if (res.ok) {
            const usuario = await res.json();
            localStorage.setItem("userId", usuario.Id);
        }
    } catch (err) {
        console.error("No se pudo obtener el usuario actual:", err);
    }
}