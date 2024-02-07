#Librerias empleadas
import telebot
from telebot import types
import threading
from sense_hat import SenseHat
from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2
import requests
import thingspeak
import matplotlib.pyplot as plt
from matplotlib.dates import date2num
import time
from datetime import datetime, timedelta
import numpy as np
from bs4 import BeautifulSoup
import pygame

#Inicializacion y definicion de variables

#Bot telegram
TOKEN = '6833819279:AAF0wAtuMjx5L5P4sSza4c3Jj2Q_RXcEB18'
bot = telebot.TeleBot(TOKEN)
chat_id = 890524575
#ThingSpeak
channel_id = "2413889"         # Identificador de canal
write_key = "Z3FK3ZAV9UHQKBKY" # Key de Escritura
read_key = "QRR3OLS638WGHCNI"  # Key de Escritura

sense=SenseHat()               #Objeto Sense_Hat

# Url obtencion tiempo
url = f"https://www.weather-forecast.com/locations/Sevilla/forecasts/latest"

# variables Globales
global Alarma        # Se ha establecido una alarma
global Sonando       # La alarma esta sonando
global Inicializado  # Variable auxiliar que indica el establecimiento de la alarma
last_command = None

# Inicializacion
Alarma = False
Sonando = False
Inicializado = False
fecha_alarma = ""
cancion = "mambo.mp3"
selected_mood = None

#Funciones empleadas
# Gestiona los datos a enviar a Telegram tras la desactivacion de la alarma
def parada():
    global Inicializado, horaestablecida, horadealarma, selected_mood
    while True:
        if not Sonando and Inicializado:
            
            # Pronostico del tiempo
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            pronostico = soup.find('span', {'class': 'phrase'}).text
            
            # Calulo dia de la semana
            now=datetime.now()
            dia_num= now.weekday()
            dia_sem= ["lunes","martes","miercoles","jueves","viernes","sevoia","domingo"]
            dia_actual= dia_sem[dia_num]
            
            # Calculo de fecha completa
            dia=now.day
            mes=now.month
            año=now.year
            
            # Envio del mensaje al bot
            bot.send_message(chat_id, f"Buenos dias! Hoy es {dia_actual}, {dia} del {mes} de {año}.\n \n El tiempo de hoy es: {pronostico}\n")
            # Mensaje Horas fotm
            numero_horasSueño()
            #Informar horas del sueño anteriores:
            selected_mood=None
            Inicializado=False
            break

# Calculo de horas de sueño y almacenamiento de datos
def numero_horasSueño():
    # Calculo horas dormidas
    num_horas = horadealarma - horaestablecida
    horas, segundos = divmod(num_horas.seconds, 3600)
    minutos, segundos = divmod(segundos, 60)
    bot. send_message(chat_id, f"Has dormido: {horas:02} horas y {minutos:02} minutos")
    
    # Envio de datos a ThingSpeak
    channel = thingspeak.Channel(id=channel_id, api_key=write_key)
    dato = horas + minutos/100
    response = channel.update({"field1": dato})

# Activacion de la camara y deteccion de ojos/luz
def camara():
    #Inicializacion
    camera = PiCamera()
    camera.resolution = (320, 240)
    camera.framerate = 30
    camera.rotation = 0
    rawCapture = PiRGBArray(camera, size=(320, 240))
    
    #Ventana de visualizacion

    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

    global Sonando
    
    # Iterar sobre los fotogramas capturados
    # Capturar de forma continua salvo salida por break
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        frame = frame.array
        
        # Detección de ojos
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        eyes = eye_cascade.detectMultiScale(gray, 8, 10)

        for (ex, ey, ew, eh) in eyes:
            cv2.rectangle(frame, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)
            Sonando = False  # Establecer Sonando en False cuando se detecta una cara
            print("Ojos detectados")
        
        # Detección de intensidad de luz
        intensidad_luz = np.mean(frame)
        umbral_intensidad = 150  

        if intensidad_luz > umbral_intensidad:
            Sonando=False # Establecer Sonando en False cuando se detecta luz considerable
            print("Intensidad de luz considerable detectada")
        print(Sonando)
        
        # Mostrar ventana creada
        cv2.imshow("Eyes Detection", frame)
        key = cv2.waitKey(1) & 0xFF
        
        # Condicion de salida. Puede producirse por la modificacion de "Sonando" en otros hilos
        if not Sonando:
            break

        # Limpiar el buffer para el próximo frame
        rawCapture.truncate(0)
    
    # Cierra la camara y la pantalla
    camera.close()
    cv2.destroyAllWindows()
