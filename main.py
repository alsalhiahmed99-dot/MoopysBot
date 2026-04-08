import discord
from discord.ext import commands
import json
import os
import random
from dotenv import load_dotenv

# 1. تحميل الإعدادات والتوكن
load_dotenv()
token = os.getenv('DISCORD_TOKEN')

# 2. إعدادات البوت والأذونات (Intents)
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # ضروري عشان إيفنت الترحيب يشتغل
bot = commands.Bot(command_prefix='!', intents=intents)

# ملف حفظ البيانات
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

# --- 🚀 الأيفنتات التلقائية (Events) ---

@bot.event
async def on_ready():
    # تغيير حالة البوت عشان يبين احترافي
    await bot.change_presence(activity=discord.Game(name="with Moopy | !credits"))
    print(f'✅ {bot.user.name} is online and ready!')

@bot.event
async def on_member_join(member):
    # إيفنت الترحيب التلقائي وإعطاء هدية دخول
    data = load_credits()
    user_id = str(member.id)
    gift = 50
    data[user_id] = data.get(user_id, 0) + gift
    save_credits(data)
    
    channel = member.guild.system_channel
    if channel:
        await channel.send(f"Welcome {member.mention} to the server! 🎉 You've received `{gift}` starting credits!")

@bot.event
async def on_message(message):
    # منع البوت من الرد على نفسه (عشان ما يصير تكرار أو Spam)
    if message.author == bot.user:
        return

    # رد تلقائي ذكي
    if message.content.lower() in ["hi", "hello", "سلام"]:
        await message.channel.send(f"Hello {message.author.name}! How are you today? 😊")

    # ضروري جداً عشان الأوامر (!credits) تشتغل مع وجود الإيفنت
    await bot.process_commands(message)

# --- 💰 أوامر الاقتصاد (Commands) ---

@bot.command()
async def credits(ctx, member: discord.Member = None):
    member = member or ctx.author
    data = load_credits()
    user_id = str(member.id)
    balance = data.get(user_id, 0)
    await ctx.send(f"💰 **{member.name}**, your balance is: `{balance}` credits.")

@bot.command()
@commands.cooldown(1, 86400, commands.BucketType.user)
async def daily(ctx):
    data = load_credits()
    user_id = str(ctx.author.id)
    reward = 100
    data[user_id] = data.get(user_id, 0) + reward
    save_credits(data)
    await ctx.send(f"🎁 **{ctx.author.name}**, you claimed your daily `{reward}` credits!")

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

# --- 🎮 ألعاب التسلية ---

@bot.command()
async def coinflip(ctx, choice: str, amount: int):
    if amount <= 0:
        await ctx.send("❌ Minimum bet is 1 credit!")
        return

    data = load_credits()
    user_id = str(ctx.author.id)
    
    if data.get(user_id, 0) < amount:
        await ctx.send("❌ You don't have enough credits to bet!")
        return

    result = random.choice(["heads", "tails"])
    if choice.lower() == result:
        data[user_id] += amount
        msg = f"🎉 **Winner!** It was **{result}**. You won `{amount}` credits!"
    else:
        data[user_id] -= amount
        msg = f"💀 **Lost!** It was **{result}**. You lost `{amount}` credits."
    
    save_credits(data)
    await ctx.send(msg)

# تشغيل البوت
if token:
    bot.run(token)
else:
    print("❌ Error: No Token found!")
