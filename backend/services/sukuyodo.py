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

        # 各關係類型的距離定義
        COMPATIBILITY_TYPES = {
            "best_for_marriage": {
                "relation": "榮親",
                "reading": "えいしん",
                "distances": [1, 3, 10, 12, 15, 17, 24, 26],
                "score": 95,
                "description": "最適合結婚的對象，相處融洽、互相扶持"
            },
            "past_life_connection": {
                "relation": "業胎",
                "reading": "ぎょうたい",
                "distances": [9, 18],
                "score": 90,
                "description": "前世之緣，一見如故、心有靈犀"
            },
            "should_avoid": {
                "relation": "安壊",
                "reading": "あんかい",
                "distances": [4, 6, 21, 23],
                "score": 55,
                "description": "超有吸引力但危險，容易互相傷害"
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
        if user_index in mansion_range:
            warnings.append({
                "type": "tai_sui",
                "name": "犯太歲",
                "reading": "はんたいさい",
                "description": f"本命宿與{zodiac_data['name']}年太歲相沖，需要特別注意",
                "advice": "宜安太歲、多行善事、保持低調"
            })
            base_score = max(50, base_score - 10)

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
        for m in sorted_months[:3]:
            month_name = f"{m['month']}月"
            theme = fortune_data["monthly_themes"].get(str(m["month"]), {})
            opportunities.append(f"{month_name}適合{theme.get('focus', '發展')}")

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


# 全域實例
sukuyodo_service = SukuyodoService()
