import discord
from datetime import datetime
from typing import Optional
from logger import get_logger

logger = get_logger('views')

class VerificationView(discord.ui.View):
    def __init__(self, config_manager, bot):
        super().__init__(timeout=None)
        self.config_manager = config_manager
        self.bot = bot
        # 延迟初始化，避免在启动时阻塞
    
    @discord.ui.button(label='申请验证', style=discord.ButtonStyle.primary, emoji='✅', custom_id='verification:apply')
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # 检查用户是否已经有验证角色
        verified_role_id = self.config_manager.get_verified_role_id(interaction.guild.id)
        if verified_role_id:
            verified_role = interaction.guild.get_role(verified_role_id)
            if verified_role and verified_role in interaction.user.roles:
                await interaction.response.send_message('你已经通过验证了！', ephemeral=True)
                return
        
        # 显示申请表单
        modal = VerificationModal(self.config_manager, self.bot)
        await interaction.response.send_modal(modal)

class VerificationModal(discord.ui.Modal):
    def __init__(self, config_manager, bot):
        super().__init__(title='验证申请')
        self.config_manager = config_manager
        self.bot = bot
        
        self.reason = discord.ui.TextInput(
            label='请说明你想加入的原因',
            placeholder='请详细描述你想加入这个服务器的原因...',
            style=discord.TextStyle.paragraph,
            max_length=1000,
            required=True
        )
        self.add_item(self.reason)
    
    async def on_submit(self, interaction: discord.Interaction):
        # 发送到审核频道
        review_channel_id = self.config_manager.get_review_channel_id(interaction.guild.id)
        if not review_channel_id:
            await interaction.response.send_message('管理员尚未设置审核频道，请联系管理员！', ephemeral=True)
            return
        
        review_channel = self.bot.get_channel(review_channel_id)
        if not review_channel:
            await interaction.response.send_message('审核频道不存在，请联系管理员！', ephemeral=True)
            return
        
        # 创建审核卡片
        embed = discord.Embed(
            title='🔍 新的验证申请',
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        embed.add_field(name='申请者', value=f'{interaction.user.mention}\n`{interaction.user} (ID: {interaction.user.id})`', inline=False)
        embed.add_field(name='申请原因', value=self.reason.value, inline=False)
        embed.add_field(name='账号信息', value=f'创建时间: {interaction.user.created_at.strftime("%Y-%m-%d %H:%M:%S")}\n加入时间: {interaction.user.joined_at.strftime("%Y-%m-%d %H:%M:%S")}', inline=False)
        
        # 创建审核按钮
        view = ReviewView(self.config_manager, self.bot, interaction.user.id)
        await review_channel.send(embed=embed, view=view)
        
        logger.info(f"新申请: 用户 {interaction.user} 提交验证申请")
        
        await interaction.response.send_message('✅ 你的申请已提交，请耐心等待管理员审核！', ephemeral=True)

class ReviewView(discord.ui.View):
    def __init__(self, config_manager, bot, user_id: int):
        super().__init__(timeout=None)  # 无超时，持久化
        self.config_manager = config_manager
        self.bot = bot
        self.user_id = user_id
    
    @discord.ui.button(label='通过', style=discord.ButtonStyle.success, emoji='✅')
    async def approve_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.check_permissions(interaction):
            await interaction.response.send_message('❌ 你没有权限执行此操作！', ephemeral=True)
            return
        
        # 获取用户和角色
        guild = interaction.guild
        logger.info(f"审核通过: 尝试获取用户 {self.user_id}")
        
        # 首先尝试从服务器成员中获取
        user = guild.get_member(self.user_id)
        
        if not user:
            # 尝试刷新服务器成员缓存
            try:
                user = await guild.fetch_member(self.user_id)
                logger.info(f"通过API获取到用户: {user}")
            except discord.NotFound:
                logger.warning(f"用户 {self.user_id} 已离开服务器")
                await interaction.response.send_message(f'❌ 用户 <@{self.user_id}> 已离开服务器！', ephemeral=True)
                return
            except Exception as e:
                logger.error(f"获取用户失败: {e}")
                await interaction.response.send_message(f'❌ 无法获取用户信息 (ID: {self.user_id})！', ephemeral=True)
                return
        
        verified_role_id = self.config_manager.get_verified_role_id(guild.id)
        if not verified_role_id:
            await interaction.response.send_message('❌ 管理员尚未设置验证身份组！', ephemeral=True)
            return
        
        verified_role = guild.get_role(verified_role_id)
        if not verified_role:
            await interaction.response.send_message('❌ 验证身份组不存在！', ephemeral=True)
            return
        
        # 分配角色
        try:
            await user.add_roles(verified_role)
            logger.info(f"成功为用户 {user} 分配身份组 {verified_role.name}")
            
            # 发送私信通知
            try:
                embed = discord.Embed(
                    title='🎉 验证通过！',
                    description=f'恭喜！你在 **{guild.name}** 的验证申请已通过！',
                    color=discord.Color.green(),
                    timestamp=datetime.now()
                )
                embed.add_field(name='获得身份组', value=verified_role.name, inline=False)
                await user.send(embed=embed)
                logger.info(f"已向用户 {user} 发送通过通知私信")
            except discord.Forbidden:
                logger.warning(f"无法向用户 {user} 发送私信，可能关闭了私信功能")
            
            # 更新审核消息
            embed = discord.Embed(
                title='✅ 验证申请已通过',
                description=f'申请者: {user.mention}',
                color=discord.Color.green(),
                timestamp=datetime.now()
            )
            embed.add_field(name='审核者', value=interaction.user.mention, inline=True)
            embed.add_field(name='分配身份组', value=verified_role.name, inline=True)
            
            self.clear_items()
            await interaction.response.edit_message(embed=embed, view=self)
            
        except discord.Forbidden:
            logger.error(f"机器人没有权限分配身份组 {verified_role.name}")
            await interaction.response.send_message('❌ 机器人没有权限分配该身份组！', ephemeral=True)
    
    @discord.ui.button(label='拒绝', style=discord.ButtonStyle.danger, emoji='❌')
    async def reject_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.check_permissions(interaction):
            await interaction.response.send_message('❌ 你没有权限执行此操作！', ephemeral=True)
            return
        
        # 直接拒绝，不发送私信
        guild = interaction.guild
        user = guild.get_member(self.user_id)
        
        logger.info(f"审核拒绝: 用户 {self.user_id} 的申请被 {interaction.user} 拒绝")
        
        # 更新审核消息
        embed = discord.Embed(
            title='❌ 验证申请已拒绝',
            description=f'申请者: {user.mention if user else f"<@{self.user_id}>"}',
            color=discord.Color.red(),
            timestamp=datetime.now()
        )
        embed.add_field(name='审核者', value=interaction.user.mention, inline=True)
        
        await interaction.response.edit_message(embed=embed, view=None)
    
    def check_permissions(self, interaction):
        """检查权限"""
        user_roles = [role.id for role in interaction.user.roles]
        return self.config_manager.is_admin(user_roles, interaction.guild.id)

