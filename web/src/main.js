import './style.css'
import API_URL from './api.js'

// App state
const state = {
  isLoggedIn: false,
  user: null,
  token: null,
  cart: [],
  products: [],
  currentOrder: null,
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
            <button>-</button>
            <input type="number" value="${item.quantity}" min="1" readonly />
            <button>+</button>
            <button class="cart-item-remove">Remove</button>
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

// Initialize
function init() {
  console.log('Shopping Cart App Initialized')
  console.log('API URL:', API_URL)
  updateUI()
  // Will load products in next step
}

init()
