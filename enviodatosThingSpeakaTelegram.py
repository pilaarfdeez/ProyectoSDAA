import requests
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.dates import date2num
import telebot


API_KEY = "QRR3OLS638WGHCNI"
CHANNEL_ID = "2413889"


TOKEN = '6833819279:AAF0wAtuMjx5L5P4sSza4c3Jj2Q_RXcEB18'
CHAT_ID = 890524575

# Obtén la fecha y hora actual
now = datetime.now()

# Calcula la fecha y hora hace 7 días
seven_days_ago = now - timedelta(days=7)

# Formatea las fechas en el formato requerido por ThingSpeak
start_date = seven_days_ago.strftime('%Y-%m-%dT%H:%M:%SZ')
end_date = now.strftime('%Y-%m-%dT%H:%M:%SZ')

# Construye la URL con el rango de fechas
url = f"https://api.thingspeak.com/channels/{CHANNEL_ID}/feeds.json?api_key={API_KEY}&start={start_date}&end={end_date}"

response = requests.get(url)
data = response.json()["feeds"]

# Procesar los datos
timestamps = []
values = []

for entry in data:
    timestamp_str = entry.get("created_at")  # Usa get para evitar problemas con campos faltantes
    value_str = entry.get("field1", None)  # Reemplaza 'field1' con el nombre de tu campo
    # Verifica si tanto timestamp_str como value_str no son None
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

plt.xlabel('Días')
plt.ylabel('Horas dormidas')
plt.title('Número de horas de sueño')
# Ajusta el tamaño de la figura
fig.set_size_inches(10, 9)  # Puedes ajustar estos valores según sea necesario

# Guardar la gráfica en un archivo
plt.savefig('grafica.png')

bot = telebot.TeleBot(TOKEN)
bot.send_photo(CHAT_ID, photo=open('grafica.png', 'rb'))