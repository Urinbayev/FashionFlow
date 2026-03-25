import { createStore } from 'vuex'
import auth from './modules/auth'
import cart from './modules/cart'
import products from './modules/products'

export default createStore({
  modules: {
    auth,
    cart,
    products,
  },
  state() {
    return {
      loading: false,
      notification: null,
    }
  },
  mutations: {
    SET_LOADING(state, value) {
      state.loading = value
    },
    SET_NOTIFICATION(state, notification) {
      state.notification = notification
    },
    CLEAR_NOTIFICATION(state) {
      state.notification = null
    },
  },
  actions: {
    showNotification({ commit }, { message, type = 'info', duration = 4000 }) {
      commit('SET_NOTIFICATION', { message, type })
      setTimeout(() => commit('CLEAR_NOTIFICATION'), duration)
    },
  },
})
