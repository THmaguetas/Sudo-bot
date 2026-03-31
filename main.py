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
from modulos import Rank

load_dotenv()

intents = discord.Intents.all()
intents.members = True
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix='.', intents=intents)

    ###########
    ## TASKS ##
    ###########

# função de verificação da agenda
async def verify_agenda():
    while True:
        agenda = Agenda.load_agenda()
        alterado = False

        for server_id, eventos in agenda.items():
            for event_id, items in eventos.items():

                if not items["notificado"]:
                    data_evento = datetime.strptime(
                        items["data_hora"], "%d/%m/%Y %H:%M"
                    )

                    if data_evento <= datetime.now():
                        canal = bot.get_channel(int(items["canal"]))
                        if canal is None:
                            continue

                        try:
                            await canal.send(
                                f"🔔 <@&{items['cargo']}> 🔔",
                                embed=embeds.embed_entrega_lembrete(
                                    title=items["tarefa"],
                                    cargo=items["cargo"]
                                )
                            )
                            items["notificado"] = True
                            alterado = True

                        except (NotFound, Forbidden, HTTPException):
                            continue

        if alterado:
            Agenda.save_agenda(agenda)

        await asyncio.sleep(60)


# função de verificação do pomodoro
async def verify_upd_embed_pomo():
    while True:
        for user_id, info in Pomo.all_pomodoros.items():
            if info['pomodoro'] != Pomo.estado['desligado']:
                # verifica troca de bloco
                changed_user = Pomo.verify_time_pomodoro(usr=user_id, inf=info)
                discord_user = bot.get_user(changed_user)

                if info['blocos'] <= 0:
                    await discord_user.send(
                        embed=embeds.embed_simples(texto='Seus blocos de estudo acabaram!! Parabéns!', cor=discord.Color.green()),
                        delete_after=360
                    )

                    try:
                        msg = await canal.fetch_message(info['msg'])
                    except discord.NotFound:
                        continue

                    # envia a embed final
                    await msg.edit(
                        embed=embeds.embed_pomodoro('desligado', 0, 0)
                        )

                    # desliga/reseta o pomodoro
                    Pomo.stop(user_id)
                    continue


                else:
                    # notificação no pv do cabra
                    if changed_user and discord_user:
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
                        blocos = Pomo.all_pomodoros[user_id]['blocos']

                        # envia a embed atualizada
                        await msg.edit(
                            embed=embeds.embed_pomodoro(bloco_act_pomo, tempo, blocos)
                        )

                        info['embed_upd_timer'] = time.time()

        await asyncio.sleep(1)


# -=-=- START -=-=-
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


    ####################
    ## COMANDOS SLASH ##
    ####################

####################
## STUDY COMMANDS ##
####################

#######################
# CRONÔMETRO POMODORO #
#######################
cronômetro = app_commands.Group(
    name="cronômetro",
    description="comandos do pomodoro"
)
bot.tree.add_command(cronômetro)

# comando de start do pomodoro
@cronômetro.command(name='start', description='inicia o cronômetro')
@app_commands.describe(
    blocos='quantidade de blocos de estudo',
    estudo='tempo do bloco de estudo', 
    descanso='tempo do bloco de descanso'
)
async def cronometro_start(interaction: discord.Interaction, blocos: int, estudo: int=25, descanso: int=5):
        server_id = interaction.guild_id
        user_id = interaction.user.id

        # add um ponto para o usuário no rank
        Rank.add_in_rank(user_id=user_id, server_id=server_id)

        if isinstance(interaction.channel, discord.DMChannel):
            canal = await interaction.user.create_dm()
            is_dm = True
        else:
            canal = interaction.channel
            is_dm = False

        Pomo.start(server_id, user_id, canal.id, is_dm, blocos, estudo, descanso)

        if Pomo.all_pomodoros[user_id]['msg'] is None:

            # converte os valores binários do bloco para a palavra certa
            if Pomo.all_pomodoros[user_id]['pomodoro'] == True:
                bloco_act_pomo = 'estudo'
            elif Pomo.all_pomodoros[user_id]['pomodoro'] == None:
                bloco_act_pomo = 'descanso'

            tempo = Pomo.tempo(user_id)

            # carrega a envia a embed no chat
            await interaction.response.send_message(
                embed=embeds.embed_pomodoro(bloco_act_pomo, tempo, blocos)
                )

            # pega o id da embed pra poder editar ela 
            msg = await interaction.original_response()
            Pomo.all_pomodoros[user_id]['msg'] = msg.id

        else:
            await interaction.response.send_message(
                embed=embeds.embed_simples(texto='você já tem uma tabela cronômetro ativa', cor=discord.Color.red()),
                ephemeral=True,
                delete_after=5
                )


@cronômetro.command(name='stop', description='encerra o pomodoro')
async def cronometro_stop(interaction: discord.Interaction):
    user_id =interaction.user.id
    server_id = interaction.guild_id

    # add um ponto para o usuário no rank
    Rank.add_in_rank(user_id=user_id, server_id=server_id)

    pomo = Pomo.stop(user_id)
    if pomo == False:
        await interaction.response.send_message(
            embed=embeds.embed_simples(texto='Cronômetro **não está ativo**, use o comando de **start** primeiro', cor=discord.Color.red()),
            ephemeral=True,
            delete_after=5
            )
    else:
        await interaction.response.send_message(
            embed=embeds.embed_simples(texto='Cronômetro **desligado**', cor=discord.Color.red()),
            ephemeral=True
            )


