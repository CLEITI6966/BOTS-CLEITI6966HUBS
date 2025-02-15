import discord
import requests
import json
import asyncio
import os
from discord.ext import commands

# Obter o token diretamente do arquivo token.env
with open("ia.env", "r") as file:
    TOKEN = file.read().strip()

# Verificar se o token foi carregado corretamente
if not TOKEN:
    raise ValueError("Token não encontrado no arquivo token.env!")

# Substitua com sua chave de API
api_key = "API-GEMINI-IA-AQUI"
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
headers = {'Content-Type': 'application/json'}

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Função para gerar uma resposta engraçada usando a API do Gemini
def generate_funny_response(text):
    data = {
        "contents": [{
            "parts": [{"text": f"responda desse jeito: com ironia e um tom meio mente poluída e passando dos limites nas mensagens usa esses emojis na mensagem 🤑🤤😫 a mensagem e ({text}) e deixe sem avisos tá"}]
        }]
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(data))
    
    if response.status_code == 200:
        response_data = response.json()
        if 'candidates' in response_data and response_data['candidates']:
            return response_data['candidates'][0]['content']['parts'][0]['text']
    
    return "Erro ao gerar resposta."

# Comando !start para iniciar o bot
@bot.command()
async def start(ctx):
    await ctx.send("Mencione eu para responder você! **BY CLEITI6966 HUBS**")

# Responde quando o bot é mencionado
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return  # Ignorar as mensagens do próprio bot

    if bot.user in message.mentions:
        async with message.channel.typing():
            response = generate_funny_response(message.content)
            await message.channel.send(response)

    await bot.process_commands(message)

# Iniciar o bot
if TOKEN:
    bot.run(TOKEN)
