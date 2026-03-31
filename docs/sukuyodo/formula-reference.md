# 宿曜道計算公式完整參考

> 本文檔記錄所有宿曜道計算的原典依據、公式推導和驗證資料

---

## 1. 原典資料

### 1.1 經典來源

| 項目 | 內容 |
|------|------|
| **正式經名** | 《文殊師利菩薩及諸仙所説吉凶時日善悪宿曜経》 |
| **簡稱** | 《宿曜經》 |
| **譯者** | 唐・不空三藏（759年於中國譯出） |
| **傳入日本** | 806年（空海）、847年（圓仁）、858年（圓珍） |
| **占術體系** | 密教占星術（真言宗） |
| **核心技法** | 三九秘宿（さんくひしゅく） |

### 1.2 理論基礎

宿曜道融合了三個占星體系：
1. **印度占星術（Jyotisha）**：二十七宿、九曜
2. **中國道教**：天體神信仰、陰陽五行
3. **西方占星術**：十二宮概念

---

## 2. 二十七宿完整資料

### 2.1 宿位順序（東→北→西→南）

#### 東方青龍七宿（木性）
| 索引 | 宿名 | 日文讀音 | 七曜元素 | 中文別名 |
|------|------|----------|----------|----------|
| 0 | 角宿 | かくしゅく | 木 | 角木蛟 |
| 1 | 亢宿 | こうしゅく | 金 | 亢金龍 |
| 2 | 氐宿 | ていしゅく | 土 | 氐土貉 |
| 3 | 房宿 | ぼうしゅく | 日 | 房日兔 |
| 4 | 心宿 | しんしゅく | 月 | 心月狐 |
| 5 | 尾宿 | びしゅく | 火 | 尾火虎 |
| 6 | 箕宿 | きしゅく | 水 | 箕水豹 |

#### 北方玄武七宿（水性）
| 索引 | 宿名 | 日文讀音 | 七曜元素 | 中文別名 |
|------|------|----------|----------|----------|
| 7 | 斗宿 | としゅく | 木 | 斗木獬 |
| 8 | 牛宿 | ぎゅうしゅく | 金 | 牛金牛 |
| 9 | 女宿 | じょしゅく | 土 | 女土蝠 |
| 10 | 虛宿 | きょしゅく | 日 | 虛日鼠 |
| 11 | 危宿 | きしゅく | 月 | 危月燕 |
| 12 | 室宿 | しつしゅく | 火 | 室火豬 |
| 13 | 壁宿 | へきしゅく | 水 | 壁水貐 |

#### 西方白虎七宿（金性）
| 索引 | 宿名 | 日文讀音 | 七曜元素 | 中文別名 |
|------|------|----------|----------|----------|
| 14 | 奎宿 | けいしゅく | 木 | 奎木狼 |
| 15 | 婁宿 | ろうしゅく | 金 | 婁金狗 |
| 16 | 胃宿 | いしゅく | 土 | 胃土雉 |
| 17 | 昴宿 | ぼうしゅく | 日 | 昴日雞 |
| 18 | 畢宿 | ひつしゅく | 月 | 畢月烏 |
| 19 | 觜宿 | ししゅく | 火 | 觜火猴 |
| 20 | 參宿 | しんしゅく | 水 | 參水猿 |

#### 南方朱雀七宿（火性）
| 索引 | 宿名 | 日文讀音 | 七曜元素 | 中文別名 |
|------|------|----------|----------|----------|
| 21 | 井宿 | せいしゅく | 木 | 井木犴 |
| 22 | 鬼宿 | きしゅく | 金 | 鬼金羊 |
| 23 | 柳宿 | りゅうしゅく | 土 | 柳土獐 |
| 24 | 星宿 | せいしゅく | 日 | 星日馬 |
| 25 | 張宿 | ちょうしゅく | 月 | 張月鹿 |
| 26 | 翼宿 | よくしゅく | 火 | 翼火蛇 |
| (27) | 軫宿 | しんしゅく | 水 | 軫水蚓 |

### 2.2 七曜元素循環規則

七曜元素按固定順序循環配置於 27 宿：

```
木 → 金 → 土 → 日 → 月 → 火 → 水 → 木 → ...（循環）
```

每 7 宿為一個循環，與七曜週期對應。

---

## 3. 本命宿計算公式

