import configparser
import os
from data_manager import DataManager
from typing import Optional, List

class ConfigManager:
    def __init__(self, config_path: str = 'config.cfg'):
        self.config_path = config_path
        self.config = configparser.ConfigParser()
        
        # 检查配置文件是否存在，不存在则创建默认配置
        if not os.path.exists(config_path):
            self.create_default_config()
        
        self.config.read(config_path, encoding='utf-8')
        
        # 数据管理器
        self.data_manager = DataManager()
    
    def create_default_config(self):
        """创建默认配置文件"""
        default_config = """[bot]
token=YOUR_BOT_TOKEN_HERE
description=Discord验证机器人
activity_type=playing
activity_name=验证管理

[database]
# 数据库文件路径
db_path=verification.db

[default_settings]
# 默认配置 - 可通过斜杠命令修改
review_channel_id=
verified_role_id=
admin_role_ids=
"""
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            f.write(default_config)
        
        print(f"✅ 已创建默认配置文件: {self.config_path}")
        print("⚠️  请编辑配置文件并填入你的机器人Token!")
    
    def get_bot_token(self) -> str:
        """获取机器人令牌"""
        token = self.config['bot']['token']
        if token == 'YOUR_BOT_TOKEN_HERE':
            print("❌ 请先在 config.cfg 文件中设置你的机器人Token!")
            print("💡 获取Token步骤:")
            print("   1. 访问 https://discord.com/developers/applications/")
            print("   2. 选择你的应用 > Bot > Token")
            print("   3. 复制Token并粘贴到 config.cfg 文件中")
            exit(1)
        return token
    
    def get_bot_description(self) -> str:
        """获取机器人描述"""
        return self.config['bot']['description']
    
    def get_activity_config(self) -> tuple:
        """获取活动配置"""
        activity_type = self.config['bot']['activity_type']
        activity_name = self.config['bot']['activity_name']
        return activity_type, activity_name
    
    def set_server_config(self, guild_id: int, **kwargs):
        """设置服务器配置"""
        return self.data_manager.update_server_config(guild_id, **kwargs)
    
    def get_server_config(self, guild_id: int) -> dict:
        """获取服务器配置"""
        return self.data_manager.get_server_config(guild_id)
    
    def get_review_channel_id(self, guild_id: int) -> Optional[int]:
        """获取审核频道ID"""
        return self.data_manager.get_review_channel_id(guild_id)
    
    def get_verified_role_id(self, guild_id: int) -> Optional[int]:
        """获取验证身份组ID"""
        return self.data_manager.get_verified_role_id(guild_id)
    
    def get_admin_role_ids(self, guild_id: int) -> List[int]:
        """获取管理员身份组ID列表"""
        return self.data_manager.get_admin_role_ids(guild_id)
    
    def is_admin(self, user_roles: List[int], guild_id: int) -> bool:
        """检查用户是否为管理员"""
        return self.data_manager.is_admin(user_roles, guild_id)
    
    def is_config_complete(self, guild_id: int) -> bool:
        """检查配置是否完整"""
        return self.data_manager.is_config_complete(guild_id)