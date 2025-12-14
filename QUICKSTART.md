# クイックスタートガイド（上級者向け）

## 🚀 5分でセットアップ

### 前提条件
- Python 3.11+
- Discord Developer Portalでのアクセス
- Git, Claude Code インストール済み

### 手順

1. **リポジトリクローン（または解凍）**
   ```bash
   cd C:\Users\YourName
   git clone <repo> discord-dev-bot
   cd discord-dev-bot
   ```

2. **依存関係インストール**
   ```bash
   pip install -r requirements.txt
   ```

3. **設定ファイル作成**
   ```bash
   copy config.json.example config.json
   notepad config.json
   ```

   Discord Tokenを設定:
   ```json
   {
     "discord_token": "YOUR_TOKEN_HERE",
     "project_dir": "C:\\path\\to\\your\\project",
   }
   ```

4. **スタートアップ登録**
   ```bash
   # 方法1: install.bat実行（推奨）
   install.bat
   
   # 方法2: 手動登録
   # Win+R → shell:startup
   # start_bot.vbs のショートカットを作成
   ```

5. **起動テスト**
   ```bash
   # 手動起動でテスト
   python bot.py
   
   # または
   start_bot.vbs
   ```

6. **Discord確認**
   ```
   !dev status
   ```

---

## 🔧 カスタマイズ

### コマンド追加

`bot.py`の`add_commands()`メソッドに追加:

```python
@self.command(name='custom')
async def custom_command(ctx, *, args: str):
    """カスタムコマンド"""
    await ctx.send(f"実行: {args}")
```

### プロジェクト切り替え

複数プロジェクト対応:

```python
@self.command(name='project')
async def switch_project(ctx, project_name: str):
    """プロジェクト切り替え"""
    projects = {
        'racing': 'C:\\Users\\YourName\\project-a',
        'rpg': 'C:\\Users\\YourName\\project-b'
    }

    if project_name in projects:
        self.config['project_dir'] = projects[project_name]
        os.chdir(projects[project_name])
        await ctx.send(f"✅ プロジェクト切り替え: {project_name}")
```

---

## 🐛 デバッグ---

## 🐛 デバッグ

### 詳細ログ有効化

`bot.py`の`logger.setLevel()`を変更:

```python
logger.setLevel(logging.DEBUG)
```

### コンソール表示

`start_bot.vbs`の代わりに直接実行:

```bash
python bot.py
```

### リモートデバッグ

VS Code launch.json:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Discord Bot",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/bot.py",
      "console": "integratedTerminal"
    }
  ]
}
```

---

## 🔐 セキュリティベストプラクティス

1. **環境変数でToken管理**
   ```python
   import os
   token = os.getenv('DISCORD_BOT_TOKEN')
   ```

2. **権限最小化**
   - Botに必要最小限の権限のみ付与

3. **コマンド認証**
   ```python
   ALLOWED_USERS = [123456789012345678]
   
   if ctx.author.id not in ALLOWED_USERS:
       await ctx.send("❌ 権限がありません")
       return
   ```

---

## 📊 監視・メトリクス

### Prometheus連携

```python
from prometheus_client import start_http_server, Counter

command_counter = Counter('bot_commands_total', 'Total commands executed')

@self.command(name='implement')
async def implement(ctx, *, content: str):
    command_counter.inc()
    # ... 処理
```

### Uptimeモニター

```python
import uptime

@self.command(name='uptime')
async def uptime_cmd(ctx):
    system_uptime = uptime.uptime()
    await ctx.send(f"システム稼働時間: {system_uptime}秒")
```

---

## 🚀 パフォーマンス最適化

### 非同期処理

```python
import asyncio

async def heavy_task(data):
    # 重い処理
    await asyncio.sleep(1)
    return result

@self.command(name='batch')
async def batch_process(ctx):
    tasks = [heavy_task(d) for d in data_list]
    results = await asyncio.gather(*tasks)
    await ctx.send(f"完了: {len(results)}件")
```

### キャッシュ

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_operation(param):
    # キャッシュされる
    return result
```

---

## 🔄 CI/CD連携

### GitHub Actions

`.github/workflows/bot-update.yml`:

```yaml
name: Update Bot

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Restart bot
        run: |
          # Bot再起動スクリプト
          wscript start_bot.vbs
```

---

## 📱 モバイル通知

### Pushover連携

```python
import http.client

def send_notification(message):
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
        urllib.parse.urlencode({
            "token": "YOUR_APP_TOKEN",
            "user": "YOUR_USER_KEY",
            "message": message,
        }), {"Content-type": "application/x-www-form-urlencoded"})
```

---

## 🎯 次のステップ

2. **Webhook連携** - GitHub/GitLab Webhookで自動デプロイ

3. **データベース** - SQLite/PostgreSQLで履歴管理

4. **Web UI** - Flask/FastAPIで管理画面

5. **クラスタリング** - 複数Botインスタンスの負荷分散

6. **AI連携** - Claude API直接統合

---

## 📚 参考資料

- [discord.py Documentation](https://discordpy.readthedocs.io/)
- [Claude Code Documentation](https://docs.claude.com/)
- [Python asyncio](https://docs.python.org/3/library/asyncio.html)
