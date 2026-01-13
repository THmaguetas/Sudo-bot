import discord
from discord import app_commands
from discord.ext import commands
from discord.errors import NotFound, Forbidden, HTTPException
import asyncio
import time
from datetime import datetime
import os
from dotenv import load_dotenv
from modulos import embeds
from modulos import Pomo
from modulos import Agenda

load_dotenv()

intents = discord.Intents.all()
intents.members = True
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix='.', intents=intents)

# -=-=- TASKS -=-=-

# -=- função de verificação da agenda -=-
async def verify_agenda():
    while True:
        agenda_json = Agenda.load_agenda()

        for server_id, eventos in list(agenda_json.items()):

            for event, items in list(eventos.items()):

                if items['notificado'] == False and datetime.strptime(items['data_hora'], "%d/%m/%Y %H:%M") <= datetime.now():
                    canal_id = int(items['canal'])
                    canal = bot.get_channel(canal_id)
                    if canal is None:
                        continue

                    try:
                        await canal.send(
                            f"🔔 <@&{items['cargo']}> 🔔",
                            embed=embeds.embed_agenda(
                                title=items['tarefa'], 
                                desc=items['descricao'], 
                                cargo=items['cargo']) 
                        )
                        items['notificado'] = True
                    except NotFound and Forbidden and HTTPException:
                        continue

                    Agenda.save_agenda(agenda_json)

        await asyncio.sleep(60)


# -=- função de verificação do pomodoro -=-
async def verify_upd_embed_pomo():
    while True:
        for user_id, info in Pomo.all_pomodoros.items():

            # verifica troca de bloco
            changed_user = Pomo.verify_time_pomodoro(usr=user_id, inf=info)

            # notificação no pv do cabra
            if changed_user:
                discord_user = bot.get_user(changed_user)
                if discord_user:
                    if info['pomodoro'] == Pomo.estado['descanso']:
                        await discord_user.send(
                            f'<@{changed_user}> BLOCO DE **ESTUDO TERMINADO!!** descanse por 5 minutos...',
                            delete_after=180
                        )
                    elif info['pomodoro'] == Pomo.estado['estudo']:
                        await discord_user.send(
                            f'<@{changed_user}> BLOCO DE **DESCANSO TERMINADO!!** vamos voltar aos estudos...',
                            delete_after=180
                        )

            # atualização da embed
            if (info['pomodoro'] != Pomo.estado['desligado']) and (info.get('msg') != None) and (time.time() - info.get('embed_upd_timer', 0) > 30):

                # acha o canal 
                if info.get('is_dm'):
                    discord_user = bot.get_user(user_id)
                    if not discord_user:
                        continue
                    canal = await discord_user.create_dm()
                else:
                    canal = bot.get_channel(info['canal'])

                if (canal is None):
                    continue

                try:
                    msg = await canal.fetch_message(info['msg'])
                except discord.NotFound:
                    continue

                # traduz o bloco ativo
                if info['pomodoro'] == Pomo.estado['estudo']:
                    bloco_act_pomo = 'estudo'
                elif info['pomodoro'] == Pomo.estado['descanso']:
                    bloco_act_pomo = 'descanso'
                else:
                    continue

                tempo = Pomo.tempo(user_id)

                # envia a embed atualizada
                await msg.edit(
                    embed=embeds.embed_pomodoro(bloco_act_pomo, tempo)
                )

                info['embed_upd_timer'] = time.time()

        await asyncio.sleep(1)



# START
@bot.event
async def on_ready():
    Pomo.all_pomodoros.clear()
    bot.loop.create_task(verify_upd_embed_pomo())
    bot.loop.create_task(verify_agenda())
    await bot.tree.sync()
    print(f'[{datetime.now()}] sudo@discord:~$ echo o sudo está online')

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

# comando de start do pomodoro
@pomodoro.command(name='start', description='inicia o pomodoro')
@app_commands.describe(
    estudo='tempo do bloco de estudo', 
    descanso='tempo do bloco de descanso'
)
async def pomodoro_start(interaction: discord.Interaction, estudo: int=25, descanso: int=5):
    
        user_id = interaction.user.id

        if isinstance(interaction.channel, discord.DMChannel):
            canal = await interaction.user.create_dm()
            is_dm = True
        else:
            canal = interaction.channel
            is_dm = False

        Pomo.start(user_id, canal.id, is_dm, estudo, descanso)

        if Pomo.all_pomodoros[user_id]['msg'] is None:

            # converte os valores binários do bloco para a palavra certa
            if Pomo.all_pomodoros[user_id]['pomodoro'] == True:
                bloco_act_pomo = 'estudo'
            elif Pomo.all_pomodoros[user_id]['pomodoro'] == None:
                bloco_act_pomo = 'descanso'

            tempo = Pomo.tempo(user_id)

            # carrega a envia a embed no chat
            await interaction.response.send_message(
                embed=embeds.embed_pomodoro(bloco_act_pomo, tempo)
                )
            
            # pega o id da embed pra poder editar ela 
            msg = await interaction.original_response()
            Pomo.all_pomodoros[user_id]['msg'] = msg.id

        else:
            await interaction.response.send_message(
                'você já tem uma tabela pomodoro ativa',
                ephemeral=True,
                delete_after=5
                )


@pomodoro.command(name='stop', description='encerra o pomodoro')
async def pomodoro_stop(interaction: discord.Interaction):
    user_id =interaction.user.id
    pomo = Pomo.stop(user_id)
    if pomo == False:
        await interaction.response.send_message(
            'Pomodoro **não está ativo**, use o comando de **start** primeiro',
            ephemeral=True,
            delete_after=5
            )
    else:
        await interaction.response.send_message(
            'Pomodoro **desligado**',
            ephemeral=True
            )



# -=- AGENDA DE TAREFAS -=-
agenda = app_commands.Group(
    name='agenda',
    description='agendamento de tarefas'
)
bot.tree.add_command(agenda)

@agenda.command(name='add', description='adiciona um lembrete')
@app_commands.describe(
    cargo = 'mencionará o cargo escolhido',
    tarefa = 'tarefa escolhida para o lembrete',
    desc = 'descrição da tarefa',
    data = 'data que o lembrete irá tocar',
    hora = 'hora que o lembrete irá tocar'
)
async def agenda_add(interaction: discord.Interaction, cargo: discord.Role, tarefa: str, desc: str, data: str, hora: str):
    server_id = str(interaction.guild_id)
    cargo_id = cargo.id
    canal = interaction.channel.id

    data_hora = Agenda.valid_data(data=data, time=hora)

    if data_hora != False:
        # salva as infos da nova tarefa no json
        Agenda.add_task(server_id, cargo_id, tarefa, desc, data_hora, canal)
        await interaction.response.send_message(
            f'Tarefa agendada com socesso para o cargo <@&{cargo_id}>!!'
        )
    else:
        await interaction.response.send_message(
            '''Digite a data ou a hora da maneira correta. 
Siga os padrões BR: **dia/mês/ano**  e  **hora:minuto**.
E insira uma data futura.'''
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
            await ctx.send(f'{membro_pronto.mention}')

# -=- limpar chat -=-
@bot.command()
#@commands.cooldown(1, 5, commands.BucketType.channel)
async def clear(ctx, quantidade: int = 100):
    if ctx.author.id == int(os.getenv("TH_ID")) or ctx.author.guild_permissions.manage_messages:
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
token = os.getenv("SUDO_TOKEN")
bot.run(token)
