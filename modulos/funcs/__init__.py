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
        value=f'Restam {tempo_restante:.1f} minutos',
        inline= True
    )
    return embed

