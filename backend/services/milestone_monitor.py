"""里程碑監控服務 - 自動檢查使用量觸發條件"""
import os
import httpx
from datetime import date, timedelta
from sqlmodel import Session, select, func
from database import engine
from models.stats import UsageStats


class MilestoneMonitor:
    """監控使用量里程碑"""

    # 觸發門檻設定
    THRESHOLDS = {
        "sukuyodo_lookup": 500,      # 本命宿查詢 >= 500 次/月
        "sukuyodo_compat": 200,      # 相性診斷 >= 200 次/月
    }

    # LINE Notify Token（從環境變數讀取）
    LINE_NOTIFY_TOKEN = os.getenv("LINE_NOTIFY_TOKEN")

    def check_milestones(self) -> dict:
        """檢查所有里程碑狀態"""
        results = {
            "check_date": date.today().isoformat(),
            "period": "30 days",
            "milestones": [],
            "any_triggered": False
        }

        with Session(engine) as session:
            # 計算 30 天內的使用量
            start_date = date.today() - timedelta(days=30)

            for feature, threshold in self.THRESHOLDS.items():
                # 查詢該功能的使用量
                stmt = select(func.sum(UsageStats.count)).where(
                    UsageStats.feature == feature,
                    UsageStats.stat_date >= start_date
                )
                total = session.exec(stmt).first() or 0

                milestone = {
                    "feature": feature,
                    "current": total,
                    "threshold": threshold,
                    "progress": round(total / threshold * 100, 1),
                    "triggered": total >= threshold
                }
                results["milestones"].append(milestone)

                if milestone["triggered"]:
                    results["any_triggered"] = True

        return results

    def send_notification(self, results: dict) -> bool:
        """發送 LINE Notify 通知"""
        if not self.LINE_NOTIFY_TOKEN:
            print("[Monitor] LINE_NOTIFY_TOKEN 未設定，跳過通知")
            return False

        # 組裝訊息
        lines = ["📊 DashAstro 里程碑報告", ""]

        for m in results["milestones"]:
            status = "🎯 達標!" if m["triggered"] else f"⏳ {m['progress']}%"
            lines.append(f"{m['feature']}: {m['current']}/{m['threshold']} {status}")

        if results["any_triggered"]:
            lines.append("")
            lines.append("🚀 有里程碑達標！可以啟動 Phase B 規劃")
            lines.append("📄 openspec/changes/sukuyodo-monetization.md")

        message = "\n".join(lines)

        # 發送 LINE Notify
        try:
            response = httpx.post(
                "https://notify-api.line.me/api/notify",
                headers={"Authorization": f"Bearer {self.LINE_NOTIFY_TOKEN}"},
                data={"message": message}
            )
            return response.status_code == 200
        except Exception as e:
            print(f"[Monitor] 通知發送失敗: {e}")
            return False

    def run_daily_check(self) -> dict:
        """執行每日檢查（供 Cron Job 呼叫）"""
        print(f"[Monitor] 執行每日里程碑檢查 - {date.today()}")

        results = self.check_milestones()

        # 記錄結果
        for m in results["milestones"]:
            print(f"  {m['feature']}: {m['current']}/{m['threshold']} ({m['progress']}%)")

        # 發送通知（可選：只在達標時通知，或每天都通知）
        # 這裡設定為：有任何達標，或是每週一固定通知
        should_notify = results["any_triggered"] or date.today().weekday() == 0

        if should_notify:
            sent = self.send_notification(results)
            results["notification_sent"] = sent
        else:
            results["notification_sent"] = False

        return results


# 全域實例
milestone_monitor = MilestoneMonitor()
