"""
Discord Dev Bot - 常時起動型開発アシスタント
Windows起動時自動起動・タスクトレイ常駐型Bot
"""

import discord
from discord.ext import commands
import asyncio
import os
import subprocess
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime, timedelta
import json
from pathlib import Path
import sys
import traceback
import pystray
from PIL import Image, ImageDraw
import threading

# ログ設定
log_dir = Path(__file__).parent / "logs"
log_dir.mkdir(exist_ok=True)

logger = logging.getLogger('discord_bot')
logger.setLevel(logging.INFO)

# ログローテーション（7日分保持）
handler = RotatingFileHandler(
    log_dir / 'bot.log',
    maxBytes=5*1024*1024,  # 5MB
    backupCount=7,
    encoding='utf-8'
)
handler.setFormatter(logging.Formatter(
    '%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
))
logger.addHandler(handler)

# コンソール出力も追加（デバッグ用）
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
logger.addHandler(console_handler)

# 設定ファイル
CONFIG_FILE = Path(__file__).parent / "config.json"
PROJECT_DIR = Path("")  # Set in config.json

# デフォルト設定
DEFAULT_CONFIG = {
    "discord_token": "",
    "command_prefix": "!dev ",
    "project_dir": str(PROJECT_DIR),
    "auto_reconnect": True,
    "startup_delay": 30
}


class Config:
    """設定管理クラス"""
    
    @staticmethod
    def load():
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # デフォルト値とマージ
                return {**DEFAULT_CONFIG, **config}
        else:
            Config.save(DEFAULT_CONFIG)
            return DEFAULT_CONFIG.copy()
    
    @staticmethod
    def save(config):
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)


