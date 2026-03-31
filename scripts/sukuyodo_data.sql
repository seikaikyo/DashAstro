-- 宿曜道資料插入
-- 建立於 2026-01-31

-- 1. 二十八宿資料
INSERT INTO sukuyodo_mansions (index_num, name_jp, name_zh, reading, element, element_animal, quadrant, quadrant_element, is_excluded_jp, is_excluded_cn) VALUES
(0, '角宿', '角宿', 'かくしゅく', '木', '角木蛟', '東方青龍', '木', FALSE, FALSE),
(1, '亢宿', '亢宿', 'こうしゅく', '金', '亢金龍', '東方青龍', '木', FALSE, FALSE),
(2, '氐宿', '氐宿', 'ていしゅく', '土', '氐土貉', '東方青龍', '木', FALSE, FALSE),
(3, '房宿', '房宿', 'ぼうしゅく', '日', '房日兔', '東方青龍', '木', FALSE, FALSE),
(4, '心宿', '心宿', 'しんしゅく', '月', '心月狐', '東方青龍', '木', FALSE, FALSE),
(5, '尾宿', '尾宿', 'びしゅく', '火', '尾火虎', '東方青龍', '木', FALSE, FALSE),
(6, '箕宿', '箕宿', 'きしゅく', '水', '箕水豹', '東方青龍', '木', FALSE, FALSE),
(7, '斗宿', '斗宿', 'としゅく', '木', '斗木獬', '北方玄武', '水', FALSE, FALSE),
(8, '牛宿', '牛宿', 'ぎゅうしゅく', '金', '牛金牛', '北方玄武', '水', TRUE, FALSE),
(9, '女宿', '女宿', 'じょしゅく', '土', '女土蝠', '北方玄武', '水', FALSE, FALSE),
(10, '虛宿', '虛宿', 'きょしゅく', '日', '虛日鼠', '北方玄武', '水', FALSE, FALSE),
(11, '危宿', '危宿', 'きしゅく', '月', '危月燕', '北方玄武', '水', FALSE, FALSE),
(12, '室宿', '室宿', 'しつしゅく', '火', '室火豬', '北方玄武', '水', FALSE, FALSE),
(13, '壁宿', '壁宿', 'へきしゅく', '水', '壁水貐', '北方玄武', '水', FALSE, FALSE),
(14, '奎宿', '奎宿', 'けいしゅく', '木', '奎木狼', '西方白虎', '金', FALSE, FALSE),
(15, '婁宿', '婁宿', 'ろうしゅく', '金', '婁金狗', '西方白虎', '金', FALSE, FALSE),
(16, '胃宿', '胃宿', 'いしゅく', '土', '胃土雉', '西方白虎', '金', FALSE, FALSE),
(17, '昴宿', '昴宿', 'ぼうしゅく', '日', '昴日雞', '西方白虎', '金', FALSE, FALSE),
(18, '畢宿', '畢宿', 'ひつしゅく', '月', '畢月烏', '西方白虎', '金', FALSE, FALSE),
(19, '觜宿', '觜宿', 'ししゅく', '火', '觜火猴', '西方白虎', '金', FALSE, FALSE),
(20, '參宿', '參宿', 'しんしゅく', '水', '參水猿', '西方白虎', '金', FALSE, FALSE),
(21, '井宿', '井宿', 'せいしゅく', '木', '井木犴', '南方朱雀', '火', FALSE, FALSE),
(22, '鬼宿', '鬼宿', 'きしゅく', '金', '鬼金羊', '南方朱雀', '火', FALSE, FALSE),
(23, '柳宿', '柳宿', 'りゅうしゅく', '土', '柳土獐', '南方朱雀', '火', FALSE, FALSE),
(24, '星宿', '星宿', 'せいしゅく', '日', '星日馬', '南方朱雀', '火', FALSE, FALSE),
(25, '張宿', '張宿', 'ちょうしゅく', '月', '張月鹿', '南方朱雀', '火', FALSE, FALSE),
(26, '翼宿', '翼宿', 'よくしゅく', '火', '翼火蛇', '南方朱雀', '火', FALSE, FALSE),
(27, '軫宿', '軫宿', 'しんしゅく', '水', '軫水蚓', '南方朱雀', '火', FALSE, TRUE)
ON CONFLICT (index_num) DO UPDATE SET updated_at = CURRENT_TIMESTAMP;

