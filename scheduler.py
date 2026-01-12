"""
定期ニュース収集スケジューラー（メール送信機能付き）
"""

import json
import os
import smtplib
import schedule
import time
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

load_dotenv()

# 設定ファイルのパス
CONFIG_FILE = "config.json"
OUTPUT_DIR = "news_reports"


def load_config():
    """設定ファイルを読み込む"""
    default_config = {
        "topics": ["日本の主要ニュース", "アメリカの主要ニュース"],
        "schedule_times": ["09:00", "18:00"],
        "language": "日本語",
        "email": {
            "enabled": True,
            "to": "hohohotv98@gmail.com"
        }
    }

    if Path(CONFIG_FILE).exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)
        return default_config


def create_news_agent():
    """ニュース収集用エージェントを作成"""
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    search = DuckDuckGoSearchRun()

    @tool
    def web_search(query: str) -> str:
        """Web検索を実行して最新ニュースを取得"""
        return search.run(query)

    agent = create_react_agent(llm, [web_search])
    return agent


def collect_news(agent, topics: list, language: str) -> str:
    """指定トピックのニュースを収集"""
    results = []

    for topic in topics:
        prompt = f"""
「{topic}」について最新ニュースを1回だけ検索してください。
検索後、結果を{language}で以下の形式でまとめてください：

## {topic}

- **ニュース1**: 概要（1文）
- **ニュース2**: 概要（1文）
- **ニュース3**: 概要（1文）

注意: 検索は1回だけ実行し、その結果からニュースをまとめてください。
"""
        try:
            # recursion_limitを設定
            config = {"recursion_limit": 10}
            response = agent.invoke({"messages": [("user", prompt)]}, config=config)
            ai_message = response["messages"][-1]
            results.append(ai_message.content)
        except Exception as e:
            results.append(f"## {topic}\n\n収集中にエラーが発生しました: {str(e)}")

    return "\n\n---\n\n".join(results)


def send_email(subject: str, body: str, to_email: str):
    """メールを送信"""
    gmail_user = os.getenv("GMAIL_ADDRESS")
    gmail_password = os.getenv("GMAIL_APP_PASSWORD")

    if not gmail_user or not gmail_password:
        print("警告: Gmail認証情報が設定されていません")
        print("  .envファイルに以下を追加してください:")
        print("  GMAIL_ADDRESS=your-email@gmail.com")
        print("  GMAIL_APP_PASSWORD=your-app-password")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = gmail_user
    msg["To"] = to_email

    # プレーンテキストとHTML両方を添付
    text_part = MIMEText(body, "plain", "utf-8")
    msg.attach(text_part)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail_user, gmail_password)
            server.sendmail(gmail_user, to_email, msg.as_string())
        print(f"[{datetime.now().strftime('%H:%M:%S')}] メール送信完了: {to_email}")
        return True
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] メール送信エラー: {e}")
        return False


def save_report(content: str) -> str:
    """レポートをファイルに保存"""
    Path(OUTPUT_DIR).mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"{OUTPUT_DIR}/news_{timestamp}.md"

    report = f"""# ニュースレポート

**収集日時**: {datetime.now().strftime("%Y年%m月%d日 %H:%M")}

---

{content}

---
*このレポートはAIエージェントにより自動生成されました*
"""

    with open(filename, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"[{datetime.now().strftime('%H:%M:%S')}] レポート保存: {filename}")
    return report


def run_collection():
    """ニュース収集を実行"""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] ニュース収集を開始...")

    config = load_config()
    agent = create_news_agent()

    content = collect_news(
        agent,
        config["topics"],
        config["language"]
    )

    report = save_report(content)

    # メール送信
    email_config = config.get("email", {})
    if email_config.get("enabled") and email_config.get("to"):
        subject = f"ニュースレポート - {datetime.now().strftime('%Y/%m/%d %H:%M')}"
        send_email(subject, report, email_config["to"])

    print(f"[{datetime.now().strftime('%H:%M:%S')}] 収集完了!")


def run_once():
    """1回だけ実行（テスト用）"""
    run_collection()


def run_scheduler():
    """スケジューラーを起動"""
    config = load_config()

    print("=" * 50)
    print("ニュース収集スケジューラー")
    print("=" * 50)
    print(f"トピック: {', '.join(config['topics'])}")
    print(f"実行時刻: {', '.join(config['schedule_times'])}")
    email_config = config.get("email", {})
    if email_config.get("enabled"):
        print(f"送信先: {email_config.get('to')}")
    print("終了するには Ctrl+C を押してください")
    print("=" * 50)
    print()

    # スケジュール設定
    for time_str in config["schedule_times"]:
        schedule.every().day.at(time_str).do(run_collection)
        print(f"スケジュール登録: 毎日 {time_str}")

    print()
    print("スケジューラー稼働中...")

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--now":
        run_once()
    else:
        run_scheduler()
