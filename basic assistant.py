import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import requests
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from fuzzywuzzy import process
import locale

# de texto a voz
motor = pyttsx3.init()

voces = motor.getProperty('voices')
motor.setProperty('voice', voces[0].id) # cambiar a 0 sino sale fuera del rango

motor.setProperty('rate', 100) # rapidez de la voz

# reconocimiento de voz
reconocedor = sr.Recognizer()

# obtener la ubicación
geolocalizador = Nominatim(user_agent="geolocator")

# manejo de idioma
idioma_actual = "es-ES"

def hablar(texto):
    motor.say(texto)
    motor.runAndWait()

def obtener_audio():
    with sr.Microphone() as source:
        print("Escuchando...")
        reconocedor.adjust_for_ambient_noise(source)
        audio = reconocedor.listen(source)
        print("Procesando...")

    try:
        comando = reconocedor.recognize_google(audio, language=idioma_actual)
        print("Comando detectado (voz): " + comando)
        return comando.lower()
    except sr.UnknownValueError:
        print("No se pudo entender el comando (voz).")
        return ""
    except sr.RequestError as e:
        print("Error en la solicitud al servicio de reconocimiento de voz: {0}".format(e))
        return ""

def obtener_texto():
    texto = input("Ingrese un comando: ")
    return texto.lower()

def obtener_volumen():
    dispositivos = AudioUtilities.GetSpeakers()
    interface = dispositivos.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volumen = cast(interface, POINTER(IAudioEndpointVolume))
    return volumen.GetMasterVolumeLevelScalar()

def establecer_volumen(nivel):
    dispositivos = AudioUtilities.GetSpeakers()
    interface = dispositivos.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volumen = cast(interface, POINTER(IAudioEndpointVolume))
    volumen.SetMasterVolumeLevelScalar(nivel, None)

def silenciar_volumen():
    dispositivos = AudioUtilities.GetSpeakers()
    interface = dispositivos.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volumen = cast(interface, POINTER(IAudioEndpointVolume))
    volumen.SetMute(1, None)  

def desmutear_volumen():
    dispositivos = AudioUtilities.GetSpeakers()
    interface = dispositivos.Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volumen = cast(interface, POINTER(IAudioEndpointVolume))
    volumen.SetMute(0, None)  

def obtener_informacion_pais(nombre_pais):
    try:
        # API
        respuesta = requests.get(f"https://restcountries.com/v3.1/name/{nombre_pais}")
        
        if respuesta.status_code == 200:
            datos = respuesta.json()  # Convertir la respuesta a JSON
            
            # Extraer información relevante
            pais = datos[0] 
            capital = pais.get("capital", ["No disponible"])[0]
            region = pais.get("region", "No disponible")
            subregion = pais.get("subregion", "No disponible")
            idioma = ", ".join(pais["languages"].values())  # los idiomas

            hablar(f"La capital de {nombre_pais.capitalize()} es {capital}.")
            hablar(f"{nombre_pais.capitalize()} está en la región {region}, subregión {subregion}.")
            hablar(f"Los idiomas hablados en {nombre_pais.capitalize()} son: {idioma}.")
        else:
            hablar(f"No se pudo obtener información para {nombre_pais}.")
    except Exception as e:
        hablar(f"Error al obtener la información: {e}")

def obtener_ubicacion():
    try:
        with sr.Microphone() as source:
            hablar("Dime tu ubicación actual")
            reconocedor.adjust_for_ambient_noise(source)
            audio = reconocedor.listen(source)
        consulta_ubicacion = reconocedor.recognize_google(audio, language=idioma_actual).lower()
        print("Ubicación detectada (voz): " + consulta_ubicacion)
        
        # obtener la ubicación
        ubicacion = geolocalizador.geocode(consulta_ubicacion)
        
        if ubicacion:
            hablar(f"Estás en {ubicacion.address}")
        else:
            hablar("No se pudo obtener la ubicación.")
    except sr.UnknownValueError:
        hablar("No se pudo entender la ubicación.")
    except sr.RequestError as e:
        hablar(f"Error al obtener la ubicación: {e}")

def calcular_distancia():
    try:
        with sr.Microphone() as source:
            hablar("Dime los dos lugares para calcular la distancia")
            reconocedor.adjust_for_ambient_noise(source)
            audio = reconocedor.listen(source)
        consulta_ubicacion = reconocedor.recognize_google(audio, language=idioma_actual).lower()
        print("Ubicación detectada (voz): " + consulta_ubicacion)
        
        lugares = consulta_ubicacion.split("y")
        if len(lugares) == 2:
            # Obtener coordenadas
            lugar1 = geolocalizador.geocode(lugares[0].strip())
            lugar2 = geolocalizador.geocode(lugares[1].strip())
            
            if lugar1 and lugar2:
                coords_1 = (lugar1.latitude, lugar1.longitude)
                coords_2 = (lugar2.latitude, lugar2.longitude)
                distancia = geodesic(coords_1, coords_2).kilometers
                hablar(f"La distancia entre {lugares[0]} y {lugares[1]} es de {distancia:.2f} kilómetros.")
            else:
                hablar("No se pudo obtener las ubicaciones.")
        else:
            hablar("Por favor, proporciona dos lugares separados por 'y'.")
    except sr.UnknownValueError:
        hablar("No se pudo entender la ubicación o las ciudades.")
    except sr.RequestError as e:
        hablar(f"Error al obtener la ubicación: {e}")

