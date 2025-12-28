import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import time
import os
from dotenv import load_dotenv
load_dotenv()
from modulos import Pomo
import funcs

intents = discord.Intents.all()
intents.members = True
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix='.', intents=intents)

# -=- função de verificação de tarefas -=-
async def verify_upd_embed_pomo():
    while True:
        for user, info in Pomo.all_pomodoros.items():

            # faz a troca de bloco automaticamente
            user_id = Pomo.verify_time_pomodoro(usr=user, inf=info)

            # manda mensagem no pv
            if user_id:
                usuario = bot.get_user(user_id)
                if usuario:
                    if info['pomodoro'] == Pomo.estado['descanso']:
                        await usuario.send(
                            f'<@{user_id}> BLOCO DE **ESTUDO TERMINADO!!** descanse por 5 minutos...',
                            delete_after=180
                            )
                    elif info['pomodoro'] == Pomo.estado['estudo']:
                        await usuario.send(
                            f'<@{user_id}> BLOCO DE **DESCANSO TERMINADO!!** vamos voltar aos estudos...',
                            delete_after=180
                            )

            # atualiza a embed
            if info['pomodoro'] != Pomo.estado['desligado']:
                if 'embed_upd_timer' not in info:
                    info['embed_upd_timer'] = 0

                if time.time() - info['embed_upd_timer'] >= 30:

                    canal_id = info.get('canal')
                    msg_id = info.get('msg')
                    canal = bot.get_channel(canal_id)

                    if canal_id is None or msg_id is None or canal is None:
                        continue

                    try:
                        msg = await canal.fetch_message(msg_id)
                    except discord.NotFound:
                        continue

                    if Pomo.all_pomodoros[user]['pomodoro'] == True:
                        bloco_act_pomo = 'estudo'
                    elif Pomo.all_pomodoros[user]['pomodoro'] == None:
                        bloco_act_pomo = 'descanso'
                    else: continue
                    tempo = Pomo.tempo(user)

                    await msg.edit(
                        embed=funcs.embed_pomodoro(bloco_act_pomo, tempo)
                    )

                    info['embed_upd_timer'] = time.time()

        await asyncio.sleep(1)


# START
@bot.event
async def on_ready():
    bot.loop.create_task(verify_upd_embed_pomo())
    await bot.tree.sync()
    print('sudo@discord:~$ echo o sudo está online')

# TRATAMENTO DE ERRO (para prefixo)
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


# -=-=- COMANDOS SLASH -=-=-

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

    Pomo.start(user_id, canal_id)

    # converte os valores binários do bloco para a palavra certa
    if Pomo.all_pomodoros[user_id]['pomodoro'] == True:
        bloco_act_pomo = 'estudo'
    elif Pomo.all_pomodoros[user_id]['pomodoro'] == None:
        bloco_act_pomo = 'descanso'

    tempo = Pomo.tempo(user_id)

    await interaction.response.send_message(
        embed=funcs.embed_pomodoro(bloco_act_pomo, tempo)
        )
    
    msg = await interaction.original_response()
    Pomo.all_pomodoros[user_id]['msg'] = msg.id


@pomodoro.command(name='stop', description='encerra o pomodoro')
async def pomodoro_stop(interaction: discord.Interaction):
    user_id =interaction.user.id
    pomo = Pomo.stop(user_id)
    if pomo == False:
        await interaction.response.send_message(
            'Pomodoro **não está ativo**, use o comando de **start** primeiro',
            ephemeral=True
            )
    else:
        await interaction.response.send_message(
            'Pomodoro **desligado**',
            ephemeral=True
            )


# -=-=- COMANDOS DE PREFIXO -=-=-

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

# -=- limpar chat -=-
@bot.command()
async def clear(ctx, quantidade: int = 100):
    if ctx.author.id == os.getenv("TH_ID") or ctx.author.guild_permissions.manage_messages:
        if quantidade > 100:
            await ctx.send(
                f'{ctx.author.id} o bot não limpa mais do que 100 mensagens por vez. ',
                delete_after=6
                )
        
        await ctx.channel.purge(limit = quantidade + 1)
    else:
        await ctx.send(
            f'<@{ctx.author.id}> você não tem permissão para usar esse comando',
            delete_after=6
            )


# -=- TOKEN DO BOT -=-
token = os.getenv("BOT_TOKEN")
bot.run(token)
