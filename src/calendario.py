# -*- coding: utf-8 -*-

'''
Criado em 04/2020
@Autor: Paulo https://github.com/alpdias

forked de exemplo como base https://github.com/freenetwork/investing.com.economic-calendar
'''

#bibliotecas importadas
from datetime import datetime
from time import sleep
import datetime as DT
import arrow 
# import requests --> bilbioteca bloqueada pelo CLOUDFLARE
import cfscrape # nova biblioteca de scraping
from bs4 import BeautifulSoup

def calendario(url): 
    
    """
    -> Funçao para obter as noticas do calendario economico a partir de um webscraping e tratando o html\
    \n:param url:\
    \n:return:\
    """

    # processo de requisiçao de dados no site -->
    
    url = url # site utilizado no webscraping

    '''
    cabeçalho = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'} # cabeçalho para obter a requisiçao do site (site só aceita acesso por navegador)

    requisiçao = requests.get(url, headers=cabeçalho) # requisiçao dentro do site
    '''

    scraper = cfscrape.create_scraper() # novo modelo de requiçao usando a biblioteca 'cfscraper'

    requisiçao = scraper.get(url)
    
    # processo de requisiçao de dados no site <--


    # processo de tratamento do html -->

    soup = BeautifulSoup(requisiçao.text, 'html.parser') # tratamento do html com o modulo 'bs4'

    tabela = soup.find('table', {'id': 'economicCalendarData'}) # apenas a tabela com o id especifico

    corpo = tabela.find('tbody') # apenas o corpo da tabela

    linhas = corpo.findAll('tr', {'class': 'js-event-item'}) # apenas as linhas da tabela

    calendario = [] # lista para as noticias

    # 'tr' linha dentro da tabela html
    # 'td' coluna dentro da tabela html
    
    for tr in linhas:

        horario = tr.attrs['data-event-datetime'] # separando o horario da noticia pela tag html 'data-event-datetime'
        horario = arrow.get(horario, 'YYYY/MM/DD HH:mm:ss') # converter uma string de horario em um formato aceito pelo python
        horario = horario.strftime('%H:%M')
        calendario.append(horario)

        horario = tr.attrs['data-event-datetime'] # separando o horario da noticia pela tag html 'data-event-datetime'
        horario = arrow.get(horario, 'YYYY/MM/DD HH:mm:ss') # converter uma string de horario em um formato aceito pelo python
        horas = (int(horario.strftime('%H')) * 60)
        minutos = int(horario.strftime('%M'))
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

        calendario.append('{}{}'.format('https://br.investing.com', a['href'])) # separando a url da noticia com o url do site e tag de referencia html 'href'

        calendario.append(a.text.strip()) # separando a chamada na notica pela tag html 'a' (texto dentro da tag)
        
    # processo de tratamento do html <--

    return calendario # retorna a lista com as noticias


# uso dos dados em html tratados em variaveis -->

dados = (calendario('https://br.investing.com/economic-calendar/')) # dados obtidos do html

print(dados) # lista com os dados
print('')

quantidade = (len(dados) / 6) # quantidade de noticias

while True:
   
    horario = dados[0] # dado especifico para o horario da 
    verificaçao = dados[1]
    pais = dados[2] # dado especifico para o pais da noticia
    impacto = dados[3] # dado especifico para o impacto da noticia
    link = dados[4] # dado especifico para o link da noticia
    chamada = dados[5] # dado especifico para a chamada da noticia

    noticia = (f'Local: {pais}\
    \nHorário: {horario}\
    \nImpacto da notícia: {impacto}\
    \nNotícia: {chamada}\
    \nPara ver mais acesse: {link}\
    \n').strip() # noticia formatada 

    print(noticia)
    print('')

    for item in range(0, 6):
        del dados[0] # apaga as ultimas informaçoes ja usadas(6 primeiros itens na lista), para nao ter repetiçoes

    quantidade = quantidade - 1

    if quantidade == 0:
        break

    else:
        pass
    
# uso dos dados em html tratados em variaveis <--
