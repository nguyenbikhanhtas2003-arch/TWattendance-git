import discord
from discord.ext import commands
from discord.ui import View
from collections import defaultdict
import logging
from dotenv import load_dotenv
import os

# Load token từ .env
load_dotenv()
token = os.getenv('DISCORD_TOKEN')

# Log
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Prefix chuẩn
bot = commands.Bot(command_prefix="!", intents=intents)

# ===== DATA =====
attendance = defaultdict(lambda: {"role": None, "status": "full"})


def format_user(user, status):
    return f"{user} ✅" if status == "full" else f"{user} ⏰"


def build_embed():
    heavy, light, medium = [], [], []

    for user, data in attendance.items():
        role = data["role"]
        status = data["status"]

        if role == "heavy":
            heavy.append(format_user(user, status))
        elif role == "light":
            light.append(format_user(user, status))
        elif role == "medium":
            medium.append(format_user(user, status))

    embed = discord.Embed(
        title="⚔️ TW Attendance",
        description="Chọn role + trạng thái tham gia",
        color=0x00ffcc
    )

    embed.add_field(name="🛡️ Giáp nặng", value="\n".join(heavy) or "Chưa có ai", inline=True)
    embed.add_field(name="⚔️ Giáp nhẹ", value="\n".join(light) or "Chưa có ai", inline=True)
    embed.add_field(name="🧙 Giáp trung", value="\n".join(medium) or "Chưa có ai", inline=True)

    embed.set_footer(text=f"Tổng: {len(attendance)} người")

    return embed


class TWView(View):
    def __init__(self):
        super().__init__(timeout=None)

    # ROLE
    @discord.ui.button(label="Giáp nặng", emoji="🛡️", style=discord.ButtonStyle.secondary)
    async def heavy(self, interaction: discord.Interaction, button: discord.ui.Button):
        attendance[str(interaction.user)]["role"] = "heavy"
        await interaction.response.edit_message(embed=build_embed(), view=self)

    @discord.ui.button(label="Giáp nhẹ", emoji="⚔️", style=discord.ButtonStyle.primary)
    async def light(self, interaction: discord.Interaction, button: discord.ui.Button):
        attendance[str(interaction.user)]["role"] = "light"
        await interaction.response.edit_message(embed=build_embed(), view=self)

    @discord.ui.button(label="Giáp trung", emoji="🧙", style=discord.ButtonStyle.success)
    async def medium(self, interaction: discord.Interaction, button: discord.ui.Button):
        attendance[str(interaction.user)]["role"] = "medium"
        await interaction.response.edit_message(embed=build_embed(), view=self)

    # STATUS
    @discord.ui.button(label="Đầy đủ", emoji="✅", style=discord.ButtonStyle.success, row=1)
    async def full(self, interaction: discord.Interaction, button: discord.ui.Button):
        attendance[str(interaction.user)]["status"] = "full"
        await interaction.response.edit_message(embed=build_embed(), view=self)

    @discord.ui.button(label="Trễ", emoji="⏰", style=discord.ButtonStyle.primary, row=1)
    async def late(self, interaction: discord.Interaction, button: discord.ui.Button):
        attendance[str(interaction.user)]["status"] = "late"
        await interaction.response.edit_message(embed=build_embed(), view=self)

    # CLEAR
    @discord.ui.button(label="Huỷ", style=discord.ButtonStyle.danger, row=1)
    async def clear(self, interaction: discord.Interaction, button: discord.ui.Button):
        attendance.pop(str(interaction.user), None)
        await interaction.response.edit_message(embed=build_embed(), view=self)


# Bot ready
@bot.event
async def on_ready():
    print(f"✅ Bot đã chạy: {bot.user}")


# Command tạo bảng
@bot.command()
async def tw(ctx):
    await ctx.send(embed=build_embed(), view=TWView())


# Run bot
bot.run(token, log_handler=handler, log_level=logging.DEBUG)