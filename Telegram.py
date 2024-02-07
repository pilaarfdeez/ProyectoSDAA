import telebot

TOKEN = ('6833819279:AAF0wAtuMjx5L5P4sSza4c3Jj2Q_RXcEB18')
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message,"Bienvenido, espero que hayas tenido un buen día! ¿A qué hora deseas despertarte mañana?")
    
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    global fecha_alarma
    
    # Verificar si la fecha y hora se ajustan al formato HH:MM y están en el rango correcto
    if len(message.text) == 5 and message.text[2] == ":" and \
            message.text[:2].isdigit() and 0 <= int(message.text[:2]) <= 23 and \
            message.text[3:].isdigit() and 0 <= int(message.text[3:]) <= 59:
        
        fecha_alarma = message.text
        bot.send_message(message.chat.id, f"Fecha de alarma registrada: {fecha_alarma}")
        
        # Aquí puedes enviar la fecha y hora a tu Raspberry Pi o realizar otras acciones necesarias
        # Puedes utilizar algún mecanismo de comunicación como sockets, MQTT, etc. dependiendo de tus necesidades.
        # Ejemplo de cómo imprimir en la Raspberry Pi:
        print(f"Fecha de alarma recibida: {fecha_alarma}")
        # Activar la alarma
        
        print("Alarma activada")
        bot.send_message(message.chat.id, "¡Alarma activada para la hora especificada!")

    else:
        bot.send_message(message.chat.id, "Introduce la fecha de alarma en el formato correcto (HH:MM) y asegúrate de que las horas estén entre 00 y 23, y los minutos entre 00 y 59.")

bot.polling(none_stop=True)
    