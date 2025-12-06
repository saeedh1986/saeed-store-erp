const API_URL = '/api/v1';

function isAuthenticated() {
    const token = localStorage.getItem('access_token');
    return !!token;
}

function normalizeFormBody(data) {
    const formBody = [];
    for (const property in data) {
        const encodedKey = encodeURIComponent(property);
        const encodedValue = encodeURIComponent(data[property]);
        formBody.push(encodedKey + "=" + encodedValue);
    }
    return formBody.join("&");
}

async function handleLogin(event) {
    event.preventDefault();
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const errorMsg = document.getElementById('errorMsg');

    try {
        const response = await fetch(`${API_URL}/login/access-token`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
            },
            body: normalizeFormBody({
                username: email,
                password: password
            })
        });

        const data = await response.json();

        if (response.ok) {
            localStorage.setItem('access_token', data.access_token);
            window.location.href = '/';
        } else {
            errorMsg.style.display = 'block';
            errorMsg.textContent = data.detail || 'Login failed';
        }
    } catch (error) {
        console.error('Login error:', error);
        errorMsg.style.display = 'block';
        errorMsg.textContent = 'Network error occurred';
    }
}

function logout() {
    localStorage.removeItem('access_token');
    window.location.href = '/login';
}

// Add Authorization header to authenticated requests
async function secureFetch(url, options = {}) {
    const token = localStorage.getItem('access_token');
    if (!token) {
        window.location.href = '/login';
        return;
    }

    const headers = {
        ...options.headers,
        'Authorization': `Bearer ${token}`
    };

    const response = await fetch(url, { ...options, headers });

    if (response.status === 401) {
        logout();
        return;
    }

    return response;
}
