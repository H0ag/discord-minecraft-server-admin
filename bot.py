import os
import discord
from discord import app_commands
from discord.app_commands import checks
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
        print(f"Synced commands !")

    async def on_ready(self):
        print(f'Logged as {self.user} (ID: {self.user.id})')

bot = Saladia()

# Command "/server-update"
@bot.tree.command(name="server-update", description="Start server update")
@app_commands.describe(version="Wanted version (e.g.: 1.21.1)")
@checks.has_role("saladia-admin")
async def server_update(interaction: discord.Interaction, version: str):
    await interaction.response.send_message(f"Server will update to version {version}")



@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingRole):
        await interaction.response.send_message(
            f"You need **`saladia-admin'** role to execute this command.", 
            ephemeral=False
        )
    else:
        # Pour les autres types d'erreurs (bug code, etc.)
        print(f"Error: {error}")
        if not interaction.response.is_done():
            await interaction.response.send_message("Something happened.", ephemeral=False)

if TOKEN:
    bot.run(TOKEN)
else:
    print("Erreur : DISCORD_TOKEN not found in .env")