class DevBot(commands.Bot):
    """開発支援Discord Bot"""
    
    def __init__(self, config, tray_icon):
        intents = discord.Intents.default()
        intents.message_content = True
        
        super().__init__(
            command_prefix=config['command_prefix'],
            intents=intents
        )
        
        self.config = config
        self.tray_icon = tray_icon
        self.start_time = datetime.now()
        self.is_shutting_down = False
        
        # コマンド登録
        self.add_commands()
        
        logger.info("Bot初期化完了")
    
    def add_commands(self):
        """コマンド登録"""
        
        @self.command(name='implement')
        async def implement(ctx, *, content: str):
            """Claude Codeで実装を実行"""
            logger.info(f"implement コマンド実行: {content[:50]}...")
            
            await ctx.send("🤖 実装を開始します...")
            
            try:
                # プロジェクトディレクトリに移動
                os.chdir(self.config['project_dir'])
                
                # Claude Code実行
                result = await self.run_claude_code(content)
                
                # 結果が空またはNoneの場合の処理
                if not result:
                    result = "実行完了（出力なし）"
                
                # 結果通知
                embed = discord.Embed(
                    title="✅ 実装完了",
                    color=discord.Color.green(),
                    timestamp=datetime.now()
                )
                embed.add_field(name="コマンド", value=content[:1024], inline=False)
                embed.add_field(name="プロジェクト", value=self.config['project_dir'], inline=False)
                
                # 出力の長さに応じて処理を分岐
                if len(result) <= 4000:
                    # 4000文字以内ならDescriptionに収まる（Markdownとして表示）
                    embed.description = result
                    await ctx.send(embed=embed)
                    
                elif len(result) <= 10000:
                    # 10000文字以内なら分割してEmbed複数で送信
                    embed.description = result[:4000]
                    embed.add_field(
                        name="⚠️ 出力が長いため分割表示",
                        value=f"全体: {len(result)}文字",
                        inline=False
                    )
                    await ctx.send(embed=embed)
                    
                    # 残りを追加のメッセージで送信
                    remaining = result[4000:]
                    while remaining:
                        chunk = remaining[:2000]
                        remaining = remaining[2000:]
                        await ctx.send(chunk)
                        
                else:
                    # 10000文字以上ならファイルとして送信
                    embed.description = f"出力が非常に長いため、ファイルとして添付しました。\n\n**プレビュー（先頭500文字）:**\n{result[:500]}\n..."
                    embed.add_field(
                        name="📊 出力統計",
                        value=f"全体: {len(result)}文字 / {len(result.splitlines())}行",
                        inline=False
                    )
                    await ctx.send(embed=embed)
                    
                    # ファイルとして送信
                    import io
                    file_content = result.encode('utf-8')
                    file = discord.File(
                        io.BytesIO(file_content),
                        filename='claude_output.txt'
                    )
                    await ctx.send(file=file)
                
                logger.info(f"実装完了: 出力{len(result)}文字")
                
            except Exception as e:
                error_msg = f"エラー: {str(e)}"
                logger.error(f"実装エラー: {error_msg}\n{traceback.format_exc()}")
                
                embed = discord.Embed(
                    title="❌ エラー発生",
                    description=f"```\n{error_msg[:4000]}\n```",
                    color=discord.Color.red(),
                    timestamp=datetime.now()
                )
                await ctx.send(embed=embed)
        
        @self.command(name='status')
        async def status(ctx):
            """Bot稼働状況を表示"""
            logger.info("status コマンド実行")
            
            uptime = datetime.now() - self.start_time
            days = uptime.days
            hours, remainder = divmod(uptime.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            uptime_str = f"{days}日 {hours}時間 {minutes}分 {seconds}秒"
            
            embed = discord.Embed(
                title="🤖 Bot ステータス",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            embed.add_field(name="状態", value="✅ 稼働中", inline=True)
            embed.add_field(name="稼働時間", value=uptime_str, inline=True)
            embed.add_field(name="プロジェクト", value=self.config['project_dir'], inline=False)
            embed.add_field(name="起動時刻", value=self.start_time.strftime('%Y-%m-%d %H:%M:%S'), inline=True)
            embed.add_field(name="Ping", value=f"{round(self.latency * 1000)}ms", inline=True)
            
            await ctx.send(embed=embed)
        
        @self.command(name='stop')
        async def stop_bot(ctx):
            """Botを安全に停止"""
            logger.info("stop コマンド実行")
            
            embed = discord.Embed(
                title="🛑 Bot停止",
                description="Botを停止します。\n次回PC起動時に自動的に再開されます。",
                color=discord.Color.orange(),
                timestamp=datetime.now()
            )
            await ctx.send(embed=embed)
            
            self.is_shutting_down = True
            await asyncio.sleep(1)
            await self.close()
            
            # トレイアイコンも終了
            if self.tray_icon:
                self.tray_icon.stop()
        
        @self.command(name='restart')
        async def restart_bot(ctx):
            """Botを再起動"""
            logger.info("restart コマンド実行")
            
            await ctx.send("🔄 Botを再起動します...")
            
            self.is_shutting_down = True
            await asyncio.sleep(1)
            
            # 再起動スクリプト実行
            script_path = Path(__file__).parent / "start_bot.vbs"
            subprocess.Popen(['wscript', str(script_path)], shell=True)
            
            await self.close()
            if self.tray_icon:
                self.tray_icon.stop()
        
        @self.command(name='diagnose')
        async def diagnose(ctx):
            """Claude環境の診断"""
            logger.info("diagnose コマンド実行")
            
            embed = discord.Embed(
                title="🔍 Claude環境診断",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            
            # claudeコマンドの検索
            try:
                claude_path = self._find_claude_command()
                embed.add_field(name="✅ Claude検出", value=f"`{claude_path}`", inline=False)
            except Exception as e:
                embed.add_field(name="❌ Claude検出失敗", value=str(e), inline=False)
            
            # npm\claudeファイルの確認（拡張子ごと）
            npm_path = os.path.join(os.environ.get('APPDATA', ''), 'npm')
            if os.path.exists(npm_path):
                extensions = ['.cmd', '.bat', '.exe', '']
                found_files = []
                for ext in extensions:
                    file_path = os.path.join(npm_path, f'claude{ext}')
                    if os.path.exists(file_path):
                        found_files.append(f"✅ `claude{ext}`")
                    else:
                        found_files.append(f"❌ `claude{ext}`")
                
                embed.add_field(
                    name="npm内のclaudeファイル",
                    value='\n'.join(found_files),
                    inline=False
                )
            
            # claudeバージョン確認（フルパス使用）
            try:
                claude_path = self._find_claude_command()
                result = subprocess.run(
                    [claude_path, '--version'],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    shell=True  # .cmdファイル実行にshellが必要
                )
                version = result.stdout.strip() if result.returncode == 0 else f"エラー: {result.stderr}"
                embed.add_field(name="Claude Version", value=version or "取得失敗", inline=False)
            except Exception as e:
                embed.add_field(name="❌ Version確認失敗", value=str(e), inline=False)
            
            # PATH確認（npmパスが含まれているか）
            path_env = os.environ.get('PATH', '')
            npm_in_path = npm_path in path_env
            embed.add_field(
                name="npmパスがPATHに含まれているか",
                value="✅ はい" if npm_in_path else f"❌ いいえ\nnpmパス: `{npm_path}`",
                inline=False
            )
            
            # PATH確認（最初の5つ）
            paths = path_env.split(os.pathsep)[:5]
            path_str = '\n'.join([f"`{p}`" for p in paths])
            embed.add_field(name="PATH (先頭5件)", value=path_str or "なし", inline=False)
            
            # プロジェクトディレクトリ
            embed.add_field(name="プロジェクト", value=f"`{self.config['project_dir']}`", inline=False)
            
            await ctx.send(embed=embed)

        @self.command(name='test')
    async def run_claude_code(self, content: str) -> str:
        """Claude Codeを実行（非インタラクティブモード）"""
        try:
            # 非インタラクティブモード（-pフラグ）で実行
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                self._run_claude_headless,
                content
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Claude Code実行エラー: {e}")
            raise
    
    def _run_claude_headless(self, content: str) -> str:
        """Claude Codeを非インタラクティブモードで同期実行（内部用）"""
        try:
            # claudeコマンドのフルパスを検索
            claude_cmd = self._find_claude_command()
            
            command = [
                claude_cmd,
                '-p',  # 非インタラクティブモード（--print）
                '--dangerously-skip-permissions',  # 全権限をスキップ（自動化用）
                '--output-format', 'text',  # テキスト形式で出力
                content
            ]
            
            logger.info(f"Claude Code実行: {' '.join(command)}")
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding='utf-8',  # UTF-8エンコーディングを明示
                errors='replace',  # デコードエラーを置換文字で処理
                timeout=300,  # 5分タイムアウト
                cwd=self.config['project_dir'],
                shell=True  # Windowsの.cmdファイル実行にはshellが必要
            )
            
            output = result.stdout if result.stdout else ""
            if result.stderr:
                output += f"\n\nエラー出力:\n{result.stderr}"
            
            # 出力が空の場合の処理
            if not output or output.strip() == "":
                output = "Claude Codeの実行は完了しましたが、出力がありませんでした。"
            
            # 実行結果をログに記録
            logger.info(f"Claude Code終了コード: {result.returncode}")
            logger.info(f"出力の長さ: {len(output)} 文字")
            
            return output
            
        except subprocess.TimeoutExpired:
            raise Exception("Claude Code実行がタイムアウトしました（5分超過）")
        except FileNotFoundError as e:
            # 詳細なエラーメッセージ
            raise Exception(
                f"claudeコマンドが見つかりません: {e}\n"
                "以下を確認してください:\n"
                "1. Claude Codeがインストールされているか: npm install -g @anthropic-ai/claude-code\n"
                "2. コマンドプロンプトで 'claude --version' が動作するか\n"
                "3. npm global binがPATHに含まれているか: npm config get prefix"
            )
        except UnicodeDecodeError as e:
            raise Exception(f"文字コードエラー: {e}\nUTF-8でデコードできない文字が含まれています")
        except Exception as e:
            raise Exception(f"Claude実行エラー: {e}")
    
    def _find_claude_command(self) -> str:
        """claudeコマンドのフルパスを検索"""
        # Windows実行可能ファイルの拡張子（優先順位順）
        # .cmdが最優先（npmのグローバルコマンドの標準）
        extensions = ['.cmd', '.bat', '.exe', '']
        
        # 候補パスのリスト
        candidates = []
        
        # 1. whereコマンドで検索（Windows）
        try:
            result = subprocess.run(
                ['where', 'claude'],
                capture_output=True,
                text=True,
                timeout=5,
                shell=True  # whereコマンドはshellが必要
            )
            if result.returncode == 0 and result.stdout.strip():
                where_paths = result.stdout.strip().split('\n')
                # .cmdファイルを優先的に選択
                for ext in extensions:
                    for where_path in where_paths:
                        where_path = where_path.strip()
                        if where_path.endswith(ext) and os.path.exists(where_path):
                            candidates.append(where_path)
                            logger.info(f"whereコマンドで検出: {where_path}")
                            break  # 見つかったら次の拡張子へ
                    if candidates:
                        break  # 既に見つかっていたら終了
        except Exception as e:
            logger.warning(f"whereコマンド失敗: {e}")
        
        # 2. npm global binのパス（よくある場所）
        npm_paths = [
            os.path.join(os.environ.get('APPDATA', ''), 'npm'),
            os.path.join(os.environ.get('PROGRAMFILES', ''), 'nodejs'),
            os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), 'nodejs'),
        ]
        
        for npm_path in npm_paths:
            if not npm_path or not os.path.exists(npm_path):
                continue
            
            # 各拡張子を優先順位順に試す
            for ext in extensions:
                claude_path = os.path.join(npm_path, f'claude{ext}')
                if os.path.exists(claude_path):
                    # 既に見つかっていない場合のみ追加
                    if claude_path not in candidates:
                        candidates.append(claude_path)
                        logger.info(f"npm pathで検出: {claude_path}")
                    break  # 見つかったら次のnpm_pathへ
        
        # 3. ユーザーディレクトリ
        username = os.environ.get('USERNAME', '')
        if username:
            user_npm = rf'C:\Users\{username}\AppData\Roaming\npm'
            if os.path.exists(user_npm):
                for ext in extensions:
                    claude_path = os.path.join(user_npm, f'claude{ext}')
                    if os.path.exists(claude_path):
                        if claude_path not in candidates:
                            candidates.append(claude_path)
                            logger.info(f"ユーザーnpmで検出: {claude_path}")
                        break  # 見つかったら終了
        
        # 最初に見つかったものを使用（.cmd優先なので安全）
        if candidates:
            selected = candidates[0]
            logger.info(f"使用するClaudeコマンド: {selected}")
            return selected
        
        # 見つからない場合は'claude.cmd'を試す
        logger.warning("claudeコマンドのフルパスが見つかりません。claude.cmdで試行")
        return 'claude.cmd'

    async def on_ready(self):
        """Bot起動完了時"""
        logger.info(f'Botログイン完了: {self.user.name}')
        logger.info(f'接続サーバー数: {len(self.guilds)}')
        
        # アクティビティ設定
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="開発プロジェクト"
            )
        )
        
        # トレイアイコン更新
        if self.tray_icon:
            self.tray_icon.title = f"Discord Dev Bot - 稼働中\n{self.user.name}"
    
    async def on_command_error(self, ctx, error):
        """コマンドエラーハンドリング"""
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("❌ 不明なコマンドです。`!dev status`で確認してください。")
        else:
            logger.error(f"コマンドエラー: {error}\n{traceback.format_exc()}")
            await ctx.send(f"❌ エラーが発生しました: {str(error)}")


