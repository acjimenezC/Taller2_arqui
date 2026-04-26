// ============================================
// APLICACIÓN FRONTEND JAVASCRIPT
// ============================================
// Interfaz de usuario para el chat con IA y catálogo de productos.
// Funciones principales:
//   - Gestionar sesiones de chat
//   - Enviar mensajes al backend
//   - Mostrar historial de conversaciones
//   - Cargar y filtrar productos disponibles
//   - Mantener estado en localStorage
// Comunicación con API REST en http://127.0.0.1:8000

// ============================================
// CONFIG
// ============================================
const API_BASE_URL = 'http://127.0.0.1:8000';
const DEFAULT_SESSION_ID_KEY = 'ecommerce_chat_session_id';

// ============================================
// STATE
// ============================================
let currentSessionId = null;
let products = [];
let isLoading = false;

// ============================================
// DOM ELEMENTS
// ============================================
const chatMessagesDiv = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const btnSend = document.getElementById('btnSend');
const sessionIdSpan = document.getElementById('sessionId');
const productsList = document.getElementById('productsList');
const btnLoadProducts = document.getElementById('btnLoadProducts');
const btnNewSession = document.getElementById('btnNewSession');
const loadingIndicator = document.getElementById('loadingIndicator');

// ============================================
// INITIALIZATION
// ============================================
document.addEventListener('DOMContentLoaded', async () => {
    // Generar o recuperar session ID
    initializeSession();
    
    // Cargar productos
    await loadProducts();
    
    // Cargar historial del chat
    await loadChatHistory();
    
    // Event listeners
    btnSend.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !isLoading) {
            sendMessage();
        }
    });
    btnLoadProducts.addEventListener('click', loadProducts);
    btnNewSession.addEventListener('click', createNewSession);
});

// ============================================
// SESSION MANAGEMENT
// ============================================
function initializeSession() {
    let sessionId = localStorage.getItem(DEFAULT_SESSION_ID_KEY);
    
    if (!sessionId) {
        sessionId = generateSessionId();
        localStorage.setItem(DEFAULT_SESSION_ID_KEY, sessionId);
    }
    
    currentSessionId = sessionId;
    sessionIdSpan.textContent = sessionId;
}

function generateSessionId() {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

function createNewSession() {
    const newSessionId = generateSessionId();
    localStorage.setItem(DEFAULT_SESSION_ID_KEY, newSessionId);
    currentSessionId = newSessionId;
    sessionIdSpan.textContent = newSessionId;
    
    // Limpiar chat visible
    chatMessagesDiv.innerHTML = `
        <div class="message assistant-message">
            <div class="message-avatar">🤖</div>
            <div class="message-content">
                <p>¡Hola! Soy tu asesor de zapatos. ¿En qué puedo ayudarte hoy? Puedo recomendarte productos según marca, talla, categoría o presupuesto.</p>
            </div>
        </div>
    `;
    
    messageInput.focus();
    console.log(`✅ Nueva sesión creada: ${newSessionId}`);
}

// ============================================
// PRODUCTS
// ============================================
async function loadProducts() {
    try {
        btnLoadProducts.disabled = true;
        productsList.innerHTML = '<p class="loading">Cargando productos...</p>';
        
        const response = await fetch(`${API_BASE_URL}/products`);
        if (!response.ok) {
            throw new Error(`Error ${response.status}: No se pudieron cargar los productos`);
        }
        
        products = await response.json();
        
        if (products.length === 0) {
            productsList.innerHTML = '<p class="loading">No hay productos disponibles.</p>';
            return;
        }
        
        renderProducts();
        console.log(`✅ ${products.length} productos cargados`);
    } catch (error) {
        console.error('❌ Error al cargar productos:', error);
        productsList.innerHTML = `<p class="loading" style="color: red;">Error: ${error.message}</p>`;
    } finally {
        btnLoadProducts.disabled = false;
    }
}

function renderProducts() {
    productsList.innerHTML = products.map(product => `
        <div class="product-item">
            <div class="product-name">${product.name}</div>
            <div class="product-meta">
                <strong>${product.brand}</strong> • ${product.category}
            </div>
            <div class="product-meta">
                Talla: ${product.size} • Color: ${product.color}
            </div>
            <div class="product-price">$${product.price.toFixed(2)}</div>
            <div class="product-stock ${product.stock > 0 ? 'in-stock' : 'out-of-stock'}">
                ${product.stock > 0 ? `✅ En stock (${product.stock})` : '❌ Agotado'}
            </div>
        </div>
    `).join('');
}

// ============================================
// CHAT MESSAGING
// ============================================
async function sendMessage() {
    const message = messageInput.value.trim();
    
    if (!message || isLoading) {
        return;
    }
    
    // Mostrar mensaje del usuario
    addMessageToChat('user', message);
    messageInput.value = '';
    messageInput.disabled = true;
    btnSend.disabled = true;
    showLoadingIndicator(true);
    
    try {
        // Enviar mensaje a la API
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: currentSessionId,
                message: message,
            }),
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `Error ${response.status}`);
        }
        
        const data = await response.json();
        
        // Mostrar respuesta del asistente
        addMessageToChat('assistant', data.response);
        
        console.log('✅ Mensaje enviado y respuesta recibida');
    } catch (error) {
        console.error('❌ Error al enviar mensaje:', error);
        addMessageToChat('assistant', `❌ Error: ${error.message}\n\nIntenta nuevamente o contacta con soporte.`);
    } finally {
        messageInput.disabled = false;
        btnSend.disabled = false;
        showLoadingIndicator(false);
        messageInput.focus();
    }
}