# Hilo motores. Los activa durante un tiempo determinado, suficiente para elevar las persianas
def motores():
   
   print("Subiendo motores")
   time.sleep(5)
   print("persianas subidas")
# Hilo altavoz. Activa la melodia mientras este sonando la alarma
def Altavoz():
    #Inicializacion
    pygame.mixer.init()
    pygame.mixer.music.load(cancion)
    pygame.mixer.music.play()
    
    # Bucle de control
    while True:
       if not Sonando: 
           pygame.mixer.music.stop()
           break
# Hilo Luces. Muestra una frase inicial y luego parpadea a leatoriamente 
def Luces():
    #Frase inicial
    sense.show_message("Despierta!",scroll_speed=0.2, text_colour=[250,0,250])
    time.sleep(0.5)
    
    # Secuecia de colores
    rainbow_colors = [
        [255, 0, 0],    # Rojo
        [255, 165, 0],  # Naranja
        [255, 255, 0],  # Amarillo
        [0, 255, 0],    # Verde
        [0, 0, 255],    # Azul
        [75, 0, 130],   # Índigo
        [128, 0, 128]   # Violeta
    ]
    # Control de parpadeo
    while Sonando:
        for color in rainbow_colors:
            sense.clear(color)
            time.sleep(0.1)
    sense.clear()

# Control de alarma. Activa la alarma si la hora actual es igual a la de la alarma
def verificar_alarma():
    global Alarma, fecha_alarma, Sonando, Inicializado, horadealarma
    
    while True:
        try:
            
            # Hora actual (HH:MM)
            ahora = datetime.now().strftime("%H:%M")
            
            # Comprobar si se debe activar la alarma
            if Alarma and ahora == fecha_alarma:
                print("Alarma Activada!")
                
                # Activamos sonando y lanzamos los hilos que se ejecutan en paralelo
                Sonando = True
                bot.send_message(chat_id, "Alarma sonando, para detenerla pulse: \n /DetenerAlarma \n")
        
                horadealarma = datetime.now()
                Inicializado=True
                
                # Hilos
                hilo_motores = threading.Thread(target=motores) # Persianas
                hilo_motores.start() 
                hilo_Luces = threading.Thread(target=Luces)     # Luces
                hilo_Luces.start()
                hilo_camara = threading.Thread(target=camara)   # Camaras
                hilo_camara.start()
                hilo_Altavoz = threading.Thread(target=Altavoz) # Altavoz
                hilo_Altavoz.start()
                hilo_parada = threading.Thread(target=parada)   # Envio de datos post alarma
                hilo_parada.start()
                
                Alarma=False 
                
                if not Alarma:
                    break

        except Exception as e:
            print(f"Error en la verificación de la alarma: {e}")

        threading.Event().wait(5)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    global last_command
    last_command = None
    bot.reply_to(message, "¡Bienvenido! ¿Cómo puedo ayudarte hoy? \n", reply_markup=create_main_keyboard())

# Crear teclado principal
def create_main_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2)
    item1 = types.KeyboardButton("Establecer Alarma")
    item2 = types.KeyboardButton("Ver Ciclo de Sueño")
    markup.add(item1, item2)
    return markup

# Crear teclado después de activar la alarma
def create_alarm_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=1)
    item1 = types.KeyboardButton("Ver Información de la Alarma")
    markup.add(item1)
    return markup

# Gestionar los botones principales
@bot.message_handler(func=lambda message: message.text in ["Establecer Alarma", "Ver Ciclo de Sueño"])
def handle_main_buttons(message):
    global last_command
    last_command = message.text

    if message.text == "Establecer Alarma":
        EstablecerAlarma(message)
    elif message.text == "Ver Ciclo de Sueño":
        HorasSueño(message)
        
