import os
import discord
from discord import app_commands
from discord.app_commands import checks
from dotenv import load_dotenv
import asyncio

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
    # Immediate response to acknowledge the interaction and prevent timeout
    await interaction.response.send_message(f"Update to version {version} initialized...")
    
    # Retrieve the original message object to allow subsequent edits
    message = await interaction.original_response()

    try:
        # Launch the bash script as an asynchronous subprocess
        # stderr is redirected to stdout to capture all output in one stream
        process = await asyncio.create_subprocess_exec(
            '/bin/bash', '/home/hoag/Documents/toto/minecraft/update-server.sh', version,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT
        )

        log_lines = []
        last_update_time = asyncio.get_event_loop().time()

        # Read the subprocess output line by line
        while True:
            line = await process.stdout.readline()
            if not line:
                break
                
            decoded_line = line.decode().strip()
            # print(f"[LOG]: {decoded_line}") 
            
            # Append the new line to our log list
            log_lines.append(f"> {decoded_line}")
            
            # Keep only the last 10 lines to stay within Discord's 2000 character limit
            display_text = "\n".join(log_lines[-10:])
            
            # Rate limiting: only edit the message every 1.5 seconds 
            # to avoid being rate-limited by Discord's API
            current_time = asyncio.get_event_loop().time()
            if current_time - last_update_time > 1.5:
                await message.edit(content=f"Update in progress for version {version}:\n```\n{display_text}\n```")
                last_update_time = current_time

        # Wait for the process to finish and get the return code
        await process.wait()
        

        if process.returncode == 0:
            final_status = (
                f"**SUCCESS**: Server update to **{version}** is complete.\n"
                f"```diff\n+ The server has been updated and restarted successfully.\n```"
            )
            await message.edit(content=final_status)
        else:
            error_status = (
                f"**FAILURE**: Update to **{version}** failed.\n"
                f"```diff\n- Process terminated with exit code: {process.returncode}\n"
                f"- Please check the system logs for more details.\n```"
            )
            await message.edit(content=error_status)

    except Exception as e:
        print(f"Error during execution: {e}")
        await message.edit(content=f"An unexpected error occurred: {e}")



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