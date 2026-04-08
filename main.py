import discord
from discord.ext import commands
import json
import os
import random
from dotenv import load_dotenv

# 1. تحميل التوكن من ملف .env المخفي
load_dotenv()
token = os.getenv('DISCORD_TOKEN')

# 2. إعدادات البوت والأذونات
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# ملف حفظ الرصيد (البيانات)
ECONOMY_FILE = "credits.json"

def load_credits():
    try:
        with open(ECONOMY_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_credits(data):
    with open(ECONOMY_FILE, "w") as f:
        json.dump(data, f)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} (Moopys Bot)')

# --- الأوامر (Commands) ---

# 1. Check Credits (!credits)
@bot.command()
async def credits(ctx, member: discord.Member = None):
    member = member or ctx.author
    data = load_credits()
    user_id = str(member.id)
    balance = data.get(user_id, 0)
    await ctx.send(f"💰 **{member.name}**, your balance is: `{balance}` credits.")

# 2. Transfer Credits (!transfer @user amount)
@bot.command()
async def transfer(ctx, member: discord.Member, amount: int):
    if amount <= 0:
        await ctx.send("❌ Amount must be positive!")
        return
    
    data = load_credits()
    sender_id = str(ctx.author.id)
    receiver_id = str(member.id)
    
    if data.get(sender_id, 0) < amount:
        await ctx.send("❌ You don't have enough credits!")
        return

    data[sender_id] -= amount
    data[receiver_id] = data.get(receiver_id, 0) + amount
    save_credits(data)
    await ctx.send(f"✅ Transferred `{amount}` credits to **{member.name}**.")

# 3. Game: Coinflip (!coinflip heads 50)
@bot.command()
async def coinflip(ctx, choice: str, amount: int):
    data = load_credits()
    user_id = str(ctx.author.id)
    
    if data.get(user_id, 0) < amount:
        await ctx.send("❌ Not enough credits to bet!")
        return

    result = random.choice(["heads", "tails"])
    if choice.lower() == result:
        data[user_id] += amount
        msg = f"🎉 You won! It was **{result}**. You got `{amount}` credits."
    else:
        data[user_id] -= amount
        msg = f"💀 You lost! It was **{result}**. You lost `{amount}` credits."
    
    save_credits(data)
    await ctx.send(msg)

# 4. Daily Reward (!daily)
@bot.command()
@commands.cooldown(1, 86400, commands.BucketType.user)
async def daily(ctx):
    data = load_credits()
    user_id = str(ctx.author.id)
    reward = 100
    data[user_id] = data.get(user_id, 0) + reward
    save_credits(data)
    await ctx.send(f"💰 **{ctx.author.name}**, you received your daily `{reward}` credits!")

# تشغيل البوت باستخدام التوكن المخفي
if token:
    bot.run(token)
else:
    print("❌ Error: DISCORD_TOKEN not found in .env file!")
