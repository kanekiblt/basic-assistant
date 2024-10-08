import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import pyaudio
from geopy.geocoders import Nominatim
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Configurar el motor de texto a voz
engine = pyttsx3.init()

voces = engine.getProperty('voices')
engine.setProperty('voice', voces[0].id)

engine.setProperty('rate', 180)

# Configurar el reconocimiento de voz
recognizer = sr.Recognizer()

# Configurar el geocodificador para obtener la ubicación
geolocator = Nominatim(user_agent="geo_locator")

def speak(text):
    engine.say(text)
    engine.runAndWait()

def get_audio():
    with sr.Microphone() as source:
        print("Escuchando...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        print("Procesando...")

    try:
        command = recognizer.recognize_google(audio, language="es-ES")
        print("Comando detectado (voz): " + command)
        return command.lower()
    except sr.UnknownValueError:
        print("No se pudo entender el comando (voz).")
        return ""
    except sr.RequestError as e:
        print("Error en la solicitud al servicio de reconocimiento de voz: {0}".format(e))
        return ""

def get_text():
    text = input("Ingrese un comando: ")
    return text.lower()

def get_volume():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    return volume.GetMasterVolumeLevelScalar()

def set_volume(level):
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    volume.SetMasterVolumeLevelScalar(level, None)

def mute_volume():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    volume.SetMute(1, None)  # 1 for mute, 0 for unmute

def unmute_volume():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    volume.SetMute(0, None)  # 0 for unmute, 1 for mute


def get_location():
    try:
        with sr.Microphone() as source:
            speak("Dime tu ubicación")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
        location_query = recognizer.recognize_google(audio, language="es-ES").lower()
        print("Ubicación detectada (voz): " + location_query)
        
        # Utilizar el geocodificador para obtener la ubicación
        location = geolocator.geocode(location_query)
        
        if location:
            speak(f"Estás en {location.address}")
        else:
            speak("No se pudo obtener la ubicación.")
    except sr.UnknownValueError:
        speak("No se pudo entender la ubicación.")
    except sr.RequestError as e:
        speak(f"Error al obtener la ubicación: {e}")

def process_command(command):
    if "hora" in command:
        current_time = datetime.datetime.now().strftime("%H:%M")
        speak("La hora actual es " + current_time)
    elif "fecha" in command:
        current_date = datetime.datetime.now().strftime("%d de %B de %Y")
        speak("La fecha actual es " + current_date)
    elif "ubicación" in command:
        get_location()
    elif any(keyword in command for keyword in ["abrir", "abre", "open"]):
        urls_to_open = []
        if "youtube" in command:
            urls_to_open.append("https://www.youtube.com/")
        if "maps" in command:
            urls_to_open.append("https://www.google.com/maps")
        if "chat gpt" in command:
            urls_to_open.append("https://chat.openai.com/")
        if "facebook" in command:
            urls_to_open.append("https://www.facebook.com/")
        if "instagram" in command:
            urls_to_open.append("https://www.instagram.com/")

        if not urls_to_open:
            speak("Sitio no reconocido. ¿Puedo ayudarte con algo más?")
            return

        for url in urls_to_open:
            webbrowser.open(url)
            speak(f"Abriendo {url}")

    else:
        speak("Comando no reconocido. ¿Puedo ayudarte con algo más?")

if __name__ == "__main__":
    speak("Hola, ¿en qué puedo ayudarte?")

    
    while True:
        print("Opciones:")
        print("1: Audio")
        print("2: Escribir")
        input_type = input("¿Quieres hablar o escribir? (1/2): ").lower()

        if input_type == '1':
            command = get_audio()
        elif input_type == '2':
            command = get_text()
        else:
            print("Entrada no válida. Intenta de nuevo.")
            continue

        if "detener" in command:
            speak("Hasta luego")
            break
        elif "subir volumen" in command:
            current_volume = get_volume()
            new_volume = min(current_volume + 0.1, 1.0)
            set_volume(new_volume)
            speak("Volumen subido al " + str(int(new_volume * 100)) + " por ciento.")

        elif "bajar volumen" in command:
            current_volume = get_volume()
            new_volume = max(current_volume - 0.1, 0.0)
            set_volume(new_volume)
            speak("Volumen bajado al " + str(int(new_volume * 100)) + " por ciento.")

        elif "silenciar" in command:
            mute_volume()
            speak("Volumen silenciado.")

        elif "desmutear" in command:
            unmute_volume()
            speak("Volumen desmutado.")

        else:

            process_command(command)
