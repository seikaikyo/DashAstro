"""
星座配對計算服務
"""
from datetime import datetime
from typing import Optional
from .astrology import astrology_service


class CompatibilityService:
    """星座配對計算"""

    # 元素相性表
    ELEMENT_COMPATIBILITY = {
        ("fire", "fire"): {"score": 4, "desc": "熱情相投，但需注意過於激烈"},
        ("fire", "air"): {"score": 5, "desc": "火借風勢，相互激發創意"},
        ("fire", "earth"): {"score": 2, "desc": "需要耐心磨合，價值觀差異大"},
        ("fire", "water"): {"score": 2, "desc": "感受方式不同，容易產生誤解"},
        ("earth", "earth"): {"score": 4, "desc": "穩定踏實，但可能過於保守"},
        ("earth", "air"): {"score": 2, "desc": "思維方式差異，需要溝通"},
        ("earth", "water"): {"score": 5, "desc": "土水相融，互相滋養成長"},
        ("air", "air"): {"score": 4, "desc": "思想交流豐富，但可能缺乏落地"},
        ("air", "water"): {"score": 2, "desc": "理性與感性的碰撞"},
        ("water", "water"): {"score": 4, "desc": "情感共鳴強，但易陷入情緒"},
    }

    # 星座代碼對應元素
    SIGN_ELEMENTS = {
        "ARI": "fire", "LEO": "fire", "SAG": "fire",
        "TAU": "earth", "VIR": "earth", "CAP": "earth",
        "GEM": "air", "LIB": "air", "AQU": "air",
        "CAN": "water", "SCO": "water", "PIS": "water",
    }

    # 星座順序 (用於計算相位)
    SIGN_ORDER = [
        "ARI", "TAU", "GEM", "CAN", "LEO", "VIR",
        "LIB", "SCO", "SAG", "CAP", "AQU", "PIS"
    ]

    # 星座中文名
    SIGN_NAMES = {
        "ARI": "牡羊座", "TAU": "金牛座", "GEM": "雙子座",
        "CAN": "巨蟹座", "LEO": "獅子座", "VIR": "處女座",
        "LIB": "天秤座", "SCO": "天蠍座", "SAG": "射手座",
        "CAP": "摩羯座", "AQU": "水瓶座", "PIS": "雙魚座",
    }

    def get_element(self, sign_code: str) -> str:
        """取得星座元素"""
        return self.SIGN_ELEMENTS.get(sign_code.upper(), "unknown")

    def get_sign_distance(self, sign1: str, sign2: str) -> int:
        """計算兩星座之間的距離 (0-6)"""
        try:
            idx1 = self.SIGN_ORDER.index(sign1.upper())
            idx2 = self.SIGN_ORDER.index(sign2.upper())
            dist = abs(idx2 - idx1)
            return min(dist, 12 - dist)
        except ValueError:
            return -1

    def get_aspect_type(self, sign1: str, sign2: str) -> dict:
        """計算兩星座的相位關係"""
        distance = self.get_sign_distance(sign1, sign2)

        aspect_types = {
            0: {"type": "conjunction", "name": "同星座", "harmony": 4, "desc": "高度相似，理解彼此"},
            1: {"type": "semi-sextile", "name": "鄰座", "harmony": 2, "desc": "需要適應不同節奏"},
            2: {"type": "sextile", "name": "六分相", "harmony": 4, "desc": "友好和諧，互相支持"},
            3: {"type": "square", "name": "四分相", "harmony": 2, "desc": "挑戰與成長並存"},
            4: {"type": "trine", "name": "三分相", "harmony": 5, "desc": "自然流動，心靈契合"},
            5: {"type": "quincunx", "name": "補十二分相", "harmony": 2, "desc": "需要調整與妥協"},
            6: {"type": "opposition", "name": "對宮", "harmony": 3, "desc": "互補吸引，需平衡"},
        }

        return aspect_types.get(distance, {"type": "unknown", "name": "未知", "harmony": 3, "desc": ""})

    def get_element_compatibility(self, sign1: str, sign2: str) -> dict:
        """取得元素相性"""
        elem1 = self.get_element(sign1)
        elem2 = self.get_element(sign2)

        # 確保順序一致 (排序)
        pair = tuple(sorted([elem1, elem2]))
        compat = self.ELEMENT_COMPATIBILITY.get(pair)

        if not compat:
            # 相同元素
            pair = (elem1, elem1) if elem1 == elem2 else pair
            compat = self.ELEMENT_COMPATIBILITY.get(pair, {"score": 3, "desc": "中等相性"})

        return {
            "element1": elem1,
            "element2": elem2,
            **compat
        }

    def calculate_compatibility(
        self,
        sign1: str,
        sign2: str,
        dt: Optional[datetime] = None
    ) -> dict:
        """計算完整配對分析"""
        sign1 = sign1.upper()
        sign2 = sign2.upper()

        # 基礎相位分析
        aspect = self.get_aspect_type(sign1, sign2)
        element = self.get_element_compatibility(sign1, sign2)

        # 計算綜合分數 (1-5)
        base_score = (aspect["harmony"] + element["score"]) / 2

        # 取得當前天象影響
        sky_influence = self._get_sky_influence(dt)

        # 調整分數
        final_score = min(5, max(1, base_score + sky_influence["modifier"]))

        return {
            "sign1_code": sign1,
            "sign1_name": self.SIGN_NAMES.get(sign1, sign1),
            "sign2_code": sign2,
            "sign2_name": self.SIGN_NAMES.get(sign2, sign2),
            "overall_score": round(final_score, 1),
            "aspect": aspect,
            "element_compatibility": element,
            "sky_influence": sky_influence,
            "advice": self._generate_advice(aspect, element, sky_influence)
        }

    def _get_sky_influence(self, dt: Optional[datetime] = None) -> dict:
        """取得當前天象對感情的影響"""
        try:
            retrograde = astrology_service.ephemeris.get_retrograde_planets(dt)
            venus_retro = any(r["planet"] == "venus" for r in retrograde)
            mercury_retro = any(r["planet"] == "mercury" for r in retrograde)

            influences = []
            modifier = 0

            if venus_retro:
                influences.append("金星逆行中，舊情可能復燃，但新關係需謹慎")
                modifier -= 0.5
            if mercury_retro:
                influences.append("水星逆行中，溝通容易產生誤會，建議多確認")
                modifier -= 0.3

            # 月相影響
            moon = astrology_service.ephemeris.get_moon_phase(dt)
            if moon:
                phase_name = moon.get("phase_name_zh", "")
                if "滿月" in phase_name:
                    influences.append("滿月期間情感能量飽滿，適合深度交流")
                    modifier += 0.3
                elif "新月" in phase_name:
                    influences.append("新月期間適合開啟新的互動模式")
                    modifier += 0.2

            if not influences:
                influences.append("目前天象平穩，適合穩定發展感情")

            return {
                "influences": influences,
                "modifier": modifier,
                "venus_retrograde": venus_retro,
                "mercury_retrograde": mercury_retro
            }
        except Exception:
            return {
                "influences": ["天象計算暫時無法使用"],
                "modifier": 0,
                "venus_retrograde": False,
                "mercury_retrograde": False
            }

    def _generate_advice(self, aspect: dict, element: dict, sky: dict) -> str:
        """生成配對建議"""
        advice_parts = []

        # 根據相位給建議
        if aspect["harmony"] >= 4:
            advice_parts.append("你們天生契合度高，自然相處即可。")
        elif aspect["harmony"] <= 2:
            advice_parts.append("你們需要更多耐心與理解，但挑戰帶來成長。")
        else:
            advice_parts.append("你們有互補的特質，可以從對方身上學習。")

        # 元素建議
        advice_parts.append(element["desc"] + "。")

        # 天象建議
        if sky.get("venus_retrograde"):
            advice_parts.append("金星逆行期間，建議回顧關係中的問題。")

        return "".join(advice_parts)

    def get_weekly_compatibility(
        self,
        sign1: str,
        sign2: str,
        dt: Optional[datetime] = None
    ) -> dict:
        """取得本週配對運勢 (簡化版，用於週運勢頁面)"""
        full = self.calculate_compatibility(sign1, sign2, dt)

        return {
            "partner_sign": full["sign2_name"],
            "score": full["overall_score"],
            "aspect_name": full["aspect"]["name"],
            "summary": full["advice"],
            "sky_note": full["sky_influence"]["influences"][0] if full["sky_influence"]["influences"] else ""
        }


# 全域實例
compatibility_service = CompatibilityService()
