/**
 * STREAMZY_PLAY - Archivo Maestro de Lógica Frontend (v2.1)
 * Optimizado para despliegue y producción.
 */

// --- CONFIGURACIÓN ---
const API_URL = window.location.hostname === 'localhost' 
    ? 'http://127.0.0.1:8000' 
    : 'https://tu-api-en-la-nube.com'; // Cambia esto al publicar

// --- ESTADO GLOBAL ---
let carrito = JSON.parse(localStorage.getItem('carrito')) || [];

// --- FUNCIONES DE GESTIÓN DE UI ---
function actualizarContador() {
    const contador = document.getElementById('carrito-contador');
    if (contador) {
        contador.textContent = carrito.reduce((sum, item) => sum + item.cantidad, 0);
    }
}

function actualizarMenu() {
    const authMenu = document.getElementById('auth-menu');
    if (!authMenu) return;

    const token = localStorage.getItem('token');
    authMenu.innerHTML = token 
        ? `<button onclick="cerrarSesion()" class="btn-nav">Cerrar Sesión</button>`
        : `<a href="/login.html" class="btn-nav">Iniciar Sesión</a>`;
}

function cerrarSesion() {
    localStorage.removeItem('token');
    localStorage.removeItem('carrito');
    window.location.reload();
}

// --- LÓGICA DE PRODUCTOS ---
async function cargarProductos() {
    const contenedor = document.getElementById('lista-productos');
    if (!contenedor) return;

    try {
        const response = await fetch(`${API_URL}/products/`);
        if (!response.ok) throw new Error('Error al conectar con la API');

        const productos = await response.json();
        contenedor.innerHTML = '';

        productos.forEach(p => {
            const variante = p.variantes?.[0];
            const precio = variante ? (p.precio_base + variante.precio_adicional) : p.precio_base;

            const card = document.createElement('div');
            card.className = 'producto-card';
            card.innerHTML = `
                ${p.imagen_url ? `<img src="${p.imagen_url}" alt="${p.titulo}" loading="lazy">` : ''}
                <h3>${p.titulo}</h3>
                <p>${p.descripcion}</p>
                <div class="precio"><strong>$${precio.toFixed(2)}</strong></div>
            `;

            const btn = document.createElement('button');
            btn.className = 'btn-comprar';
            btn.textContent = variante ? 'Agregar al carrito' : 'Sin stock';
            btn.disabled = !variante;
            btn.onclick = () => variante && agregarAlCarrito(variante.id, p.titulo, precio, btn);
            
            card.appendChild(btn);
            contenedor.appendChild(card);
        });
    } catch (error) {
        contenedor.innerHTML = `<p class="error">${error.message}</p>`;
    }
}

function agregarAlCarrito(id, titulo, precio, btnElement) {
    const index = carrito.findIndex(item => item.id === id);
    if (index > -1) carrito[index].cantidad += 1;
    else carrito.push({ id, titulo, precio, cantidad: 1 });
    
    localStorage.setItem('carrito', JSON.stringify(carrito));
    actualizarContador();
    
    // Feedback visual
    btnElement.textContent = '¡Agregado!';
    setTimeout(() => btnElement.textContent = 'Agregar al carrito', 1200);
}

// --- LÓGICA DE CHECKOUT ---
async function procesarCheckout() {
    const btn = document.getElementById('btn-finalizar');
    const token = localStorage.getItem('token');
    
    if (!token) return window.location.href = '/login.html';
    if (carrito.length === 0) return alert("Tu carrito está vacío.");

    btn.disabled = true;
    btn.textContent = 'Procesando...';

    try {
        const response = await fetch(`${API_URL}/orders/checkout`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}` 
            },
            body: JSON.stringify(carrito.map(i => ({ variante_id: i.id, cantidad: i.cantidad })))
        });

        if (!response.ok) throw new Error('No se pudo procesar el pago.');

        alert("¡Compra exitosa! Gracias por tu confianza.");
        carrito = [];
        localStorage.removeItem('carrito');
        location.reload();
    } catch (err) {
        alert(err.message);
        btn.disabled = false;
        btn.textContent = 'Finalizar Compra';
    }
}

// --- INICIALIZACIÓN ---
document.addEventListener('DOMContentLoaded', () => {
    cargarProductos();
    actualizarContador();
    actualizarMenu();
    
    const btnFinalizar = document.getElementById('btn-finalizar');
    if (btnFinalizar) btnFinalizar.onclick = procesarCheckout;
});