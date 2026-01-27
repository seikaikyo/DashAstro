import { createRouter, createWebHistory } from 'vue-router'
import { trackPageView } from '../composables/useGtag'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../views/HomeView.vue'),
      meta: {
        title: 'DashAstro - 星座運勢、塔羅占卜、宿曜道',
        description: '免費星座運勢查詢、塔羅牌占卜、宿曜道本命宿分析。融合東西方占星智慧。'
      }
    },
    {
      path: '/horoscope',
      name: 'horoscope',
      component: () => import('../views/HoroscopeView.vue'),
      meta: {
        title: '12星座運勢 - 每日/週/月運勢查詢 | DashAstro',
        description: '牡羊座到雙魚座，每日更新的星座運勢、感情運、事業運。免費查詢你的星座運勢。'
      }
    },
    {
      path: '/horoscope/:code',
      name: 'horoscope-detail',
      component: () => import('../views/HoroscopeDetailView.vue'),
      meta: {
        title: '星座運勢詳情 | DashAstro',
        description: '查看完整星座運勢分析，包含感情、事業、健康運勢及幸運指南。'
      }
    },
    {
      path: '/tarot',
      name: 'tarot',
      component: () => import('../views/TarotView.vue'),
      meta: {
        title: '線上塔羅占卜 - AI 解讀牌義 | DashAstro',
        description: '免費線上塔羅牌占卜，AI 即時解讀牌義，支援單牌、三牌、凱爾特十字牌陣。'
      }
    },
    {
      path: '/tarot/reading/:id',
      name: 'tarot-reading',
      component: () => import('../views/TarotReadingView.vue'),
      meta: {
        title: '塔羅解讀結果 | DashAstro',
        description: 'AI 智慧解讀你的塔羅牌陣，提供深入的牌義分析與建議。'
      }
    },
    {
      path: '/sky',
      name: 'sky',
      component: () => import('../views/SkyView.vue'),
      meta: {
        title: '即時星空 - 行星位置與相位 | DashAstro',
        description: '查看當前天空的行星位置、星座分佈與重要相位。'
      }
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('../views/ProfileView.vue'),
      meta: {
        title: '個人資料設定 | DashAstro',
        description: '設定你的星座、生日與關注對象，獲得個人化的運勢分析。'
      }
    },
    {
      path: '/stats',
      name: 'stats',
      component: () => import('../views/StatsView.vue'),
      meta: {
        title: '使用統計 | DashAstro',
        description: '查看網站使用統計與功能數據。'
      }
    },
    {
      path: '/sukuyodo',
      name: 'sukuyodo',
      component: () => import('../views/SukuyodoViewV2.vue'),
      meta: {
        title: '宿曜道 - 真言宗密教占星術 | 本命宿查詢',
        description: '源自印度、唐代傳入日本的密教占星術。輸入生日查詢你的本命宿，使用三九秘法分析雙人相性。'
      }
    },
    {
      path: '/sukuyodo-legacy',
      name: 'sukuyodo-legacy',
      component: () => import('../views/SukuyodoView.vue'),
      meta: {
        title: '宿曜道 (舊版) | 本命宿查詢',
        description: '宿曜道舊版介面，已由新版取代。'
      }
    }
  ],
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// 頁面追蹤 + 動態更新 meta
router.afterEach((to) => {
  // 更新頁面標題
  const title = to.meta.title as string || 'DashAstro'
  document.title = title

  // 更新 meta description
  const description = to.meta.description as string
  if (description) {
    let metaDescription = document.querySelector('meta[name="description"]')
    if (metaDescription) {
      metaDescription.setAttribute('content', description)
    }

    // 更新 OG description
    let ogDescription = document.querySelector('meta[property="og:description"]')
    if (ogDescription) {
      ogDescription.setAttribute('content', description)
    }
  }

  // 更新 canonical URL
  let canonical = document.querySelector('link[rel="canonical"]')
  if (canonical) {
    canonical.setAttribute('href', `https://astro.dashai.dev${to.path}`)
  }

  // 更新 OG URL
  let ogUrl = document.querySelector('meta[property="og:url"]')
  if (ogUrl) {
    ogUrl.setAttribute('content', `https://astro.dashai.dev${to.path}`)
  }

  // GA4 頁面追蹤
  trackPageView(to.path, title)
})

export default router