async function loadChatHistory() {
    try {
        const response = await fetch(`${API_BASE_URL}/chat/history?session_id=${currentSessionId}`);
        
        if (!response.ok) {
            // No hay historial, que es normal para sesión nueva
            return;
        }
        
        const history = await response.json();
        
        if (history.length === 0) {
            return; // Sesión vacía
        }
        
        // Limpiar el mensaje inicial
        chatMessagesDiv.innerHTML = '';
        
        // Agregar todos los mensajes del historial
        history.forEach(msg => {
            addMessageToChat(msg.role, msg.content);
        });
        
        console.log(`✅ Historial cargado: ${history.length} mensajes`);
    } catch (error) {
        console.error('❌ Error al cargar historial:', error);
        // Sin historial es aceptable
    }
}

function addMessageToChat(role, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role === 'user' ? 'user-message' : 'assistant-message'}`;
    
    const avatar = role === 'user' ? '👤' : '🤖';
    const now = new Date().toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' });
    
    // Procesar el contenido para destacar productos si es necesario
    const processedContent = content;
    
    messageDiv.innerHTML = `
        <div class="message-avatar">${avatar}</div>
        <div>
            <div class="message-content">
                ${escapeHtml(processedContent).split('\n').map(line => `<p>${line}</p>`).join('')}
            </div>
            <div class="message-time">${now}</div>
        </div>
    `;
    
    chatMessagesDiv.appendChild(messageDiv);
    
    // Auto-scroll al último mensaje
    chatMessagesDiv.scrollTop = chatMessagesDiv.scrollHeight;
}

function showLoadingIndicator(show) {
    isLoading = show;
    if (show) {
        loadingIndicator.classList.remove('hidden');
    } else {
        loadingIndicator.classList.add('hidden');
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ============================================
// HEALTH CHECK (opcional)
// ============================================
async function checkApiHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            console.log('✅ API está disponible');
            return true;
        } else {
            console.warn('⚠️ API respondió con status:', response.status);
            return false;
        }
    } catch (error) {
        console.error('❌ No se puede conectar a la API:', error);
        alert('⚠️ No se puede conectar con el servidor. Asegúrate de que la API esté corriendo en http://127.0.0.1:8000');
        return false;
    }
}

// Verificar salud de la API al cargar
window.addEventListener('load', checkApiHealth);
