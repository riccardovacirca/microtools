import { writable } from 'svelte/store'

export const auth = writable({
  isAuthenticated: false,
  user: null,
  token: null
})

// Check authentication status on load
export async function checkAuth() {
  try {
    const response = await fetch('/api/auth/check', {
      credentials: 'include'
    })

    if (response.ok) {
      const data = await response.json()
      
      if (data.authenticated) {
        const userResponse = await fetch('/api/auth/me', {
          credentials: 'include'
        })

        if (userResponse.ok) {
          const user = await userResponse.json()
          auth.set({ 
            isAuthenticated: true, 
            user,
            token: true  // Cookie-based auth, no explicit token
          })
          return true
        }
      }
    }
  } catch (error) {
    console.error('Auth check error:', error)
  }

  auth.set({ isAuthenticated: false, user: null, token: null })
  return false
}

// Logout function
export async function logout() {
  try {
    await fetch('/api/auth/logout', {
      method: 'POST',
      credentials: 'include'
    })
  } catch (error) {
    console.error('Logout error:', error)
  }

  auth.set({ isAuthenticated: false, user: null, token: null })
}
