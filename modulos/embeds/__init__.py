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


def embed_agenda(title, desc, cargo):
    embed = discord.Embed(
        title=f"⏰ {title}",
        description=f"🔔 **Lembrete para:** <@&{cargo}>",
        color=discord.Color.green(),
    )

    embed.add_field(
        name="📌 Descrição:",
        value=desc if desc.strip() else "Sem descrição.",
        inline=False
    )

    embed.set_footer(text="Agenda • Lembrete automático")
    embed.timestamp = discord.utils.utcnow()

    return embed


def embed_rank(top3, server):
    embed = discord.Embed(
        title="🏆 TOP 3 DO SERVIDOR",
        description="Os usuários com mais comandos rodados são:",
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


def embed_simples(titulo='', texto='', cor=discord.Color.green()):
    embed = discord.Embed(
        title=titulo,
        description=texto,
        color=cor
    )
    return embed

