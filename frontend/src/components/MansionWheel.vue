<script setup lang="ts">
import { computed, ref } from 'vue'

interface Mansion {
  index: number
  name_jp: string
  name_zh: string
  reading: string
  element: string
}

interface Props {
  mansions: Mansion[]
  userMansionIndex?: number | null
  highlightedIndices?: number[]
  highlightType?: string
}

const props = withDefaults(defineProps<Props>(), {
  userMansionIndex: null,
  highlightedIndices: () => [],
  highlightType: 'relation'
})

const emit = defineEmits<{
  (e: 'select', mansion: Mansion): void
}>()

// SVG 配置
const svgSize = 400
const centerX = svgSize / 2
const centerY = svgSize / 2
const outerRadius = 170
const innerRadius = 100
const textRadius = 140

// 四象分區（依照傳統天文排列）
const quadrants = [
  { name: '東方青龍', color: '#4A9B5A', startIndex: 0, endIndex: 6 },   // 角亢氐房心尾箕
  { name: '北方玄武', color: '#2D3436', startIndex: 7, endIndex: 13 },  // 斗牛女虛危室壁
  { name: '西方白虎', color: '#F5F5F5', startIndex: 14, endIndex: 20 }, // 奎婁胃昴畢觜參
  { name: '南方朱雀', color: '#E85D4C', startIndex: 21, endIndex: 26 }  // 井鬼柳星張翼軫
]

// 元素顏色
const elementColors: Record<string, string> = {
  '木': '#4A9B5A',
  '金': '#C4A052',
  '土': '#8B7355',
  '日': '#E89B3C',
  '月': '#7CB3D9',
  '火': '#E85D4C',
  '水': '#2D3436'
}

// 計算每個宿的位置
const mansionSegments = computed(() => {
  if (!props.mansions || props.mansions.length === 0) return []

  const anglePerMansion = 360 / props.mansions.length

  return props.mansions.map((mansion, i) => {
    // 從正上方（-90度）開始，順時針排列
    const startAngle = -90 + i * anglePerMansion
    const endAngle = startAngle + anglePerMansion
    const midAngle = startAngle + anglePerMansion / 2

    // 轉換為弧度
    const startRad = (startAngle * Math.PI) / 180
    const endRad = (endAngle * Math.PI) / 180
    const midRad = (midAngle * Math.PI) / 180

    // 計算扇形路徑
    const x1 = centerX + outerRadius * Math.cos(startRad)
    const y1 = centerY + outerRadius * Math.sin(startRad)
    const x2 = centerX + outerRadius * Math.cos(endRad)
    const y2 = centerY + outerRadius * Math.sin(endRad)
    const x3 = centerX + innerRadius * Math.cos(endRad)
    const y3 = centerY + innerRadius * Math.sin(endRad)
    const x4 = centerX + innerRadius * Math.cos(startRad)
    const y4 = centerY + innerRadius * Math.sin(startRad)

    // 文字位置
    const textX = centerX + textRadius * Math.cos(midRad)
    const textY = centerY + textRadius * Math.sin(midRad)

    // 判斷是否需要大弧
    const largeArc = anglePerMansion > 180 ? 1 : 0

    const path = `
      M ${x1} ${y1}
      A ${outerRadius} ${outerRadius} 0 ${largeArc} 1 ${x2} ${y2}
      L ${x3} ${y3}
      A ${innerRadius} ${innerRadius} 0 ${largeArc} 0 ${x4} ${y4}
      Z
    `

    // 判斷所屬四象
    let quadrant = quadrants.find(q => i >= q.startIndex && i <= q.endIndex)

    // 判斷是否高亮
    const isUser = props.userMansionIndex === i
    const isHighlighted = props.highlightedIndices.includes(i)

    return {
      ...mansion,
      path,
      textX,
      textY,
      midAngle,
      color: elementColors[mansion.element] || '#666',
      quadrantColor: quadrant?.color || '#666',
      isUser,
      isHighlighted
    }
  })
})

// 四象標籤位置
const quadrantLabels = computed(() => {
  return [
    { name: '東方青龍', x: svgSize - 30, y: centerY, anchor: 'end' },
    { name: '北方玄武', x: centerX, y: 25, anchor: 'middle' },
    { name: '西方白虎', x: 30, y: centerY, anchor: 'start' },
    { name: '南方朱雀', x: centerX, y: svgSize - 15, anchor: 'middle' }
  ]
})

// 懸停狀態
const hoveredIndex = ref<number | null>(null)

function handleClick(mansion: Mansion & { path: string }) {
  emit('select', mansion)
}
</script>

