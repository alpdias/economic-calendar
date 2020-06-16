# -*- coding: utf-8 -*-

'''
Criado em 06/2020
Autor: Paulo https://github.com/alpdias
'''

# bibliotecas utilizadas para o tratamento e o webscraping do calendario economico
from datetime import datetime
import datetime as DT
from time import sleep
import arrow 
import requests
from bs4 import BeautifulSoup

# bibliotecas para a API do telegram 'telepot' https://github.com/nickoala/telepot
import telepot
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

# bibliotecas complementares
import emoji

token = 'token' # token de acesso

usuario = 'ID' # numero inteiro (Telegram ID user)

chave = 'chave' # chave para atualizar (string)

ChannelID = 'ID' # numero inteiro (Telegram ID Channel)

bot = telepot.Bot(token) # telegram bot

def calendario(url): # funçao para obter as noticas do calendario economico a partir de um webscraping e tratando o html

    url = url # site utilizado no webscraping

    cabeçalho = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'} # cabeçalho para obter a requisiçao do site (site só aceita acesso por navegador(simulação))

    requisiçao = requests.get(url, headers=cabeçalho) # requisiçao dentro do site

    soup = BeautifulSoup(requisiçao.text, 'html.parser') # tratamento do html com o modulo 'bs4'

    tabela = soup.find('table', {'id': 'economicCalendarData'}) # apenas a tabela com o id especifico

    corpo = tabela.find('tbody') # apenas o corpo da tabela

    linhas = corpo.findAll('tr', {'class': 'js-event-item'}) # apenas as linhas da tabela

    calendario = [] # lista para as noticias
    
    for tr in linhas:

        horario = tr.attrs['data-event-datetime'] # separando o horario da noticia pela tag html 'data-event-datetime'
        horario = arrow.get(horario, 'YYYY/MM/DD HH:mm:ss').timestamp # converter uma string de horario em um formato aceito pelo python
        horario = datetime.utcfromtimestamp(horario).strftime('%H:%M')
        calendario.append(horario)

        horario = tr.attrs['data-event-datetime'] # separando o horario da noticia pela tag html 'data-event-datetime'
        horario = arrow.get(horario, 'YYYY/MM/DD HH:mm:ss').timestamp # converter uma string de horario em um formato aceito pelo python
        horas = (int(datetime.utcfromtimestamp(horario).strftime('%H')) * 60)
        minutos = int(datetime.utcfromtimestamp(horario).strftime('%M'))
        verificaçao = horas + minutos # horario em minutos para verrificar o tempo em minutos para envio da noticia
        calendario.append(verificaçao)

        coluna = tr.find('td', {'class': 'flagCur'}) # separando o pais da noticia pela tag html 'flagCur'
        bandeira = coluna.find('span')
        calendario.append(bandeira.get('title'))

        impacto = tr.find('td', {'class': 'sentiment'})
        touro = impacto.findAll('i', {'class': 'grayFullBullishIcon'}) # separando o impacto da noticia pela tag html 'grayFullBullishIcon' e sua quantidade respectiva
        calendario.append(len(touro))

        evento = tr.find('td', {'class': 'event'})
        a = evento.find('a') # separando a tag html especifica 'a' para obter o nome e a url da noticia

        calendario.append('{}{}'.format(url, a['href'])) # separando a url da noticia com o url do site e tag de referencia html 'href'

        calendario.append(a.text.strip()) # separando a chamada na notica pela tag html 'a' (texto dentro da tag)

    return calendario # retorna a lista com as noticias


def enviarMensagens(msgID, texto, botao=''): # funçao para enviar as mensagens atravez do bot
    bot.sendChatAction(msgID, 'typing') # mostra a açao de 'escrever' no chat
    sleep(1)
    bot.sendMessage(msgID, texto, reply_markup=botao, disable_notification=False) # retorna uma mensagem pelo ID da conversa + um texto + um botao


