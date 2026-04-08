import discord
from discord.ext import commands
import json
import os
import random
from dotenv import load_dotenv

# 1. تحميل التوكن من ملف .env أو إعدادات Railway
load_dotenv()
token = os.getenv('DISCORD_TOKEN')

# 2. إعدادات الأذونات (Intents)
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # ضروري عشان الترحيب وأمر الـ ac يشتغلوا صح
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
    await bot.change_presence(activity=discord.Game(name="with Moopy | !credits"))
    print(f'✅ {bot.user.name} is online and ready!')

@bot.event
async def on_member_join(member):
    # ترحيب تلقائي + هدية دخول
    data = load_credits()
    user_id = str(member.id)
    gift = 50
    data[user_id] = data.get(user_id, 0) + gift
    save_credits(data)
    
    channel = member.guild.system_channel
    if channel:
        await channel.send(f"Welcome {member.mention}! 🎉 You've received `{gift}` starting credits!")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # ردود تلقائية ذكية
    if message.content.lower() in ["hi", "hello", "سلام"]:
        await message.channel.send(f"Hello {message.author.name}! 😊")

    # ضروري جداً عشان الأوامر تشتغل
    await bot.process_commands(message)

# --- 👑 أمر المالك الحصري (Owner Only) ---

@bot.command()
async def ac(ctx, member: discord.Member, amount: int):
    # لا يمكن لأحد استخدامه إلا صاحب السيرفر فقط
    if ctx.author.id == ctx.guild.owner_id:
        data = load_credits()
        user_id = str(member.id)
        data[user_id] = data.get(user_id, 0) + amount
        save_credits(data)
        await ctx.send(f"👑 **Owner Action:** Added `{amount}` credits to **{member.name}**!")
    else:
        await ctx.send("❌ Only the **Server Owner** can use this command!")

# --- 💰 أوامر الاقتصاد (Economy) ---

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
    if amount <= 0: return
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

# --- 🎮 ألعاب التسلية (Games) ---

@bot.command()
async def coinflip(ctx, choice: str, amount: int):
    if amount <= 0: return
    data = load_credits()
    user_id = str(ctx.author.id)
    
    if data.get(user_id, 0) < amount:
        await ctx.send("❌ Not enough credits!")
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

@bot.command()
async def slots(ctx, amount: int):
    if amount <= 0: return
    data = load_credits()
    user_id = str(ctx.author.id)
    if data.get(user_id, 0) < amount:
        await ctx.send("❌ Not enough credits!")
        return

    items = ["🍎", "🍋", "💎", "🔔", "🍒"]
    s1, s2, s3 = random.choice(items), random.choice(items), random.choice(items)
    display = f"**[ {s1} | {s2} | {s3} ]**\n"
    
    if s1 == s2 == s3:
        win = amount * 10
        data[user_id] += win
        await ctx.send(f"{display} 🎉 JACKPOT! Won `{win}`!")
    elif s1 == s2 or s2 == s3 or s1 == s3:
        win = amount * 2
        data[user_id] += win
        await ctx.send(f"{display} ✨ Nice! Won `{win}`!")
    else:
        data[user_id] -= amount
        await ctx.send(f"{display} 💀 Better luck next time!")
    save_credits(data)

# --- 🛠️ أوامر الإدارة (Admin) ---

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🧹 Deleted `{amount}` messages!", delete_after=5)

# تشغيل البوت
if token:
    bot.run(token)
else:
    print("❌ Error: No DISCORD_TOKEN found!")
