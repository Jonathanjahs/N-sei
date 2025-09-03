import discord
from discord import app_commands
from discord.ext import commands
import os

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        
    @discord.ui.button(label="Abrir Ticket", style=discord.ButtonStyle.green, custom_id="ticket_button")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        support_role = discord.utils.get(interaction.guild.roles, name="ADM") 
        if not support_role:
            await interaction.response.send_message("Cargo 'ADM' não encontrado. Crie um e tente novamente.", ephemeral=True)
            return

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            support_role: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }

        channel = await interaction.guild.create_text_channel(
            f"ticket-{interaction.user.name}",
            overwrites=overwrites
        )

        await channel.send(
            "Você criou um ticket, espere o suporte chegar.",
            view=CloseTicketView()
        )
        
        await interaction.response.send_message("Seu ticket foi criado!", ephemeral=True)


class CloseTicketView(discord.ui.View):
    @discord.ui.button(label="Fechar Ticket", style=discord.ButtonStyle.red)
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.channel.delete()


intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")
    await bot.change_presence(activity=discord.Game(name="Aguardando /ticket"))
    try:
        synced = await bot.tree.sync()
        print(f"Sincronizei {len(synced)} comandos.")
    except Exception as e:
        print(e)
    bot.add_view(TicketView())


@bot.tree.command(name="ticket", description="Abre o painel de tickets.")
async def ticket_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Abrir Ticket",
        description="Aperte no botão abaixo para abrir um ticket de suporte."
    )
    await interaction.response.send_message(embed=embed, view=TicketView())


if __name__ == "__main__":
    bot.run(os.getenv("TOKEN"))