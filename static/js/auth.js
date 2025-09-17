// Authentication JavaScript

// Tab switching
function showLogin() {
    document.getElementById('login-form').classList.add('active');
    document.getElementById('register-form').classList.remove('active');
    document.querySelectorAll('.tab-btn')[0].classList.add('active');
    document.querySelectorAll('.tab-btn')[1].classList.remove('active');
}

function showRegister() {
    document.getElementById('login-form').classList.remove('active');
    document.getElementById('register-form').classList.add('active');
    document.querySelectorAll('.tab-btn')[0].classList.remove('active');
    document.querySelectorAll('.tab-btn')[1].classList.add('active');
}

// Password visibility toggle
function togglePassword(inputId) {
    const input = document.getElementById(inputId);
    const button = input.parentElement.querySelector('.toggle-password');
    const icon = button.querySelector('i');
    
    if (input.type === 'password') {
        input.type = 'text';
        icon.className = 'fas fa-eye-slash';
    } else {
        input.type = 'password';
        icon.className = 'fas fa-eye';
    }
}

// Password strength checker
function checkPasswordStrength(password) {
    let score = 0;
    let feedback = 'Muy débil';
    
    if (password.length >= 8) score++;
    if (password.match(/[a-z]/)) score++;
    if (password.match(/[A-Z]/)) score++;
    if (password.match(/[0-9]/)) score++;
    if (password.match(/[^a-zA-Z0-9]/)) score++;
    
    switch (score) {
        case 0:
        case 1:
            feedback = 'Muy débil';
            break;
        case 2:
            feedback = 'Débil';
            break;
        case 3:
            feedback = 'Regular';
            break;
        case 4:
            feedback = 'Buena';
            break;
        case 5:
            feedback = 'Muy fuerte';
            break;
    }
    
    return { score, feedback };
}

// Update password strength indicator
function updatePasswordStrength() {
    const password = document.getElementById('register-password').value;
    const strengthFill = document.getElementById('strength-fill');
    const strengthText = document.getElementById('strength-text');
    
    if (!password) {
        strengthFill.className = 'strength-fill';
        strengthText.textContent = 'Ingresa una contraseña';
        return;
    }
    
    const { score, feedback } = checkPasswordStrength(password);
    
    strengthFill.className = 'strength-fill';
    strengthText.textContent = feedback;
    
    switch (score) {
        case 0:
        case 1:
            strengthFill.classList.add('weak');
            break;
        case 2:
            strengthFill.classList.add('fair');
            break;
        case 3:
            strengthFill.classList.add('good');
            break;
        case 4:
        case 5:
            strengthFill.classList.add('strong');
            break;
    }
}

// Handle login form submission
async function handleLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    const loginBtn = document.getElementById('login-btn');
    
    // Validate inputs
    if (!email || !password) {
        showNotification('Por favor completa todos los campos', 'error', 'Campos requeridos');
        return;
    }
    
    // Disable button and show loading
    loginBtn.disabled = true;
    loginBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Iniciando sesión...';
    
    try {
        const result = await api.login(email, password);
        showNotification('¡Bienvenido de vuelta!', 'success', 'Inicio de sesión exitoso');
        
        // Redirect to dashboard
        setTimeout(() => {
            window.location.href = '/dashboard';
        }, 1000);
        
    } catch (error) {
        console.error('Login error:', error);
        showNotification(error.message, 'error', 'Error de autenticación');
    } finally {
        // Re-enable button
        loginBtn.disabled = false;
        loginBtn.innerHTML = '<i class="fas fa-sign-in-alt"></i> Iniciar Sesión';
    }
}

// Handle register form submission
async function handleRegister(event) {
    event.preventDefault();
    
    const username = document.getElementById('register-username').value;
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;
    const confirmPassword = document.getElementById('register-confirm-password').value;
    const registerBtn = document.getElementById('register-btn');
    
    // Validate inputs
    if (!username || !email || !password || !confirmPassword) {
        showNotification('Por favor completa todos los campos', 'error', 'Campos requeridos');
        return;
    }
    
    // Validate passwords match
    if (password !== confirmPassword) {
        showNotification('Las contraseñas no coinciden', 'error', 'Error de validación');
        return;
    }
    
    // Check password strength
    const { score } = checkPasswordStrength(password);
    if (score < 3) {
        showNotification('La contraseña debe ser más fuerte', 'warning', 'Contraseña débil');
        return;
    }
    
    // Disable button and show loading
    registerBtn.disabled = true;
    registerBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Registrando...';
    
    try {
        await api.register({
            username: username,
            email: email,
            password: password
        });
        
        showNotification('Cuenta creada exitosamente. Ahora puedes iniciar sesión.', 'success', 'Registro exitoso');
        
        // Switch to login tab
        setTimeout(() => {
            showLogin();
            document.getElementById('login-email').value = email;
        }, 1500);
        
    } catch (error) {
        console.error('Register error:', error);
        showNotification(error.message, 'error', 'Error en el registro');
    } finally {
        // Re-enable button
        registerBtn.disabled = false;
        registerBtn.innerHTML = '<i class="fas fa-user-plus"></i> Registrarse';
    }
}

// Initialize auth page
document.addEventListener('DOMContentLoaded', function() {
    // Check if already authenticated
    if (isAuthenticated()) {
        window.location.href = '/dashboard';
        return;
    }
    
    // Add password strength checker
    const passwordInput = document.getElementById('register-password');
    if (passwordInput) {
        passwordInput.addEventListener('input', updatePasswordStrength);
    }
    
    // Add form event listeners
    const loginForm = document.querySelector('#login-form form');
    const registerForm = document.querySelector('#register-form form');
    
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }
});