def create_tray_image():
    """トレイアイコン用画像作成"""
    # 簡単なロボットアイコンを生成
    width = 64
    height = 64
    image = Image.new('RGB', (width, height), color='black')
    draw = ImageDraw.Draw(image)
    
    # ロボット顔
    draw.ellipse([10, 10, 54, 54], fill='#5865F2')  # Discord カラー
    draw.ellipse([20, 20, 28, 28], fill='white')  # 左目
    draw.ellipse([36, 20, 44, 28], fill='white')  # 右目
    draw.rectangle([24, 38, 40, 42], fill='white')  # 口
    
    return image


def create_tray_icon(bot_loop, bot_instance):
    """タスクトレイアイコン作成"""
    
    def on_status(icon, item):
        """ステータス確認"""
        logger.info("トレイ: ステータス確認")
        # ブラウザでログファイルを開く
        log_file = log_dir / 'bot.log'
        if log_file.exists():
            os.startfile(log_file)
    
    def on_restart(icon, item):
        """再起動"""
        logger.info("トレイ: 再起動")
        asyncio.run_coroutine_threadsafe(
            bot_instance.close(),
            bot_loop
        )
        icon.stop()
        
        # 再起動
        script_path = Path(__file__).parent / "start_bot.vbs"
        subprocess.Popen(['wscript', str(script_path)], shell=True)
    
    def on_quit(icon, item):
        """終了"""
        logger.info("トレイ: 終了")
        asyncio.run_coroutine_threadsafe(
            bot_instance.close(),
            bot_loop
        )
        icon.stop()
    
    # メニュー作成
    menu = pystray.Menu(
        pystray.MenuItem("ステータス確認", on_status),
        pystray.MenuItem("ログ表示", on_status),
        pystray.MenuItem("再起動", on_restart),
        pystray.MenuItem("終了", on_quit)
    )
    
    # アイコン作成
    icon = pystray.Icon(
        "discord_dev_bot",
        create_tray_image(),
        "Discord Dev Bot - 起動中",
        menu
    )
    
    return icon


