"""
占星計算服務 - 相位計算和解讀
"""
from datetime import datetime
from typing import Optional
from .ephemeris import ephemeris_service


class AstrologyService:
    """占星計算服務"""

    # 主要相位定義 (角度, 容許度, 名稱, 性質)
    ASPECTS = [
        (0, 8, "合相", "conjunction", "強烈"),
        (60, 6, "六分相", "sextile", "和諧"),
        (90, 8, "四分相", "square", "緊張"),
        (120, 8, "三分相", "trine", "和諧"),
        (180, 8, "對分相", "opposition", "對立"),
    ]

    # 行星主宰星座
    RULERSHIPS = {
        "sun": ["LEO"],
        "moon": ["CAN"],
        "mercury": ["GEM", "VIR"],
        "venus": ["TAU", "LIB"],
        "mars": ["ARI", "SCO"],
        "jupiter": ["SAG", "PIS"],
        "saturn": ["CAP", "AQU"],
        "uranus": ["AQU"],
        "neptune": ["PIS"],
        "pluto": ["SCO"],
    }

    def __init__(self):
        self.ephemeris = ephemeris_service

    def calculate_aspect(self, lon1: float, lon2: float) -> Optional[dict]:
        """計算兩個黃經之間的相位"""
        diff = abs(lon1 - lon2)
        if diff > 180:
            diff = 360 - diff

        for angle, orb, name_zh, name_en, nature in self.ASPECTS:
            if abs(diff - angle) <= orb:
                return {
                    "aspect_angle": angle,
                    "actual_angle": round(diff, 2),
                    "orb": round(abs(diff - angle), 2),
                    "name_zh": name_zh,
                    "name_en": name_en,
                    "nature": nature
                }

        return None

    def get_all_aspects(self, dt: Optional[datetime] = None) -> list[dict]:
        """取得所有行星之間的相位"""
        positions = self.ephemeris.get_planet_positions(dt)
        aspects = []

        # 過濾掉有錯誤的行星
        valid_positions = [p for p in positions if "error" not in p]

        # 計算所有行星對之間的相位
        for i, p1 in enumerate(valid_positions):
            for p2 in valid_positions[i + 1:]:
                aspect = self.calculate_aspect(p1["longitude"], p2["longitude"])
                if aspect:
                    aspects.append({
                        "planet1": p1["planet"],
                        "planet1_zh": p1["name_zh"],
                        "planet2": p2["planet"],
                        "planet2_zh": p2["name_zh"],
                        **aspect
                    })

        return aspects

    def is_planet_dignified(self, planet: str, sign_code: str) -> dict:
        """判斷行星是否在入廟或落陷"""
        rulerships = self.RULERSHIPS.get(planet, [])

        # 入廟 (在自己主宰的星座)
        if sign_code in rulerships:
            return {
                "status": "domicile",
                "status_zh": "入廟",
                "description": "行星力量強大"
            }

        # 落陷 (在對面的星座)
        OPPOSITE_SIGNS = {
            "ARI": "LIB", "TAU": "SCO", "GEM": "SAG", "CAN": "CAP",
            "LEO": "AQU", "VIR": "PIS", "LIB": "ARI", "SCO": "TAU",
            "SAG": "GEM", "CAP": "CAN", "AQU": "LEO", "PIS": "VIR"
        }

        for ruled_sign in rulerships:
            if OPPOSITE_SIGNS.get(ruled_sign) == sign_code:
                return {
                    "status": "detriment",
                    "status_zh": "落陷",
                    "description": "行星力量減弱"
                }

        return {
            "status": "neutral",
            "status_zh": "中性",
            "description": "行星正常運作"
        }

    def get_current_sky_summary(self, dt: Optional[datetime] = None) -> dict:
        """取得當前天象摘要"""
        positions = self.ephemeris.get_planet_positions(dt)
        moon_phase = self.ephemeris.get_moon_phase(dt)
        retrograde = self.ephemeris.get_retrograde_planets(dt)
        aspects = self.get_all_aspects(dt)

        # 找出重要相位 (容許度小於 3 度)
        major_aspects = [a for a in aspects if a["orb"] < 3]

        # 統計元素分布
        elements = {"fire": 0, "earth": 0, "air": 0, "water": 0}
        element_signs = {
            "fire": ["ARI", "LEO", "SAG"],
            "earth": ["TAU", "VIR", "CAP"],
            "air": ["GEM", "LIB", "AQU"],
            "water": ["CAN", "SCO", "PIS"]
        }

        for pos in positions:
            if "sign_code" in pos:
                for elem, signs in element_signs.items():
                    if pos["sign_code"] in signs:
                        elements[elem] += 1
                        break

        element_zh = {"fire": "火象", "earth": "土象", "air": "風象", "water": "水象"}
        dominant_element = max(elements, key=elements.get)

        return {
            "datetime": dt.isoformat() if dt else datetime.utcnow().isoformat(),
            "moon_phase": moon_phase,
            "retrograde_planets": retrograde,
            "retrograde_count": len(retrograde),
            "major_aspects": major_aspects[:5],  # 最多顯示 5 個
            "element_distribution": elements,
            "dominant_element": dominant_element,
            "dominant_element_zh": element_zh[dominant_element],
            "planet_positions": positions
        }


# 全域實例
astrology_service = AstrologyService()
