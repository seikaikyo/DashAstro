-- DashAstro - 牌陣資料

INSERT INTO tarot_spreads (code, name_zh, description, card_count, positions, suitable_questions) VALUES
('single', '單牌抽取', '最簡單直接的占卜方式，適合快速獲得指引', 1,
 '[{"position": 1, "name": "核心訊息", "description": "宇宙想告訴你的訊息"}]'::jsonb,
 ARRAY['今日指引', '簡單是非題', '快速建議']),

('three-card', '三牌陣', '經典的過去-現在-未來牌陣，呈現事件的時間軸', 3,
 '[{"position": 1, "name": "過去", "description": "影響現況的過去因素"},
   {"position": 2, "name": "現在", "description": "當前的狀況和能量"},
   {"position": 3, "name": "未來", "description": "可能的發展方向"}]'::jsonb,
 ARRAY['感情走向', '事業發展', '一般性問題']),

('love-cross', '愛情十字', '專門用於感情問題的牌陣', 5,
 '[{"position": 1, "name": "你的感受", "description": "你對這段關係的真實感受"},
   {"position": 2, "name": "對方感受", "description": "對方可能的想法和感受"},
   {"position": 3, "name": "關係現況", "description": "目前關係的狀態"},
   {"position": 4, "name": "挑戰", "description": "需要克服的障礙"},
   {"position": 5, "name": "發展方向", "description": "關係可能的走向"}]'::jsonb,
 ARRAY['感情問題', '關係發展', '曖昧對象']),

('career-path', '事業指引', '針對工作和職涯問題的牌陣', 4,
 '[{"position": 1, "name": "現況", "description": "目前的工作狀態"},
   {"position": 2, "name": "挑戰", "description": "面臨的困難和阻礙"},
   {"position": 3, "name": "建議", "description": "可以採取的行動"},
   {"position": 4, "name": "結果", "description": "可能達成的成果"}]'::jsonb,
 ARRAY['工作問題', '職涯規劃', '創業決策'])

ON CONFLICT (code) DO NOTHING;
