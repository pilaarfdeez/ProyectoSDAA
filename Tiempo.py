import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

url = f"https://www.weather-forecast.com/locations/Sevilla/forecasts/latest"
response = requests.get(url)


if __name__ == "__main__":

    
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    pronostico = soup.find('span', {'class': 'phrase'}).text
  
    now=datetime.now()
    dia_num= now.weekday()
    dia_sem= ["lunes","martes","miercoles","jueves","viernes","sevoia","domingo"]
    dia_actual= dia_sem[dia_num]
    dia=now.day
    mes=now.month
    año=now.year
    print(dia_actual)
    print(dia)
    print(mes)
    print(año)
    
    #bot.send_message(chat_id, "Buenos dias! Hoy {dia_actual},{dia}-{mes}-{año}\n")
    #bot.send_message(chat_id, "El tiempo de hoy es: {pronostico}\n")



