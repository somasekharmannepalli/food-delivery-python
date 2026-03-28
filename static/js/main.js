let currentUser = null;

async function checkAuth() {
    const response = await fetch('/auth/me');
    const result = await response.json();
    const userActions = document.getElementById('user-actions');
    
    if (result.authenticated) {
        currentUser = result.user;
        userActions.innerHTML = `
            <div class="navbar-profile">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
                <ul class="nav-profile-dropdown">
                    <li onclick="location.href='/orders'">Orders</li>
                    <hr>
                    <li onclick="logout()">Logout</li>
                </ul>
            </div>
        `;
        updateCartDot(result.user.cartData);
    }
}

function updateCartDot(cartData) {
    const dot = document.getElementById('cart-dot');
    const total = Object.values(cartData).reduce((a, b) => a + b, 0);
    dot.style.display = total > 0 ? 'block' : 'none';
}

async function logout() {
    await fetch('/auth/logout', { method: 'POST' });
    location.href = '/';
}

async function addToCart(itemId) {
    const response = await fetch('/api/cart/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ itemId })
    });
    const result = await response.json();
    if (result.success) {
        checkAuth(); // Refresh cart dot
    } else {
        location.href = '/login';
    }
}

window.addEventListener('load', checkAuth);
