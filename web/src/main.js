import './style.css'
import API_URL, {
  fetchProducts,
  addToCart,
  login,
  register,
  fetchCart,
  removeFromCart,
  updateCartItem,
  checkout,
  fetchOrders
} from './api.js'

// App state
const state = {
  isLoggedIn: false,
  user: null,
  token: null,
  cart: [],
  products: [],
  currentOrder: null,
  isLoadingProducts: false,
}

// DOM Elements
const authBtn = document.getElementById('authBtn')
const authModal = document.getElementById('authModal')
const closeAuthBtn = document.getElementById('closeAuthBtn')
const loginForm = document.getElementById('loginForm')
const registerForm = document.getElementById('registerForm')
const switchToRegisterBtn = document.getElementById('switchToRegisterBtn')
const switchToLoginBtn = document.getElementById('switchToLoginBtn')
const loginFormElement = document.getElementById('loginFormElement')
const registerFormElement = document.getElementById('registerFormElement')
const productsGrid = document.getElementById('productsGrid')
const cartItems = document.getElementById('cartItems')
const checkoutBtn = document.getElementById('checkoutBtn')
const continueShoppingBtn = document.getElementById('continueShoppingBtn')
const orderConfirmation = document.getElementById('orderConfirmation')
const newOrderBtn = document.getElementById('newOrderBtn')
const viewOrdersBtn = document.getElementById('viewOrdersBtn')
const orderHistorySection = document.getElementById('orderHistorySection')
const backToCartBtn = document.getElementById('backToCartBtn')
const orderHistoryList = document.getElementById('orderHistoryList')

// Event Listeners
authBtn.addEventListener('click', () => {
  if (state.isLoggedIn) {
    logout()
  } else {
    authModal.classList.remove('hidden')
    loginForm.classList.remove('hidden')
    registerForm.classList.add('hidden')
  }
})

closeAuthBtn.addEventListener('click', () => {
  authModal.classList.add('hidden')
})

switchToRegisterBtn.addEventListener('click', () => {
  loginForm.classList.add('hidden')
  registerForm.classList.remove('hidden')
})

switchToLoginBtn.addEventListener('click', () => {
  registerForm.classList.add('hidden')
  loginForm.classList.remove('hidden')
})

loginFormElement.addEventListener('submit', handleLogin)
registerFormElement.addEventListener('submit', handleRegister)
checkoutBtn.addEventListener('click', handleCheckout)
viewOrdersBtn.addEventListener('click', showOrderHistory)
backToCartBtn.addEventListener('click', hideOrderHistory)

// Auth Functions
async function handleLogin(e) {
  e.preventDefault()
  const formData = new FormData(loginFormElement)
  const email = formData.get('email')
  const password = formData.get('password')

  // Get password from correct field
  const inputs = loginFormElement.querySelectorAll('input')
  const email_input = inputs[0].value
  const password_input = inputs[1].value

  try {
    authBtn.disabled = true
    const response = await login(email_input, password_input)

    // Store token in localStorage
    state.token = response.access_token
    localStorage.setItem('token', response.access_token)

    // Get user info
    const { getCurrentUser } = await import('./api.js')
    const user = await getCurrentUser(state.token)
    state.user = user
    state.isLoggedIn = true

    // Load user's cart
    const cartData = await fetchCart(state.token)
    state.cart = cartData.items

    // Clear forms and close modal
    loginFormElement.reset()
    registerFormElement.reset()
    authModal.classList.add('hidden')

    updateUI()
    showMessage(`Welcome, ${user.full_name}!`, 'success')
  } catch (error) {
    console.error('Login error:', error)
    showMessage('Login failed: ' + error.message, 'error')
  } finally {
    authBtn.disabled = false
  }
}

async function handleRegister(e) {
  e.preventDefault()
  const inputs = registerFormElement.querySelectorAll('input')
  const email = inputs[0].value
  const fullName = inputs[1].value
  const password = inputs[2].value

  try {
    authBtn.disabled = true
    await register(email, password, fullName)

    // Auto-login after registration
    const response = await login(email, password)
    state.token = response.access_token
    localStorage.setItem('token', response.access_token)

    const { getCurrentUser } = await import('./api.js')
    const user = await getCurrentUser(state.token)
    state.user = user
    state.isLoggedIn = true

    // Load user's cart
    const cartData = await fetchCart(state.token)
    state.cart = cartData.items

    loginFormElement.reset()
    registerFormElement.reset()
    authModal.classList.add('hidden')

    updateUI()
    showMessage(`Welcome, ${user.full_name}! Your account has been created.`, 'success')
  } catch (error) {
    console.error('Registration error:', error)
    showMessage('Registration failed: ' + error.message, 'error')
  } finally {
    authBtn.disabled = false
  }
}

