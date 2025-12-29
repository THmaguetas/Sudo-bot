esse projeto é um bot do discord que (por enquanto) está focado no auxílio em estudos.

# comandos

## pomodoro:
o comando pomodoro foi feito pensando em facilitar a contagem dos blocos para o usuário ter mais conforto no estudo.
- quando o comando é iniciado, é gerada uma embed cujo bloco ativo e contagem em tempo real dos minutos são feitas.
- quando o tempo do bloco ativo acaba é enviada uma notificação na dm do usuário para que se atente mais facilmente.
- todas as mensagens que o bot envia, exeto a embed, são ou privadas ou temporárias para evitar a poluição dos chats.
- toda a lógica do comando é feita de forma assíncrona e indivioval para cada usuário, dessa forma não existe travamento no código do bot e nem quantidade limitida do usuários por vez.