# Envia la informacion del sueño acumulado
@bot.message_handler(commands=['EstablecerAlarma'])
def EstablecerAlarma(message):
    bot.reply_to(message, "Por favor, introduce la hora de la alarma (formato HH:MM)")

# Gestiona la detencion manual de la alarma
@bot.message_handler(commands=['DetenerAlarma'])
def detener_alarma(message):
    global Sonando
    Sonando = False
    sense.clear()

# Envia la informacion del sueño acumulado
@bot.message_handler(commands=['CicloSueño'])
def HorasSueño(message):
    
    # Fecha y hora actual
    now = datetime.now()

    # Fecha y hora hace 7 dias
    seven_days_ago = now - timedelta(days=7)

    # Formateo de fechas valido para ThingSpeak
    start_date = seven_days_ago.strftime('%Y-%m-%dT%H:%M:%SZ')
    end_date = now.strftime('%Y-%m-%dT%H:%M:%SZ')

    # url con el intervao de fechas y el id del canal
    url = f"https://api.thingspeak.com/channels/{channel_id}/feeds.json?api_key={read_key}&start={start_date}&end={end_date}"
    
    # Obtiene la respuesta en formato json
    response = requests.get(url)
    data = response.json()["feeds"]

    # Procesar los datos
    timestamps = []
    values = []

    for entry in data:
        timestamp_str = entry.get("created_at")  
        value_str = entry.get("field1", None)
        
        if timestamp_str and value_str is not None:
            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%SZ")
            value = float(value_str)

            timestamps.append(timestamp)
            values.append(value)

    # Procesa los datos y genera la gráfica
    fig, ax = plt.subplots()
    ax.bar(date2num(timestamps), values, width = 0.0001)

    # Formatea las etiquetas del eje x como fechas
    plt.xticks(rotation=45, ha='right')
    ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%H:%M'))
    
    # Nombres a los ejes y titulo
    plt.xlabel('Días')
    plt.ylabel('Horas dormidas')
    plt.title('Número de horas de sueño')
    # Ajusta el tamaño de la figura
    fig.set_size_inches(10, 9) 

    # Guarda la grafica en una imagn png y se la envia al bot
    plt.savefig('grafica.png')
    bot.send_photo(chat_id, photo=open('grafica.png', 'rb'))

# Gestion de hora introducida
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    global fecha_alarma, Alarma, horaestablecida
    
    try:
        # Hilo Verificacion de alarma
        hilo_alarma = threading.Thread(target=verificar_alarma)
        hilo_alarma.start()
        # Comprobar el formato de datos y si se encuentran en un intervalo valido
        if len(message.text) == 5 and message.text[2] == ":" and \
                message.text[:2].isdigit() and 0 <= int(message.text[:2]) <= 23 and \
                message.text[3:].isdigit() and 0 <= int(message.text[3:]) <= 59:
            
            # Fecha valida
            fecha_alarma = message.text
                 
            markup = types.InlineKeyboardMarkup(row_width=2)
            item3 = types.InlineKeyboardButton("Energico", callback_data='Energico')
            
            
            item4 = types.InlineKeyboardButton("Relajado", callback_data='Relajado')
            markup.add(item3,item4)
            
            bot.send_message(message.chat.id, "Elije modo de despertar; 'Energico' o 'Relajado'", reply_markup=markup)        
            
            while selected_mood is None:
                time.sleep(1)
                
            bot.send_message(message.chat.id, f"Alarma establecida a las {fecha_alarma}. ¡Espero que descanses bien!")
            # Activar la alarma
            Alarma = True
            
            
            horaestablecida = datetime.now()
       
            last_command = None  # Reiniciar el último comando
            
        else:
            bot.send_message(message.chat.id, "Introduce la fecha de alarma en el formato correcto (HH:MM), dentro del intervalo 00-23, y 00-59 respectivamente.")

    except Exception as e:
        bot.send_message(message.chat.id, f"Error al procesar el mensaje: {e}")

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    global selected_mood, cancion
    selected_mood=call.data
    if selected_mood == 'Energico':
        cancion='mambo.mp3'
    if selected_mood == 'Relajado':
        cancion='chill.mp3'
    print(cancion)

bot.polling(none_stop=True)




