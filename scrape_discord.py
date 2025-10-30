import discord
from dotenv import load_dotenv
import os

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.messages = True

client = discord.Client(intents=intents)

load_dotenv() 
bot_token = os.getenv("DISCORD_BOT_TOKEN")

YOUR_USER_ID = 790279314410045500  # Replace with your actual Discord user ID

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')
    with open("data/my_messages.txt", "w", encoding="utf-8") as f:
        for guild in client.guilds:
            for channel in guild.text_channels:
                try:
                    async for message in channel.history(limit=None):
                        if message.author.id == YOUR_USER_ID:
                            f.write(f"{message.created_at} -/-/- {message.content}\n")
                except Exception as e:
                    print(f"Could not read {channel.name}: {e}")
    await client.close()

client.run(bot_token);