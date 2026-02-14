import os
import discord
from discord import app_commands
from dotenv import load_dotenv

# Get TOKEN
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

class Saladia(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()
        print(f"Commandes synchronisées !")

    async def on_ready(self):
        print(f'Connecté en tant que {self.user} (ID: {self.user.id})')

bot = Saladia()

# Command "/server-update"
@bot.tree.command(name="server-update", description="Demarrer la mise à jour du serveur")
@app_commands.describe(version="La version de destination (ex: 1.21.1)")
async def server_update(interaction: discord.Interaction, version: str):
    # On répond à l'utilisateur
    await interaction.response.send_message(f"Server will update to version {version}")

if TOKEN:
    bot.run(TOKEN)
else:
    print("Erreur : DISCORD_TOKEN non trouvé dans le fichier .env")