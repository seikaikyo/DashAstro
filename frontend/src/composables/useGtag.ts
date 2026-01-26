/**
 * Google Analytics 4 事件追蹤
 */

declare global {
  interface Window {
    gtag: (...args: unknown[]) => void
    dataLayer: unknown[]
  }
}

type GtagEventParams = Record<string, string | number | boolean | undefined>

/**
 * 發送 GA4 事件
 */
export function trackEvent(eventName: string, params?: GtagEventParams) {
  if (typeof window !== 'undefined' && window.gtag) {
    window.gtag('event', eventName, params)
  }
}

/**
 * 追蹤頁面瀏覽
 */
export function trackPageView(path: string, title?: string) {
  trackEvent('page_view', {
    page_path: path,
    page_title: title
  })
}

// ============ 預定義事件 ============

/**
 * 追蹤宿曜道本命宿查詢
 */
export function trackSukuyodoLookup(mansionName: string) {
  trackEvent('sukuyodo_lookup', {
    mansion_name: mansionName
  })
}

/**
 * 追蹤宿曜道相性診斷
 */
export function trackSukuyodoCompatibility(relationType: string, score: number) {
  trackEvent('sukuyodo_compatibility', {
    relation_type: relationType,
    score: score
  })
}

/**
 * 追蹤星座運勢查看
 */
export function trackHoroscopeView(zodiacCode: string, period: 'daily' | 'weekly' | 'monthly' | 'yearly') {
  trackEvent('horoscope_view', {
    zodiac_code: zodiacCode,
    period: period
  })
}

/**
 * 追蹤塔羅抽牌
 */
export function trackTarotDraw(spreadType: string, cardCount: number) {
  trackEvent('tarot_draw', {
    spread_type: spreadType,
    card_count: cardCount
  })
}

/**
 * 追蹤分享結果
 */
export function trackShare(contentType: string) {
  trackEvent('share_result', {
    content_type: contentType
  })
}

/**
 * 追蹤功能使用（通用）
 */
export function trackFeatureUse(featureName: string, action: string) {
  trackEvent('feature_use', {
    feature_name: featureName,
    action: action
  })
}