async def main():
    """メイン処理"""
    logger.info("=" * 50)
    logger.info("Discord Dev Bot 起動開始")
    logger.info(f"Python: {sys.version}")
    logger.info(f"作業ディレクトリ: {Path.cwd()}")
    logger.info("=" * 50)
    
    # 設定読み込み
    config = Config.load()
    
    if not config['discord_token']:
        logger.error("Discord Tokenが設定されていません！")
        logger.error(f"config.jsonに設定してください: {CONFIG_FILE}")
        input("Enterキーで終了...")
        return
    
    # Bot作成（トレイアイコンは後で設定）
    bot = DevBot(config, None)
    
    # トレイアイコン作成（別スレッド）
    loop = asyncio.get_event_loop()
    tray_icon = create_tray_icon(loop, bot)
    bot.tray_icon = tray_icon
    
    # トレイアイコン起動（別スレッド）
    tray_thread = threading.Thread(target=tray_icon.run, daemon=True)
    tray_thread.start()
    
    # 起動遅延（他サービス待機）
    if config.get('startup_delay', 0) > 0:
        logger.info(f"{config['startup_delay']}秒待機中...")
        await asyncio.sleep(config['startup_delay'])
    
    # Bot起動（自動再接続付き）
    retry_count = 0
    max_retries = 5
    
    while retry_count < max_retries:
        try:
            logger.info("Bot接続開始...")
            await bot.start(config['discord_token'])
            break  # 正常終了
            
        except discord.LoginFailure:
            logger.error("ログイン失敗: Discord Tokenが無効です")
            break
            
        except Exception as e:
            retry_count += 1
            logger.error(f"接続エラー ({retry_count}/{max_retries}): {e}")
            
            if retry_count < max_retries and config.get('auto_reconnect', True):
                wait_time = min(60, 10 * retry_count)  # 最大60秒
                logger.info(f"{wait_time}秒後に再接続...")
                await asyncio.sleep(wait_time)
            else:
                logger.error("再接続を諦めました")
                break
    
    # 終了処理
    logger.info("Bot終了")
    if tray_icon:
        tray_icon.stop()


if __name__ == "__main__":
    try:
        # Windows用イベントループポリシー設定
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
        asyncio.run(main())
        
    except KeyboardInterrupt:
        logger.info("キーボード割り込みで終了")
    except Exception as e:
        logger.error(f"予期しないエラー: {e}\n{traceback.format_exc()}")
        input("Enterキーで終了...")
