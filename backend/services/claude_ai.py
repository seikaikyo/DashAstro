"""
Claude AI 服務 - 塔羅解讀與星座運勢生成
"""
from anthropic import Anthropic
from typing import Optional
from config import get_settings

settings = get_settings()


class ClaudeAIService:
    """Claude AI 服務"""

    def __init__(self):
        if settings.anthropic_api_key:
            self.client = Anthropic(api_key=settings.anthropic_api_key)
        else:
            self.client = None

    def _is_available(self) -> bool:
        return self.client is not None

    async def interpret_tarot_reading(
        self,
        cards: list[dict],
        question: Optional[str] = None,
        spread_name: str = "單牌"
    ) -> str:
        """
        解讀塔羅牌陣

        Args:
            cards: 抽取的牌列表，每張包含 name_zh, position_name, is_reversed, meaning
            question: 用戶的問題
            spread_name: 牌陣名稱
        """
        if not self._is_available():
            return None

        # 構建牌陣描述
        cards_description = []
        for card in cards:
            direction = "逆位" if card.get("is_reversed") else "正位"
            cards_description.append(
                f"- {card['position_name']}：{card['name_zh']}（{direction}）\n"
                f"  關鍵詞：{', '.join(card.get('keywords', []))}\n"
                f"  牌義：{card.get('meaning', '')}"
            )

        cards_text = "\n\n".join(cards_description)

        question_part = f"\n問題：「{question}」\n" if question else ""

        prompt = f"""你是一位專業的塔羅解讀師，風格溫暖但務實，提供有見地的指引。

用戶使用「{spread_name}」牌陣進行占卜。{question_part}

抽出的牌：
{cards_text}

請提供一段約 200-300 字的綜合解讀：
1. 首先概述整體牌面呈現的能量和主題
2. 針對每個位置的牌給予簡短但有意義的解釋
3. 如果有用戶問題，將解讀與問題連結
4. 最後給予務實、可行動的建議

語氣要求：
- 使用繁體中文（台灣用語）
- 親切但專業，像是智慧的朋友在對話
- 避免過度神秘化或模糊的說法
- 不要使用「命運」「注定」等宿命論詞彙
- 強調個人選擇和行動的重要性"""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            print(f"Claude API 錯誤: {e}")
            return None

    async def generate_weekly_horoscope(
        self,
        zodiac_name: str,
        zodiac_element: str,
        current_aspects: list[dict],
        retrograde_planets: list[str]
    ) -> dict:
        """
        生成週運勢

        Args:
            zodiac_name: 星座名稱
            zodiac_element: 元素 (火象/土象/風象/水象)
            current_aspects: 當前重要相位
            retrograde_planets: 逆行中的行星
        """
        if not self._is_available():
            return None

        aspects_text = ""
        if current_aspects:
            aspects_list = [
                f"{a['planet1_zh']} {a['name_zh']} {a['planet2_zh']}"
                for a in current_aspects[:5]
            ]
            aspects_text = f"本週重要相位：{', '.join(aspects_list)}\n"

        retro_text = ""
        if retrograde_planets:
            retro_text = f"逆行中的行星：{', '.join(retrograde_planets)}\n"

        prompt = f"""你是一位專業的占星師，為台灣讀者撰寫週運勢。

星座：{zodiac_name}（{zodiac_element}）
{aspects_text}{retro_text}

請生成本週運勢，以 JSON 格式回覆：
{{
  "summary": "整體運勢摘要，約 80-100 字",
  "love_advice": "感情建議，約 50 字",
  "career_advice": "事業建議，約 50 字",
  "health_advice": "健康建議，約 30 字",
  "lucky_day": "週幾（如：週三）",
  "lucky_color": "顏色名稱",
  "lucky_number": 數字（1-99）,
  "overall_score": 整體運勢評分（1-5）
}}

寫作要求：
- 繁體中文（台灣用語）
- 務實具體，避免空泛的說法
- 結合當前天象給予建議
- 語氣正向但不過度樂觀
- 只回覆 JSON，不要其他文字"""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )

            import json
            result_text = response.content[0].text.strip()
            # 移除可能的 markdown 標記
            if result_text.startswith("```"):
                result_text = result_text.split("\n", 1)[1]
            if result_text.endswith("```"):
                result_text = result_text.rsplit("\n", 1)[0]

            return json.loads(result_text)
        except Exception as e:
            print(f"Claude API 錯誤: {e}")
            return None


# 全域實例
claude_service = ClaudeAIService()