#####################
# AGENDA DE TAREFAS #
#####################
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
    user = interaction.user.id

    # add um ponto para o usuário no rank
    Rank.add_in_rank(user_id=user, server_id=server_id)

    data_hora = Agenda.valid_data(data=data, time=hora)

    if data_hora != False:
        # salva as infos da nova tarefa no json
        Agenda.add_task(server_id, cargo_id, tarefa, desc, data_hora, canal)

        await interaction.response.send_message(
            embed=embeds.embed_agenda_lembrete(
                title= tarefa,
                desc= desc,
                cargo= cargo_id,
                data= data_hora
            )

        )
    else:
        texto = '''Digite a data ou a hora da maneira correta. 
Siga os padrões BR: **dia/mês/ano**  e  **hora:minuto**.    
E insira uma **data futura**.'''        
        await interaction.response.send_message(
            embed=embeds.embed_simples(titulo='ERRO!', texto=texto, cor=discord.Color.red()),
            ephemeral=True       
        )


@agenda.command(name='list', description='mostra os lembretes já marcados')
@app_commands.describe(
    cargo = 'listar os lembretes apenas do cargo selecionado'
)
async def agenda_list(interaction: discord.Interaction, cargo: discord.Role | None=None):
    server_id = str(interaction.guild_id)
    user = interaction.user.id

    if server_id in Agenda.load_agenda():
        # add um ponto para o usuário no rank
        Rank.add_in_rank(user_id=user, server_id=server_id)

        if cargo is not None:
            cargo_id = cargo.id
            eventos_valid = Agenda.list_agenda(server_id, cargo_id)
        else:
            eventos_valid = Agenda.list_agenda(server_id=server_id)

        if len(eventos_valid) != 0:
            texto = "\n".join(eventos_valid)
            await interaction.response.send_message(
                embed= embeds.embed_simples(titulo='📅 Lembretes Pendentes:', texto=texto)
            )
        else:
            await interaction.response.send_message(
                embed=embeds.embed_simples(texto='não existe nenhum lembrete agendado', cor=discord.Color.red())
            )
    else:
        await interaction.response.send_message(
            embed=embeds.embed_simples(texto='não existe nenhum lembrete agendado', cor=discord.Color.red())
        )



########
# RANK #
########
@bot.tree.command(name='rank', description='top usuários do bot')
async def rank(interaction: discord.Interaction):
    server_id = interaction.guild_id

    top3_cmd = Rank.show_cmd_rank(server=server_id)
    top3_temp = Rank.show_temp_rank(server=server_id)

    if top3_cmd == []:
        await interaction.response.send_message(
            embed=embeds.embed_simples(texto='este servidor ainda não tem uma classificação', cor=discord.Color.red()),
            allowed_mentions=discord.AllowedMentions(users=True)
        )

    else:
        resposta_embeds = [embeds.embed_cmd_rank(top3_cmd)]
        if top3_temp != []:
            resposta_embeds.append(embeds.embed_temp_rank(top3_temp))

        await interaction.response.send_message(
            embeds=resposta_embeds
        )


##################
## ADM COMMANDS ##
##################
adm = app_commands.Group(
    name='adm',
    description='adm commands'
)
bot.tree.add_command(adm)

@adm.command(name='ban', description='permite adm banir usuário mais facilmente')
@app_commands.checks.has_permissions(ban_members=True)
@app_commands.describe(
    user = 'menção do usuário que será banido'
)
async def ban(interaction: discord.Interaction, user: str):
    

    # tentando dar um jeito em como filtrar tanto mention quanto id para conseguir banir até usuários que não estão no server
    print(user)
    #await interaction.guild.ban(user)

    await interaction.response.send_message(
        f'{user} banido'
    )



    #########################
    ## COMANDOS DE PREFIXO ##
    #########################

# github
@bot.command()
async def github(ctx):
    await ctx.send(
        embed=embeds.embed_simples(titulo='Github do adm:', texto='https://github.com/THmaguetas') 
        )


# spam mention 
@bot.command()
async def mention(ctx, membro: str):
    id_membro = int(membro.strip('<@!>'))
    membro_pronto = ctx.guild.get_member(id_membro)
    if membro_pronto:
        for _ in range(0, 40):
            await ctx.send(f'{membro_pronto.mention}')


# limpeza de chat
@bot.command()
async def clear(ctx, quantidade: int = 100):

    if not (ctx.author.id == int(os.getenv("TH_ID")) or ctx.author.guild_permissions.manage_messages):
        await ctx.send(
            f'<@{ctx.author.id}> você não tem permissão para usar esse comando',
            delete_after=6
        )
    else:
        # valida quantidade
        if quantidade < 1:
            await ctx.send(
                "A quantidade deve ser maior que 0.",
                delete_after=5
            )
        elif quantidade > 100:
            await ctx.send(
                "O bot não limpa mais do que 100 mensagens por vez.",
                delete_after=6
            )

        else:
            Rank.add_in_rank(ctx.author.id, ctx.author.guild.id)

            # apaga mensagens (+1 para apagar o comando)
            await ctx.channel.purge(limit=quantidade + 1)


    ##################
    ## TOKEN DO BOT ##
    ##################
token = os.getenv("SUDO_TOKEN")
bot.run(token)
