// API base URL - fetch calls run in the browser, so we use localhost:8000
// (not http://api:8000 which is only for container-to-container communication)
const API_URL = 'http://localhost:8000'

/**
 * Fetch products from the API
 * @param {number} skip - Number of products to skip (for pagination)
 * @param {number} limit - Number of products to return
 * @param {number} categoryId - Optional category ID to filter by
 * @returns {Promise<Object>} - Response with items, total, page info
 */
export async function fetchProducts(skip = 0, limit = 20, categoryId = null) {
  try {
    let url = `${API_URL}/products?skip=${skip}&limit=${limit}`
    if (categoryId) {
      url += `&category_id=${categoryId}`
    }

    const response = await fetch(url)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    return data
  } catch (error) {
    console.error('Error fetching products:', error)
    throw error
  }
}

/**
 * Fetch a single product by ID
 * @param {number} productId - Product ID
 * @returns {Promise<Object>} - Product data
 */
export async function fetchProduct(productId) {
  try {
    const response = await fetch(`${API_URL}/products/${productId}`)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    return data
  } catch (error) {
    console.error('Error fetching product:', error)
    throw error
  }
}

/**
 * Fetch all categories
 * @returns {Promise<Array>} - Array of categories
 */
export async function fetchCategories() {
  try {
    const response = await fetch(`${API_URL}/categories`)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    return data
  } catch (error) {
    console.error('Error fetching categories:', error)
    throw error
  }
}

/**
 * Register a new user
 * @param {string} email - User email
 * @param {string} password - User password
 * @param {string} fullName - User full name
 * @returns {Promise<Object>} - User data
 */
export async function register(email, password, fullName) {
  try {
    const response = await fetch(`${API_URL}/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email,
        password,
        full_name: fullName,
      }),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Registration failed')
    }

    const data = await response.json()
    return data
  } catch (error) {
    console.error('Error registering:', error)
    throw error
  }
}

/**
 * Login user
 * @param {string} email - User email
 * @param {string} password - User password
 * @returns {Promise<Object>} - Token data
 */
export async function login(email, password) {
  try {
    const response = await fetch(`${API_URL}/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email,
        password,
      }),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Login failed')
    }

    const data = await response.json()
    return data
  } catch (error) {
    console.error('Error logging in:', error)
    throw error
  }
}

/**
 * Get current user info
 * @param {string} token - JWT token
 * @returns {Promise<Object>} - User data
 */
export async function getCurrentUser(token) {
  try {
    const response = await fetch(`${API_URL}/me`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    })

    if (!response.ok) {
      throw new Error('Failed to get current user')
    }

    const data = await response.json()
    return data
  } catch (error) {
    console.error('Error getting current user:', error)
    throw error
  }
}

/**
 * Fetch user's cart
 * @param {string} token - JWT token
 * @returns {Promise<Object>} - Cart data with items
 */
export async function fetchCart(token) {
  try {
    const response = await fetch(`${API_URL}/cart`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    })

    if (!response.ok) {
      throw new Error('Failed to fetch cart')
    }

    const data = await response.json()
    return data
  } catch (error) {
    console.error('Error fetching cart:', error)
    throw error
  }
}

/**
 * Add item to cart
 * @param {number} productId - Product ID
 * @param {number} quantity - Quantity
 * @param {string} token - JWT token
 * @returns {Promise<Object>} - Cart item data
 */
export async function addToCart(productId, quantity, token) {
  try {
    const response = await fetch(`${API_URL}/cart/items`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({
        product_id: productId,
        quantity,
      }),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to add to cart')
    }

    const data = await response.json()
    return data
  } catch (error) {
    console.error('Error adding to cart:', error)
    throw error
  }
}

/**
 * Update cart item quantity
 * @param {number} itemId - Cart item ID
 * @param {number} quantity - New quantity
 * @param {string} token - JWT token
 * @returns {Promise<Object>} - Updated cart item data
 */
export async function updateCartItem(itemId, quantity, token) {
  try {
    const response = await fetch(`${API_URL}/cart/items/${itemId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({ quantity }),
    })

    if (!response.ok) {
      throw new Error('Failed to update cart item')
    }

    const data = await response.json()
    return data
  } catch (error) {
    console.error('Error updating cart item:', error)
    throw error
  }
}

/**
 * Remove item from cart
 * @param {number} itemId - Cart item ID
 * @param {string} token - JWT token
 * @returns {Promise<void>}
 */
export async function removeFromCart(itemId, token) {
  try {
    const response = await fetch(`${API_URL}/cart/items/${itemId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    })

    if (!response.ok) {
      throw new Error('Failed to remove item from cart')
    }
  } catch (error) {
    console.error('Error removing from cart:', error)
    throw error
  }
}

/**
 * Checkout and create order
 * @param {string} token - JWT token
 * @returns {Promise<Object>} - Order data
 */
export async function checkout(token) {
  try {
    const response = await fetch(`${API_URL}/checkout`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({}),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Checkout failed')
    }

    const data = await response.json()
    return data
  } catch (error) {
    console.error('Error during checkout:', error)
    throw error
  }
}

/**
 * Fetch user's orders
 * @param {string} token - JWT token
 * @returns {Promise<Object>} - Orders data
 */
export async function fetchOrders(token) {
  try {
    const response = await fetch(`${API_URL}/orders`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    })

    if (!response.ok) {
      throw new Error('Failed to fetch orders')
    }

    const data = await response.json()
    return data
  } catch (error) {
    console.error('Error fetching orders:', error)
    throw error
  }
}

export default API_URL
