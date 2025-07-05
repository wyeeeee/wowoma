import discord
from discord.ext import commands
from discord import app_commands
from verification_views import VerificationView

class VerificationCommands(commands.Cog):
    def __init__(self, bot, config_manager):
        self.bot = bot
        self.config_manager = config_manager
    
    @app_commands.command(name="验证面板", description="创建验证面板")
    async def verification_panel(self, interaction: discord.Interaction):
        """创建验证面板"""
        user_roles = [role.id for role in interaction.user.roles]
        if not self.config_manager.is_admin(user_roles, interaction.guild.id):
            await interaction.response.send_message('❌ 你没有权限使用此命令！', ephemeral=True)
            return
        
        # 检查配置是否完整
        if not self.config_manager.is_config_complete(interaction.guild.id):
            await interaction.response.send_message('❌ 请先使用 `/设置` 命令完成配置！', ephemeral=True)
            return
        
        embed = discord.Embed(
            title='🔐 身份验证',
            description='欢迎来到我们的服务器！\n\n点击下方按钮申请验证，管理员将会审核你的申请。',
            color=discord.Color.blue()
        )
        embed.add_field(
            name='📝 注意事项', 
            value='• 请如实填写申请原因\n• 申请后请耐心等待审核\n• 重复申请可能会被拒绝\n• 通过验证后将获得相应身份组', 
            inline=False
        )
        
        view = VerificationView(self.config_manager, self.bot)
        await interaction.response.send_message(embed=embed, view=view)
    
    @app_commands.command(name="设置", description="设置验证系统配置")
    @app_commands.describe(
        审核频道="选择审核频道",
        验证身份组="选择验证身份组",
        管理员身份组="选择管理员身份组（可选）"
    )
    async def setup_verification(
        self, 
        interaction: discord.Interaction,
        审核频道: discord.TextChannel,
        验证身份组: discord.Role,
        管理员身份组: discord.Role = None
    ):
        """一键设置验证系统"""
        # 检查权限
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message('❌ 只有服务器管理员才能设置验证系统！', ephemeral=True)
            return
        
        # 检查机器人是否有权限分配身份组
        if 验证身份组.position >= interaction.guild.me.top_role.position:
            await interaction.response.send_message('❌ 机器人没有权限分配该身份组！请确保机器人的身份组位置高于要分配的身份组。', ephemeral=True)
            return
        
        # 准备配置数据
        config_data = {
            'review_channel_id': 审核频道.id,
            'verified_role_id': 验证身份组.id
        }
        
        # 设置管理员身份组
        if 管理员身份组:
            config_data['admin_role_ids'] = [管理员身份组.id]
        else:
            # 如果没有指定管理员身份组，使用默认配置
            existing_admin_ids = self.config_manager.get_admin_role_ids(interaction.guild.id)
            if existing_admin_ids:
                config_data['admin_role_ids'] = existing_admin_ids
            else:
                config_data['admin_role_ids'] = []
        
        # 保存配置
        success = self.config_manager.set_server_config(interaction.guild.id, **config_data)
        
        if success:
            embed = discord.Embed(
                title='✅ 设置成功',
                description='验证系统配置已完成！',
                color=discord.Color.green()
            )
            embed.add_field(name='📋 审核频道', value=审核频道.mention, inline=False)
            embed.add_field(name='🎖️ 验证身份组', value=验证身份组.mention, inline=False)
            if 管理员身份组:
                embed.add_field(name='👑 管理员身份组', value=管理员身份组.mention, inline=False)
            embed.add_field(name='📝 下一步', value='使用 `/验证面板` 命令创建验证面板', inline=False)
            
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message('❌ 保存配置失败！请稍后重试。', ephemeral=True)
    
    @app_commands.command(name="配置", description="查看或修改当前服务器的验证配置")
    async def view_config(self, interaction: discord.Interaction):
        """查看配置"""
        user_roles = [role.id for role in interaction.user.roles]
        if not self.config_manager.is_admin(user_roles, interaction.guild.id) and not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message('❌ 你没有权限使用此命令！', ephemeral=True)
            return
        
        config = self.config_manager.get_server_config(interaction.guild.id)
        
        embed = discord.Embed(
            title='⚙️ 服务器验证配置',
            color=discord.Color.blue()
        )
        
        # 审核频道
        review_channel_id = config.get('review_channel_id')
        if review_channel_id:
            review_channel = interaction.guild.get_channel(review_channel_id)
            embed.add_field(
                name='📋 审核频道',
                value=review_channel.mention if review_channel else f'频道不存在 (ID: {review_channel_id})',
                inline=False
            )
        else:
            embed.add_field(name='📋 审核频道', value='未设置', inline=False)
        
        # 验证身份组
        verified_role_id = config.get('verified_role_id')
        if verified_role_id:
            verified_role = interaction.guild.get_role(verified_role_id)
            embed.add_field(
                name='🎖️ 验证身份组',
                value=verified_role.mention if verified_role else f'身份组不存在 (ID: {verified_role_id})',
                inline=False
            )
        else:
            embed.add_field(name='🎖️ 验证身份组', value='未设置', inline=False)
        
        # 管理员身份组
        admin_role_ids = self.config_manager.get_admin_role_ids(interaction.guild.id)
        if admin_role_ids:
            admin_roles = []
            for role_id in admin_role_ids:
                role = interaction.guild.get_role(role_id)
                if role:
                    admin_roles.append(role.mention)
                else:
                    admin_roles.append(f'身份组不存在 (ID: {role_id})')
            embed.add_field(
                name='👑 管理员身份组',
                value='\n'.join(admin_roles) if admin_roles else '无',
                inline=False
            )
        else:
            embed.add_field(name='👑 管理员身份组', value='未设置', inline=False)
        
        # 配置状态
        is_complete = self.config_manager.is_config_complete(interaction.guild.id)
        status = "✅ 已完成" if is_complete else "⚠️ 未完成"
        embed.add_field(name='📊 配置状态', value=status, inline=False)
        
        if not is_complete:
            embed.add_field(
                name='💡 配置提示',
                value='请使用 `/设置` 命令完成配置\n格式：`/设置 审核频道:#channel 验证身份组:@role`',
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)
    
    @commands.command(name='sync')
    @commands.is_owner()
    async def sync_commands(self, ctx):
        """强制同步斜杠命令（仅限机器人所有者）"""
        try:
            synced = await ctx.bot.tree.sync()
            await ctx.send(f'✅ 已强制同步 {len(synced)} 个斜杠命令')
            for command in synced:
                print(f'   - /{command.name}')
        except Exception as e:
            await ctx.send(f'❌ 同步失败: {e}')

async def setup(bot):
    config_manager = getattr(bot, 'config_manager', None)
    if config_manager:
        await bot.add_cog(VerificationCommands(bot, config_manager))