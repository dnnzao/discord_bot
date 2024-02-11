import discord
from discord.ext import commands
import openai
from cryptography.fernet import Fernet
import os

# Define intents for the bot
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

# Load the encryption key from an environment variable
encryption_key = os.environ.get('DISCORD_BOT_ENCRYPTION_KEY')
if encryption_key is None:
    raise ValueError("Environment variable 'DISCORD_BOT_ENCRYPTION_KEY' not found")
encryption_key = encryption_key.encode()

# Initialize Fernet with the encryption key
cipher_suite = Fernet(encryption_key)

# Decrypt the API keys from the new location
with open('encrypted_keys.txt', 'rb') as file:
    encrypted_keys = file.readlines()
    discord_bot_token = cipher_suite.decrypt(encrypted_keys[0].strip()).decode()
    openai_api_key = cipher_suite.decrypt(encrypted_keys[1].strip()).decode()

# Initialize the OpenAI client with the decrypted API key
openai.api_key = openai_api_key

# Initialize the Discord bot with intents
bot = commands.Bot(command_prefix=commands.when_mentioned, intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.event
async def on_message(message):
    # Check if the bot is mentioned and the message is not from the bot itself
    if bot.user.mentioned_in(message) and message.author != bot.user:
        # Your logic to process the message goes here
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": "You are a helpful assistant."},
                          {"role": "user", "content": message.content}],
            )
            # Extracting the text from the response
            answer = response.choices[0].message['content'].strip()
            
            # Sending the response back to the Discord channel
            await message.channel.send(answer)
        except Exception as e:
            await message.channel.send('Sorry, I encountered an error. Please try again later.')
            print(e)

    # Important: process commands if you have any other commands to handle
    await bot.process_commands(message)

# Run the bot with the decrypted Discord bot token
bot.run(discord_bot_token)
