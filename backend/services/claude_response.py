"""
讀 Claude 回應的文字與結束原因

官方要求（claude-platform 文件，2026-11-19 對照）：
- 依區塊 type 挑文字，不讀 content[0]：Opus 5、Sonnet 5 以後沒帶 thinking 也會先思考，
  第一塊可能是 thinking（build-with-claude/prompt-engineering/claude-prompting-best-practices.md:779）
- 每次讀 stop_reason：拒答是 HTTP 200 加 refusal，不是錯誤（build-with-claude/handling-stop-reasons.md:1783）；
  思考算進 max_tokens，上限太小會在出文字前停住（models/fable-5-2/migration-guide.md:95）
"""
import logging

logger = logging.getLogger(__name__)

REFUSAL_REPLY = "這個請求模型沒有回答，請換個說法再試一次。"

INCOMPLETE_STOP_REASONS = ("refusal", "max_tokens")


class ClaudeIncompleteResponse(Exception):
    """回應以拒答或截斷結束，呼叫端不能把內容當完整結果用"""

    def __init__(self, stop_reason: str, text: str = ""):
        super().__init__(f"Claude 回應未完成：stop_reason={stop_reason}")
        self.stop_reason = stop_reason
        self.text = text


def text_and_stop_reason(message) -> tuple[str, str | None]:
    """收集所有 text 區塊的文字，連同 stop_reason 一起回傳"""
    parts = [
        getattr(block, "text", "")
        for block in (getattr(message, "content", None) or [])
        if getattr(block, "type", None) == "text"
    ]
    return "".join(parts), getattr(message, "stop_reason", None)


def chat_reply_text(message, where: str = "") -> str:
    """聊天類用：拒答回固定說明，截斷照回並記警告"""
    text, stop = text_and_stop_reason(message)
    if stop == "refusal":
        logger.warning("Claude refusal%s", f" ({where})" if where else "")
        return text or REFUSAL_REPLY
    if stop == "max_tokens":
        logger.warning("Claude reply truncated at max_tokens%s", f" ({where})" if where else "")
    return text


def complete_text(message) -> str:
    """要拿去解析的內容用（例如 JSON）：拒答或截斷直接丟錯"""
    text, stop = text_and_stop_reason(message)
    if stop in INCOMPLETE_STOP_REASONS:
        raise ClaudeIncompleteResponse(stop, text)
    return text
