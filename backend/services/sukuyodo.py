"""宿曜道計算服務 - 日本真言宗占星術"""
import json
from datetime import date
from pathlib import Path
from typing import Optional


class SukuyodoService:
    """
    宿曜道（真言宗宿曜占星術）計算服務

    基於空海《宿曜經》，使用農曆生日計算本命宿（27宿之一），
    並提供雙人相性診斷（六種關係）。
    """

    # 月宿傍通曆：農曆月份對應的起始宿
    # 每月初一從這個宿開始，之後每天進一宿
    MONTH_START_MANSION = {
        1: 11,   # 正月：危宿（室宿之後）
        2: 13,   # 二月：壁宿
        3: 15,   # 三月：婁宿
        4: 17,   # 四月：昴宿
        5: 19,   # 五月：觜宿
        6: 21,   # 六月：井宿
        7: 24,   # 七月：星宿
        8: 0,    # 八月：角宿
        9: 2,    # 九月：氐宿
        10: 4,   # 十月：心宿
        11: 7,   # 十一月：斗宿
        12: 9,   # 十二月：女宿
    }

    def __init__(self):
        self._mansions_data = None
        self._relations_data = None
        self._elements_data = None
        self._metadata = None

    def _load_data(self):
        """載入所有資料"""
        if self._mansions_data is None:
            data_path = Path(__file__).parent.parent / "data" / "sukuyodo_mansions.json"
            with open(data_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._mansions_data = data["mansions"]
                self._relations_data = data["relations"]
                self._elements_data = data.get("elements", {})
                self._metadata = data.get("metadata", {})

    @property
    def mansions_data(self) -> list[dict]:
        """載入 27 宿資料"""
        self._load_data()
        return self._mansions_data

    @property
    def relations_data(self) -> dict:
        """載入關係資料"""
        self._load_data()
        return self._relations_data

    @property
    def elements_data(self) -> dict:
        """載入元素資料"""
        self._load_data()
        return self._elements_data

    @property
    def metadata(self) -> dict:
        """載入元資料"""
        self._load_data()
        return self._metadata

    def solar_to_lunar(self, solar_date: date) -> tuple[int, int, int, bool]:
        """
        西曆轉農曆

        Args:
            solar_date: 西曆日期

        Returns:
            (年, 月, 日, 是否閏月)
        """
        try:
            from lunarcalendar import Converter, Solar
            solar = Solar(solar_date.year, solar_date.month, solar_date.day)
            lunar = Converter.Solar2Lunar(solar)
            return (lunar.year, lunar.month, lunar.day, lunar.isleap)
        except ImportError:
            # 如果沒有安裝 lunarcalendar，使用簡易近似算法
            # 這只是備用方案，生產環境應該安裝 lunarcalendar
            return self._approximate_lunar(solar_date)

    def _approximate_lunar(self, solar_date: date) -> tuple[int, int, int, bool]:
        """
        簡易農曆近似算法（備用）

        注意：這只是近似值，可能有 1-2 天誤差
        生產環境請安裝 lunarcalendar 套件
        """
        # 以春節（約 2 月初）為基準估算
        # 這是非常簡化的算法，只用於沒有 lunarcalendar 時的備用
        year = solar_date.year
        month = solar_date.month
        day = solar_date.day

        # 春節約在 1/21 - 2/20 之間
        # 簡化：假設春節在 2 月 1 日
        if month == 1 or (month == 2 and day < 10):
            lunar_year = year - 1
            lunar_month = 12 if month == 1 else 1
        else:
            lunar_year = year
            # 農曆月份約比西曆晚 1 個月
            lunar_month = (month - 1) if month > 1 else 12

        # 日期簡化處理
        lunar_day = day if day <= 30 else 30

        return (lunar_year, lunar_month, lunar_day, False)

    def lunar_to_solar(self, lunar_year: int, lunar_month: int, lunar_day: int) -> date | None:
        """
        農曆轉西曆

        Args:
            lunar_year: 農曆年
            lunar_month: 農曆月 (1-12)
            lunar_day: 農曆日 (1-30)

        Returns:
            對應的西曆日期，若無效則返回 None
        """
        try:
            from lunarcalendar import Converter, Lunar
            lunar = Lunar(lunar_year, lunar_month, lunar_day, isleap=False)
            solar = Converter.Lunar2Solar(lunar)
            return date(solar.year, solar.month, solar.day)
        except (ImportError, ValueError, Exception):
            # 無法轉換（可能是無效日期）
            return None

    def get_solar_dates_for_lunar(
        self,
        lunar_month: int,
        lunar_day: int,
        year_range: int = 20
    ) -> list[dict]:
        """
        將農曆月日轉換為多年的西曆日期

        Args:
            lunar_month: 農曆月 (1-12)
            lunar_day: 農曆日 (1-30)
            year_range: 年份範圍（±N 年）

        Returns:
            西曆日期列表
        """
        from datetime import date as dt
        current_year = dt.today().year
        start_year = current_year - year_range
        end_year = current_year + year_range

        results = []
        for year in range(start_year, end_year + 1):
            solar_date = self.lunar_to_solar(year, lunar_month, lunar_day)
            if solar_date:
                results.append({
                    "lunar_year": year,
                    "solar_date": solar_date.isoformat(),
                    "display": f"{solar_date.year}/{solar_date.month}/{solar_date.day}"
                })

        return results

    def get_mansion_index(self, lunar_month: int, lunar_day: int) -> int:
        """
        根據農曆月日計算本命宿索引

        使用月宿傍通曆：每月初一有固定的起始宿，
        之後每天進一宿（27宿循環）

        Args:
            lunar_month: 農曆月份 (1-12)
            lunar_day: 農曆日期 (1-30)

        Returns:
            本命宿索引 (0-26)
        """
        # 處理閏月：使用對應的月份
        month = lunar_month if 1 <= lunar_month <= 12 else 1

        # 取得該月起始宿
        start = self.MONTH_START_MANSION.get(month, 0)

        # 每天進一宿
        return (start + lunar_day - 1) % 27

    def get_mansion(self, solar_date: date) -> dict:
        """
        根據西曆生日取得本命宿資料

        Args:
            solar_date: 西曆生日

        Returns:
            包含本命宿完整資料的字典
        """
        lunar_year, lunar_month, lunar_day, is_leap = self.solar_to_lunar(solar_date)
        mansion_index = self.get_mansion_index(lunar_month, lunar_day)
        mansion = self.mansions_data[mansion_index]

        return {
            **mansion,
            "solar_date": solar_date.isoformat(),
            "lunar_date": {
                "year": lunar_year,
                "month": lunar_month,
                "day": lunar_day,
                "is_leap": is_leap,
                "display": f"農曆 {lunar_month} 月 {lunar_day} 日"
            }
        }

    def get_relation_type(self, index1: int, index2: int) -> dict:
        """
        計算兩個宿位之間的關係

        三九秘法：根據兩宿之間的距離判斷關係類型

        Args:
            index1: 第一個宿的索引 (0-26)
            index2: 第二個宿的索引 (0-26)

        Returns:
            關係資料
        """
        # 計算距離（雙向）
        distance = abs(index2 - index1)
        reverse_distance = 27 - distance

        # 檢查各種關係
        for rel_key, rel_data in self.relations_data.items():
            distances = rel_data["distances"]
            if distance in distances or reverse_distance in distances:
                return {
                    "type": rel_key,
                    **rel_data
                }

        # 預設：未知關係（不應該發生）
        return {
            "type": "unknown",
            "name": "未知",
            "score": 50,
            "description": "無法判斷關係類型",
            "advice": ""
        }

    def calculate_compatibility(
        self,
        date1: date,
        date2: date
    ) -> dict:
        """
        計算兩人的相性

        Args:
            date1: 第一個人的西曆生日
            date2: 第二個人的西曆生日

        Returns:
            相性分析結果
        """
        mansion1 = self.get_mansion(date1)
        mansion2 = self.get_mansion(date2)

        relation = self.get_relation_type(mansion1["index"], mansion2["index"])

        # 計算距離
        distance = abs(mansion2["index"] - mansion1["index"])
        if distance > 13:
            distance = 27 - distance

        # 計算元素相性加成
        element_bonus = self._calculate_element_bonus(
            mansion1["element"],
            mansion2["element"]
        )

        # 取得元素資料
        elem1_data = self.elements_data.get(mansion1["element"], {})
        elem2_data = self.elements_data.get(mansion2["element"], {})

        # 綜合分數
        final_score = min(100, relation["score"] + element_bonus)

        return {
            "person1": {
                "date": date1.isoformat(),
                "mansion": mansion1["name_jp"],
                "reading": mansion1["reading"],
                "element": mansion1["element"],
                "element_reading": elem1_data.get("reading", ""),
                "element_traits": elem1_data.get("traits", ""),
                "keywords": mansion1["keywords"],
                "index": mansion1["index"]
            },
            "person2": {
                "date": date2.isoformat(),
                "mansion": mansion2["name_jp"],
                "reading": mansion2["reading"],
                "element": mansion2["element"],
                "element_reading": elem2_data.get("reading", ""),
                "element_traits": elem2_data.get("traits", ""),
                "keywords": mansion2["keywords"],
                "index": mansion2["index"]
            },
            "relation": {
                "type": relation["type"],
                "name": relation["name"],
                "name_jp": relation.get("name_jp", relation["name"]),
                "reading": relation.get("reading", ""),
                "description": relation["description"],
                "detailed": relation.get("detailed", ""),
                "advice": relation["advice"],
                "tips": relation.get("tips", []),
                "avoid": relation.get("avoid", []),
                "good_for": relation.get("good_for", [])
            },
            "calculation": {
                "distance": distance,
                "formula": f"|{mansion1['index']} - {mansion2['index']}| = {abs(mansion2['index'] - mansion1['index'])} → 距離 {distance}",
                "element_relation": self._get_element_relation(mansion1["element"], mansion2["element"])
            },
            "score": final_score,
            "element_bonus": element_bonus,
            "summary": self._generate_summary(mansion1, mansion2, relation)
        }

    def _get_element_relation(self, elem1: str, elem2: str) -> str:
        """取得元素關係說明"""
        GENERATING = {
            ("木", "火"): "木生火",
            ("火", "土"): "火生土",
            ("土", "金"): "土生金",
            ("金", "水"): "金生水",
            ("水", "木"): "水生木"
        }

        if elem1 == elem2:
            return f"同元素（{elem1}）+10 分"

        pair = (elem1, elem2)
        reverse_pair = (elem2, elem1)

        if pair in GENERATING:
            return f"{GENERATING[pair]} +5 分"
        if reverse_pair in GENERATING:
            return f"{GENERATING[reverse_pair]} +5 分"

        return "無特殊加成"

    def _calculate_element_bonus(self, elem1: str, elem2: str) -> int:
        """計算元素相性加成"""
        # 五行相生：木生火、火生土、土生金、金生水、水生木
        GENERATING = [
            ("木", "火"),
            ("火", "土"),
            ("土", "金"),
            ("金", "水"),
            ("水", "木")
        ]

        # 日月為特殊元素
        if elem1 == elem2:
            return 10  # 同元素加分

        pair = (elem1, elem2)
        reverse_pair = (elem2, elem1)

        if pair in GENERATING or reverse_pair in GENERATING:
            return 5  # 相生加分

        return 0

    def _generate_summary(
        self,
        mansion1: dict,
        mansion2: dict,
        relation: dict
    ) -> str:
        """生成相性總結"""
        rel_name = relation["name"]
        name1 = mansion1["name_jp"]
        name2 = mansion2["name_jp"]
        score = relation["score"]

        if score >= 90:
            level = "非常合拍"
        elif score >= 75:
            level = "相當不錯"
        elif score >= 60:
            level = "需要磨合"
        else:
            level = "要多小心"

        return (
            f"{name1}與{name2}的關係是「{rel_name}」，整體評價：{level}。\n"
            f"{relation['description']}\n"
            f"建議：{relation['advice']}"
        )

    def get_all_mansions(self) -> list[dict]:
        """取得所有 27 宿資料"""
        return self.mansions_data

    def get_mansion_lunar_dates(self, mansion_index: int) -> list[dict]:
        """
        取得某個宿位對應的農曆生日範圍

        Args:
            mansion_index: 宿位索引 (0-26)

        Returns:
            對應的農曆月日列表
        """
        results = []

        # 每個月檢查哪些日期會對應到這個宿位
        for month, start_mansion in self.MONTH_START_MANSION.items():
            # 計算這個月的哪一天對應到目標宿位
            # mansion_index = (start_mansion + day - 1) % 27
            # day = (mansion_index - start_mansion + 1) % 27
            # 如果結果 <= 0，加 27

            day = (mansion_index - start_mansion + 1) % 27
            if day <= 0:
                day += 27

            # 農曆每月最多 30 天，只取有效日期
            if 1 <= day <= 30:
                month_names = {
                    1: "正月", 2: "二月", 3: "三月", 4: "四月",
                    5: "五月", 6: "六月", 7: "七月", 8: "八月",
                    9: "九月", 10: "十月", 11: "十一月", 12: "十二月"
                }
                results.append({
                    "lunar_month": month,
                    "lunar_month_name": month_names[month],
                    "lunar_day": day,
                    "display": f"{month_names[month]}{day}日"
                })

        return results

    def find_compatible_mansions(self, solar_date: date) -> dict:
        """
        根據生日找出最佳配對與需要避免的本命宿

        Args:
            solar_date: 西曆生日

        Returns:
            包含榮親、業胎、安壊三類配對宿位的資料
        """
        mansion = self.get_mansion(solar_date)
        user_index = mansion["index"]

        # 各關係類型的距離定義（完整六種關係）
        COMPATIBILITY_TYPES = {
            "mei": {
                "relation": "命",
                "reading": "めい",
                "distances": [0],
                "score": 85,
                "description": "如同鏡子般的存在，彼此理解但優缺點皆被放大"
            },
            "gyotai": {
                "relation": "業胎",
                "reading": "ぎょうたい",
                "distances": [9, 18],
                "score": 90,
                "description": "前世因緣深厚，常有似曾相識之感"
            },
            "eishin": {
                "relation": "榮親",
                "reading": "えいしん",
                "distances": [1, 3, 10, 12, 15, 17, 24, 26],
                "score": 95,
                "description": "最適合結婚的對象，互相提攜成長的良緣"
            },
            "yusui": {
                "relation": "友衰",
                "reading": "ゆうすい",
                "distances": [2, 5, 11, 13, 14, 16, 22, 25],
                "score": 70,
                "description": "相處舒適自在，但需注意不要一起停滯不前"
            },
            "ankai": {
                "relation": "安壊",
                "reading": "あんかい",
                "distances": [4, 6, 21, 23],
                "score": 50,
                "description": "強烈吸引力但權力不對等，需謹慎經營"
            },
            "kisei": {
                "relation": "危成",
                "reading": "きせい",
                "distances": [7, 8, 19, 20],
                "score": 75,
                "description": "互補的關係，需要磨合但能促進彼此成長"
            }
        }

        result = {
            "your_mansion": {
                "name_jp": mansion["name_jp"],
                "name_zh": mansion["name_zh"],
                "reading": mansion["reading"],
                "index": user_index,
                "element": mansion["element"],
                "lunar_date": mansion["lunar_date"]
            }
        }

        # 計算各類型的配對宿位
        for key, config in COMPATIBILITY_TYPES.items():
            indices = set()
            for d in config["distances"]:
                indices.add((user_index + d) % 27)
                indices.add((user_index - d + 27) % 27)

            # 取得這些宿位的詳細資料
            mansions = []
            for idx in sorted(indices):
                m = self.mansions_data[idx]
                elem_data = self.elements_data.get(m["element"], {})
                lunar_dates = self.get_mansion_lunar_dates(idx)

                # 為每個農曆日期加上西曆對照
                for ld in lunar_dates:
                    ld["solar_dates"] = self.get_solar_dates_for_lunar(
                        ld["lunar_month"],
                        ld["lunar_day"],
                        year_range=20
                    )

                mansions.append({
                    "name_jp": m["name_jp"],
                    "name_zh": m["name_zh"],
                    "reading": m["reading"],
                    "index": idx,
                    "element": m["element"],
                    "element_reading": elem_data.get("reading", ""),
                    "keywords": m["keywords"],
                    "personality": m["personality"],
                    "lunar_dates": lunar_dates
                })

            result[key] = {
                "relation": config["relation"],
                "reading": config["reading"],
                "score": config["score"],
                "description": config["description"],
                "mansions": mansions
            }

        return result

    # ==================== 運勢計算 ====================

    def _load_fortune_data(self):
        """載入運勢資料"""
        if not hasattr(self, '_fortune_data') or self._fortune_data is None:
            data_path = Path(__file__).parent.parent / "data" / "sukuyodo_fortune.json"
            with open(data_path, "r", encoding="utf-8") as f:
                self._fortune_data = json.load(f)
        return self._fortune_data

    def _calc_fortune_element_relation(self, elem1: str, elem2: str) -> tuple[str, int]:
        """
        計算運勢用的元素關係

        Returns:
            (關係類型, 加成分數)
        """
        fortune_data = self._load_fortune_data()

        if elem1 == elem2:
            return ("same", fortune_data["element_relations"]["same"]["bonus"])

        # 檢查相生
        for pair in fortune_data["generating_pairs"]:
            if (elem1 == pair[0] and elem2 == pair[1]) or \
               (elem1 == pair[1] and elem2 == pair[0]):
                return ("generating", fortune_data["element_relations"]["generating"]["bonus"])

        # 檢查相剋
        for pair in fortune_data["conflicting_pairs"]:
            if (elem1 == pair[0] and elem2 == pair[1]) or \
               (elem1 == pair[1] and elem2 == pair[0]):
                return ("conflicting", fortune_data["element_relations"]["conflicting"]["bonus"])

        # 檢查相洩
        for pair in fortune_data["weakening_pairs"]:
            if (elem1 == pair[0] and elem2 == pair[1]) or \
               (elem1 == pair[1] and elem2 == pair[0]):
                return ("weakening", fortune_data["element_relations"]["weakening"]["bonus"])

        # 日月特殊處理
        if elem1 in ["日", "月"] or elem2 in ["日", "月"]:
            return ("generating", 5)  # 日月與大部分元素相合

        return ("neutral", fortune_data["element_relations"]["neutral"]["bonus"])

    def calculate_daily_fortune(self, birth_date: date, target_date: date) -> dict:
        """
        計算每日運勢

        Args:
            birth_date: 出生日期
            target_date: 要查詢的日期

        Returns:
            每日運勢資料
        """
        import random

        fortune_data = self._load_fortune_data()
        mansion = self.get_mansion(birth_date)
        user_element = mansion["element"]

        # 取得當日七曜
        weekday = target_date.weekday()  # 0=Monday
        # 轉換為日本七曜（0=Sunday）
        jp_weekday = (weekday + 1) % 7
        day_info = fortune_data["weekday_elements"][str(jp_weekday)]
        day_element = day_info["element"]

        # 計算元素關係
        relation_type, base_bonus = self._calc_fortune_element_relation(user_element, day_element)
        relation_desc = fortune_data["element_relations"].get(
            relation_type,
            fortune_data["element_relations"]["neutral"]
        )["description"]

        # 基礎分數 (60-80)
        base_score = 70

        # 根據關係調整
        overall_score = max(30, min(100, base_score + base_bonus))

        # 計算各項運勢（加入一些變化）
        random.seed(f"{birth_date.isoformat()}{target_date.isoformat()}")

        def calc_category_score(category: str) -> int:
            cat_data = fortune_data["fortune_categories"][category]
            cat_bonus = 5 if user_element in cat_data["favorable_elements"] else 0
            day_bonus = 5 if day_element in cat_data["favorable_elements"] else 0
            variation = random.randint(-8, 8)
            return max(30, min(100, base_score + base_bonus + cat_bonus + day_bonus + variation))

        career_score = calc_category_score("career")
        love_score = calc_category_score("love")
        health_score = calc_category_score("health")
        wealth_score = calc_category_score("wealth")

        # 選擇建議
        if overall_score >= 85:
            advice_list = fortune_data["daily_advice"]["excellent"]
        elif overall_score >= 70:
            advice_list = fortune_data["daily_advice"]["good"]
        elif overall_score >= 55:
            advice_list = fortune_data["daily_advice"]["neutral"]
        elif overall_score >= 40:
            advice_list = fortune_data["daily_advice"]["caution"]
        else:
            advice_list = fortune_data["daily_advice"]["challenging"]

        advice = random.choice(advice_list)

        # 幸運物品
        lucky = fortune_data["lucky_items"]
        lucky_direction = lucky["directions"].get(day_element, lucky["directions"]["土"])
        lucky_color = lucky["colors"].get(day_element, lucky["colors"]["土"])
        lucky_numbers = lucky["numbers"].get(day_element, [5])

        return {
            "date": target_date.isoformat(),
            "weekday": {
                "name": day_info["name"],
                "reading": day_info["reading"],
                "element": day_element,
                "planet": day_info["planet"]
            },
            "your_mansion": {
                "name_jp": mansion["name_jp"],
                "reading": mansion["reading"],
                "element": user_element,
                "index": mansion["index"]
            },
            "element_relation": {
                "type": relation_type,
                "description": relation_desc
            },
            "fortune": {
                "overall": overall_score,
                "career": career_score,
                "love": love_score,
                "health": health_score,
                "wealth": wealth_score
            },
            "advice": advice,
            "lucky": {
                "direction": lucky_direction["direction"],
                "direction_reading": lucky_direction["reading"],
                "color": lucky_color["color"],
                "color_reading": lucky_color["reading"],
                "color_hex": lucky_color["hex"],
                "numbers": lucky_numbers
            }
        }

    def calculate_monthly_fortune(self, birth_date: date, year: int, month: int) -> dict:
        """
        計算每月運勢

        Args:
            birth_date: 出生日期
            year: 年份
            month: 月份 (1-12)

        Returns:
            每月運勢資料
        """
        import random
        from datetime import timedelta

        fortune_data = self._load_fortune_data()
        mansion = self.get_mansion(birth_date)
        user_index = mansion["index"]
        user_element = mansion["element"]

        # 取得該月的月宿（使用月宿傍通曆）
        month_mansion_index = self.MONTH_START_MANSION.get(month, 0)
        month_mansion = self.mansions_data[month_mansion_index]

        # 計算本命宿與月宿的關係
        relation = self.get_relation_type(user_index, month_mansion_index)

        # 基於關係類型計算基礎分數
        base_score = relation["score"]

        # 月份主題加成
        month_theme = fortune_data["monthly_themes"].get(str(month), {})
        theme_element = month_theme.get("element_boost", "土")
        if user_element == theme_element:
            base_score = min(100, base_score + 5)

        # 計算各項運勢
        random.seed(f"{birth_date.isoformat()}{year}{month}")

        def calc_monthly_category(category: str) -> int:
            cat_data = fortune_data["fortune_categories"][category]
            cat_bonus = 8 if user_element in cat_data["favorable_elements"] else 0
            variation = random.randint(-10, 10)
            return max(30, min(100, base_score + cat_bonus + variation))

        # 計算每週運勢
        weekly = []
        first_day = date(year, month, 1)
        for week in range(4):
            week_seed = f"{birth_date.isoformat()}{year}{month}week{week}"
            random.seed(week_seed)
            week_score = max(40, min(100, base_score + random.randint(-15, 15)))
            categories = ["career", "love", "health", "wealth"]
            focus = random.choice(categories)
            weekly.append({
                "week": week + 1,
                "score": week_score,
                "focus": fortune_data["fortune_categories"][focus]["name"]
            })

        random.seed(f"{birth_date.isoformat()}{year}{month}")

        return {
            "year": year,
            "month": month,
            "month_mansion": {
                "name_jp": month_mansion["name_jp"],
                "reading": month_mansion["reading"],
                "index": month_mansion_index,
                "element": month_mansion["element"]
            },
            "your_mansion": {
                "name_jp": mansion["name_jp"],
                "reading": mansion["reading"],
                "element": user_element,
                "index": user_index
            },
            "relation": {
                "type": relation["type"],
                "name": relation["name"],
                "reading": relation.get("reading", ""),
                "description": relation["description"]
            },
            "theme": {
                "title": month_theme.get("theme", ""),
                "focus": month_theme.get("focus", ""),
                "element_boost": theme_element
            },
            "fortune": {
                "overall": base_score,
                "career": calc_monthly_category("career"),
                "love": calc_monthly_category("love"),
                "health": calc_monthly_category("health"),
                "wealth": calc_monthly_category("wealth")
            },
            "weekly": weekly,
            "advice": f"本月為{relation['name']}月，{relation['advice']}"
        }

    def calculate_weekly_fortune(self, birth_date: date, year: int, week: int) -> dict:
        """
        計算每週運勢

        Args:
            birth_date: 出生日期
            year: 年份
            week: ISO 週數 (1-53)

        Returns:
            每週運勢資料
        """
        import random
        from datetime import timedelta

        fortune_data = self._load_fortune_data()
        mansion = self.get_mansion(birth_date)
        user_index = mansion["index"]
        user_element = mansion["element"]

        # 計算該週的起始和結束日期
        # ISO 週數：第 1 週包含該年第一個星期四
        jan_4 = date(year, 1, 4)
        start_of_week_1 = jan_4 - timedelta(days=jan_4.weekday())
        week_start = start_of_week_1 + timedelta(weeks=week - 1)
        week_end = week_start + timedelta(days=6)

        # 取得該週的主宰七曜（以週一為準）
        weekday = week_start.weekday()
        jp_weekday = (weekday + 1) % 7
        day_info = fortune_data["weekday_elements"].get(str(jp_weekday), {
            "name": "月曜日", "reading": "げつようび", "element": "月", "planet": "月"
        })
        week_element = day_info["element"]

        # 計算元素關係
        relation_type, base_bonus = self._calc_fortune_element_relation(user_element, week_element)
        relation_desc = fortune_data["element_relations"].get(
            relation_type,
            fortune_data["element_relations"]["neutral"]
        )["description"]

        # 基礎分數
        base_score = 70 + base_bonus

        # 計算各項運勢
        random.seed(f"{birth_date.isoformat()}{year}week{week}")

        def calc_weekly_category(category: str) -> int:
            cat_data = fortune_data["fortune_categories"][category]
            cat_bonus = 6 if user_element in cat_data["favorable_elements"] else 0
            week_bonus = 4 if week_element in cat_data["favorable_elements"] else 0
            variation = random.randint(-10, 10)
            return max(30, min(100, base_score + cat_bonus + week_bonus + variation))

        overall_score = max(30, min(100, base_score))
        career_score = calc_weekly_category("career")
        love_score = calc_weekly_category("love")
        health_score = calc_weekly_category("health")
        wealth_score = calc_weekly_category("wealth")

        # 計算每日運勢概覽
        daily_overview = []
        for day_offset in range(7):
            day_date = week_start + timedelta(days=day_offset)
            day_weekday = (day_date.weekday() + 1) % 7
            day_element_info = fortune_data["weekday_elements"].get(str(day_weekday), {})
            day_element = day_element_info.get("element", "土")

            _, day_bonus = self._calc_fortune_element_relation(user_element, day_element)
            day_score = max(40, min(100, 70 + day_bonus + random.randint(-8, 8)))

            daily_overview.append({
                "date": day_date.isoformat(),
                "weekday": day_element_info.get("name", ""),
                "score": day_score
            })

        # 選擇建議
        if overall_score >= 85:
            advice_list = fortune_data["daily_advice"]["excellent"]
        elif overall_score >= 70:
            advice_list = fortune_data["daily_advice"]["good"]
        elif overall_score >= 55:
            advice_list = fortune_data["daily_advice"]["neutral"]
        elif overall_score >= 40:
            advice_list = fortune_data["daily_advice"]["caution"]
        else:
            advice_list = fortune_data["daily_advice"]["challenging"]

        advice = random.choice(advice_list)

        # 幸運物品
        lucky = fortune_data["lucky_items"]
        lucky_direction = lucky["directions"].get(week_element, lucky["directions"]["土"])
        lucky_color = lucky["colors"].get(week_element, lucky["colors"]["土"])

        return {
            "year": year,
            "week": week,
            "week_start": week_start.isoformat(),
            "week_end": week_end.isoformat(),
            "week_element": {
                "name": day_info["name"],
                "reading": day_info["reading"],
                "element": week_element,
                "planet": day_info["planet"]
            },
            "your_mansion": {
                "name_jp": mansion["name_jp"],
                "reading": mansion["reading"],
                "element": user_element,
                "index": user_index
            },
            "element_relation": {
                "type": relation_type,
                "description": relation_desc
            },
            "fortune": {
                "overall": overall_score,
                "career": career_score,
                "love": love_score,
                "health": health_score,
                "wealth": wealth_score
            },
            "daily_overview": daily_overview,
            "advice": advice,
            "lucky": {
                "direction": lucky_direction["direction"],
                "direction_reading": lucky_direction["reading"],
                "color": lucky_color["color"],
                "color_reading": lucky_color["reading"],
                "color_hex": lucky_color["hex"]
            }
        }

    def calculate_yearly_fortune(self, birth_date: date, year: int) -> dict:
        """
        計算每年運勢

        Args:
            birth_date: 出生日期
            year: 年份

        Returns:
            每年運勢資料
        """
        import random

        fortune_data = self._load_fortune_data()
        mansion = self.get_mansion(birth_date)
        user_index = mansion["index"]
        user_element = mansion["element"]

        # 取得該年的天干地支
        year_info = None
        for yc in fortune_data["year_cycle"]:
            if yc["year"] == year:
                year_info = yc
                break

        # 如果找不到，計算
        if not year_info:
            stems = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
            branches = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
            stem_idx = (year - 4) % 10
            branch_idx = (year - 4) % 12
            year_info = {
                "year": year,
                "stem": stems[stem_idx],
                "branch": branches[branch_idx]
            }

        stem = year_info["stem"]
        branch = year_info["branch"]

        stem_data = fortune_data["heavenly_stems"].get(stem, {})
        zodiac_data = fortune_data["yearly_zodiac"].get(branch, {})

        # 計算年運基礎分數
        year_element = stem_data.get("element", "土")
        zodiac_element = zodiac_data.get("element", "土")

        # 元素關係
        _, stem_bonus = self._calc_fortune_element_relation(user_element, year_element)
        _, zodiac_bonus = self._calc_fortune_element_relation(user_element, zodiac_element)

        base_score = 70 + (stem_bonus + zodiac_bonus) // 2

        # 檢查是否犯太歲
        warnings = []
        mansion_range = zodiac_data.get("mansion_range", [])
        tai_sui_penalty = 0
        if user_index in mansion_range:
            warnings.append("本命宿與太歲相沖，重大決策宜謹慎，可透過行善積德化解")
            tai_sui_penalty = 10

        # 計算每月趨勢
        random.seed(f"{birth_date.isoformat()}{year}")
        monthly_trend = []
        for m in range(1, 13):
            month_score = max(40, min(100, base_score + random.randint(-20, 20)))
            monthly_trend.append({
                "month": m,
                "score": month_score
            })

        # 找出機會月份（分數最高的 3 個月）
        sorted_months = sorted(monthly_trend, key=lambda x: x["score"], reverse=True)
        opportunities = []
        opportunity_details = {
            "規劃": "制定年度目標、整理思緒、規劃未來方向",
            "執行": "落實計畫、按部就班推進、將想法化為行動",
            "人際": "拓展人脈、參加社交活動，可能遇到貴人相助",
            "學習": "進修充電、考取證照、閱讀學習新技能",
            "事業": "積極爭取升遷機會、展現專業能力、建立職場影響力",
            "健康": "調養身心、建立運動習慣、關注身體警訊",
            "社交": "參加聚會活動、結交新朋友、維繫重要關係",
            "財運": "投資理財好時機、開拓收入來源、把握賺錢機會",
            "專業": "深耕專業領域、累積實力、建立個人品牌",
            "家庭": "陪伴家人、處理家務事、增進家庭和諧",
            "內省": "沉澱反思、調整心態、重新審視人生方向",
            "總結": "回顧年度成果、整理資源、為明年做準備"
        }
        for m in sorted_months[:3]:
            month_name = f"{m['month']}月"
            theme = fortune_data["monthly_themes"].get(str(m["month"]), {})
            focus = theme.get("focus", "發展")
            detail = opportunity_details.get(focus, "把握機會積極行動")
            opportunities.append(f"{month_name}（運勢分數 {m['score']}）：{detail}")

        # 找出需注意的月份（分數最低的）
        worst_months = sorted(monthly_trend, key=lambda x: x["score"])[:2]
        for wm in worst_months:
            if wm["score"] < 55:
                warnings.append(f"{wm['month']}月運勢較低（{wm['score']}分），避免重大投資或簽約")

        # 應用犯太歲減分
        base_score = max(50, base_score - tai_sui_penalty)

        # 各項運勢
        random.seed(f"{birth_date.isoformat()}{year}categories")

        def calc_yearly_category(category: str) -> int:
            cat_data = fortune_data["fortune_categories"][category]
            cat_bonus = 10 if user_element in cat_data["favorable_elements"] else 0
            year_boost = 5 if year_element in cat_data["favorable_elements"] else 0
            variation = random.randint(-12, 12)
            return max(35, min(100, base_score + cat_bonus + year_boost + variation))

        # 年度建議
        if base_score >= 80:
            advice = f"{stem}{branch}年對{mansion['name_jp']}而言是大展身手的好年，把握機會積極行動！"
        elif base_score >= 65:
            advice = f"{stem}{branch}年運勢平穩，適合穩紮穩打、累積實力。"
        elif base_score >= 50:
            advice = f"{stem}{branch}年需要謹慎，避免冒進，多聽取他人意見。"
        else:
            advice = f"{stem}{branch}年運勢較為挑戰，保持低調、韜光養晦為上策。"

        return {
            "year": year,
            "stem": {
                "character": stem,
                "reading": stem_data.get("reading", ""),
                "element": year_element,
                "yin_yang": stem_data.get("yin_yang", "")
            },
            "branch": {
                "character": branch,
                "name": zodiac_data.get("name", ""),
                "reading": zodiac_data.get("reading", ""),
                "element": zodiac_element
            },
            "your_mansion": {
                "name_jp": mansion["name_jp"],
                "reading": mansion["reading"],
                "element": user_element,
                "index": user_index
            },
            "fortune": {
                "overall": base_score,
                "career": calc_yearly_category("career"),
                "love": calc_yearly_category("love"),
                "health": calc_yearly_category("health"),
                "wealth": calc_yearly_category("wealth")
            },
            "monthly_trend": monthly_trend,
            "opportunities": opportunities,
            "warnings": warnings,
            "advice": advice
        }

    # 職業類型資料
    CAREER_BY_ELEMENT = {
        "日": {
            "categories": [
                {"name": "領導管理", "jobs": ["企業主管", "專案經理", "創業家", "執行長"]},
                {"name": "表演藝術", "jobs": ["演員", "導演", "主持人", "藝術家"]},
                {"name": "公共事務", "jobs": ["政治人物", "公關", "發言人", "外交官"]}
            ],
            "traits": "日性能量賦予領導特質和決斷力，使你在需要統籌全局、激勵團隊的位置上能充分發揮。你的存在感和自信是帶領他人前進的重要資源。"
        },
        "月": {
            "categories": [
                {"name": "照護服務", "jobs": ["護理師", "社工", "心理諮商師", "幼教老師"]},
                {"name": "藝術創作", "jobs": ["作家", "插畫家", "音樂家", "設計師"]},
                {"name": "生活產業", "jobs": ["餐飲業", "旅遊業", "美容美髮", "花藝師"]}
            ],
            "traits": "月性能量賦予細膩的感受力和同理心，使你能理解他人的需求和情緒。在需要照顧他人或創造美好體驗的領域，你能展現獨特的價值。"
        },
        "火": {
            "categories": [
                {"name": "業務銷售", "jobs": ["業務主管", "行銷經理", "房仲", "保險業務"]},
                {"name": "體能相關", "jobs": ["運動員", "教練", "軍警消防", "廚師"]},
                {"name": "技術工程", "jobs": ["機械工程師", "電機工程師", "建築師", "技師"]}
            ],
            "traits": "火性能量帶來強大的行動力和執行力，使你在需要主動出擊、快速決策的環境中如魚得水。你的熱情和衝勁是推動事情前進的動力。"
        },
        "水": {
            "categories": [
                {"name": "研究分析", "jobs": ["研究員", "數據分析師", "市場調查員", "科學家"]},
                {"name": "資訊科技", "jobs": ["軟體工程師", "系統分析師", "AI 工程師", "資安專家"]},
                {"name": "金融財務", "jobs": ["投資分析師", "精算師", "財務顧問", "交易員"]}
            ],
            "traits": "水性能量賦予靈活的思維和分析能力，使你善於處理複雜的問題和變化的情境。在需要邏輯思考、數據分析的領域，你的能力能得到充分發揮。"
        },
        "木": {
            "categories": [
                {"name": "教育文化", "jobs": ["教師", "教授", "培訓講師", "圖書館員"]},
                {"name": "法律媒體", "jobs": ["律師", "法官", "記者", "編輯"]},
                {"name": "環保農業", "jobs": ["環保工程師", "農業專家", "園藝師", "獸醫"]}
            ],
            "traits": "木性能量代表成長和正義，使你具有傳承知識、引導他人的天賦。在需要教育啟發、維護公平的領域，你的價值觀和理想能成為指引方向的力量。"
        },
        "金": {
            "categories": [
                {"name": "金融會計", "jobs": ["會計師", "稽核員", "銀行家", "證券分析師"]},
                {"name": "精密工業", "jobs": ["珠寶設計師", "精密機械師", "品管工程師", "鐘錶師"]},
                {"name": "法務行政", "jobs": ["法務專員", "行政主管", "人資經理", "採購專員"]}
            ],
            "traits": "金性能量帶來嚴謹和精確的特質，使你在需要高標準品質控管的領域能夠勝任。你對細節的講究和專業判斷力，是確保成果品質的重要保障。"
        },
        "土": {
            "categories": [
                {"name": "不動產", "jobs": ["建築師", "室內設計師", "不動產經紀", "土地開發"]},
                {"name": "行政管理", "jobs": ["行政助理", "總務主管", "秘書", "辦公室經理"]},
                {"name": "物流倉儲", "jobs": ["物流經理", "倉管人員", "供應鏈管理", "貨運業"]}
            ],
            "traits": "土性能量賦予穩定和務實的特質，使你在需要長期耕耘、穩健推進的領域能夠發光。你的可靠和耐心是建立持久成就的基礎。"
        }
    }

    def get_career_guidance(self, birth_date: date) -> dict:
        """
        取得求職離職指引

        Args:
            birth_date: 西曆生日

        Returns:
            職業建議和吉日列表
        """
        from datetime import timedelta

        mansion = self.get_mansion(birth_date)
        user_element = mansion["element"]
        user_index = mansion["index"]

        # 取得適合職業
        career_data = self.CAREER_BY_ELEMENT.get(user_element, self.CAREER_BY_ELEMENT["土"])
        suitable_careers = career_data["categories"]
        career_traits = career_data["traits"]

        # 計算未來 30 天的吉日
        today = date.today()
        job_seeking_days = []
        resignation_days = []
        avoid_days = []

        fortune_data = self._load_fortune_data()

        for i in range(30):
            check_date = today + timedelta(days=i)

            # 計算當日運勢分數
            daily_fortune = self.calculate_daily_fortune(birth_date, check_date)
            score = daily_fortune["fortune"]["overall"]

            # 取得當日七曜元素
            weekday = check_date.weekday()
            day_element = fortune_data["weekday_elements"][str(weekday)]["element"]
            day_name = fortune_data["weekday_elements"][str(weekday)]["name"]

            # 計算當日宿
            lunar_year, lunar_month, lunar_day, _ = self.solar_to_lunar(check_date)
            day_mansion_index = self.get_mansion_index(lunar_month, lunar_day)

            # 計算與本命宿的關係
            relation = self.get_relation_type(user_index, day_mansion_index)
            relation_type = relation["type"]

            # 判斷求職吉日
            is_job_seeking_lucky = False
            job_reason = ""

            if relation_type in ["榮親", "業胎"]:
                is_job_seeking_lucky = True
                job_reason = f"{relation['name']}日，貴人運旺"
            elif day_element == user_element:
                is_job_seeking_lucky = True
                job_reason = f"{day_name}（{day_element}）同元素，能量充沛"
            elif self._is_generating(day_element, user_element):
                is_job_seeking_lucky = True
                job_reason = f"{day_name}，元素相生，運勢順利"
            elif score >= 75:
                is_job_seeking_lucky = True
                job_reason = f"運勢佳（{score}分），適合面試"

            if is_job_seeking_lucky and len(job_seeking_days) < 5:
                job_seeking_days.append({
                    "date": check_date.isoformat(),
                    "weekday": day_name,
                    "score": score,
                    "reason": job_reason
                })

            # 判斷離職吉日（月底、月初，運勢穩定）
            is_resignation_ok = False
            resign_reason = ""

            if check_date.day <= 5 or check_date.day >= 25:
                if score >= 65 and relation_type not in ["安壞", "危成"]:
                    is_resignation_ok = True
                    resign_reason = "月初/月底，運勢穩定" if score >= 70 else "運勢平穩，可行"

            if is_resignation_ok and len(resignation_days) < 3:
                resignation_days.append({
                    "date": check_date.isoformat(),
                    "weekday": day_name,
                    "score": score,
                    "reason": resign_reason
                })

            # 需避開的日子
            if score < 50 or relation_type in ["安壞", "危成"]:
                if len(avoid_days) < 5:
                    avoid_reason = "運勢低迷" if score < 50 else f"{relation['name']}日，不宜重大決定"
                    avoid_days.append({
                        "date": check_date.isoformat(),
                        "weekday": day_name,
                        "score": score,
                        "reason": avoid_reason
                    })

        return {
            "your_mansion": {
                "name_jp": mansion["name_jp"],
                "reading": mansion["reading"],
                "element": user_element
            },
            "suitable_careers": suitable_careers,
            "career_traits": career_traits,
            "lucky_days": {
                "job_seeking": job_seeking_days,
                "resignation": resignation_days
            },
            "avoid_days": avoid_days,
            "general_advice": self._get_career_advice(user_element)
        }

    # ==================== 通用吉日查詢 ====================

    # 吉日查詢類別定義
    # 關係類型對照：mei(命), gyotai(業胎), eishin(榮親), yusui(友衰), ankai(安壞), kisei(危成)
    LUCKY_DAY_CATEGORIES = {
        "career": {
            "name": "事業",
            "icon": "briefcase",
            "actions": {
                "interview": {"name": "求職面試", "favor_relations": ["eishin", "gyotai"], "favor_score": 75},
                "resign": {"name": "離職提出", "favor_relations": ["yusui"], "month_day_range": [1, 5, 25, 31], "favor_score": 65},
                "opening": {"name": "開業", "favor_relations": ["eishin", "mei"], "favor_score": 80},
                "contract": {"name": "簽約", "favor_relations": ["eishin", "gyotai"], "favor_score": 70}
            }
        },
        "study": {
            "name": "學業",
            "icon": "book",
            "actions": {
                "enrollment": {"name": "入學報到", "favor_relations": ["eishin", "gyotai"], "favor_score": 70},
                "exam": {"name": "考試", "favor_relations": ["eishin", "mei"], "favor_weekdays": [1, 3], "favor_score": 75},
                "tutor": {"name": "補習報名", "favor_relations": ["gyotai", "yusui"], "favor_score": 65}
            }
        },
        "housing": {
            "name": "居住",
            "icon": "house",
            "actions": {
                "move_in": {"name": "搬家入宅", "favor_relations": ["eishin", "mei"], "favor_score": 75},
                "renovation": {"name": "裝潢開工", "favor_relations": ["eishin"], "favor_weekdays": [0, 3], "favor_score": 70},
                "purchase": {"name": "購屋簽約", "favor_relations": ["eishin", "gyotai"], "favor_score": 80}
            }
        },
        "marriage": {
            "name": "婚姻",
            "icon": "heart",
            "actions": {
                "register": {"name": "結婚登記", "favor_relations": ["eishin", "mei", "gyotai", "yusui"], "favor_score": 70},
                "wedding": {"name": "婚禮", "favor_relations": ["eishin", "gyotai", "mei", "yusui"], "favor_score": 70},
                "engagement": {"name": "訂婚", "favor_relations": ["eishin", "gyotai", "yusui"], "favor_score": 70}
            }
        },
        "medical": {
            "name": "醫療",
            "icon": "heart-pulse",
            "actions": {
                "surgery": {"name": "手術", "favor_relations": ["eishin"], "avoid_relations": ["ankai", "kisei"], "favor_score": 80},
                "checkup": {"name": "健康檢查", "favor_relations": ["yusui", "eishin"], "favor_score": 65},
                "visit": {"name": "看診", "favor_relations": ["yusui"], "favor_score": 60}
            }
        },
        "travel": {
            "name": "旅行",
            "icon": "airplane",
            "actions": {
                "abroad": {"name": "出國", "favor_relations": ["eishin", "gyotai"], "favor_score": 75},
                "trip": {"name": "旅遊出發", "favor_relations": ["eishin", "yusui"], "favor_score": 70}
            }
        },
        "beauty": {
            "name": "美容",
            "icon": "scissors",
            "actions": {
                "haircut": {"name": "剪頭髮", "favor_relations": ["eishin", "yusui"], "favor_weekdays": [1, 3, 5], "favor_score": 70},
                "hair_coloring": {"name": "染髮", "favor_relations": ["eishin"], "favor_score": 65},
                "perm": {"name": "燙髮", "favor_relations": ["eishin", "gyotai"], "favor_score": 65},
                "nail": {"name": "美甲", "favor_relations": ["eishin", "yusui"], "favor_score": 60},
                "skincare": {"name": "護膚美容", "favor_relations": ["eishin", "mei"], "favor_score": 65},
                "tattoo": {"name": "紋繡/刺青", "favor_relations": ["eishin"], "avoid_relations": ["ankai"], "favor_score": 70}
            }
        },
        "dating": {
            "name": "感情",
            "icon": "chat-heart",
            "actions": {
                "first_date": {"name": "第一次約會", "favor_relations": ["eishin", "gyotai", "yusui"], "favor_weekdays": [4, 5], "favor_score": 70},
                "confession": {"name": "告白", "favor_relations": ["eishin", "mei", "yusui"], "favor_score": 70},
                "matchmaking": {"name": "相親", "favor_relations": ["eishin", "gyotai", "yusui"], "favor_score": 70},
                "breakup": {"name": "分手", "favor_relations": ["yusui", "ankai"], "favor_score": 60}
            }
        },
        "shopping": {
            "name": "購物",
            "icon": "bag",
            "actions": {
                "clothing": {"name": "買衣服", "favor_relations": ["eishin", "yusui"], "favor_weekdays": [4, 5, 6], "favor_score": 65},
                "jewelry": {"name": "買首飾", "favor_relations": ["eishin", "mei"], "favor_score": 70},
                "big_purchase": {"name": "大額消費", "favor_relations": ["eishin", "gyotai"], "favor_score": 75}
            }
        }
    }

    def get_lucky_days(
        self,
        birth_date: date,
        category: str,
        action: str,
        days_ahead: int = 30
    ) -> dict:
        """
        通用吉日查詢

        Args:
            birth_date: 西曆生日
            category: 類別（career/study/housing/marriage/medical/travel/beauty/dating/shopping）
            action: 具體項目
            days_ahead: 查詢未來幾天（預設 30）

        Returns:
            吉日列表和建議
        """
        from datetime import timedelta

        # 驗證類別和項目
        if category not in self.LUCKY_DAY_CATEGORIES:
            raise ValueError(f"無效的類別: {category}")

        cat_config = self.LUCKY_DAY_CATEGORIES[category]
        if action not in cat_config["actions"]:
            raise ValueError(f"無效的項目: {action}")

        action_config = cat_config["actions"][action]

        mansion = self.get_mansion(birth_date)
        user_element = mansion["element"]
        user_index = mansion["index"]

        today = date.today()
        lucky_days = []
        avoid_days = []

        fortune_data = self._load_fortune_data()

        # 取得項目配置
        favor_relations = action_config.get("favor_relations", ["eishin"])
        avoid_relations = action_config.get("avoid_relations", ["ankai", "kisei"])
        favor_score = action_config.get("favor_score", 70)
        favor_weekdays = action_config.get("favor_weekdays", None)
        month_day_range = action_config.get("month_day_range", None)

        for i in range(days_ahead):
            check_date = today + timedelta(days=i)

            # 計算當日運勢分數
            daily_fortune = self.calculate_daily_fortune(birth_date, check_date)
            score = daily_fortune["fortune"]["overall"]

            # 取得當日資訊
            weekday = check_date.weekday()
            day_element = fortune_data["weekday_elements"][str(weekday)]["element"]
            day_name = fortune_data["weekday_elements"][str(weekday)]["name"]

            # 計算當日宿
            lunar_year, lunar_month, lunar_day, _ = self.solar_to_lunar(check_date)
            day_mansion_index = self.get_mansion_index(lunar_month, lunar_day)

            # 計算與本命宿的關係
            relation = self.get_relation_type(user_index, day_mansion_index)
            relation_type = relation["type"]

            # 判斷是否吉日
            is_lucky = False
            lucky_reason = ""

            # 檢查避開的關係
            if relation_type in avoid_relations:
                if len(avoid_days) < 5:
                    avoid_days.append({
                        "date": check_date.isoformat(),
                        "weekday": day_name,
                        "score": score,
                        "reason": f"{relation['name']}日，不宜{action_config['name']}"
                    })
                continue

            # 檢查運勢過低
            if score < 50:
                if len(avoid_days) < 5:
                    avoid_days.append({
                        "date": check_date.isoformat(),
                        "weekday": day_name,
                        "score": score,
                        "reason": "運勢低迷，建議避開"
                    })
                continue

            # 檢查特定月日範圍（如離職適合月初月底）
            if month_day_range:
                day_of_month = check_date.day
                in_range = any(
                    day_of_month <= month_day_range[1] or day_of_month >= month_day_range[2]
                    for _ in [1]
                )
                if not in_range:
                    continue

            # 判斷吉日條件
            if relation_type in favor_relations:
                is_lucky = True
                lucky_reason = f"{relation['name']}日，{self._get_relation_benefit(relation_type, action)}"
            elif day_element == user_element and score >= favor_score:
                is_lucky = True
                lucky_reason = f"{day_name}（{day_element}）同元素，能量充沛"
            elif self._is_generating(day_element, user_element) and score >= favor_score:
                is_lucky = True
                lucky_reason = f"{day_name}，元素相生，運勢順利"
            elif score >= favor_score + 5:
                # 特定星期加分
                if favor_weekdays and weekday in favor_weekdays:
                    is_lucky = True
                    lucky_reason = f"運勢佳（{score}分），{day_name}適合{action_config['name']}"
                elif score >= favor_score + 10:
                    is_lucky = True
                    lucky_reason = f"運勢極佳（{score}分）"

            if is_lucky and len(lucky_days) < 8:
                # 計算評級
                rating = "大吉" if score >= 85 else "吉" if score >= 70 else "中吉"
                lucky_days.append({
                    "date": check_date.isoformat(),
                    "weekday": day_name,
                    "score": score,
                    "rating": rating,
                    "reason": lucky_reason
                })

        return {
            "category": category,
            "category_name": cat_config["name"],
            "action": action,
            "action_name": action_config["name"],
            "your_mansion": {
                "name_jp": mansion["name_jp"],
                "reading": mansion["reading"],
                "element": user_element
            },
            "lucky_days": lucky_days,
            "avoid_days": avoid_days,
            "advice": self._get_action_advice(category, action, user_element)
        }

    def get_all_lucky_day_categories(self) -> list:
        """取得所有吉日查詢類別"""
        return [
            {
                "key": key,
                "name": cat["name"],
                "icon": cat["icon"],
                "actions": [
                    {"key": act_key, "name": act["name"]}
                    for act_key, act in cat["actions"].items()
                ]
            }
            for key, cat in self.LUCKY_DAY_CATEGORIES.items()
        ]

    def _get_relation_benefit(self, relation_type: str, action: str) -> str:
        """取得關係類型對特定行動的好處描述"""
        benefits = {
            "榮親": "貴人相助，順利圓滿",
            "業胎": "前世因緣，水到渠成",
            "命": "能量共鳴，心想事成",
            "友衰": "平穩順遂，適合進行",
            "危成": "需謹慎行事",
            "安壞": "建議避開此日"
        }
        return benefits.get(relation_type, "")

    def _get_action_advice(self, category: str, action: str, element: str) -> str:
        """取得特定行動的建議"""
        advice_templates = {
            "career": {
                "interview": f"{element}性本命宿者，面試時宜展現穩重與專業，選擇上午時段精神較佳。",
                "resign": f"{element}性本命宿者，離職時保持和善態度，為未來留下良好印象。",
                "opening": f"{element}性本命宿者，開業宜選擇與本命宿相合之方位，增添運勢。",
                "contract": f"{element}性本命宿者，簽約前仔細審閱條款，選擇運勢高峰時段。"
            },
            "study": {
                "enrollment": f"{element}性本命宿者，入學報到時保持正向心態，有助於學業順遂。",
                "exam": f"{element}性本命宿者，考試當日宜早起準備，穿戴與本命元素相合的顏色。",
                "tutor": f"{element}性本命宿者，選擇補習時考量與老師的相性，有助學習效果。"
            },
            "housing": {
                "move_in": f"{element}性本命宿者，搬家入宅宜選擇上午時段，並注意方位吉凶。",
                "renovation": f"{element}性本命宿者，裝潢開工前可先淨宅，增添正能量。",
                "purchase": f"{element}性本命宿者，購屋時多考量房屋座向與本命宿的相合度。"
            },
            "marriage": {
                "register": f"{element}性本命宿者，登記時心懷感恩，為婚姻奠定良好基礎。",
                "wedding": f"{element}性本命宿者，婚禮當日保持愉悅心情，吉祥圓滿。",
                "engagement": f"{element}性本命宿者，訂婚時誠意為重，雙方家庭和睦為佳。"
            },
            "medical": {
                "surgery": f"{element}性本命宿者，手術前保持平靜心態，信任醫療團隊。",
                "checkup": f"{element}性本命宿者，定期健康檢查有助於預防保健。",
                "visit": f"{element}性本命宿者，看診時詳述症狀，配合醫囑調養。"
            },
            "travel": {
                "abroad": f"{element}性本命宿者，出國前確認行程安排，注意旅途安全。",
                "trip": f"{element}性本命宿者，旅遊時放鬆心情，享受當下美好時光。"
            }
        }
        return advice_templates.get(category, {}).get(action, "選擇運勢良好的日子進行，有助於事半功倍。")

    def _is_generating(self, elem1: str, elem2: str) -> bool:
        """檢查是否為相生關係"""
        GENERATING_PAIRS = [
            ("木", "火"), ("火", "土"), ("土", "金"),
            ("金", "水"), ("水", "木")
        ]
        return (elem1, elem2) in GENERATING_PAIRS or (elem2, elem1) in GENERATING_PAIRS

    def _get_career_advice(self, element: str) -> str:
        """取得職涯建議"""
        advice_map = {
            "日": "日性能量賦予你領導者的氣質，求職時可著重展現統籌協調和決策能力。面試中適度分享對工作的願景和想法，能讓面試官看到你的潛力。",
            "月": "月性能量帶來的同理心和感受力是重要的職場資產。建議在求職過程中強調團隊協作和照顧他人的經驗。選擇能發揮感性特質的工作環境，有助於長期發展。",
            "火": "火性能量帶來的行動力和執行力是職場上的競爭優勢。面試時展現積極主動的態度會加分。建議選擇有挑戰性、能持續發揮執行力的職位。",
            "水": "水性能量賦予的分析和思考能力是重要的專業資源。求職時建議準備充分的資料和數據來佐證你的能力。需要策略思考的工作能讓你發揮所長。",
            "木": "木性能量帶來的正直和理想性是珍貴的特質。選擇符合個人價值觀的工作對長期發展很重要。教育、法律、環保等能實踐理想的領域可能帶來較高的工作滿足感。",
            "金": "金性能量賦予的嚴謹和精確是專業工作的重要特質。面試時展現對品質的堅持和專業判斷力。需要高標準品質控管的職位能讓你充分發揮。",
            "土": "土性能量帶來的穩定和可靠是團隊中重要的支柱特質。建議選擇穩定的工作環境，能讓你的踏實特質得到發揮。長期耕耘型的職位往往能帶來豐碩的成果。"
        }
        return advice_map.get(element, "建議根據個人特質，選擇能充分發揮所長的工作方向。")


# 全域實例
sukuyodo_service = SukuyodoService()
