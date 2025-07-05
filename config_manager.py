import configparser
from data_manager import DataManager
from typing import Optional, List

class ConfigManager:
    def __init__(self, config_path: str = 'config.cfg'):
        self.config_path = config_path
        self.config = configparser.ConfigParser()
        self.config.read(config_path, encoding='utf-8')
        
        # 数据管理器
        self.data_manager = DataManager()
    
    def get_bot_token(self) -> str:
        """获取机器人令牌"""
        return self.config['bot']['token']
    
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