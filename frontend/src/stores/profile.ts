import { ref, computed, watch } from 'vue'

export interface Partner {
  id: string
  nickname: string
  gender: 'male' | 'female' | 'other'
  zodiacCode: string
  isPrimary: boolean
  birthDate?: string  // YYYY-MM-DD 格式，選填
}

export interface UserProfile {
  gender: 'male' | 'female' | 'other' | null
  zodiacCode: string | null
  birthDate?: string  // YYYY-MM-DD 格式，選填
  partners: Partner[]
}

const STORAGE_KEY = 'dashastro_profile'

// 從 localStorage 讀取
function loadProfile(): UserProfile {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) {
      return JSON.parse(saved)
    }
  } catch (e) {
    console.error('載入個人檔案失敗')
  }
  return {
    gender: null,
    zodiacCode: null,
    partners: []
  }
}

// 儲存到 localStorage
function saveProfile(profile: UserProfile) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(profile))
  } catch (e) {
    console.error('儲存個人檔案失敗')
  }
}

// 全域狀態
const profile = ref<UserProfile>(loadProfile())

// 監聽變化自動儲存
watch(profile, (newProfile) => {
  saveProfile(newProfile)
}, { deep: true })

// 星座列表
export const ZODIAC_SIGNS = [
  { code: 'ARI', name: '牡羊座', symbol: '\u2648' },
  { code: 'TAU', name: '金牛座', symbol: '\u2649' },
  { code: 'GEM', name: '雙子座', symbol: '\u264A' },
  { code: 'CAN', name: '巨蟹座', symbol: '\u264B' },
  { code: 'LEO', name: '獅子座', symbol: '\u264C' },
  { code: 'VIR', name: '處女座', symbol: '\u264D' },
  { code: 'LIB', name: '天秤座', symbol: '\u264E' },
  { code: 'SCO', name: '天蠍座', symbol: '\u264F' },
  { code: 'SAG', name: '射手座', symbol: '\u2650' },
  { code: 'CAP', name: '摩羯座', symbol: '\u2651' },
  { code: 'AQU', name: '水瓶座', symbol: '\u2652' },
  { code: 'PIS', name: '雙魚座', symbol: '\u2653' }
]

export const GENDER_OPTIONS = [
  { value: 'male', label: '男' },
  { value: 'female', label: '女' },
  { value: 'other', label: '其他' }
]

// 從生日推算星座
export function getZodiacFromBirthDate(birthDate: string): string | null {
  if (!birthDate) return null

  const [, monthStr, dayStr] = birthDate.split('-')
  const month = parseInt(monthStr, 10)
  const day = parseInt(dayStr, 10)

  if (isNaN(month) || isNaN(day)) return null

  // 星座日期範圍
  const zodiacRanges = [
    { code: 'CAP', start: [1, 1], end: [1, 19] },
    { code: 'AQU', start: [1, 20], end: [2, 18] },
    { code: 'PIS', start: [2, 19], end: [3, 20] },
    { code: 'ARI', start: [3, 21], end: [4, 19] },
    { code: 'TAU', start: [4, 20], end: [5, 20] },
    { code: 'GEM', start: [5, 21], end: [6, 20] },
    { code: 'CAN', start: [6, 21], end: [7, 22] },
    { code: 'LEO', start: [7, 23], end: [8, 22] },
    { code: 'VIR', start: [8, 23], end: [9, 22] },
    { code: 'LIB', start: [9, 23], end: [10, 22] },
    { code: 'SCO', start: [10, 23], end: [11, 21] },
    { code: 'SAG', start: [11, 22], end: [12, 21] },
    { code: 'CAP', start: [12, 22], end: [12, 31] }
  ]

  for (const range of zodiacRanges) {
    const [startMonth, startDay] = range.start
    const [endMonth, endDay] = range.end

    if (startMonth === endMonth) {
      if (month === startMonth && day >= startDay && day <= endDay) {
        return range.code
      }
    } else {
      if (
        (month === startMonth && day >= startDay) ||
        (month === endMonth && day <= endDay)
      ) {
        return range.code
      }
    }
  }

  return null
}

export function useProfile() {
  const isProfileSet = computed(() => {
    return profile.value.gender !== null && profile.value.zodiacCode !== null
  })

  const myZodiac = computed(() => {
    return ZODIAC_SIGNS.find(z => z.code === profile.value.zodiacCode)
  })

  const primaryPartner = computed(() => {
    return profile.value.partners.find(p => p.isPrimary) || profile.value.partners[0] || null
  })

  const myBirthDate = computed(() => profile.value.birthDate || null)

  // 取得有填寫生日的對象（可用於宿曜道功能）
  const partnersWithBirthDate = computed(() => {
    return profile.value.partners.filter(p => p.birthDate)
  })

  const getPartnerZodiac = (partner: Partner) => {
    return ZODIAC_SIGNS.find(z => z.code === partner.zodiacCode)
  }

  function setMyProfile(
    gender: 'male' | 'female' | 'other',
    zodiacCode: string,
    birthDate?: string
  ) {
    profile.value.gender = gender
    profile.value.zodiacCode = zodiacCode
    if (birthDate) {
      profile.value.birthDate = birthDate
    }
  }

  function addPartner(partner: Omit<Partner, 'id'>) {
    if (profile.value.partners.length >= 5) {
      throw new Error('最多只能新增 5 個關注對象')
    }

    const newPartner: Partner = {
      ...partner,
      id: crypto.randomUUID()
    }

    // 如果是第一個，設為主要
    if (profile.value.partners.length === 0) {
      newPartner.isPrimary = true
    }

    profile.value.partners.push(newPartner)
  }

  function removePartner(id: string) {
    const idx = profile.value.partners.findIndex(p => p.id === id)
    if (idx === -1) return

    const wasPrimary = profile.value.partners[idx].isPrimary
    profile.value.partners.splice(idx, 1)

    // 如果移除的是主要對象，設定第一個為主要
    if (wasPrimary && profile.value.partners.length > 0) {
      profile.value.partners[0].isPrimary = true
    }
  }

  function setPrimaryPartner(id: string) {
    profile.value.partners.forEach(p => {
      p.isPrimary = p.id === id
    })
  }

  function clearProfile() {
    profile.value = {
      gender: null,
      zodiacCode: null,
      partners: []
    }
  }

  return {
    profile,
    isProfileSet,
    myZodiac,
    myBirthDate,
    primaryPartner,
    partnersWithBirthDate,
    getPartnerZodiac,
    setMyProfile,
    addPartner,
    removePartner,
    setPrimaryPartner,
    clearProfile
  }
}