<template>
  <div class="mansion-wheel">
    <svg :viewBox="`0 0 ${svgSize} ${svgSize}`" class="wheel-svg">
      <!-- 背景圓 -->
      <circle
        :cx="centerX"
        :cy="centerY"
        :r="outerRadius + 5"
        fill="none"
        stroke="var(--border-default)"
        stroke-width="1"
      />

      <!-- 內圓 -->
      <circle
        :cx="centerX"
        :cy="centerY"
        :r="innerRadius - 5"
        fill="var(--cosmos-night)"
        stroke="var(--border-default)"
        stroke-width="1"
      />

      <!-- 中心文字 -->
      <text
        :x="centerX"
        :y="centerY - 15"
        text-anchor="middle"
        class="center-title"
      >二十七宿</text>
      <text
        :x="centerX"
        :y="centerY + 10"
        text-anchor="middle"
        class="center-subtitle"
      >輪盤</text>

      <!-- 宿星扇形 -->
      <g v-for="segment in mansionSegments" :key="segment.index">
        <path
          :d="segment.path"
          :fill="segment.isUser ? 'var(--stellar-gold)' : segment.isHighlighted ? 'rgba(199, 163, 101, 0.5)' : segment.color"
          :stroke="hoveredIndex === segment.index ? 'var(--stellar-gold)' : 'var(--cosmos-night)'"
          :stroke-width="hoveredIndex === segment.index || segment.isUser ? 2 : 1"
          :opacity="segment.isUser ? 1 : segment.isHighlighted ? 0.9 : 0.7"
          class="mansion-segment"
          @mouseenter="hoveredIndex = segment.index"
          @mouseleave="hoveredIndex = null"
          @click="handleClick(segment)"
        />

        <!-- 宿名文字 -->
        <text
          :x="segment.textX"
          :y="segment.textY"
          text-anchor="middle"
          dominant-baseline="middle"
          class="mansion-name"
          :class="{ 'user-mansion': segment.isUser, 'highlighted': segment.isHighlighted }"
          :transform="`rotate(${segment.midAngle + 90}, ${segment.textX}, ${segment.textY})`"
          @click="handleClick(segment)"
        >{{ segment.name_zh.replace('宿', '') }}</text>
      </g>

      <!-- 四象標籤 -->
      <text
        v-for="label in quadrantLabels"
        :key="label.name"
        :x="label.x"
        :y="label.y"
        :text-anchor="label.anchor"
        class="quadrant-label"
      >{{ label.name }}</text>
    </svg>

    <!-- 圖例 -->
    <div class="wheel-legend">
      <div class="legend-item" v-for="(color, element) in elementColors" :key="element">
        <span class="legend-dot" :style="{ background: color }"></span>
        <span class="legend-text">{{ element }}</span>
      </div>
    </div>

    <!-- 懸停提示 -->
    <div v-if="hoveredIndex !== null && mansionSegments[hoveredIndex]" class="hover-tooltip">
      <strong>{{ mansionSegments[hoveredIndex].name_jp }}</strong>
      <ruby>
        {{ mansionSegments[hoveredIndex].name_zh }}
        <rp>(</rp><rt>{{ mansionSegments[hoveredIndex].reading }}</rt><rp>)</rp>
      </ruby>
      <span class="tooltip-element" :style="{ color: elementColors[mansionSegments[hoveredIndex].element] }">
        {{ mansionSegments[hoveredIndex].element }}
      </span>
    </div>
  </div>
</template>

<style scoped>
.mansion-wheel {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-4);
}

.wheel-svg {
  width: 100%;
  max-width: 400px;
  height: auto;
}

.mansion-segment {
  cursor: pointer;
  transition: all 0.2s ease;
}

.mansion-segment:hover {
  opacity: 1 !important;
}

.mansion-name {
  font-size: 10px;
  fill: var(--cosmos-night);
  font-weight: 600;
  pointer-events: none;
  user-select: none;
}

.mansion-name.user-mansion {
  fill: var(--cosmos-night);
  font-weight: 700;
}

.mansion-name.highlighted {
  fill: var(--cosmos-night);
}

.center-title {
  font-size: 14px;
  fill: var(--stellar-gold);
  font-weight: 600;
}

.center-subtitle {
  font-size: 12px;
  fill: var(--text-muted);
}

.quadrant-label {
  font-size: 11px;
  fill: var(--text-muted);
  font-weight: 500;
}

.wheel-legend {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: var(--space-3);
  padding: var(--space-2) var(--space-4);
  background: var(--cosmos-night);
  border-radius: var(--radius-md);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: var(--space-1);
}

.legend-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.legend-text {
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.hover-tooltip {
  position: absolute;
  bottom: -60px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-2) var(--space-4);
  background: var(--cosmos-twilight);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  font-size: 0.9rem;
  white-space: nowrap;
  z-index: 10;
}

.hover-tooltip strong {
  color: var(--stellar-gold);
}

.hover-tooltip ruby rt {
  font-size: 0.6em;
}

.tooltip-element {
  font-weight: 600;
}

@media (max-width: 500px) {
  .wheel-svg {
    max-width: 320px;
  }

  .mansion-name {
    font-size: 8px;
  }

  .center-title {
    font-size: 12px;
  }

  .center-subtitle {
    font-size: 10px;
  }

  .quadrant-label {
    font-size: 9px;
  }

  .hover-tooltip {
    font-size: 0.8rem;
  }
}
</style>