function logout() {
  state.isLoggedIn = false
  state.user = null
  state.token = null
  state.cart = []
  localStorage.removeItem('token')
  updateUI()
  showMessage('You have been logged out', 'success')
}

// Cart Functions
async function handleCheckout() {
  if (!state.isLoggedIn) {
    alert('Please log in to checkout')
    return
  }

  if (state.cart.length === 0) {
    alert('Your cart is empty')
    return
  }

  try {
    checkoutBtn.disabled = true
    const order = await checkout(state.token)

    // Show order confirmation
    state.currentOrder = order
    displayOrderConfirmation(order)

    // Clear cart
    state.cart = []
    updateCart()
    showMessage('Order placed successfully!', 'success')
  } catch (error) {
    console.error('Checkout error:', error)
    showMessage('Checkout failed: ' + error.message, 'error')
  } finally {
    checkoutBtn.disabled = false
  }
}

function displayOrderConfirmation(order) {
  const confirmationHTML = `
    <h3>✓ Order Placed!</h3>
    <p>Thank you for your purchase.</p>
    <p>Order ID: <strong>#${order.id}</strong></p>
    <p>Total: <strong>$${order.total_price.toFixed(2)}</strong></p>
    <p>Status: <strong>${order.status}</strong></p>
    <h4>Items Ordered:</h4>
    <ul style="text-align: left; padding-left: 20px;">
      ${order.items.map(item => `
        <li>${item.product.name} x${item.quantity} @ $${item.price_at_purchase.toFixed(2)}</li>
      `).join('')}
    </ul>
    <button id="newOrderBtn" class="btn btn-primary full-width">Place Another Order</button>
  `

  orderConfirmation.innerHTML = confirmationHTML
  orderConfirmation.classList.remove('hidden')

  // Re-attach event listener
  document.getElementById('newOrderBtn').addEventListener('click', handleNewOrder)
}

function handleNewOrder() {
  orderConfirmation.classList.add('hidden')
  state.currentOrder = null
  updateCart()
}

async function showOrderHistory() {
  try {
    viewOrdersBtn.disabled = true
    const response = await fetchOrders(state.token)
    displayOrderHistory(response.items)
    orderHistorySection.classList.remove('hidden')
    document.querySelector('.cart-summary').classList.add('hidden')
    checkoutBtn.classList.add('hidden')
    continueShoppingBtn.classList.add('hidden')
  } catch (error) {
    console.error('Error fetching orders:', error)
    showMessage('Failed to load orders: ' + error.message, 'error')
  } finally {
    viewOrdersBtn.disabled = false
  }
}

function hideOrderHistory() {
  orderHistorySection.classList.add('hidden')
  document.querySelector('.cart-summary').classList.remove('hidden')
  checkoutBtn.classList.remove('hidden')
  continueShoppingBtn.classList.remove('hidden')
}

function displayOrderHistory(orders) {
  if (orders.length === 0) {
    orderHistoryList.innerHTML = '<p class="empty-message">No orders yet</p>'
    return
  }

  orderHistoryList.innerHTML = orders.map(order => `
    <div class="order-item">
      <div class="order-item-header">
        <span>Order #${order.id}</span>
        <span class="order-item-price">$${order.total_price.toFixed(2)}</span>
      </div>
      <div class="order-item-date">${new Date(order.created_at).toLocaleDateString()}</div>
      <span class="order-item-status">${order.status}</span>
      <div class="order-detail">
        <h4>Items:</h4>
        <ul>
          ${order.items.map(item => `
            <li>${item.product.name} x${item.quantity} @ $${item.price_at_purchase.toFixed(2)}</li>
          `).join('')}
        </ul>
      </div>
    </div>
  `).join('')
}

// Product Functions
async function loadProducts() {
  state.isLoadingProducts = true
  renderProducts()

  try {
    const response = await fetchProducts(0, 20)
    state.products = response.items
    renderProducts()
  } catch (error) {
    console.error('Failed to load products:', error)
    renderProductError('Failed to load products. Please refresh the page.')
  } finally {
    state.isLoadingProducts = false
  }
}

function renderProducts() {
  if (state.isLoadingProducts) {
    productsGrid.innerHTML = `
      <div class="product-card">
        <div class="product-placeholder">Loading products...</div>
      </div>
    `
    return
  }

  if (state.products.length === 0) {
    productsGrid.innerHTML = `
      <div class="product-card">
        <div class="product-placeholder">No products available</div>
      </div>
    `
    return
  }

  productsGrid.innerHTML = state.products.map(product => `
    <div class="product-card">
      <div class="product-image">
        📦 ${product.category?.name || 'Uncategorized'}
      </div>
      <div class="product-name">${product.name}</div>
      <div class="product-price">$${product.price.toFixed(2)}</div>
      <div class="product-description">${product.description || 'No description'}</div>
      <button class="btn btn-primary full-width" onclick="addProductToCart(${product.id})">
        Add to Cart
      </button>
    </div>
  `).join('')
}

