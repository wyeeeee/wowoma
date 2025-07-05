import discord
from discord.ext import commands
import asyncio
from config_manager import ConfigManager
from verification_views import VerificationView
from logger import setup_logger, get_logger

# 初始化日志系统
logger = setup_logger()

# 初始化配置管理器
config_manager = ConfigManager()

# 设置机器人意图
intents = discord.Intents.default()
intents.guilds = True
intents.guild_messages = True
intents.members = True  # 需要成员意图来获取成员信息

# 创建机器人实例
bot = commands.Bot(command_prefix='/', description=config_manager.get_bot_description(), intents=intents)
bot.config_manager = config_manager

async def load_extensions():
    """加载扩展"""
    try:
        await bot.load_extension('commands')
        logger.info('已加载命令模块')
    except Exception as e:
        logger.error(f'加载命令模块失败: {e}')

@bot.event
async def on_ready():
    logger.info(f'机器人 {bot.user} 已连接到Discord!')
    
    try:
        # 设置机器人活动状态
        activity_type, activity_name = config_manager.get_activity_config()
        if activity_type.lower() == 'playing':
            activity = discord.Game(name=activity_name)
        elif activity_type.lower() == 'listening':
            activity = discord.Activity(type=discord.ActivityType.listening, name=activity_name)
        elif activity_type.lower() == 'watching':
            activity = discord.Activity(type=discord.ActivityType.watching, name=activity_name)
        else:
            activity = discord.Game(name=activity_name)
        
        await bot.change_presence(activity=activity)
        logger.info('活动状态已设置')
        
        # 添加持久化视图
        logger.info('正在加载验证视图...')
        try:
            view = VerificationView(config_manager, bot)
            bot.add_view(view)
            logger.info('验证视图已加载')
        except Exception as e:
            logger.error(f'验证视图加载失败: {e}')
            logger.warning('继续运行但无持久化视图')
        
    except Exception as e:
        logger.error(f'on_ready 执行出错: {e}')
    
    logger.info('机器人已就绪！')

async def setup_hook():
    """机器人启动前的设置"""
    await load_extensions()
    
    # 在这里同步命令，避免在 on_ready 中阻塞
    try:
        synced = await bot.tree.sync()
        logger.info(f'已同步 {len(synced)} 个斜杠命令')
        for command in synced:
            logger.info(f'  - /{command.name}')
    except Exception as e:
        logger.error(f'同步斜杠命令失败: {e}')
    
    logger.info('机器人设置完成')

async def main():
    """主函数"""
    async with bot:
        # 设置启动钩子
        bot.setup_hook = setup_hook
        await bot.start(config_manager.get_bot_token())

if __name__ == '__main__':
    asyncio.run(main())