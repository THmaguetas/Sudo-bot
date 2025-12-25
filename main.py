import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv
load_dotenv()
from modulos import Pomo
import asyncio

intents = discord.Intents.all()
intents.members = True
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix='.', intents=intents)

# -=- função de verificação do pomodoro -=-
async def verify_full_time():
    while True:
        user_id = Pomo.verify_time_pomodoro()
        if user_id:
            info = Pomo.all_pomodoros[user_id]
            canal = bot.get_channel(info['canal_id'])
            if canal:
                estado_atual = info['pomodoro']
                if estado_atual == Pomo.estado['descanso']:
                    await canal.send(f"<@{user_id}> BLOCO DE **ESTUDO** TERMINADO!! descanse por 5 minutos...")
                elif estado_atual == Pomo.estado['estudo']:
                    await canal.send(f"<@{user_id}> BLOCO DE **DESCANSO** TERMINADO!! vamos voltar aos estudos...")
        await asyncio.sleep(1)


# start
@bot.event
async def on_ready():
    bot.loop.create_task(verify_full_time())
    await bot.tree.sync()
    print('sudo@discord:~$ echo o sudo está online')

# TRATAMENTO DE ERRO
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("comando incompleto")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("comando inexistente")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("sem permissão para usar esse comando")
    elif isinstance(error, commands.CommandInvokeError):
        await ctx.send("o Th errou na hora de codar esse comando")
        print(f"Erro interno: {error}")
    else:
        await ctx.send("não sei o que aconteceu, mas deu pau na máquina")
        print(f"Erro desconhecido: {error}")


# github
@bot.command()
async def github(ctx):
    await ctx.send('https://github.com/THmaguetas')

# spam mention 
@bot.command()
async def mention(ctx, membro: str):
    id_membro = int(membro.strip('<@!>'))
    membro_pronto = ctx.guild.get_member(id_membro)
    if membro_pronto:
        for _ in range(1, 41):
            await ctx.send(f'vamo acordar {membro_pronto.mention}')


# -=- POMODORO -=-
pomodoro = app_commands.Group(
    name="pomodoro",
    description="comandos do pomodoro"
)
bot.tree.add_command(pomodoro)


@pomodoro.command(name='start', description='inicia o pomodoro')
async def pomodoro_start(interaction: discord.Interaction):
    user_id =interaction.user.id
    canal_id = interaction.channel.id
    pomo = Pomo.start(user_id, canal_id)
    if pomo == True:
        await interaction.response.send_message('O pomodoro foi iniciado, bons estudos...')
    if pomo == False:
        await interaction.response.send_message('O pomodoro já está ativo')


@pomodoro.command(name='tempo', description='vê quando tempo do bloco falta')
async def pomodoro_tempo(interaction: discord.Interaction):
    user_id =interaction.user.id
    pomo = Pomo.tempo(user_id)
    if pomo == False:
        await interaction.response.send_message(f'O pomodoro não está ativo, use o comando de start primeiro')
    else:
        await interaction.response.send_message(f'{pomo} minutos para este bloco acabar')


@pomodoro.command(name='stop', description='encerra o pomodoro')
async def pomodoro_stop(interaction: discord.Interaction):
    user_id =interaction.user.id
    pomo = Pomo.stop(user_id)
    if pomo == False:
        await interaction.response.send_message(f'O pomodoro não está ativo, use o comando de start primeiro')
    else:
        await interaction.response.send_message('pomodoro desligado')



# -=- limpar chat -=-
@bot.command()
async def clear(ctx, quantidade: int = 100):
    if quantidade > 100:
        await ctx.send('o bot não limpa mais do que 100 mensagens por vez. ', delete_after=6)
        await ctx.send(' -para conseguir apagar as mensagens, digite o comando e especifique o número de mensagens que deve ser apagado.', delete_after=6)
        return
    await ctx.channel.purge(limit = quantidade + 1)

# -=- TOKEN DO BOT -=-
token = os.getenv("BOT_TOKEN")
bot.run(token)