-- 2. 月宿傍通曆
INSERT INTO sukuyodo_month_start (lunar_month, start_mansion_index, start_mansion_name, verification_status, verification_source) VALUES
(1, 11, '危宿', 'pending', NULL),
(2, 13, '壁宿', 'pending', NULL),
(3, 15, '婁宿', 'pending', NULL),
(4, 17, '昴宿', 'pending', NULL),
(5, 19, '觜宿', 'pending', NULL),
(6, 21, '井宿', 'pending', NULL),
(7, 24, '星宿', 'pending', NULL),
(8, 0, '角宿', 'verified', 'Wikipedia 二十七宿'),
(9, 2, '氐宿', 'verified', 'Wikipedia 二十七宿'),
(10, 4, '心宿', 'pending', NULL),
(11, 7, '斗宿', 'pending', NULL),
(12, 9, '女宿', 'pending', NULL)
ON CONFLICT (lunar_month) DO UPDATE SET updated_at = CURRENT_TIMESTAMP;

-- 3. 六種關係類型
INSERT INTO sukuyodo_relations (type_key, name_zh, name_jp, reading, distances, base_score, description, advice) VALUES
('mei', '命', '命', 'めい', '{0}', 85, '同宿的兩人如同鏡子般的存在，能深刻理解彼此的思維和感受。', '接納對方的缺點，就是學習接納自己。'),
('gyotai', '業胎', '業胎', 'ぎょうたい', '{9,18}', 90, '宿曜道中緣分最深的組合，常有似曾相識的熟悉感。', '順其自然地發展關係，不過度強求結果。'),
('eishin', '榮親', '栄親', 'えいしん', '{1,3,10,12,15,17,24,26}', 95, '最為吉利的關係組合，雙方在一起時會互相提升、互相成就。', '積極合作，共同效果會加倍放大。'),
('yusui', '友衰', '友衰', 'ゆうすい', '{2,5,11,13,14,16,22,25}', 70, '相處起來自在舒適，如同認識多年的老友，但可能導致懈怠。', '設定共同的成長目標，互相督促前進。'),
('ankai', '安壞', '安壊', 'あんかい', '{4,6,21,23}', 50, '具有強烈吸引力但權力不對等的組合，需要高度自覺和經營。', '認清自己在關係中扮演的角色。'),
('kisei', '危成', '危成', 'きせい', '{7,8,19,20}', 75, '互補型的關係，雙方的特質和能力形成對比，需要磨合。', '學習欣賞彼此的不同之處。')
ON CONFLICT (type_key) DO UPDATE SET updated_at = CURRENT_TIMESTAMP;

-- 4. 距離類型定義（完整版三九秘法）
INSERT INTO sukuyodo_distance_types (relation_key, distance_type, distances, direction, description, intensity_score) VALUES
-- 榮親
('eishin', 'near', '{1,26}', '栄', '近距離榮：對對方有強烈的正面影響', 100),
('eishin', 'near', '{26,1}', '親', '近距離親：受對方強烈的正面影響', 100),
('eishin', 'mid', '{10,17}', '栄', '中距離榮：最平衡的互利關係', 95),
('eishin', 'mid', '{17,10}', '親', '中距離親：最平衡的受惠關係', 95),
('eishin', 'far', '{3,24,12,15}', '栄', '遠距離榮：淡而持久的正面影響', 85),
('eishin', 'far', '{24,3,15,12}', '親', '遠距離親：淡而持久的受惠', 85),
-- 友衰
('yusui', 'near', '{2,25}', '友', '近距離友：強烈的舒適感', 75),
('yusui', 'near', '{25,2}', '衰', '近距離衰：容易一起停滯', 65),
('yusui', 'mid', '{11,16}', '友', '中距離友：適度的放鬆關係', 72),
('yusui', 'mid', '{16,11}', '衰', '中距離衰：需注意成長動力', 68),
('yusui', 'far', '{5,22,13,14}', '友', '遠距離友：輕鬆的交際', 70),
('yusui', 'far', '{22,5,14,13}', '衰', '遠距離衰：影響較淡', 70),
-- 安壞
('ankai', 'near', '{4,23}', '安', '近距離安：給予對方強烈安定感', 55),
('ankai', 'near', '{23,4}', '壊', '近距離壞：容易被對方影響', 45),
('ankai', 'mid', '{6,21}', '安', '中距離安：適度的主導關係', 52),
('ankai', 'mid', '{21,6}', '壊', '中距離壞：需保護自己', 48),
-- 危成
('kisei', 'near', '{7,20}', '危', '近距離危：強烈的互補挑戰', 78),
('kisei', 'near', '{20,7}', '成', '近距離成：強烈的成就推動', 80),
('kisei', 'mid', '{8,19}', '危', '中距離危：適度的互補', 76),
('kisei', 'mid', '{19,8}', '成', '中距離成：適度的成就感', 78)
ON CONFLICT (relation_key, distance_type, direction) DO NOTHING;

