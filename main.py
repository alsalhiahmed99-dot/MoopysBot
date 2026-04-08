import discord
from discord.ext import commands
import json
import os
import random
from dotenv import load_dotenv

# 1. الإعدادات الأساسية
load_dotenv()
token = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)
bot.remove_command('help') # حذف الهيلب القديم

ECONOMY_FILE = "credits.json"

def load_credits():
    try:
        with open(ECONOMY_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_credits(data):
    with open(ECONOMY_FILE, "w") as f:
        json.dump(data, f, indent=4)

# --- 🚀 الأيفنتات ---

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="with Moopy | !help"))
    print(f'✅ {bot.user.name} is online!')

@bot.event
async def on_message(message):
    if message.author.bot: return
    await bot.process_commands(message)

# --- 📜 أمر المساعدة الاحترافي ---

@bot.command()
async def help(ctx):
    embed = discord.Embed(title="🤖 Moopys Bot Help", color=discord.Color.gold())
    embed.add_field(name="💰 Economy", value="`!credits`, `!daily`, `!transfer`", inline=False)
    embed.add_field(name="🎮 Games", value="`!coinflip`, `!slots`", inline=False)
    embed.add_field(name="🛠️ Admin", value="`!clear`, `!ac (Owner)`")
    embed.set_footer(text="Developed by Ahmad 👑")
    await ctx.send(embed=embed)

# --- 👑 أمر المالك (Owner Only) ---

@bot.command()
async def ac(ctx, member: discord.Member, amount: int):
    if ctx.author.id == ctx.guild.owner_id:
        data = load_credits()
        user_id = str(member.id)
        data[user_id] = data.get(user_id, 0) + amount
        save_credits(data)
        await ctx.send(f"👑 Added `{amount}` to **{member.name}**!")
    else:
        await ctx.send("❌ Owners only!")

# --- 💰 الاقتصاد (تم تعديل الـ Daily لـ 200) ---

@bot.command()
async def credits(ctx, member: discord.Member = None):
    member = member or ctx.author
    data = load_credits()
    await ctx.send(f"💰 **{member.name}**, your balance: `{data.get(str(member.id), 0)}`")

@bot.command()
@commands.cooldown(1, 86400, commands.BucketType.user)
async def daily(ctx):
    data = load_credits()
    user_id = str(ctx.author.id)
    reward = 200  # تم التعديل بطلب من Moopy
    data[user_id] = data.get(user_id, 0) + reward
    save_credits(data)
    await ctx.send(f"🎁 **{ctx.author.name}**, you claimed your daily `{reward}` credits!")

@bot.command()
async def transfer(ctx, member: discord.Member, amount: int):
    data = load_credits()
    if data.get(str(ctx.author.id), 0) < amount or amount <= 0:
        await ctx.send("❌ Invalid amount!")
        return
    data[str(ctx.author.id)] -= amount
    data[str(member.id)] = data.get(str(member.id), 0) + amount
    save_credits(data)
    await ctx.send(f"✅ Sent `{amount}` to **{member.name}**.")

# --- 🎮 الألعاب ---

@bot.command()
async def coinflip(ctx, choice: str, amount: int):
    data = load_credits()
    if data.get(str(ctx.author.id), 0) < amount or amount <= 0:
        await ctx.send("❌ No credits!")
        return
    result = random.choice(["heads", "tails"])
    if choice.lower() == result:
        data[str(ctx.author.id)] += amount
        await ctx.send(f"🎉 Winner! It was {result}.")
    else:
        data[str(ctx.author.id)] -= amount
        await ctx.send(f"💀 Lost! It was {result}.")
    save_credits(data)

@bot.command()
async def slots(ctx, amount: int):
    data = load_credits()
    if data.get(str(ctx.author.id), 0) < amount:
        await ctx.send("❌ No credits!")
        return
    items = ["🍎", "💎", "🍒"]
    s = [random.choice(items) for _ in range(3)]
    res = f"**[ {' | '.join(s)} ]**"
    if s[0] == s[1] == s[2]:
        data[str(ctx.author.id)] += amount * 10
        await ctx.send(f"{res} 🎯 JACKPOT!")
    elif s[0] == s[1] or s[1] == s[2] or s[0] == s[2]:
        data[str(ctx.author.id)] += amount * 2
        await ctx.send(f"{res} ✨ Win!")
    else:
        data[str(ctx.author.id)] -= amount
        await ctx.send(f"{res} 💀 Lost.")
    save_credits(data)

# --- 🛠️ الإدارة ---

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🧹 Deleted {amount} messages.", delete_after=3)

if token:
    bot.run(token)
