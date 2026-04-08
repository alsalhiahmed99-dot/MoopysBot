import discord
from discord.ext import commands
import json
import os
import random
from dotenv import load_dotenv

# 1. تحميل الإعدادات
load_dotenv()
token = os.getenv('DISCORD_TOKEN')

# 2. إعدادات الأذونات (Intents)
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

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

# --- 🚀 الأيفنتات المحمية (Protected Events) ---

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="with Moopy | !credits"))
    print(f'✅ {bot.user.name} is ONLINE. Make sure other instances are CLOSED!')

@bot.event
async def on_message(message):
    # 🛡️ السطر المنقذ: يمنع البوت من الرد على نفسه أو أي بوت آخر (يحل مشكلة التكرار)
    if message.author.bot:
        return

    # رد تلقائي بسيط
    if message.content.lower() in ["hi", "hello", "سلام"]:
        await message.channel.send(f"Hello {message.author.name}! 😊")

    # ضروري جداً لتشغيل الأوامر
    await bot.process_commands(message)

@bot.event
async def on_member_join(member):
    data = load_credits()
    user_id = str(member.id)
    data[user_id] = data.get(user_id, 0) + 50
    save_credits(data)
    channel = member.guild.system_channel
    if channel:
        await channel.send(f"Welcome {member.mention}! 🎉 You got `50` credits!")

# --- 👑 أمر المالك (Owner Only) ---

@bot.command()
async def ac(ctx, member: discord.Member, amount: int):
    if ctx.author.id == ctx.guild.owner_id:
        data = load_credits()
        user_id = str(member.id)
        data[user_id] = data.get(user_id, 0) + amount
        save_credits(data)
        await ctx.send(f"👑 **Success:** Added `{amount}` to **{member.name}**.")
    else:
        await ctx.send("❌ Only the Server Owner can use this!")

# --- 💰 الاقتصاد والألعاب (Economy & Games) ---

@bot.command()
async def credits(ctx, member: discord.Member = None):
    member = member or ctx.author
    data = load_credits()
    balance = data.get(str(member.id), 0)
    await ctx.send(f"💰 **{member.name}**, your balance: `{balance}`")

@bot.command()
@commands.cooldown(1, 86400, commands.BucketType.user)
async def daily(ctx):
    data = load_credits()
    user_id = str(ctx.author.id)
    data[user_id] = data.get(user_id, 0) + 100
    save_credits(data)
    await ctx.send(f"🎁 {ctx.author.name}, you got your daily `100` credits!")

@bot.command()
async def coinflip(ctx, choice: str, amount: int):
    data = load_credits()
    user_id = str(ctx.author.id)
    if data.get(user_id, 0) < amount or amount <= 0:
        await ctx.send("❌ Check your balance/amount!")
        return
    result = random.choice(["heads", "tails"])
    if choice.lower() == result:
        data[user_id] += amount
        await ctx.send(f"🎉 Winner! It was **{result}**.")
    else:
        data[user_id] -= amount
        await ctx.send(f"💀 Lost! It was **{result}**.")
    save_credits(data)

@bot.command()
async def slots(ctx, amount: int):
    data = load_credits()
    user_id = str(ctx.author.id)
    if data.get(user_id, 0) < amount or amount <= 0:
        await ctx.send("❌ Check your balance!")
        return
    items = ["🍎", "💎", "🍒"]
    s = [random.choice(items) for _ in range(3)]
    display = f"**[ {' | '.join(s)} ]**"
    if s[0] == s[1] == s[2]:
        data[user_id] += amount * 10
        await ctx.send(f"{display} 🎉 JACKPOT!")
    elif s[0] == s[1] or s[1] == s[2] or s[0] == s[2]:
        data[user_id] += amount * 2
        await ctx.send(f"{display} ✨ Win!")
    else:
        data[user_id] -= amount
        await ctx.send(f"{display} 💀 Lost!")
    save_credits(data)

# --- 🛠️ الإدارة (Admin) ---

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🧹 Cleared `{amount}` messages.", delete_after=3)

# 🏁 التشغيل
if token:
    bot.run(token)
