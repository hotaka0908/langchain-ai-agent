# LangChain AI Agent

LangChainを使用したAIエージェント。Web検索、コード実行、会話記憶機能を備えた対話型アシスタントと、定期的にニュースを収集してメール送信するスケジューラーを含みます。

## 機能

### 対話型エージェント (`agent.py`)
- **Web検索**: DuckDuckGoを使用してインターネットから情報を取得
- **Pythonコード実行**: 計算やデータ処理をその場で実行
- **会話記憶**: 会話の文脈を保持して自然な対話が可能

### ニューススケジューラー (`scheduler.py`)
- **定期実行**: 毎日指定時刻に自動でニュース収集
- **メール送信**: 収集したニュースをResend経由でメール配信
- **カスタマイズ可能**: トピック、実行時刻、送信先を設定ファイルで変更可能

## セットアップ

### 1. リポジトリをクローン

```bash
git clone https://github.com/hotaka0908/langchain-ai-agent.git
cd langchain-ai-agent
```

### 2. 仮想環境を作成

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. 依存パッケージをインストール

```bash
pip install -r requirements.txt
```

### 4. 環境変数を設定

```bash
cp .env.example .env
```

`.env`ファイルを編集:

```env
# OpenAI API キー（必須）
OPENAI_API_KEY=sk-your-api-key-here

# Resend API キー（メール送信する場合）
RESEND_API_KEY=re_your-api-key-here
```

### 5. 設定ファイルを作成（スケジューラー用）

```bash
cp config.example.json config.json
```

`config.json`を編集してトピックや送信先を設定:

```json
{
  "topics": [
    "日本の主要ニュース",
    "アメリカの主要ニュース"
  ],
  "schedule_times": [
    "09:00",
    "18:00"
  ],
  "language": "日本語",
  "email": {
    "enabled": true,
    "to": "your-email@example.com"
  }
}
```

## 使い方

### 対話型エージェント

```bash
source venv/bin/activate
python agent.py
```

```
==================================================
AI エージェント
機能: Web検索、Pythonコード実行、会話記憶
終了するには 'quit' または 'exit' と入力してください
==================================================

あなた: 今日の天気を調べて
AI: (Web検索を実行して回答)

あなた: 1から100までの合計を計算して
AI: 5050です。（Pythonで sum(range(1, 101)) を実行しました）

あなた: quit
さようなら!
```

### ニューススケジューラー

**1回だけ実行（テスト用）:**

```bash
python scheduler.py --now
```

**スケジューラーを起動（バックグラウンド実行）:**

```bash
python scheduler.py
```

または nohup で永続実行:

```bash
nohup python scheduler.py > scheduler.log 2>&1 &
```

## APIキーの取得方法

### OpenAI API
1. https://platform.openai.com にアクセス
2. アカウント作成・ログイン
3. API Keys → Create new secret key

### Resend API（メール送信用）
1. https://resend.com にアクセス
2. アカウント作成（GitHubアカウントで簡単登録可能）
3. API Keys → Create API Key

**注意**: Resendの無料プランでは、ドメイン認証なしの場合、登録したメールアドレスにのみ送信可能です。

## ファイル構成

```
langchain-ai-agent/
├── agent.py           # 対話型AIエージェント
├── scheduler.py       # ニュース収集スケジューラー
├── requirements.txt   # 依存パッケージ
├── .env.example       # 環境変数サンプル
├── config.example.json# 設定ファイルサンプル
└── README.md          # このファイル
```

## 技術スタック

- **LangChain**: LLMアプリケーションフレームワーク
- **LangGraph**: エージェントワークフロー構築
- **OpenAI GPT-4o-mini**: 言語モデル
- **DuckDuckGo Search**: Web検索
- **Resend**: メール送信API
- **schedule**: Pythonスケジューラー

## ライセンス

MIT
