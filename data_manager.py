import json
import os
from typing import Optional, Dict, Any
from datetime import datetime

class DataManager:
    def __init__(self, data_file: str = 'server_data.json'):
        self.data_file = data_file
        self.data = self.load_data()
    
    def load_data(self) -> Dict[str, Any]:
        """加载数据文件"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return {}
        return {}
    
    def save_data(self) -> bool:
        """保存数据到文件"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存数据失败: {e}")
            return False
    
    def get_server_config(self, guild_id: int) -> Dict[str, Any]:
        """获取服务器配置"""
        guild_key = str(guild_id)
        return self.data.get(guild_key, {})
    
    def set_server_config(self, guild_id: int, config: Dict[str, Any]) -> bool:
        """设置服务器配置"""
        guild_key = str(guild_id)
        if guild_key not in self.data:
            self.data[guild_key] = {}
        
        self.data[guild_key].update(config)
        self.data[guild_key]['updated_at'] = datetime.now().isoformat()
        
        return self.save_data()
    
    def update_server_config(self, guild_id: int, **kwargs) -> bool:
        """更新服务器配置"""
        config = self.get_server_config(guild_id)
        for key, value in kwargs.items():
            if key in ['review_channel_id', 'verified_role_id', 'admin_role_ids']:
                config[key] = value
        
        return self.set_server_config(guild_id, config)
    
    def get_review_channel_id(self, guild_id: int) -> Optional[int]:
        """获取审核频道ID"""
        config = self.get_server_config(guild_id)
        channel_id = config.get('review_channel_id')
        return int(channel_id) if channel_id else None
    
    def get_verified_role_id(self, guild_id: int) -> Optional[int]:
        """获取验证身份组ID"""
        config = self.get_server_config(guild_id)
        role_id = config.get('verified_role_id')
        return int(role_id) if role_id else None
    
    def get_admin_role_ids(self, guild_id: int) -> list:
        """获取管理员身份组ID列表"""
        config = self.get_server_config(guild_id)
        admin_ids = config.get('admin_role_ids', [])
        if isinstance(admin_ids, str):
            # 兼容旧格式
            return [int(id.strip()) for id in admin_ids.split(',') if id.strip()]
        elif isinstance(admin_ids, list):
            return [int(id) for id in admin_ids if id]
        return []
    
    def is_admin(self, user_roles: list, guild_id: int) -> bool:
        """检查用户是否为管理员"""
        admin_role_ids = self.get_admin_role_ids(guild_id)
        if not admin_role_ids:
            return False
        return any(role_id in admin_role_ids for role_id in user_roles)
    
    def is_config_complete(self, guild_id: int) -> bool:
        """检查配置是否完整"""
        config = self.get_server_config(guild_id)
        return all([
            config.get('review_channel_id'),
            config.get('verified_role_id'),
            config.get('admin_role_ids')
        ])
    
    def delete_server_config(self, guild_id: int) -> bool:
        """删除服务器配置"""
        guild_key = str(guild_id)
        if guild_key in self.data:
            del self.data[guild_key]
            return self.save_data()
        return True