function renderProductError(message) {
  productsGrid.innerHTML = `
    <div class="product-card">
      <div class="product-placeholder">${message}</div>
    </div>
  `
}

// Make addProductToCart globally available for onclick handlers
window.addProductToCart = async function(productId) {
  if (!state.isLoggedIn) {
    alert('Please log in to add items to your cart')
    authModal.classList.remove('hidden')
    return
  }

  try {
    const product = state.products.find(p => p.id === productId)
    if (!product) return

    await addToCart(productId, 1, state.token)

    // Add to local cart state
    const existingItem = state.cart.find(item => item.product_id === productId)
    if (existingItem) {
      existingItem.quantity += 1
    } else {
      state.cart.push({
        id: Date.now(),
        product_id: productId,
        quantity: 1,
        product: product,
      })
    }

    updateCart()
    showMessage('Added to cart!', 'success')
  } catch (error) {
    console.error('Error adding to cart:', error)
    showMessage('Failed to add to cart: ' + error.message, 'error')
  }
}

// UI Updates
function updateUI() {
  updateAuthBtn()
  updateCart()
  updateOrderHistoryButton()
}

function updateOrderHistoryButton() {
  if (state.isLoggedIn) {
    viewOrdersBtn.classList.remove('hidden')
  } else {
    viewOrdersBtn.classList.add('hidden')
    hideOrderHistory()
  }
}

function updateAuthBtn() {
  if (state.isLoggedIn) {
    authBtn.textContent = `Logout (${state.user?.full_name})`
    authBtn.classList.remove('btn-secondary')
    authBtn.classList.add('btn-primary')
  } else {
    authBtn.textContent = 'Login'
    authBtn.classList.remove('btn-primary')
    authBtn.classList.add('btn-secondary')
  }
}

function updateCart() {
  const total = state.cart.reduce((sum, item) => sum + (item.product.price * item.quantity), 0)

  if (state.cart.length === 0) {
    cartItems.innerHTML = '<p class="empty-message">Your cart is empty</p>'
  } else {
    cartItems.innerHTML = state.cart.map(item => `
      <div class="cart-item">
        <div class="cart-item-info">
          <div class="cart-item-name">${item.product.name}</div>
          <div class="cart-item-price">$${item.product.price.toFixed(2)}</div>
          <div class="cart-item-quantity">
            <button onclick="decreaseQuantity(${state.cart.indexOf(item)})">-</button>
            <input type="number" value="${item.quantity}" min="1" readonly />
            <button onclick="increaseQuantity(${state.cart.indexOf(item)})">+</button>
            <button class="cart-item-remove" onclick="removeCartItem(${state.cart.indexOf(item)})">Remove</button>
          </div>
        </div>
      </div>
    `).join('')
  }

  document.getElementById('subtotal').textContent = `$${total.toFixed(2)}`
  document.getElementById('tax').textContent = `$${(total * 0.1).toFixed(2)}`
  document.getElementById('total').textContent = `$${(total * 1.1).toFixed(2)}`

  checkoutBtn.disabled = state.cart.length === 0 || !state.isLoggedIn
  continueShoppingBtn.disabled = orderConfirmation.classList.contains('hidden') === false
}

// Cart manipulation functions (global for onclick handlers)
window.decreaseQuantity = function(index) {
  const item = state.cart[index]
  if (item && item.quantity > 1) {
    item.quantity--
    updateCart()
  }
}

window.increaseQuantity = function(index) {
  const item = state.cart[index]
  if (item) {
    item.quantity++
    updateCart()
  }
}

window.removeCartItem = function(index) {
  state.cart.splice(index, 1)
  updateCart()
}

// Load persisted token on page init
function restoreSession() {
  const savedToken = localStorage.getItem('token')
  if (savedToken) {
    state.token = savedToken
    // Verify token is still valid
    import('./api.js').then(async (module) => {
      try {
        const user = await module.getCurrentUser(savedToken)
        state.user = user
        state.isLoggedIn = true

        const cartData = await module.fetchCart(savedToken)
        state.cart = cartData.items

        updateUI()
      } catch (error) {
        console.log('Saved token is invalid, clearing...')
        localStorage.removeItem('token')
        state.token = null
      }
    })
  }
}

// Message Display Functions
function showMessage(message, type = 'success') {
  const messageEl = document.createElement('div')
  messageEl.className = `${type}-message`
  messageEl.textContent = message

  // Insert at top of main products section
  const productSection = document.querySelector('.products-section')
  productSection.insertBefore(messageEl, productSection.firstChild)

  // Auto-remove after 3 seconds
  setTimeout(() => {
    messageEl.remove()
  }, 3000)
}

// Initialize
function init() {
  console.log('Shopping Cart App Initialized')
  console.log('API URL:', API_URL)
  restoreSession()
  updateUI()
  loadProducts()
}

init()