def procesar_comando(comando):
    global idioma_actual  
    # Usamos fuzzywuzzy para manejar variaciones y errores tipográficos
    comando = comando.strip()
    
    palabras_clave = [
        "hora", "fecha", "ubicación", "distancia", "capital", "región", "departamento", 
        "abrir", "subir volumen", "bajar volumen", "silenciar", "desmutear", "detener", 
        "cambiar idioma"
    ]
    
    mejor_coincidencia, puntuacion = process.extractOne(comando, palabras_clave)
    
    if puntuacion < 80: 
        mejor_coincidencia = comando
    
    if "hora" in mejor_coincidencia:
        if idioma_actual == "es-ES":
            locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")
        else:
            locale.setlocale(locale.LC_TIME, "en_US.UTF-8")
        
        hora_actual = datetime.datetime.now().strftime("%H:%M")
        hablar(f"La hora actual es {hora_actual}")
    elif "fecha" in mejor_coincidencia:
        if idioma_actual == "es-ES":
            locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")
        else:
            locale.setlocale(locale.LC_TIME, "en_US.UTF-8")
        
        fecha_actual = datetime.datetime.now().strftime("%d de %B de %Y")
        hablar(f"La fecha actual es {fecha_actual}")
    elif "ubicación" in mejor_coincidencia or "donde estoy" in mejor_coincidencia or "donde me encuentro" in mejor_coincidencia:
        obtener_ubicacion()
    elif "distancia" in mejor_coincidencia or "distancia entre" in mejor_coincidencia:
        calcular_distancia()
    elif "capital" in mejor_coincidencia or "región" in mejor_coincidencia or "departamento" in mejor_coincidencia:
        nombre_pais = comando.split("de")[-1].strip() 
        obtener_informacion_pais(nombre_pais)
    elif any(palabra in mejor_coincidencia for palabra in ["abrir", "abre", "open"]):
        sitios = {
            "youtube": "YouTube",
            "maps": "Google Maps",
            "chat gpt": "Chat GPT",
            "facebook": "Facebook",
            "instagram": "Instagram"
        }
        
        urls_a_abrir = []
        
        for sitio, nombre in sitios.items():
            if sitio in comando:
                urls_a_abrir.append(nombre)
        
        if not urls_a_abrir:
            hablar("Sitio no reconocido. ¿Puedo ayudarte con algo más?")
            return

        for nombre in urls_a_abrir:
            hablar(f"Abriendo {nombre}.")
            webbrowser.open(f"https://www.{nombre.lower().replace(' ', '')}.com")
    
    elif "cambiar idioma" in mejor_coincidencia:
        hablar("¿A qué idioma te gustaría cambiar?")
        idioma_nuevo = obtener_audio()
        if "inglés" in idioma_nuevo:
            idioma_actual = "en-US"
            hablar("Idioma cambiado a inglés.")
        elif "español" in idioma_nuevo:
            idioma_actual = "es-ES"
            hablar("Idioma cambiado a español.")
        else:
            hablar("Idioma no reconocido. Continuamos en español.")
    
    elif "detener" in mejor_coincidencia:
        hablar("Hasta luego")
        return True

    elif "subir volumen" in mejor_coincidencia:
        volumen_actual = obtener_volumen()
        if volumen_actual < 1.0:
            establecer_volumen(min(volumen_actual + 0.1, 1.0))
        hablar("Volumen aumentado.")

    elif "bajar volumen" in mejor_coincidencia:
        volumen_actual = obtener_volumen()
        if volumen_actual > 0.0:
            establecer_volumen(max(volumen_actual - 0.1, 0.0))
        hablar("Volumen reducido.")

    elif "silenciar" in mejor_coincidencia:
        silenciar_volumen()
        hablar("Volumen silenciado.")

    elif "desmutear" in mejor_coincidencia:
        desmutear_volumen()
        hablar("Volumen activado.")

    return False

if __name__ == "__main__":
    hablar("Hola, ¿en qué puedo ayudarte?")
    
    while True:
        print("Opciones:")
        print("1: Audio")
        print("2: Escribir")
        tipo_entrada = input("¿Quieres hablar o escribir? (1/2): ").lower()

        if tipo_entrada == '1':
            comando = obtener_audio()
        elif tipo_entrada == '2':
            comando = obtener_texto()
        else:
            print("Entrada no válida. Intenta de nuevo.")
            continue

        if procesar_comando(comando):
            break
