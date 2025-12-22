import RPi.GPIO as GPIO
import time
from datetime import datetime

# Configurazione Pin GPIO
LEDS = [16, 26, 21, 14, 15]
BUZZ = 12

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

for pin in LEDS:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

GPIO.setup(BUZZ, GPIO.OUT)
GPIO.output(BUZZ, GPIO.LOW)

def trigger_reminder():
    print(f"[{datetime.now()}] Attivazione promemoria medicine...")
    # Accendi tutto
    for pin in LEDS:
        GPIO.output(pin, GPIO.HIGH)
    GPIO.output(BUZZ, GPIO.HIGH)
    
    # Buzzer per 2 secondi
    time.sleep(2)
    GPIO.output(BUZZ, GPIO.LOW)
    
    # LED restano accesi per altri 3 secondi (totale 5s)
    time.sleep(3)
    for pin in LEDS:
        GPIO.output(pin, GPIO.LOW)
    print(f"[{datetime.now()}] Promemoria completato.")

# Orari programmati
SCHEDULE = ["10:00", "13:00", "19:00"]

print("Script promemoria medicine avviato...")
print(f"Orari attivi: {', '.join(SCHEDULE)}")

try:
    triggered_today = set()
    last_day = datetime.now().day

    while True:
        now = datetime.now()
        current_day = now.day
        current_time = now.strftime("%H:%M")

        # Reset giornaliero dei trigger
        if current_day != last_day:
            triggered_today = set()
            last_day = current_day

        # Controlla se è orario di medicina
        if current_time in SCHEDULE and current_time not in triggered_today:
            trigger_reminder()
            triggered_today.add(current_time)

        # Aspetta un po' prima del prossimo controllo per non sovraccaricare la CPU
        time.sleep(30)

except KeyboardInterrupt:
    print("\nScript interrotto dall'utente.")
finally:
    GPIO.cleanup()