def receberMensagens(msg): # funçao para buscar as mensagens recebidas pelo bot e executar os comandos
    msgID = msg['chat']['id'] # variavel para receber o ID da conversa
    nome = msg['chat']['first_name'] # variavel para receber o nome do usuario que enviou a msg
    botao = '' # variavel para receber o botao a ser enviado dentro da interface do telegram

    if msg['text'] == '/start' and msgID != usuario:
        bemvindo = (emoji.emojize(f'Olá {nome}, esse bot serve somente para controlar e atualizar o envio de mensagens em um canal no telegram sobre notícias do calendário econômico, se quiser \
saber mais sobre o meu funcionamento ou quiser relatar alguma coisa, entre em contato com o meu desenvolvedor, é só clicar no botão abaixo :backhand_index_pointing_down:', use_aliases=True)) # msg dando boas vindas e explicando o funcionamento do bot
        botao = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=(emoji.emojize('+ INFO :receipt:', use_aliases=True)), url='https://t.me/alpdias')]]) # botao com link para ajuda
        enviarMensagens(msgID, bemvindo, botao)

    elif msg['text'] == chave and msgID != usuario:
        negado = (emoji.emojize(f'{nome}, você não tem acesso a essa função, acesso negado :prohibited:', use_aliases=True)) # msg para usuario sem acesso (caso acerte a chave de acesso)
        enviarMensagens(msgID, negado)
        
    elif msg['text'] == '/start' and msgID == usuario:
        solicitar = (emoji.emojize(f'Olá {nome}, me envie a chave de atualização :key:', use_aliases=True)) # msg dando boas vindas e solicitando a chave de atualizaçao para usuario com acesso
        enviarMensagens(msgID, solicitar)

    elif msg['text'] == chave and msgID == usuario:
        atualizar = (emoji.emojize('Atualizando... :globe_with_meridians:', use_aliases=True)) # msg de atualizaçao
        enviarMensagens(msgID, atualizar)

        try:
            dados = calendario('https://br.investing.com/economic-calendar/')
            atualizado = (emoji.emojize('Atualizado com sucesso! :thumbs_up:', use_aliases=True)) # msg de sucesso na atualizaçao
            enviarMensagens(msgID, atualizado)

        except:
            erro = (emoji.emojize('Erro inesperado ao atualizar! :pensive_face:', use_aliases=True)) # msg de erro na atualizaçao
            enviarMensagens(msgID, erro)

        quantidade = (len(dados) / 6) # quantidade de noticias

        while True:

            # mostra o horario atual da maquina para verificar junto com o horario da noticia
            agora = (datetime.now())
            minutos = (agora.minute)
            atual = ((agora.hour * 60) + minutos)
            
            horario = dados[0] # dado especifico para o horario da noticia
            verificaçao = dados[1]# dado especifico para verificar o horario da noticia em minutos

            if verificaçao == 0:
                verificaçao = verificaçao

            else:
                verificaçao = (verificaçao - 5)

            local = dados[2] # dado especifico para o pais da noticia
            impacto = dados[3] # dado especifico para o impacto da noticia
            impacto = (emoji.emojize(int(impacto) * f':ox:', use_aliases=True)) # transformando dado em emoji
            link = dados[4] # dado especifico para o link da noticia
            chamada = dados[5] # dado especifico para a chamada da noticia

            noticia = (emoji.emojize(f'Local: {local.strip()} :globe_showing_Americas:\
            \nHorário: {horario}\
            \nImpacto da notícia: {impacto}\
            \n:loudspeaker: {chamada.strip()}\
            \nPara ver mais acesse :backhand_index_pointing_down:', use_aliases=True)) # noticia formatada 

            botao = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=(emoji.emojize('+ NOTÍCIA :receipt:', use_aliases=True)), url=f'{link.strip()}')]]) # botao com link acesso a noticia
            
            if verificaçao == 0 and atual == 0:
                enviarMensagens(ChannelID, noticia, botao)
                quantidade = quantidade - 1

                for item in range(0, 6):
                    del dados[0] # apaga as ultimas informaçoes ja usadas(6 primeiros itens na lista), para nao ter repetiçoes
                
            elif verificaçao == 0 and verificaçao < atual:
                quantidade = quantidade - 1

                for item in range(0, 6):
                    del dados[0] # apaga as ultimas informaçoes ja usadas(6 primeiros itens na lista), para nao ter repetiçoes

            elif verificaçao == atual:
                enviarMensagens(ChannelID, noticia, botao)
                quantidade = quantidade - 1

                for item in range(0, 6):
                    del dados[0] # apaga as ultimas informaçoes ja usadas(6 primeiros itens na lista), para nao ter repetiçoes
            
            elif verificaçao <= atual:
                quantidade = quantidade - 1

                for item in range(0, 6):
                    del dados[0] # apaga as ultimas informaçoes ja usadas(6 primeiros itens na lista), para nao ter repetiçoes
            
            else:
                pass

            if quantidade == 0:
                break

            else:
                pass

    elif msgID == usuario and msg['text'] != chave:
        incompreendido = (emoji.emojize(f'{nome}, não entendi seu comando ou você me enviou a chave errada, tente novamente! :grimacing_face:', use_aliases=True))
        enviarMensagens(msgID, incompreendido)

    else:
        info = (emoji.emojize(f'{nome}, desculpe mas não entendi seu comando, meu uso é exclusivo para atualização de um canal no telegram, para saber mais entre \
em contato com meu desenvolvedor :backhand_index_pointing_down:', use_aliases=True)) # msg para mais informaçoes
        botao = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=(emoji.emojize('+ INFO :receipt:', use_aliases=True)), url='https://t.me/alpdias')]]) # botao com link para ajuda
        enviarMensagens(msgID, info, botao)

# loop do modulo 'telepot' para procurar e receber novas mensagens, executando as funçoes
bot.message_loop(receberMensagens) 

# loop em python para manter o programa rodando
while True:
    pass
