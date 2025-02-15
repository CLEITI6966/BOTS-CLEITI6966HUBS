import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio
from datetime import datetime

# Carrega as variáveis do arquivo .env
load_dotenv('spam.env')

# Lista de tokens dos bots
tokens = [
    os.getenv('TOKEN1'),
    os.getenv('TOKEN2'),
    os.getenv('TOKEN3'),
    os.getenv('TOKEN4'),
    os.getenv('TOKEN5'),
    os.getenv('TOKEN6'),
    os.getenv('TOKEN7')
]

# Função para ler o conteúdo de um arquivo .txt
def ler_arquivo(nome_arquivo):
    try:
        with open(nome_arquivo, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return None

# Função para salvar logs em um arquivo .txt
def salvar_logs(logs, nome_arquivo_logs):
    with open(nome_arquivo_logs, 'a', encoding='utf-8') as file:
        for log in logs:
            file.write(log + "\n")

# Função para criar e iniciar um bot
async def start_bot(token):
    intents = discord.Intents.default()
    intents.message_content = True

    bot = commands.Bot(command_prefix="!", intents=intents)

    # Variáveis de controle para spam e DM
    spam_active = False
    dm_active = False

    @bot.event
    async def on_ready():
        print(f'Bot {bot.user.name} está online!')

    @bot.command(name='hello')
    async def hello(ctx):
        await ctx.send(f'Olá, {ctx.author.name}! Eu sou o bot {bot.user.name}.')

    @bot.command(name='spam')
    async def spam(ctx, quantidade: int, delay: float, *, mensagem: str = None):
        nonlocal spam_active

        # Verifica se a mensagem é um arquivo .txt
        if mensagem and mensagem.endswith('.txt'):
            conteudo = ler_arquivo(mensagem)
            if conteudo is None:
                await ctx.send(f"Arquivo '{mensagem}' não encontrado.")
                return
            mensagem = conteudo

        spam_active = True
        logs = []  # Lista para armazenar logs

        for i in range(quantidade):
            if not spam_active:
                break  # Para o spam se a flag for desativada
            msg = await ctx.send(mensagem)
            # Registra informações no log
            logs.append(
                f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
                f"ID da Mensagem: {msg.id} | "
                f"Bot: {bot.user.name} ({bot.user.id}) | "
                f"Autor do Comando: {ctx.author.name} ({ctx.author.id}) | "
                f"Canal: {ctx.channel.name} | "
                f"Conteúdo: {mensagem}"
            )
            await asyncio.sleep(delay)

        # Salva os logs em um único arquivo de log
        nome_arquivo_logs = "logs_unificados.txt"
        salvar_logs(logs, nome_arquivo_logs)
        await ctx.send(f"Spam concluído! Logs salvos.", file=discord.File(nome_arquivo_logs))

    @bot.command(name='dm')
    async def dm(ctx, quantidade: int, delay: float, mensagem: str, usuario: discord.User):
        nonlocal dm_active

        # Verifica se a mensagem é um arquivo .txt
        if mensagem.endswith('.txt'):
            conteudo = ler_arquivo(mensagem)
            if conteudo is None:
                await ctx.send(f"Arquivo '{mensagem}' não encontrado.")
                return
            mensagem = conteudo

        dm_active = True
        logs = []  # Lista para armazenar logs

        for i in range(quantidade):
            if not dm_active:
                break  # Para o DM se a flag for desativada
            msg = await usuario.send(mensagem)  # Envia a mensagem na DM do usuário
            # Registra informações no log
            logs.append(
                f"Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
                f"ID da Mensagem: {msg.id} | "
                f"Bot: {bot.user.name} ({bot.user.id}) | "
                f"Autor do Comando: {ctx.author.name} ({ctx.author.id}) | "
                f"Usuário Alvo: {usuario.name} ({usuario.id}) | "
                f"Conteúdo: {mensagem}"
            )
            await asyncio.sleep(delay)

        # Salva os logs em um único arquivo de log
        nome_arquivo_logs = "logs_unificados.txt"
        salvar_logs(logs, nome_arquivo_logs)
        await ctx.send(f"DM concluído! Logs salvos.", file=discord.File(nome_arquivo_logs))

    @bot.command(name='stop')
    async def stop(ctx):
        nonlocal spam_active, dm_active
        spam_active = False
        dm_active = False
        await ctx.send("Todos os comandos (spam e DM) foram interrompidos com sucesso!")

    @bot.command(name='cmds')
    async def cmds(ctx):
        # Cria uma mensagem embed com instruções
        embed = discord.Embed(
            title="📜 Comandos do Bot",
            description="Aqui estão os comandos disponíveis e como usá-los:",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="!hello",
            value="Receba uma mensagem do bot.",
            inline=False
        )
        embed.add_field(
            name="!spam (quantidade) (delay) (mensagem ou arquivo.txt)",
            value="Envia uma mensagem repetidamente no canal.\nExemplo: `!spam 5 2 Olá, mundo!` ou `!spam 5 2 arquivo.txt`",
            inline=False
        )
        embed.add_field(
            name="!dm (quantidade) (delay) (mensagem ou arquivo.txt) (@usuário)",
            value="Envia mensagens diretas (DM) para um usuário mencionado.\nExemplo: `!dm 3 1 Olá! @usuário` ou `!dm 3 1 arquivo.txt @usuário`",
            inline=False
        )
        embed.add_field(
            name="!stop",
            value="Interrompe os comandos `!spam` e `!dm` em execução.",
            inline=False
        )
        embed.add_field(
            name="!cmds",
            value="Mostra esta mensagem de ajuda.",
            inline=False
        )
        embed.set_footer(text="Use os comandos com responsabilidade!")

        await ctx.send(embed=embed)

    await bot.start(token)

# Inicia todos os bots
async def main():
    tasks = [start_bot(token) for token in tokens]
    await asyncio.gather(*tasks)

# Executa o loop principal
asyncio.run(main())
