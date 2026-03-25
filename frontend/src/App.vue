<template>
  <div id="fashionflow-app">
    <NavBar />
    <main class="main-content">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
    <CartDrawer />
    <FooterBar />
  </div>
</template>

<script>
import NavBar from '@/components/layout/NavBar.vue'
import FooterBar from '@/components/layout/FooterBar.vue'
import CartDrawer from '@/components/cart/CartDrawer.vue'

export default {
  name: 'App',
  components: {
    NavBar,
    FooterBar,
    CartDrawer,
  },
  created() {
    this.$store.dispatch('auth/initializeAuth')
    this.$store.dispatch('cart/loadCart')
  },
}
</script>

<style>
*,
*::before,
*::after {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

:root {
  --color-primary: #1a1a2e;
  --color-secondary: #16213e;
  --color-accent: #e94560;
  --color-accent-hover: #d63851;
  --color-gold: #c9a96e;
  --color-bg: #ffffff;
  --color-bg-secondary: #f8f9fa;
  --color-bg-dark: #1a1a2e;
  --color-text: #2d2d2d;
  --color-text-light: #6b7280;
  --color-text-white: #ffffff;
  --color-border: #e5e7eb;
  --color-success: #10b981;
  --color-warning: #f59e0b;
  --color-error: #ef4444;
  --font-display: 'Playfair Display', serif;
  --font-body: 'Inter', sans-serif;
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.07);
  --shadow-lg: 0 10px 25px rgba(0, 0, 0, 0.1);
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --max-width: 1400px;
  --transition: all 0.3s ease;
}

body {
  font-family: var(--font-body);
  color: var(--color-text);
  background-color: var(--color-bg);
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

a {
  color: inherit;
  text-decoration: none;
}

button {
  cursor: pointer;
  font-family: var(--font-body);
}

img {
  max-width: 100%;
  height: auto;
  display: block;
}

.main-content {
  min-height: calc(100vh - 160px);
}

.container {
  max-width: var(--max-width);
  margin: 0 auto;
  padding: 0 24px;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 12px 28px;
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  border: none;
  border-radius: var(--radius-sm);
  transition: var(--transition);
  cursor: pointer;
}

.btn-primary {
  background-color: var(--color-primary);
  color: var(--color-text-white);
}

.btn-primary:hover {
  background-color: var(--color-secondary);
}

.btn-accent {
  background-color: var(--color-accent);
  color: var(--color-text-white);
}

.btn-accent:hover {
  background-color: var(--color-accent-hover);
}

.btn-outline {
  background: transparent;
  border: 2px solid var(--color-primary);
  color: var(--color-primary);
}

.btn-outline:hover {
  background-color: var(--color-primary);
  color: var(--color-text-white);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.section-title {
  font-family: var(--font-display);
  font-size: 32px;
  font-weight: 600;
  color: var(--color-primary);
  margin-bottom: 32px;
}

.price {
  font-weight: 600;
  color: var(--color-primary);
}

.price-sale {
  color: var(--color-accent);
}

.price-original {
  text-decoration: line-through;
  color: var(--color-text-light);
  font-weight: 400;
}

@media (max-width: 768px) {
  .container {
    padding: 0 16px;
  }

  .section-title {
    font-size: 24px;
    margin-bottom: 20px;
  }
}
</style>
