import { createRouter, createWebHistory } from 'vue-router'
import store from '@/store'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/HomePage.vue'),
    meta: { title: 'FashionFlow - Discover Your Style' },
  },
  {
    path: '/shop',
    name: 'Shop',
    component: () => import('@/views/ShopPage.vue'),
    meta: { title: 'Shop - FashionFlow' },
  },
  {
    path: '/product/:slug',
    name: 'Product',
    component: () => import('@/views/ProductPage.vue'),
    meta: { title: 'Product - FashionFlow' },
    props: true,
  },
  {
    path: '/collection/:slug',
    name: 'Collection',
    component: () => import('@/views/CollectionPage.vue'),
    meta: { title: 'Collection - FashionFlow' },
    props: true,
  },
  {
    path: '/cart',
    name: 'Cart',
    component: () => import('@/views/CartPage.vue'),
    meta: { title: 'Shopping Cart - FashionFlow' },
  },
  {
    path: '/checkout',
    name: 'Checkout',
    component: () => import('@/views/CheckoutPage.vue'),
    meta: { title: 'Checkout - FashionFlow', requiresAuth: true },
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/ProfilePage.vue'),
    meta: { title: 'My Profile - FashionFlow', requiresAuth: true },
  },
  {
    path: '/outfits',
    name: 'Outfits',
    component: () => import('@/views/OutfitsPage.vue'),
    meta: { title: 'Outfit Builder - FashionFlow' },
  },
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('@/views/AdminPanel.vue'),
    meta: { title: 'Admin Panel - FashionFlow', requiresAuth: true, requiresAdmin: true },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) return savedPosition
    return { top: 0 }
  },
})

router.beforeEach((to, from, next) => {
  document.title = to.meta.title || 'FashionFlow'

  const isAuthenticated = store.getters['auth/isAuthenticated']
  const isAdmin = store.getters['auth/isAdmin']

  if (to.meta.requiresAuth && !isAuthenticated) {
    next({ name: 'Home', query: { login: 'true', redirect: to.fullPath } })
    return
  }

  if (to.meta.requiresAdmin && !isAdmin) {
    next({ name: 'Home' })
    return
  }

  next()
})

export default router