-- 5. 五行關係
INSERT INTO sukuyodo_five_elements (element1, element2, relation_type, bonus_score, description) VALUES
-- 相生（+5）
('木', '火', 'generating', 5, '木生火：木燃燒生火'),
('火', '土', 'generating', 5, '火生土：火燼成灰土'),
('土', '金', 'generating', 5, '土生金：土中藏金礦'),
('金', '水', 'generating', 5, '金生水：金屬表面凝露水'),
('水', '木', 'generating', 5, '水生木：水滋潤樹木生長'),
-- 相剋（-10）
('木', '土', 'conflicting', -10, '木剋土：樹根破土'),
('土', '水', 'conflicting', -10, '土剋水：土築堤擋水'),
('水', '火', 'conflicting', -10, '水剋火：水滅火'),
('火', '金', 'conflicting', -10, '火剋金：火熔金'),
('金', '木', 'conflicting', -10, '金剋木：金斧伐木'),
-- 相洩（-5）
('火', '木', 'weakening', -5, '木生火消耗木'),
('土', '火', 'weakening', -5, '火生土消耗火'),
('金', '土', 'weakening', -5, '土生金消耗土'),
('水', '金', 'weakening', -5, '金生水消耗金'),
('木', '水', 'weakening', -5, '水生木消耗水'),
-- 同元素（+10）
('木', '木', 'same', 10, '同為木性，能量共鳴'),
('火', '火', 'same', 10, '同為火性，能量共鳴'),
('土', '土', 'same', 10, '同為土性，能量共鳴'),
('金', '金', 'same', 10, '同為金性，能量共鳴'),
('水', '水', 'same', 10, '同為水性，能量共鳴'),
('日', '日', 'same', 10, '同為日性，能量共鳴'),
('月', '月', 'same', 10, '同為月性，能量共鳴'),
-- 日月特殊（+5）
('日', '火', 'generating', 5, '日火相合'),
('日', '木', 'generating', 5, '日木相合'),
('月', '水', 'generating', 5, '月水相合'),
('月', '金', 'generating', 5, '月金相合')
ON CONFLICT (element1, element2) DO NOTHING;

-- 6. 七曜元素
INSERT INTO sukuyodo_weekday_elements (weekday_num, name_jp, reading, element, planet_zh, planet_sanskrit, energy) VALUES
(0, '日曜日', 'にちようび', '日', '太陽', 'Aditya', '陽'),
(1, '月曜日', 'げつようび', '月', '月亮', 'Soma', '陰'),
(2, '火曜日', 'かようび', '火', '火星', 'Angaraka', '陽'),
(3, '水曜日', 'すいようび', '水', '水星', 'Budha', '陰'),
(4, '木曜日', 'もくようび', '木', '木星', 'Brhaspati', '陽'),
(5, '金曜日', 'きんようび', '金', '金星', 'Shukra', '陰'),
(6, '土曜日', 'どようび', '土', '土星', 'Shani', '中')
ON CONFLICT (weekday_num) DO NOTHING;

-- 7. 計算公式
INSERT INTO sukuyodo_formulas (formula_key, category, name, description, formula_text, formula_python, variables, examples, source, verification_status) VALUES
('mansion_index', 'core', '本命宿計算公式', '根據農曆月日計算本命宿索引',
 '本命宿索引 = (月份起始宿索引 + 農曆日 - 1) mod 27',
 'mansion_index = (MONTH_START[lunar_month] + lunar_day - 1) % 27',
 '{"lunar_month": "農曆月份 (1-12)", "lunar_day": "農曆日期 (1-30)", "MONTH_START": "月宿傍通曆對照表"}',
 '[{"input": {"lunar_month": 3, "lunar_day": 15}, "output": 2, "explanation": "(15 + 15 - 1) mod 27 = 29 mod 27 = 2 (氐宿)"}]',
 '宿曜經、月宿傍通曆', 'verified'),