### 3.1 月宿傍通曆（げっしゅくぼうつうれき）

每個農曆月份的初一（朔日）有固定的起始宿位：

```python
MONTH_START_MANSION = {
    1: 11,   # 正月初一：危宿（索引 11）
    2: 13,   # 二月初一：壁宿（索引 13）
    3: 15,   # 三月初一：婁宿（索引 15）
    4: 17,   # 四月初一：昴宿（索引 17）
    5: 19,   # 五月初一：觜宿（索引 19）
    6: 21,   # 六月初一：井宿（索引 21）
    7: 24,   # 七月初一：星宿（索引 24）
    8: 0,    # 八月初一：角宿（索引 0）
    9: 2,    # 九月初一：氐宿（索引 2）
    10: 4,   # 十月初一：心宿（索引 4）
    11: 7,   # 十一月初一：斗宿（索引 7）
    12: 9,   # 十二月初一：女宿（索引 9）
}
```

### 3.2 本命宿計算公式

```
本命宿索引 = (月份起始宿索引 + 農曆日 - 1) mod 27
```

#### 計算範例

某人農曆生日為「三月十五日」：
- 三月起始宿 = 婁宿（索引 15）
- 計算：(15 + 15 - 1) mod 27 = 29 mod 27 = 2
- 本命宿 = 氐宿（索引 2）

### 3.3 西曆轉農曆

使用 `lunarcalendar` 套件進行精確轉換：

```python
from lunarcalendar import Converter, Solar

solar = Solar(year, month, day)
lunar = Converter.Solar2Lunar(solar)
# lunar.year, lunar.month, lunar.day, lunar.isleap
```

---

## 4. 三九秘法（相性計算）

### 4.1 六種關係類型定義

| 關係 | 日文 | 讀音 | 距離值 | 說明 |
|------|------|------|--------|------|
| 命 | 命 | めい | 0 | 同宿 |
| 業胎 | 業胎 | ぎょうたい | 9, 18 | 前世/來世因緣 |
| 榮親 | 栄親 | えいしん | 1, 3, 10, 12, 15, 17, 24, 26 | 互相提升 |
| 友衰 | 友衰 | ゆうすい | 2, 5, 11, 13, 14, 16, 22, 25 | 舒適但易懈怠 |
| 安壞 | 安壊 | あんかい | 4, 6, 21, 23 | 權力不對等 |
| 危成 | 危成 | きせい | 7, 8, 19, 20 | 互補需磨合 |

### 4.2 距離計算公式

```python
def calculate_distance(index1: int, index2: int) -> int:
    """計算兩宿之間的最短距離（0-13）"""
    distance = abs(index2 - index1)
    if distance > 13:
        distance = 27 - distance
    return distance
```

### 4.3 關係判定邏輯

```python
def get_relation_type(index1: int, index2: int) -> str:
    distance = abs(index2 - index1)
    reverse_distance = 27 - distance

    RELATION_DISTANCES = {
        "mei": [0],
        "gyotai": [9, 18],
        "eishin": [1, 3, 10, 12, 15, 17, 24, 26],
        "yusui": [2, 5, 11, 13, 14, 16, 22, 25],
        "ankai": [4, 6, 21, 23],
        "kisei": [7, 8, 19, 20],
    }

    for rel_type, distances in RELATION_DISTANCES.items():
        if distance in distances or reverse_distance in distances:
            return rel_type

    return "unknown"
```

### 4.4 完整版：距離類型（近/中/遠）

原典中，除「命」「業」「胎」外，其他關係各有三種距離：

| 關係 | 近距離 | 中距離 | 遠距離 |
|------|--------|--------|--------|
| 栄 | 1, 26 | 10, 17 | 19, 8 |
| 親 | 26, 1 | 17, 10 | 8, 19 |
| 友 | 2, 25 | 11, 16 | 20, 7 |
| 衰 | 25, 2 | 16, 11 | 7, 20 |
| 安 | 4, 23 | 13, 14 | 22, 5 |
| 壊 | 23, 4 | 14, 13 | 5, 22 |
| 危 | 6, 21 | 15, 12 | 24, 3 |
| 成 | 21, 6 | 12, 15 | 3, 24 |

距離影響：
- **近距離**：關係特徵最強烈
- **中距離**：關係最為平衡（戀愛最佳）
- **遠距離**：關係特徵較淡

