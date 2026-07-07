import './style.css'
import API_URL, { fetchProducts, addToCart } from './api.js'

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

// Event Listeners
authBtn.addEventListener('click', () => {
  if (state.isLoggedIn) {
    logout()
  } else {
    authModal.classList.remove('hidden')
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
newOrderBtn.addEventListener('click', handleNewOrder)

// Auth Functions
async function handleLogin(e) {
  e.preventDefault()
  const formData = new FormData(loginFormElement)
  // Will implement in next step
  console.log('Login form submitted')
}

async function handleRegister(e) {
  e.preventDefault()
  const formData = new FormData(registerFormElement)
  // Will implement in next step
  console.log('Register form submitted')
}

function logout() {
  state.isLoggedIn = false
  state.user = null
  state.token = null
  state.cart = []
  updateUI()
}

// Cart Functions
async function handleCheckout() {
  // Will implement in later steps
  console.log('Checkout clicked')
}

function handleNewOrder() {
  orderConfirmation.classList.add('hidden')
  state.currentOrder = null
  state.cart = []
  updateUI()
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
    alert('Added to cart!')
  } catch (error) {
    console.error('Error adding to cart:', error)
    alert('Failed to add to cart: ' + error.message)
  }
}

// UI Updates
function updateUI() {
  updateAuthBtn()
  updateCart()
}

function updateAuthBtn() {
  if (state.isLoggedIn) {
    authBtn.textContent = `Logout (${state.user?.full_name})`
  } else {
    authBtn.textContent = 'Login'
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
            <button onclick="decreaseQuantity(${item.id})">-</button>
            <input type="number" value="${item.quantity}" min="1" readonly />
            <button onclick="increaseQuantity(${item.id})">+</button>
            <button class="cart-item-remove" onclick="removeCartItem(${item.id})">Remove</button>
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
window.decreaseQuantity = function(itemId) {
  const item = state.cart.find(i => i.id === itemId)
  if (item && item.quantity > 1) {
    item.quantity--
    updateCart()
  }
}

window.increaseQuantity = function(itemId) {
  const item = state.cart.find(i => i.id === itemId)
  if (item) {
    item.quantity++
    updateCart()
  }
}

window.removeCartItem = function(itemId) {
  state.cart = state.cart.filter(item => item.id !== itemId)
  updateCart()
}

// Initialize
function init() {
  console.log('Shopping Cart App Initialized')
  console.log('API URL:', API_URL)
  updateUI()
  loadProducts()
}

init()
