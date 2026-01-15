import discord

def embed_pomodoro(bloco_atual, tempo_restante):
    embed = discord.Embed(
        title='**POMODORO**',
        description='estude usando o método pomodoro',
        color=discord.Color.green()
    )

    embed.add_field(
        name='Bloco atual:',
        value=f'BLOCO de **{bloco_atual.upper()}**',
        inline= True
    )

    embed.add_field(
        name='Tempo restante no bloco:',
        value=f'Restam **{tempo_restante:.0f}** minutos',
        inline= True
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

    embed.set_footer(
        text="Agenda • Lembrete automático"
    )

    return embed


def embed_simples(titulo='', texto='', cor=discord.Color.green()):
    embed = discord.Embed(
        title=titulo,
        description=texto,
        color=cor
    )
    return embed

