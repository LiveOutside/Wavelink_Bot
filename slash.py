from typing import Any
import discord
from discord import app_commands
from discord.flags import Intents
from info import TOKEN

class aclient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.synced = False

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync(guild=discord.Object(id=1057637826545590282))
            self.synced = True
        print(f"Successfuly logged as a {self.user}")


client = aclient()
tree = app_commands.CommandTree(client)


@tree.command(name="test", description="testing", guild=discord.Object(id=1057637826545590282))
async def self(interaction: discord.Interaction, name: str):
    await interaction.response.send_message(f"Hello {name}! You've just used a slash-type command")


client.run(TOKEN)