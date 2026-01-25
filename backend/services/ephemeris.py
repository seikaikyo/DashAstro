"""
星曆計算服務 - 使用 Skyfield 計算行星位置
"""
from datetime import datetime, timezone
from typing import Optional
from skyfield.api import load, Topos
from skyfield.timelib import Time
from functools import lru_cache
import math


class EphemerisService:
    """星曆計算服務"""

    # 行星對應表 (使用 Skyfield 內建的行星名稱)
    PLANETS = {
        "sun": ("sun", "太陽"),
        "moon": ("moon", "月亮"),
        "mercury": ("mercury barycenter", "水星"),
        "venus": ("venus barycenter", "金星"),
        "mars": ("mars barycenter", "火星"),
        "jupiter": ("jupiter barycenter", "木星"),
        "saturn": ("saturn barycenter", "土星"),
        "uranus": ("uranus barycenter", "天王星"),
        "neptune": ("neptune barycenter", "海王星"),
        "pluto": ("pluto barycenter", "冥王星"),
    }

    # 星座對應表 (黃道十二宮)
    ZODIAC_SIGNS = [
        ("ARI", "牡羊座", 0),
        ("TAU", "金牛座", 30),
        ("GEM", "雙子座", 60),
        ("CAN", "巨蟹座", 90),
        ("LEO", "獅子座", 120),
        ("VIR", "處女座", 150),
        ("LIB", "天秤座", 180),
        ("SCO", "天蠍座", 210),
        ("SAG", "射手座", 240),
        ("CAP", "摩羯座", 270),
        ("AQU", "水瓶座", 300),
        ("PIS", "雙魚座", 330),
    ]

    def __init__(self):
        self.ts = load.timescale()
        self._ephemeris = None

    @property
    def ephemeris(self):
        """懶加載星曆資料"""
        if self._ephemeris is None:
            # 使用較小的 de421.bsp 檔案 (17MB)
            self._ephemeris = load("de421.bsp")
        return self._ephemeris

    def _get_time(self, dt: Optional[datetime] = None) -> Time:
        """將 datetime 轉換為 Skyfield Time"""
        if dt is None:
            dt = datetime.now(timezone.utc)
        elif dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return self.ts.from_datetime(dt)

    def _ecliptic_longitude(self, body, t: Time) -> float:
        """計算天體的黃經 (ecliptic longitude)"""
        earth = self.ephemeris["earth"]
        target = self.ephemeris[body]

        astrometric = earth.at(t).observe(target)
        lat, lon, distance = astrometric.ecliptic_latlon()

        return lon.degrees

    def _longitude_to_zodiac(self, longitude: float) -> dict:
        """將黃經轉換為星座位置"""
        # 確保經度在 0-360 範圍內
        longitude = longitude % 360

        for i, (code, name, start) in enumerate(self.ZODIAC_SIGNS):
            next_start = self.ZODIAC_SIGNS[(i + 1) % 12][2]
            if next_start == 0:
                next_start = 360

            if start <= longitude < next_start or (start > next_start and (longitude >= start or longitude < next_start)):
                degree_in_sign = longitude - start
                if degree_in_sign < 0:
                    degree_in_sign += 360
                return {
                    "sign_code": code,
                    "sign_name": name,
                    "degree": round(degree_in_sign, 2),
                    "longitude": round(longitude, 2)
                }

        # 預設回傳牡羊座
        return {
            "sign_code": "ARI",
            "sign_name": "牡羊座",
            "degree": round(longitude, 2),
            "longitude": round(longitude, 2)
        }

    def get_planet_positions(self, dt: Optional[datetime] = None) -> list[dict]:
        """取得所有行星位置"""
        t = self._get_time(dt)
        positions = []

        for planet_key, (body, name_zh) in self.PLANETS.items():
            try:
                longitude = self._ecliptic_longitude(body, t)
                zodiac = self._longitude_to_zodiac(longitude)

                positions.append({
                    "planet": planet_key,
                    "name_zh": name_zh,
                    **zodiac
                })
            except Exception as e:
                positions.append({
                    "planet": planet_key,
                    "name_zh": name_zh,
                    "error": str(e)
                })

        return positions

    def get_moon_phase(self, dt: Optional[datetime] = None) -> dict:
        """計算月相"""
        t = self._get_time(dt)

        sun_lon = self._ecliptic_longitude("sun", t)
        moon_lon = self._ecliptic_longitude("moon", t)

        # 月相角度 (月亮與太陽的黃經差)
        phase_angle = (moon_lon - sun_lon) % 360

        # 月相名稱
        phase_names = [
            (0, 45, "新月", "new_moon"),
            (45, 90, "上弦月漸盈", "waxing_crescent"),
            (90, 135, "上弦月", "first_quarter"),
            (135, 180, "盈凸月", "waxing_gibbous"),
            (180, 225, "滿月", "full_moon"),
            (225, 270, "虧凸月", "waning_gibbous"),
            (270, 315, "下弦月", "last_quarter"),
            (315, 360, "下弦月漸虧", "waning_crescent"),
        ]

        phase_zh = "新月"
        phase_en = "new_moon"
        for start, end, zh, en in phase_names:
            if start <= phase_angle < end:
                phase_zh = zh
                phase_en = en
                break

        # 月亮亮度 (近似值)
        illumination = (1 - math.cos(math.radians(phase_angle))) / 2

        return {
            "phase_angle": round(phase_angle, 2),
            "phase_name_zh": phase_zh,
            "phase_name_en": phase_en,
            "illumination": round(illumination * 100, 1),
            "moon_longitude": round(moon_lon, 2),
            "sun_longitude": round(sun_lon, 2)
        }

    def is_retrograde(self, planet_key: str, dt: Optional[datetime] = None) -> bool:
        """
        判斷行星是否逆行
        透過比較前後兩天的黃經變化來判斷
        """
        if planet_key in ["sun", "moon"]:
            return False  # 太陽和月亮不會逆行

        t = self._get_time(dt)

        # 計算前一天和後一天的黃經
        t_before = self.ts.tt_jd(t.tt - 1)
        t_after = self.ts.tt_jd(t.tt + 1)

        body = self.PLANETS.get(planet_key, (None, None))[0]
        if body is None:
            return False

        lon_before = self._ecliptic_longitude(body, t_before)
        lon_after = self._ecliptic_longitude(body, t_after)

        # 處理跨越 0 度的情況
        diff = lon_after - lon_before
        if diff > 180:
            diff -= 360
        elif diff < -180:
            diff += 360

        return diff < 0

    def get_retrograde_planets(self, dt: Optional[datetime] = None) -> list[dict]:
        """取得所有逆行中的行星"""
        retrograde = []

        for planet_key, (body, name_zh) in self.PLANETS.items():
            if planet_key in ["sun", "moon"]:
                continue

            if self.is_retrograde(planet_key, dt):
                retrograde.append({
                    "planet": planet_key,
                    "name_zh": name_zh
                })

        return retrograde


# 全域實例
ephemeris_service = EphemerisService()
