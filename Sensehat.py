
import time
from sense_hat import SenseHat
sense=SenseHat()



sense.show_message("¡Despierta!",scroll_speed=0.2, text_colour=[250,0,250])
time.sleep(1)
rainbow_colors = [
    [255, 0, 0],   # Rojo
    [255, 165, 0],  # Naranja
    [255, 255, 0],  # Amarillo
    [0, 255, 0],    # Verde
    [0, 0, 255],    # Azul
    [75, 0, 130],   # Índigo
    [128, 0, 128]   # Violeta
]

# Parpadeo arcoíris
for _ in range(10):  # Cambia este valor según la duración deseada del parpadeo
    for color in rainbow_colors:
        sense.clear(color)
        time.sleep(0.1)

sense.clear()