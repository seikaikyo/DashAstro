-- DashAstro - 星座基礎資料

INSERT INTO zodiac_signs (code, name_zh, name_en, symbol, element, modality, ruling_planet, date_start, date_end) VALUES
('ARI', '牡羊座', 'Aries', '♈', 'fire', 'cardinal', 'Mars', '03-21', '04-19'),
('TAU', '金牛座', 'Taurus', '♉', 'earth', 'fixed', 'Venus', '04-20', '05-20'),
('GEM', '雙子座', 'Gemini', '♊', 'air', 'mutable', 'Mercury', '05-21', '06-20'),
('CAN', '巨蟹座', 'Cancer', '♋', 'water', 'cardinal', 'Moon', '06-21', '07-22'),
('LEO', '獅子座', 'Leo', '♌', 'fire', 'fixed', 'Sun', '07-23', '08-22'),
('VIR', '處女座', 'Virgo', '♍', 'earth', 'mutable', 'Mercury', '08-23', '09-22'),
('LIB', '天秤座', 'Libra', '♎', 'air', 'cardinal', 'Venus', '09-23', '10-22'),
('SCO', '天蠍座', 'Scorpio', '♏', 'water', 'fixed', 'Pluto', '10-23', '11-21'),
('SAG', '射手座', 'Sagittarius', '♐', 'fire', 'mutable', 'Jupiter', '11-22', '12-21'),
('CAP', '摩羯座', 'Capricorn', '♑', 'earth', 'cardinal', 'Saturn', '12-22', '01-19'),
('AQU', '水瓶座', 'Aquarius', '♒', 'air', 'fixed', 'Uranus', '01-20', '02-18'),
('PIS', '雙魚座', 'Pisces', '♓', 'water', 'mutable', 'Neptune', '02-19', '03-20')
ON CONFLICT (code) DO NOTHING;