### 4.5 完整版：榮/親方向性

在完整版三九秘法中，「榮」和「親」有方向性：

```
若 A 的本命宿到 B 的本命宿距離為「栄」的距離值：
  → A 是「栄」方（對 B 有利，給予繁榮）
  → B 是「親」方（受 A 恩惠，獲得親愛）
```

這表示同一對關係中，兩人的角色是不同的。

---

## 5. 七曜與五行

### 5.1 七曜對照表

| 曜日 | 元素 | 行星 | 梵文 | 能量 |
|------|------|------|------|------|
| 日曜日（週日）| 日 | 太陽 | Aditya | 陽 |
| 月曜日（週一）| 月 | 月亮 | Soma | 陰 |
| 火曜日（週二）| 火 | 火星 | Angaraka | 陽 |
| 水曜日（週三）| 水 | 水星 | Budha | 陰 |
| 木曜日（週四）| 木 | 木星 | Brhaspati | 陽 |
| 金曜日（週五）| 金 | 金星 | Shukra | 陰 |
| 土曜日（週六）| 土 | 土星 | Shani | 中 |

### 5.2 五行相生（生成關係）

```
木 → 火 → 土 → 金 → 水 → 木（循環）

木生火：木燃燒生火
火生土：火燼成灰土
土生金：土中藏金礦
金生水：金屬表面凝露水
水生木：水滋潤樹木生長
```

### 5.3 五行相剋（克制關係）

```
木 → 土 → 水 → 火 → 金 → 木（循環）

木剋土：樹根破土
土剋水：土築堤擋水
水剋火：水滅火
火剋金：火熔金
金剋木：金斧伐木
```

### 5.4 五行相洩（消耗關係）

```
被生者消耗生者的能量

木洩水：木吸收水分
水洩金：金生水時消耗金
金洩土：土生金時消耗土
土洩火：火生土時消耗火
火洩木：木生火時消耗木
```

### 5.5 元素相性加成公式

```python
def calculate_element_bonus(elem1: str, elem2: str) -> int:
    GENERATING = [("木", "火"), ("火", "土"), ("土", "金"), ("金", "水"), ("水", "木")]
    CONFLICTING = [("木", "土"), ("土", "水"), ("水", "火"), ("火", "金"), ("金", "木")]
    WEAKENING = [("木", "水"), ("水", "金"), ("金", "土"), ("土", "火"), ("火", "木")]

    if elem1 == elem2:
        return 10  # 同元素：最大加成

    pair = (elem1, elem2)
    reverse = (elem2, elem1)

    if pair in GENERATING or reverse in GENERATING:
        return 5   # 相生：正向加成

    if pair in CONFLICTING or reverse in CONFLICTING:
        return -10  # 相剋：負向減成

    if pair in WEAKENING or reverse in WEAKENING:
        return -5   # 相洩：輕微減成

    # 日月為特殊元素，與其他元素多為中性或正向
    if elem1 in ["日", "月"] or elem2 in ["日", "月"]:
        return 5

    return 0  # 中性
```

---

## 6. 運勢計算公式

### 6.1 每日運勢核心邏輯

```python
def calculate_daily_fortune(birth_date, target_date):
    # 1. 取得本命宿
    user_mansion = get_mansion(birth_date)
    user_index = user_mansion["index"]
    user_element = user_mansion["element"]

    # 2. 計算當日宿
    lunar = solar_to_lunar(target_date)
    day_index = get_mansion_index(lunar.month, lunar.day)
    day_mansion = mansions_data[day_index]

    # 3. 計算本命宿與當日宿的關係（三九秘法核心）
    relation = get_relation_type(user_index, day_index)

    # 4. 根據關係類型決定基礎分數
    SCORE_RANGES = {
        "eishin": (85, 95),   # 榮親：大吉
        "gyotai": (78, 88),   # 業胎：吉
        "mei": (72, 82),      # 命：中吉
        "yusui": (60, 72),    # 友衰：中吉偏低
        "kisei": (45, 58),    # 危成：小吉
        "ankai": (32, 48),    # 安壞：凶
    }
    base_score = random_in_range(SCORE_RANGES[relation])

    # 5. 七曜元素微調
    weekday_element = get_weekday_element(target_date)
    element_bonus = calculate_element_bonus(user_element, weekday_element)

    # 6. 最終分數
    final_score = clamp(base_score + element_bonus // 2, 30, 100)

    return final_score
```

