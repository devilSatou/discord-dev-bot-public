# Discord Dev Bot - 常時起動型開発アシスタント

Windows起動時に自動起動し、通勤中でもDiscordから開発指示を出せる環境を構築するBotです。

## ✨ 特徴

- 🚀 Windows起動時に自動起動
- 🖥️ タスクトレイに常駐（邪魔にならない）
- 🔄 自動再接続機能
- 📝 ログ自動管理（7日間保持）
- 🤖 Claude Codeとの連携
- 🔐 Git自動コミット＆プッシュ
- 💬 Discord通知

## 📋 必要なもの

- Windows 10/11
- Python 3.11以上
- Discord アカウント
- Claude Code（インストール済み）
- Git（インストール済み）


## 🎯 セットアップ手順（初心者向け）

### ステップ1: Pythonのインストール

1. [Python公式サイト](https://www.python.org/downloads/)にアクセス
2. 「Download Python 3.11」をクリック
3. インストーラーを実行
4. **重要**: 「Add Python to PATH」に必ずチェック ✅
5. 「Install Now」をクリック

**確認方法:**
```cmd
python --version
```
→ `Python 3.11.x` と表示されればOK

---

### ステップ2: Discord Botの作成

#### 2-1. Discord Developer Portalにアクセス

1. [Discord Developer Portal](https://discord.com/developers/applications)を開く
2. Discordにログイン
3. 右上の「New Application」をクリック

#### 2-2. Botアプリケーションを作成

1. 名前を入力（例: `Dev Bot`）
2. 利用規約に同意してチェック
3. 「Create」をクリック

#### 2-3. Botを設定

1. 左メニューから「Bot」をクリック
2. 「Reset Token」をクリック
3. **重要**: 表示されたTokenをコピー（一度しか表示されません！）
   ```
   例: YOUR_BOT_TOKEN_WILL_APPEAR_HERE
   ```
4. 下にスクロールして以下を有効化:
   - ✅ MESSAGE CONTENT INTENT

#### 2-4. Botを招待

1. 左メニューから「OAuth2」→「URL Generator」
2. **Scopes**で以下を選択:
   - ✅ `bot`
3. **Bot Permissions**で以下を選択:
   - ✅ `Send Messages`
   - ✅ `Read Message History`
   - ✅ `View Channels`
4. 下部に生成されたURLをコピー
5. ブラウザの新しいタブでそのURLを開く
6. Botを追加するサーバーを選択
7. 「認証」をクリック

---

### ステップ3: Botのインストール

#### 3-1. ファイルの配置

1. すべてのファイルを任意のフォルダに配置
   ```
   C:\Users\YourName\discord-dev-bot\
   ├── bot.py
   ├── start_bot.vbs
   ├── install.bat
   ├── requirements.txt
   └── README.md
   ```

#### 3-2. インストール実行

1. `install.bat`を**右クリック**
2. 「管理者として実行」を選択
3. 自動的にセットアップが開始されます
4. 完了まで待機（数分かかる場合があります）

---

### ステップ4: 設定ファイルの編集

#### 4-1. config.jsonを開く

インストール後、`config.json`が作成されます。
メモ帳で開いて編集してください。

```json
{
  "discord_token": "ここにステップ2-3でコピーしたTokenを貼り付け",
  "command_prefix": "!dev ",
  "project_dir": "C:\\Users\\YourName\\your-project",
  "auto_reconnect": true,
  "startup_delay": 30
}
```

#### 4-2. 各設定の説明

- `discord_token`: Discord BotのToken（必須）
- `command_prefix`: コマンドの接頭辞（デフォルト: `!dev `）
- `project_dir`: 開発プロジェクトのパス（`\\`でエスケープ）
- `auto_reconnect`: 自動再接続を有効化（true推奨）
- `startup_delay`: 起動時の待機時間（秒）

---

### ステップ5: テスト起動

#### 5-1. 手動起動でテスト

1. `start_bot.vbs`をダブルクリック
2. タスクトレイに🤖アイコンが表示されるまで待つ（30秒程度）
3. タスクトレイアイコンを右クリック→「ログ表示」で確認

#### 5-2. Discord で動作確認

Botを招待したサーバーで以下のコマンドを送信:

```
!dev status
```

以下のような情報が表示されればOK:
- ✅ 稼働中
- ⏱️ 稼働時間
- 📁 プロジェクトパス
- 🏓 Ping

---

### ステップ6: 自動起動の確認

#### 6-1. スタートアップ登録確認

1. `Win + R`キーを押す
2. `shell:startup`と入力してEnter
3. 「Discord Dev Bot」のショートカットがあればOK

#### 6-2. 自動起動テスト

1. PCを再起動
2. ログイン後、30秒待つ
3. タスクトレイに🤖アイコンが表示されるか確認
4. Discordで`!dev status`を送信して動作確認

---

## 🎮 使い方

### コマンド一覧

#### 1. `!dev implement <内容>`
Claude Codeで実装を実行し、自動コミット＆プッシュ

**例:**
```
!dev implement ログイン機能を追加してください
```

**実行される処理:**
1. Claude Codeで実装
2. `git add .`
3. `git commit -m "[Bot] ログイン機能を追加してください"`
4. `git push`
5. Discord通知

---

#### 2. `!dev status`
Bot稼働状況を表示

**表示内容:**
- 状態（稼働中/停止中）
- 稼働時間
- プロジェクトパス
- 起動時刻
- Ping

---

#### 3. `!dev stop`
Botを安全に停止

**動作:**
- Botを停止
- 次回PC起動時は自動的に再開

**使用例:**
```
!dev stop
```

---

#### 4. `!dev restart`
Botを再起動

**動作:**
- 現在のBotプロセスを終了
- 新しいプロセスで起動

**使用例:**
```
!dev restart
```

---

#### 5. `!dev diagnose`
Claude環境の診断

**表示内容:**
- Claudeコマンドの検出状況
- npmパスの確認
- Claudeバージョン
- PATH環境変数

**使用例:**
```
!dev diagnose
```

---

### タスクトレイメニュー

タスクトレイの🤖アイコンを右クリック:

- **ステータス確認**: ログファイルを開く
- **ログ表示**: ログファイルを開く
- **再起動**: Botを再起動
- **終了**: Botを終了

---

## 📂 ファイル構成

```
C:\Users\YourName\discord-dev-bot\
├── bot.py              # Bot本体
├── start_bot.vbs       # サイレント起動スクリプト
├── install.bat         # インストーラー
├── requirements.txt    # 依存パッケージ
├── config.json         # 設定ファイル（自動生成）
├── config.json.example # 設定ファイルのサンプル
├── README.md           # このファイル
└── logs/
    └── bot.log         # ログファイル（自動生成）
```

---

## 🔧 トラブルシューティング

### Bot が起動しない

#### 原因1: Discord Token が間違っている

**確認方法:**
1. `logs\bot.log`を開く
2. `ログイン失敗: Discord Tokenが無効です`と表示されている

**解決方法:**
1. [Discord Developer Portal](https://discord.com/developers/applications)を開く
2. 自分のアプリケーションを選択
3. 「Bot」タブ → 「Reset Token」
4. 新しいTokenをコピー
5. `config.json`の`discord_token`を更新

---

#### 原因2: Python が見つからない

**確認方法:**
```cmd
python --version
```
→ エラーが表示される

**解決方法:**
1. Pythonを再インストール
2. **必ず**「Add Python to PATH」にチェック
3. PCを再起動

---

#### 原因3: パッケージがインストールされていない

**解決方法:**
```cmd
cd C:\Users\YourName\discord-dev-bot
pip install -r requirements.txt
```

---

### タスクトレイにアイコンが表示されない

**原因:** 起動に時間がかかっている

**解決方法:**
1. 30秒〜1分待つ
2. `logs\bot.log`でエラーを確認
3. 手動起動を試す:
   ```cmd
   cd C:\Users\YourName\discord-dev-bot
   python bot.py
   ```

---

### コマンドに反応しない

**原因:** Bot にメッセージ権限がない

**解決方法:**
1. Discordサーバー設定を開く
2. 「役割」→ Botの役割を選択
3. 以下を有効化:
   - ✅ メッセージを送信
   - ✅ メッセージ履歴を読む
   - ✅ チャンネルを見る

---

### `!dev implement`が動かない

**原因1:** Claude Code がインストールされていない

**解決方法:**
```cmd
# Claude Code インストール確認
claude --version

# インストールされていない場合
npm install -g @anthropic-ai/claude
```

---

**原因2:** Git がインストールされていない

**解決方法:**
1. [Git公式サイト](https://git-scm.com/downloads)からインストール
2. インストール後、PCを再起動

---

### ログが大量に溜まる

**自動管理:**
- ログは7日間自動保持
- 古いログは自動削除
- 各ログファイルは最大5MB

**手動削除:**
```cmd
cd C:\Users\YourName\discord-dev-bot\logs
del bot.log.*
```

---

## 🔐 セキュリティ

### Discord Token の管理

- **絶対にGitHubにプッシュしない**
- `config.json`は`.gitignore`に追加
- Tokenが漏洩した場合は即座にリセット

### .gitignore例

```gitignore
# Discord Dev Bot
config.json
logs/
*.log

# Python
__pycache__/
*.pyc
*.pyo
```

---

## 📝 ログの見方

### ログファイルの場所

```
C:\Users\YourName\discord-dev-bot\logs\bot.log
```

### ログの例

```
2025-11-12 09:00:00 [INFO] Bot起動開始
2025-11-12 09:00:30 [INFO] Bot接続開始...
2025-11-12 09:00:35 [INFO] Botログイン完了: Dev Bot
2025-11-12 09:00:35 [INFO] 接続サーバー数: 1
2025-11-12 10:15:22 [INFO] implement コマンド実行: ログイン機能を追加...
2025-11-12 10:15:45 [INFO] 実装完了
2025-11-12 10:15:46 [INFO] Git commit & push 完了
```

---

## 🚀 応用編

### 複数プロジェクトの管理

プロジェクトごとに別のBotを起動:

1. フォルダを複製
   ```
   discord-dev-bot-project1\
   discord-dev-bot-project2\
   ```

2. 各`config.json`で`project_dir`を変更

3. それぞれ`install.bat`を実行

---

### コマンド接頭辞の変更

`config.json`を編集:

```json
{
  "command_prefix": "!bot ",
}
```

コマンド例: `!bot status`

---

### 起動遅延の調整

**デフォルト:** 30秒（他サービス待機）

**変更方法:**
`config.json`を編集:

```json
{
  "startup_delay": 60
}
```

---

## 🆘 よくある質問（FAQ）

### Q1: PCをスリープから復帰したとき、Botは動作しますか？

**A:** はい、自動的に再接続します。

---

### Q2: 外出先から使えますか？

**A:** はい、自宅PCが起動していればDiscordから操作できます。

**注意点:**
- PCをスリープにしない
- インターネット接続を維持

---

### Q3: スタートアップを解除したい

**解除方法:**
1. `Win + R` → `shell:startup`
2. 「Discord Dev Bot」ショートカットを削除

---

### Q4: 複数のサーバーで使えますか？

**A:** はい、Botを招待したすべてのサーバーで使えます。

---

### Q5: Botが勝手に停止してしまう

**原因と解決方法:**

| 原因 | 解決方法 |
|------|----------|
| ネットワーク切断 | 自動再接続（設定済み） |
| Discordメンテナンス | 復旧後に自動再接続 |
| Windowsアップデート | PC再起動後に自動起動 |
| PCシャットダウン | 次回起動時に自動起動 |

---

## 📞 サポート

### ログの確認

問題が発生した場合、まず`logs\bot.log`を確認してください。

### 再インストール

```cmd
cd C:\Users\YourName\discord-dev-bot
install.bat
```

---

## 📄 ライセンス

このプロジェクトはMITライセンスです。

---

## 🎉 完成！

これで通勤中でも開発指示を出せる環境が完成しました！

**次のステップ:**
1. Discordで`!dev status`を試す
2. `!dev implement ミニマルな機能を追加`を試す
4. 実際のプロジェクトで活用

**Have fun coding! 🚀**
