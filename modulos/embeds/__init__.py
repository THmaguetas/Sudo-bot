import discord

def embed_pomodoro(bloco_atual, tempo_restante, blocos):
    embed = discord.Embed(
        title='⏱️ CRONÔMETRO POMODORO',
        description='Organize seu estudo usando **blocos de foco**.',
        color=discord.Color.green()
    )

    embed.add_field(
        name='📌 Bloco atual',
        value=f'**{bloco_atual.upper()}**',
        inline=False
    )

    embed.add_field(
        name='⏳ Tempo restante',
        value=f'**{tempo_restante:.0f} min**',
        inline=False
    )

    embed.add_field(
        name='📦 Blocos restantes',
        value=f'**{blocos-1}**',
        inline=False
    )

    embed.set_footer(
        text='• Mantenha o foco'
    )

    return embed


def embed_agenda_lembrete(title, desc, cargo, data):
    embed = discord.Embed(
        title=f"📔 {title}",
        description=f"🔔 Lembrete **agendado** para: <@&{cargo}>",
        color=discord.Color.dark_green(),
    )

    embed.add_field(
        name="📌 Descrição:",
        value=desc if desc.strip() else "Sem descrição.",
        inline=False
    )

    embed.add_field(
        name = "🗓️ Data de entrega:",
        value= f"{data}",
        inline = False
    )

    embed.set_footer(text="Agenda • Lembrete agendado")

    return embed


def embed_entrega_lembrete(title, cargo):
    embed = discord.Embed(
        title= f"⏰ Entrega de: {title}",
        description=f"🔔**Entrega** do lembrete para: <@&{cargo}>",
        color= discord.Color.orange()
    )   

    embed.set_footer(text="Agenda • Lembrete automático")
    embed.timestamp = discord.utils.utcnow()

    return embed


def embed_cmd_rank(top3):
    embed = discord.Embed(
        title="🏆 TOP 3 DO SERVIDOR",
        description="**Categoria:** Comandos Rodados.",
        color=discord.Color.gold()
    )

    medalhas = ['🥇', '🥈', '🥉']
    for posit, (user_id, info) in enumerate(top3):
        user_id = int(user_id)
        embed.add_field(
            name=f"{medalhas[posit]} Top {posit + 1}",
            value=(
                f"👤 Usuário: <@{user_id}>\n"
                f"📊 Comandos usados: **{info['quant_comandos']}**"
            ),
            inline=False
        )

    embed.set_footer(text="Server Rating")
    embed.timestamp = discord.utils.utcnow()

    return embed


def embed_temp_rank(top3):
    embed = discord.Embed(
        title="🏆 TOP 3 DO SERVIDOR",
        description="**Categoria:** Tempo de Estudo.",
        color=discord.Color.gold()
    )

    medalhas = ['🥇', '🥈', '🥉']
    for posit, (user_id, info) in enumerate(top3):
        user_id = int(user_id)
        embed.add_field(
            name=f"{medalhas[posit]} Top {posit + 1}",
            value=(
                f"👤 Usuário: <@{user_id}>\n"
                f"📊 Tempo estudado: **{int(info['temp_estudo']/60)}** min"
            ),
            inline=False
        )

    embed.set_footer(text="Server Rating")
    embed.timestamp = discord.utils.utcnow()

    return embed


def embed_simples(titulo='', texto='', cor=discord.Color.green()):
    embed = discord.Embed(
        title=titulo,
        description=texto,
        color=cor
    )
    return embed