### 6.2 運勢等級判定

| 分數範圍 | 等級 | 說明 |
|----------|------|------|
| 85-100 | 大吉 | 行動日，把握機會 |
| 70-84 | 吉 | 順利日，適合推進 |
| 55-69 | 中吉 | 平穩日，按部就班 |
| 40-54 | 小吉 | 謹慎日，避免冒進 |
| 30-39 | 凶 | 低調日，韜光養晦 |

---

## 7. 吉日判定公式

### 7.1 通用吉日條件

```python
def is_lucky_day(birth_date, target_date, action_config):
    fortune = calculate_daily_fortune(birth_date, target_date)
    relation = get_relation_type(user_index, day_index)

    # 條件 1：避開不利關係
    if relation in action_config.avoid_relations:
        return False

    # 條件 2：運勢過低
    if fortune.score < 50:
        return False

    # 條件 3：符合有利關係
    if relation in action_config.favor_relations:
        return True

    # 條件 4：元素相合且分數達標
    if is_element_compatible() and fortune.score >= action_config.favor_score:
        return True

    # 條件 5：高分日
    if fortune.score >= action_config.favor_score + 10:
        return True

    return False
```

---

## 8. 待完善項目（完整版規劃）

### 8.1 牛宿處理問題

日本主流宿曜占星術排除「牛宿」而非「軫宿」。

**現行實作**：保留牛宿（索引 8），排除軫宿
**日本主流**：排除牛宿，保留軫宿

需決定是否調整。

### 8.2 距離類型細分

目前未實作近/中/遠距離區分。完整版應：
- 在相性結果中顯示距離類型
- 提供距離類型對應的詳細解讀

### 8.3 榮/親方向性

目前「榮親」合併為單一關係。完整版應：
- 區分「我對對方是栄」或「我對對方是親」
- 提供方向性對應的角色建議

### 8.4 月份起始宿驗證

部分月份的起始宿尚無權威文獻佐證。需：
- 尋找《宿曜經》原典校勘本
- 對照日本宿曜道流派的傳承資料

---

## 9. 參考文獻

1. 《文殊師利菩薩及諸仙所説吉凶時日善悪宿曜経》（唐・不空譯，759年）
2. 《梵天火羅九曜》
3. 《七曜星辰別行法》
4. 日本維基百科 - 宿曜道、二十七宿、二十八宿
5. 宿曜占星術 八雲院 (yakumoin.net)
6. 日本占星術協會 (uranai.org)
7. 佛學大辭典 - 宿曜經條目
8. 國立天文台曆計算室 - 二十八宿

---

---

## 10. 資料儲存位置

### 本地 PostgreSQL（Docker）

所有宿曜道公式和參考資料已儲存至本地 PostgreSQL 資料庫：

**連線資訊**：
```
Host: localhost:5432
Database: sinopilot
User: sinopilot
Password: localdev
Container: sinopilot-db
```

**資料表清單**：

| 資料表 | 筆數 | 說明 |
|--------|------|------|
| `sukuyodo_mansions` | 28 | 二十七/二十八宿基本資料 |
| `sukuyodo_month_start` | 12 | 月宿傍通曆（各月起始宿） |
| `sukuyodo_relations` | 6 | 六種關係類型定義 |
| `sukuyodo_distance_types` | 20 | 完整版距離類型（近/中/遠） |
| `sukuyodo_five_elements` | 26 | 五行相生相剋相洩關係 |
| `sukuyodo_weekday_elements` | 7 | 七曜元素對照 |
| `sukuyodo_formulas` | 5 | 計算公式文檔 |
| `sukuyodo_verification_log` | 8 | 原典驗證記錄 |

**SQL 檔案位置**：
- Schema: `scripts/sukuyodo_schema.sql`
- Data: `scripts/sukuyodo_data.sql`

**查詢範例**：
```bash
# 查詢計算公式
docker exec sinopilot-db psql -U sinopilot -d sinopilot \
  -c "SELECT formula_key, formula_text FROM sukuyodo_formulas;"

# 查詢驗證狀態
docker exec sinopilot-db psql -U sinopilot -d sinopilot \
  -c "SELECT * FROM sukuyodo_verification_log WHERE status = 'pending';"
```

---

**最後更新**：2026-01-31
**版本**：1.1