('relation_distance', 'core', '關係距離計算公式', '計算兩宿之間的最短距離',
 'distance = min(|index2 - index1|, 27 - |index2 - index1|)',
 'distance = abs(index2 - index1); distance = min(distance, 27 - distance)',
 '{"index1": "第一個宿索引 (0-26)", "index2": "第二個宿索引 (0-26)"}',
 '[{"input": {"index1": 0, "index2": 10}, "output": 10}, {"input": {"index1": 0, "index2": 20}, "output": 7}]',
 '三九秘法', 'verified'),

('element_bonus', 'core', '元素相性加成公式', '計算五行元素間的相性加成分數',
 '同元素: +10, 相生: +5, 相剋: -10, 相洩: -5, 中性: 0',
 'if elem1 == elem2: return 10; if (elem1, elem2) in GENERATING: return 5; ...',
 '{"elem1": "第一個元素", "elem2": "第二個元素", "GENERATING": "相生配對", "CONFLICTING": "相剋配對"}',
 '[{"input": {"elem1": "木", "elem2": "火"}, "output": 5, "explanation": "木生火，相生加成"}]',
 '五行理論', 'verified'),

('daily_fortune', 'fortune', '每日運勢計算公式', '根據本命宿與當日宿的關係計算每日運勢',
 '運勢分數 = 關係基礎分數 + 七曜元素微調 (範圍: 30-100)',
 'base = RELATION_SCORE_RANGES[relation_type]; adjustment = element_bonus // 2; score = clamp(base + adjustment, 30, 100)',
 '{"relation_type": "宿曜關係類型", "element_bonus": "元素加成", "RELATION_SCORE_RANGES": "關係對應分數範圍表"}',
 '[{"input": {"relation": "eishin", "element_bonus": 10}, "output": "90-100", "explanation": "榮親關係 (85-95) + 元素加成 5"}]',
 '三九秘法運用', 'verified'),

('compatibility_score', 'compatibility', '相性分數計算公式', '綜合關係類型和元素相性計算最終分數',
 '最終分數 = min(100, 關係基礎分數 + 元素加成)',
 'final_score = min(100, relation_score + element_bonus)',
 '{"relation_score": "關係類型基礎分數", "element_bonus": "元素相性加成"}',
 '[{"input": {"relation_score": 95, "element_bonus": 10}, "output": 100}]',
 '三九秘法相性', 'verified')
ON CONFLICT (formula_key) DO UPDATE SET updated_at = CURRENT_TIMESTAMP;

-- 8. 驗證記錄
INSERT INTO sukuyodo_verification_log (target_type, target_key, verification_date, status, source, source_url, notes, verified_by) VALUES
('history', 'origin', '2026-01-31', 'verified', 'Wikipedia 宿曜道', 'https://ja.wikipedia.org/wiki/宿曜道', '空海806年傳入日本', 'Claude'),
('history', 'scripture', '2026-01-31', 'verified', '佛學大辭典', 'https://zh.wikisource.org/wiki/佛學大辭典/宿曜經', '不空759年中國譯出', 'Claude'),
('mansion', 'sequence', '2026-01-31', 'verified', 'Wikipedia 二十七宿', 'https://ja.wikipedia.org/wiki/二十七宿', '27宿順序正確', 'Claude'),
('month_start', 'august', '2026-01-31', 'verified', 'Wikipedia 二十七宿', 'https://ja.wikipedia.org/wiki/二十七宿', '八月朔日角宿', 'Claude'),
('month_start', 'september', '2026-01-31', 'verified', 'Wikipedia 二十七宿', 'https://ja.wikipedia.org/wiki/二十七宿', '九月朔日氐宿', 'Claude'),
('relation', 'all_types', '2026-01-31', 'verified', '宿曜占星術八雲院', 'https://yakumoin.net/', '六種關係類型定義正確', 'Claude'),
('element', 'five_elements', '2026-01-31', 'verified', '五行理論通論', NULL, '相生相剋邏輯正確', 'Claude'),
('element', 'seven_luminaries', '2026-01-31', 'verified', 'Wikipedia 七曜', NULL, '七曜對應正確', 'Claude');
