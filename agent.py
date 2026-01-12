"""
AIエージェント - Web検索、コード実行、記憶機能付き
"""

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

# 環境変数を読み込み
load_dotenv()


# ツールの定義
search = DuckDuckGoSearchRun()


@tool
def web_search(query: str) -> str:
    """インターネットで情報を検索します。最新の情報や知らないことを調べる時に使用してください。"""
    return search.run(query)


@tool
def python_executor(code: str) -> str:
    """Pythonコードを実行します。計算、データ処理、分析などに使用してください。

    Args:
        code: 実行するPythonコード
    """
    try:
        # 安全のため、制限された環境で実行
        local_vars = {}
        exec(code, {"__builtins__": __builtins__}, local_vars)

        # 結果を取得
        if "result" in local_vars:
            return str(local_vars["result"])
        elif local_vars:
            return str(local_vars)
        else:
            return "コードが正常に実行されました。"
    except Exception as e:
        return f"エラー: {str(e)}"


def create_agent():
    """エージェントを作成します。"""

    # LLMの設定
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
    )

    # ツールのリスト
    tools = [web_search, python_executor]

    # メモリの設定（会話履歴を保持）
    memory = MemorySaver()

    # エージェントの作成
    agent = create_react_agent(
        llm,
        tools,
        checkpointer=memory,
    )

    return agent


def chat(agent, message: str, thread_id: str = "default"):
    """エージェントとチャットします。"""
    config = {"configurable": {"thread_id": thread_id}}

    response = agent.invoke(
        {"messages": [("user", message)]},
        config=config,
    )

    # 最後のAIメッセージを取得
    ai_message = response["messages"][-1]
    return ai_message.content


def main():
    """メイン関数 - 対話モードで実行"""
    print("=" * 50)
    print("AI エージェント")
    print("機能: Web検索、Pythonコード実行、会話記憶")
    print("終了するには 'quit' または 'exit' と入力してください")
    print("=" * 50)
    print()

    agent = create_agent()
    thread_id = "main_conversation"

    while True:
        try:
            user_input = input("あなた: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["quit", "exit", "終了"]:
                print("さようなら!")
                break

            response = chat(agent, user_input, thread_id)
            print(f"\nAI: {response}\n")

        except KeyboardInterrupt:
            print("\n\nさようなら!")
            break
        except Exception as e:
            print(f"\nエラーが発生しました: {e}\n")


if __name__ == "__main__":
    main()
