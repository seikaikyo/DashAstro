"""日本吉日計算服務（一粒萬倍日、天赦日等）"""
from datetime import date, timedelta
from typing import Optional


class JapaneseCalendarService:
    """日本傳統吉日計算"""

    # 一粒萬倍日對照表：月份（節氣月）對應的地支
    # 一粒萬倍日指「一粒種子可結萬倍果實」的吉日
    ICHIRYU_MANBAI_BRANCHES = {
        1: ["丑", "午"],   # 正月（立春後）
        2: ["酉", "寅"],   # 二月（驚蟄後）
        3: ["子", "卯"],   # 三月（清明後）
        4: ["卯", "辰"],   # 四月（立夏後）
        5: ["巳", "午"],   # 五月（芒種後）
        6: ["酉", "午"],   # 六月（小暑後）
        7: ["子", "未"],   # 七月（立秋後）
        8: ["卯", "申"],   # 八月（白露後）
        9: ["酉", "午"],   # 九月（寒露後）
        10: ["酉", "戌"],  # 十月（立冬後）
        11: ["亥", "子"],  # 十一月（大雪後）
        12: ["卯", "子"],  # 十二月（小寒後）
    }

    # 十二地支
    EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳",
                        "午", "未", "申", "酉", "戌", "亥"]

    # 天干
    HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊",
                      "己", "庚", "辛", "壬", "癸"]

    # 六曜（大安、赤口、先勝、友引、先負、佛滅）
    ROKUYO = ["大安", "赤口", "先勝", "友引", "先負", "佛滅"]

    # 基準日：已知的干支日（2024年1月1日為甲子日的第 21 天）
    # 2024/1/1 是癸卯年甲子月甲辰日
    REFERENCE_DATE = date(2024, 1, 1)
    REFERENCE_DAY_INDEX = 40  # 甲辰 = 第 41 個干支（從 0 算是 40）

    def get_day_ganzhi(self, target_date: date) -> tuple[str, str, int]:
        """取得指定日期的干支

        Returns:
            (天干, 地支, 六十甲子序號 0-59)
        """
        days_diff = (target_date - self.REFERENCE_DATE).days
        ganzhi_index = (self.REFERENCE_DAY_INDEX + days_diff) % 60

        stem_index = ganzhi_index % 10
        branch_index = ganzhi_index % 12

        return (
            self.HEAVENLY_STEMS[stem_index],
            self.EARTHLY_BRANCHES[branch_index],
            ganzhi_index
        )

    def get_solar_term_month(self, target_date: date) -> int:
        """取得節氣月份（近似計算）

        節氣月以立春開始，每月約 30-31 天
        這是簡化計算，實際應用中可引入更精確的節氣計算
        """
        # 簡化：使用西曆月份但調整立春（約2月4日）
        year = target_date.year
        month = target_date.month
        day = target_date.day

        # 立春約在 2 月 4 日
        if month == 1 or (month == 2 and day < 4):
            return 12  # 還在前一年的臘月
        elif month == 2:
            return 1
        elif month == 3 and day < 6:
            return 1
        elif month == 3:
            return 2
        elif month == 4 and day < 5:
            return 2
        elif month == 4:
            return 3
        elif month == 5 and day < 6:
            return 3
        elif month == 5:
            return 4
        elif month == 6 and day < 6:
            return 4
        elif month == 6:
            return 5
        elif month == 7 and day < 7:
            return 5
        elif month == 7:
            return 6
        elif month == 8 and day < 8:
            return 6
        elif month == 8:
            return 7
        elif month == 9 and day < 8:
            return 7
        elif month == 9:
            return 8
        elif month == 10 and day < 8:
            return 8
        elif month == 10:
            return 9
        elif month == 11 and day < 8:
            return 9
        elif month == 11:
            return 10
        elif month == 12 and day < 7:
            return 10
        elif month == 12 and day < 22:
            return 11
        else:
            return 12

    def is_ichiryu_manbai(self, target_date: date) -> bool:
        """判斷是否為一粒萬倍日"""
        _, branch, _ = self.get_day_ganzhi(target_date)
        solar_month = self.get_solar_term_month(target_date)
        lucky_branches = self.ICHIRYU_MANBAI_BRANCHES.get(solar_month, [])
        return branch in lucky_branches

    def get_rokuyo(self, target_date: date) -> str:
        """取得六曜（簡化計算）

        六曜循環：舊曆每月 1 日固定
        - 正月、七月 1 日：先勝
        - 二月、八月 1 日：友引
        - 三月、九月 1 日：先負
        - 四月、十月 1 日：佛滅
        - 五月、十一月 1 日：大安
        - 六月、十二月 1 日：赤口

        這裡用簡化公式近似
        """
        # 簡化計算：用西曆近似
        base = (target_date.month + target_date.day) % 6
        return self.ROKUYO[base]

    def is_taian(self, target_date: date) -> bool:
        """判斷是否為大安日"""
        return self.get_rokuyo(target_date) == "大安"

    def get_lucky_days_in_range(
        self,
        start_date: date,
        end_date: date,
        day_type: str = "ichiryu_manbai"
    ) -> list[dict]:
        """取得指定範圍內的吉日

        Args:
            start_date: 開始日期
            end_date: 結束日期
            day_type: 吉日類型 (ichiryu_manbai, taian, all)

        Returns:
            吉日列表
        """
        result = []
        current = start_date

        while current <= end_date:
            stem, branch, _ = self.get_day_ganzhi(current)
            rokuyo = self.get_rokuyo(current)
            is_ichiryu = self.is_ichiryu_manbai(current)
            is_taian_day = rokuyo == "大安"

            include = False
            types = []

            if day_type == "all":
                if is_ichiryu:
                    types.append("一粒萬倍日")
                if is_taian_day:
                    types.append("大安")
                include = bool(types)
            elif day_type == "ichiryu_manbai":
                include = is_ichiryu
                if is_ichiryu:
                    types.append("一粒萬倍日")
            elif day_type == "taian":
                include = is_taian_day
                if is_taian_day:
                    types.append("大安")

            if include:
                result.append({
                    "date": current.isoformat(),
                    "weekday": ["日", "一", "二", "三", "四", "五", "六"][current.weekday()],
                    "ganzhi": f"{stem}{branch}",
                    "rokuyo": rokuyo,
                    "types": types,
                    "is_double_lucky": is_ichiryu and is_taian_day
                })

            current += timedelta(days=1)

        return result

    def get_month_lucky_days(
        self,
        year: int,
        month: int,
        day_type: str = "all"
    ) -> list[dict]:
        """取得指定月份的吉日"""
        start_date = date(year, month, 1)

        # 計算月底
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)

        return self.get_lucky_days_in_range(start_date, end_date, day_type)

    def get_next_lucky_day(
        self,
        from_date: Optional[date] = None,
        day_type: str = "ichiryu_manbai"
    ) -> Optional[dict]:
        """取得下一個吉日"""
        if from_date is None:
            from_date = date.today()

        # 最多搜尋 60 天
        end_date = from_date + timedelta(days=60)
        lucky_days = self.get_lucky_days_in_range(from_date, end_date, day_type)

        return lucky_days[0] if lucky_days else None


# 全域實例
japanese_calendar = JapaneseCalendarService()
