/**
 * API 配置
 *
 * 統一管理 API URL，避免硬編碼分散在各處
 */

// API Base URL
// 開發環境使用環境變數，生產環境使用 Render 部署的 API
export const apiUrl = import.meta.env.VITE_API_URL || 'https://dashastro-api.onrender.com'

// API 端點
export const endpoints = {
  // 健康檢查
  health: `${apiUrl}/healthz`,

  // 星座運勢
  horoscope: {
    zodiacs: `${apiUrl}/api/horoscope/zodiacs`,
    weekly: `${apiUrl}/api/horoscope/weekly`,
    monthly: `${apiUrl}/api/horoscope/monthly`,
  },

  // 塔羅占卜
  tarot: {
    cards: `${apiUrl}/api/tarot/cards`,
    spreads: `${apiUrl}/api/tarot/spreads`,
    draw: `${apiUrl}/api/tarot/draw`,
    reading: `${apiUrl}/api/tarot/reading`,
  },

  // 宿曜道
  sukuyodo: {
    mansions: `${apiUrl}/api/sukuyodo/mansions`,
    mansion: (date: string) => `${apiUrl}/api/sukuyodo/mansion/${date}`,
    compatibility: `${apiUrl}/api/sukuyodo/compatibility`,
    relations: `${apiUrl}/api/sukuyodo/relations`,
    elements: `${apiUrl}/api/sukuyodo/elements`,
    metadata: `${apiUrl}/api/sukuyodo/metadata`,
    compatibilityFinder: (date: string) => `${apiUrl}/api/sukuyodo/compatibility-finder/${date}`,
    fortune: {
      daily: (date: string, birthDate: string) =>
        `${apiUrl}/api/sukuyodo/fortune/daily/${date}?birth_date=${birthDate}`,
      weekly: (year: number, week: number, birthDate: string) =>
        `${apiUrl}/api/sukuyodo/fortune/weekly/${year}/${week}?birth_date=${birthDate}`,
      monthly: (year: number, month: number, birthDate: string) =>
        `${apiUrl}/api/sukuyodo/fortune/monthly/${year}/${month}?birth_date=${birthDate}`,
      yearly: (year: number, birthDate: string) =>
        `${apiUrl}/api/sukuyodo/fortune/yearly/${year}?birth_date=${birthDate}`,
    },
    luckyDays: {
      categories: `${apiUrl}/api/sukuyodo/lucky-days/categories`,
      query: (date: string, category: string, action: string) =>
        `${apiUrl}/api/sukuyodo/lucky-days/${date}?category=${category}&action=${action}`,
    },
  },

  // 天文
  astronomy: {
    planets: `${apiUrl}/api/astronomy/planets`,
    aspects: `${apiUrl}/api/astronomy/aspects`,
  },

  // 星座配對
  compatibility: {
    zodiac: `${apiUrl}/api/compatibility/zodiac`,
  },

  // 統計
  stats: {
    track: `${apiUrl}/api/stats/track`,
    summary: `${apiUrl}/api/stats`,
  },
} as const
