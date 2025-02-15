import discord
import os
import aiohttp
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime

# Carregar variáveis do arquivo token.env
load_dotenv(dotenv_path='token.env')
TOKEN = os.getenv('DISCORD_TOKEN')
if not TOKEN:
    raise ValueError("Token não encontrado no arquivo token.env!")

# Configurar intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intenbotts.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Variáveis globais
salvar_midias = False
salvar_mensagens_apagadas = False
salvar_mensagens_editadas = False
salvar_midias_channel = None

# Criar pastas se não existirem
os.makedirs('./mensagens', exist_ok=True)
os.makedirs('./fotos', exist_ok=True)
os.makedirs('./mensagens-editadas', exist_ok=True)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Bot conectado como {bot.user}")

# Comando para ativar/desativar o salvamento de mídias
@bot.tree.command(name="salvar-midias")
async def salvar_midias_cmd(interaction: discord.Interaction):
    global salvar_midias, salvar_midias_channel
    salvar_midias = not salvar_midias
    salvar_midias_channel = interaction.channel
    status = "ativado" if salvar_midias else "desativado"
    await interaction.response.send_message(f"Salvamento de mídias {status}!")

# Evento para salvar mídias enviadas
@bot.event
async def on_message(message: discord.Message):
    if salvar_midias and message.attachments:
        for attachment in message.attachments:
            file_path = os.path.join('./fotos', attachment.filename)
            async with aiohttp.ClientSession() as session:
                async with session.get(attachment.url) as response:
                    if response.status == 200:
                        with open(file_path, 'wb') as f:
                            f.write(await response.read())

            await salvar_midias_channel.send(
                f"{message.author.mention} enviou uma foto e foi salva na pasta 'fotos'."
            )

# Comando para ativar/desativar o salvamento de mensagens apagadas
@bot.tree.command(name="salvar-mensagens-apagadas")
async def salvar_mensagens_apagadas_cmd(interaction: discord.Interaction):
    global salvar_mensagens_apagadas
    salvar_mensagens_apagadas = not salvar_mensagens_apagadas
    status = "ativado" if salvar_mensagens_apagadas else "desativado"
    await interaction.response.send_message(f"Salvamento de mensagens apagadas {status}!")

# Evento para salvar mensagens apagadas
@bot.event
async def on_message_delete(message: discord.Message):
    if message.author.bot:
        return  # Ignorar mensagens de bots
    
    if salvar_mensagens_apagadas:
        file_name = f"{message.id}.txt"
        file_path = os.path.join('./mensagens', file_name)
        
        try:
            # Se a mensagem tiver anexos (fotos ou outros arquivos)
            conteudo = message.content
            if message.attachments:
                # Se tiver anexos, adicionar o nome do arquivo ao conteúdo
                conteudo = ', '.join([attachment.filename for attachment in message.attachments])

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"Autor: {message.author.name}#{message.author.discriminator}\n")
                f.write(f"ID do Autor: {message.author.id}\n")
                f.write(f"Servidor: {message.guild.name if message.guild else 'DM'}\n")
                f.write(f"ID do Servidor: {message.guild.id if message.guild else 'DM'}\n")
                f.write(f"Canal: {message.channel.name}\n")
                f.write(f"ID do Canal: {message.channel.id}\n")
                f.write(f"Data de Exclusão: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Mensagem ID: {message.id}\n")
                f.write(f"Timestamp de Criação: {message.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Conteúdo: {conteudo}\n")
                f.write(f"Reações: {', '.join([str(reaction) for reaction in message.reactions])}\n")
                f.write(f"Mentions: {', '.join([user.name for user in message.mentions])}\n")
                f.write(f"Links: {', '.join([url for url in message.content.split() if url.startswith('http')])}\n")
                f.write(f"Menções a Cargos: {', '.join([role.name for role in message.role_mentions])}\n")
                f.write(f"Embed: {message.embeds[0] if message.embeds else 'Nenhum'}\n")
                f.write(f"Foi uma mensagem de bot? {'Sim' if message.author.bot else 'Não'}\n")
                f.write(f"Markdown: {'Sim' if any(char in message.content for char in ['*', '_', '~']) else 'Não'}\n")
                f.write(f"@everyone/@here mencionado? {'Sim' if '@everyone' in message.content or '@here' in message.content else 'Não'}\n")
                f.write(f"Emojis: {', '.join([str(emoji) for emoji in message.content if emoji in ['😊', '😂', '😢']])}\n")

            await message.channel.send(
                f"{message.author.mention} apagou uma mensagem. A mensagem foi salva na pasta 'mensagens'."
            )
        except Exception as e:
            print(f"Erro ao salvar mensagem apagada: {e}")

# Evento para salvar edições de mensagens
@bot.event
async def on_message_edit(before: discord.Message, after: discord.Message):
    if salvar_mensagens_editadas:
        file_name = f"edit_{before.id}.txt"
        file_path = os.path.join('./mensagens-editadas', file_name)
        
        edicao_numero = 1
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                edicao_numero = sum(1 for linha in f if linha.startswith("Edição #")) + 1

        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(f"\nEdição #{edicao_numero}\n")
            f.write(f"Autor: {before.author.name}#{before.author.discriminator}\n")
            f.write(f"ID do Autor: {before.author.id}\n")
            f.write(f"Servidor: {before.guild.name if before.guild else 'DM'}\n")
            f.write(f"ID do Servidor: {before.guild.id if before.guild else 'DM'}\n")
            f.write(f"Canal: {before.channel.name}\n")
            f.write(f"ID do Canal: {before.channel.id}\n")
            f.write(f"Data da Edição: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Mensagem ID: {before.id}\n")
            f.write(f"Timestamp de Criação: {before.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Conteúdo anterior: {before.content}\n")
            f.write(f"Conteúdo novo: {after.content}\n")
            f.write(f"Reações: {', '.join([str(reaction) for reaction in after.reactions])}\n")
            f.write(f"Mentions: {', '.join([user.name for user in after.mentions])}\n")
            f.write(f"Links: {', '.join([url for url in after.content.split() if url.startswith('http')])}\n")
            f.write(f"Menções a Cargos: {', '.join([role.name for role in after.role_mentions])}\n")
            f.write(f"Embed: {after.embeds[0] if after.embeds else 'Nenhum'}\n")
            f.write(f"Foi uma mensagem de bot? {'Sim' if after.author.bot else 'Não'}\n")
            f.write(f"Markdown: {'Sim' if any(char in after.content for char in ['*', '_', '~']) else 'Não'}\n")
            f.write(f"@everyone/@here mencionado? {'Sim' if '@everyone' in after.content or '@here' in after.content else 'Não'}\n")
            f.write(f"Emojis: {', '.join([str(emoji) for emoji in after.content if emoji in ['😊', '😂', '😢']])}\n")
            f.write("-" * 50 + "\n")

        await before.channel.send(
            f"{before.author.mention} editou uma mensagem. Esta é a edição número {edicao_numero}. As edições foram salvas na pasta 'mensagens-editadas'."
        )

bot.run(TOKEN)