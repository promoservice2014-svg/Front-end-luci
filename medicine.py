from gpiozero import LED, Buzzer
import time
from datetime import datetime
import signal
import sys

# Configurazione Pin GPIO (BCM)
# LED1=16, LED2=26, LED3=21, LED4=14, LED5=15
led_pins = [16, 26, 21, 14, 15]
leds = [LED(pin) for pin in led_pins]
buzz = Buzzer(12)

def trigger_reminder():
    print(f"[{datetime.now()}] Attivazione promemoria medicine...")
    # Accendi tutto
    for led in leds:
        led.on()
    buzz.on()
    
    # Buzzer per 2 secondi
    time.sleep(2)
    buzz.off()
    
    # LED restano accesi per altri 3 secondi (totale 5s)
    time.sleep(3)
    for led in leds:
        led.off()
    print(f"[{datetime.now()}] Promemoria completato.")

# Orari programmati
SCHEDULE = ["10:00", "13:00", "19:00"]

print("Script promemoria medicine avviato (GPIOZero version)...")
print(f"Orari attivi: {', '.join(SCHEDULE)}")

def handle_exit(sig, frame):
    print("\nScript interrotto dall'utente.")
    sys.exit(0)

signal.signal(signal.SIGINT, handle_exit)

triggered_today = set()
last_day = datetime.now().day

try:
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

        # Aspetta un po' prima del prossimo controllo
        time.sleep(30)
except Exception as e:
    print(f"Errore imprevisto: {e}")
