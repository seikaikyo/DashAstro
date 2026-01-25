import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../views/HomeView.vue')
    },
    {
      path: '/horoscope',
      name: 'horoscope',
      component: () => import('../views/HoroscopeView.vue')
    },
    {
      path: '/horoscope/:code',
      name: 'horoscope-detail',
      component: () => import('../views/HoroscopeDetailView.vue')
    },
    {
      path: '/tarot',
      name: 'tarot',
      component: () => import('../views/TarotView.vue')
    },
    {
      path: '/tarot/reading/:id',
      name: 'tarot-reading',
      component: () => import('../views/TarotReadingView.vue')
    },
    {
      path: '/sky',
      name: 'sky',
      component: () => import('../views/SkyView.vue')
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('../views/ProfileView.vue')
    }
  ]
})

export default router
