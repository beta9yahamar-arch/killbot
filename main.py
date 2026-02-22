import discord
from discord.ext import commands
import asyncio
from flask import Flask
import threading
import os

# --- Flask setup ---
app = Flask("")

@app.route("/")
def home():
    return "Bot is running!"

def run_flask():
    # Render uses the PORT environment variable
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

# --- Discord Bot Setup ---
# Use os.getenv to keep your token secret!
TOKEN = "MTQ3NDk1NjUyMDExNzYzMzEwNQ.Gw0m5i.do095yE8W1zq3HSrtwvdis2i1ye5qi05t_qhEw"

ALLOWED_CHANNEL_ID = 1474580043081711686
ALLOWED_ROLE_ID = 1474953542673367084

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

class CancelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=10) # Timeout after 10s
        self.cancelled = False

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.cancelled = True
        await interaction.response.send_message("❌ Closing canceled!", ephemeral=True)
        self.stop()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}!")

@bot.command()
async def exit(ctx):
    if ctx.channel.id != ALLOWED_CHANNEL_ID:
        return await ctx.send("❌ You cannot use this command here.")

    if not any(role.id == ALLOWED_ROLE_ID for role in ctx.author.roles):
        return await ctx.send("❌ You do not have permission.")

    view = CancelView()
    message = await ctx.send(f"⚠️ Channel will be deleted in 5 seconds...", view=view)

    for i in range(4, -1, -1):
        await asyncio.sleep(1)
        if view.cancelled:
            await message.edit(content="❌ Deletion was cancelled.", view=None)
            return
        await message.edit(content=f"⚠️ Channel will be deleted in {i} seconds...", view=view)

    await ctx.send("💥 Deleting now...")
    await ctx.channel.delete()

# Start Flask in background
threading.Thread(target=run_flask, daemon=True).start()

# Start Bot
if TOKEN:
    bot.run(TOKEN)
else:
    print("ERROR: No DISCORD_TOKEN found in environment variables!")
