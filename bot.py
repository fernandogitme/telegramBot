import os
import json
import tempfile
import whisper
import ollama
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    ChatMemberHandler,
    filters,
)
from TTS.api import TTS

# Cargar .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Cargar modelo de Whisper
modelo_whisper = whisper.load_model("large-v3")

# Configurar Ollama
OLLAMA_MODEL = "phi3:3.8b-mini-128k-instruct-q4_K_M"
print("Inicializando TTS...")

# Variables globales para TTS
tts = None
tts_speaker = None

def get_available_speakers(tts_instance):
    """Obtiene la lista de speakers disponibles"""
    try:
        speaker_manager = tts_instance.synthesizer.tts_model.speaker_manager
        if speaker_manager and hasattr(speaker_manager, 'speakers'):
            return list(speaker_manager.speakers.keys())
    except Exception as e:
        print(f"Error obteniendo speakers: {e}")
    
    # Fallback con speakers conocidos
    return ["Claribel Dervla", "Daisy Studious", "Andrew Chipper", "Craig Gutsy"]

TEXTO_INSTRUCCIONES_BASICAS = (
    "**⚙️ Para empezar, cada miembro debe hacer esto:**\n"
    "1. Usen el comando `/idioma` seguido del código de su idioma. Por ejemplo, si hablan español, escriban:\n"
    "`/idioma es`\n\n"
    "2. Para ver una lista de idiomas disponibles, usen el comando `/idiomas_disponibles`."
)

try:
    tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", gpu=True)
    
    # Obtener speakers disponibles y seleccionar uno
    speakers = get_available_speakers(tts)
    if speakers:
        tts_speaker = speakers[0]  # Usar el primer speaker disponible
        print(f"✅ TTS inicializado correctamente con speaker: {tts_speaker}")
    else:
        print("❌ No se pudieron obtener speakers, TTS deshabilitado")
        tts = None
        
except Exception as e:
    print(f"❌ Error crítico al inicializar TTS: {e}")
    print("El bot funcionará sin la capacidad de enviar audios.")
    tts = None
    tts_speaker = None
    
# Archivo JSON y estructura base
ARCHIVO_IDIOMAS = "idiomas.json"
idiomas = {}

if os.path.exists(ARCHIVO_IDIOMAS):
    try:
        with open(ARCHIVO_IDIOMAS, "r") as f:
            idiomas = json.load(f)
    except json.JSONDecodeError:
        idiomas = {}

def guardar_idiomas():
    with open(ARCHIVO_IDIOMAS, "w") as f:
        json.dump(idiomas, f)

# Diccionario de códigos de idioma a nombres completos
NOMBRES_IDIOMAS = {
    'es': 'spanish',
    'en': 'english',
    'fr': 'french',
    'de': 'german',
    'it': 'italian',
    'pt': 'portuguese',
    'ru': 'russian',
    'ja': 'japanese',
    'ko': 'korean',
    'zh': 'chinese',
    'ar': 'arabic',
    'hi': 'hindi',
    'nl': 'dutch',
    'sv': 'swedish',
    'da': 'danish',
    'no': 'norwegian',
    'fi': 'finnish',
    'pl': 'polish',
    'tr': 'turkish',
    'he': 'hebrew',
    'th': 'thai',
    'vi': 'vietnamese',
    'id': 'indonesian',
    'ms': 'malay',
    'tl': 'tagalog',
    'ca': 'catalan',
    'eu': 'basque',
    'gl': 'galician',
    'uk': 'ukrainian',
    'cs': 'czech',
    'sk': 'slovak',
    'hu': 'hungarian',
    'ro': 'romanian',
    'bg': 'bulgarian',
    'hr': 'croatian',
    'sr': 'serbian',
    'sl': 'slovenian',
    'et': 'estonian',
    'lv': 'latvian',
    'lt': 'lithuanian',
    'mt': 'maltese',
    'is': 'icelandic',
    'cy': 'welsh',
    'ga': 'irish',
    'mk': 'macedonian',
    'be': 'belarusian',
    'kk': 'kazakh',
    'hy': 'armenian',
    'az': 'azerbaijani',
    'ka': 'georgian',
    'my': 'myanmar',
    'km': 'khmer',
    'lo': 'lao',
    'si': 'sinhala',
    'ne': 'nepali',
    'bn': 'bengali',
    'ur': 'urdu',
    'fa': 'persian',
    'ps': 'pashto',
    'sd': 'sindhi',
    'gu': 'gujarati',
    'pa': 'punjabi',
    'ml': 'malayalam',
    'kn': 'kannada',
    'ta': 'tamil',
    'te': 'telugu',
    'mr': 'marathi',
    'or': 'odia',
    'as': 'assamese',
    'sa': 'sanskrit',
    'bo': 'tibetan',
    'dz': 'dzongkha',
    'mn': 'mongolian',
    'ug': 'uyghur',
    'ky': 'kyrgyz',
    'uz': 'uzbek',
    'tk': 'turkmen',
    'tg': 'tajik',
    'am': 'amharic',
    'ti': 'tigrinya',
    'om': 'oromo',
    'so': 'somali',
    'sw': 'swahili',
    'rw': 'kinyarwanda',
    'yo': 'yoruba',
    'ig': 'igbo',
    'ha': 'hausa',
    'zu': 'zulu',
    'af': 'afrikaans',
    'sq': 'albanian',
    'eu': 'basque',
    'br': 'breton',
    'co': 'corsican',
    'eo': 'esperanto',
    'fy': 'frisian',
    'gd': 'scots gaelic',
    'gl': 'galician',
    'jv': 'javanese',
    'la': 'latin',
    'lb': 'luxembourgish',
    'mi': 'maori',
    'oc': 'occitan',
    'sn': 'shona',
    'st': 'sesotho',
    'su': 'sundanese',
    'tl': 'filipino',
    'xh': 'xhosa'
}

# Mapeo de idiomas soportados por XTTS_v2
IDIOMAS_SOPORTADOS_TTS = {
    'es', 'en', 'fr', 'de', 'it', 'pt', 'pl', 'tr', 'ru', 'nl', 'cs', 'ar', 'zh', 'ja', 'hu', 'ko'
}

def limpiar_chat_del_json(chat_id):
    """
    Elimina un chat del JSON de idiomas
    """
    chat_id_str = str(chat_id)
    if chat_id_str in idiomas:
        del idiomas[chat_id_str]
        guardar_idiomas()
        print(f"🗑️ Chat {chat_id} eliminado del JSON")
        return True
    return False

def limpiar_usuario_del_json(chat_id, user_id):
    """
    Elimina un usuario específico del JSON de idiomas
    """
    chat_id_str = str(chat_id)
    user_id_str = str(user_id)
    
    if chat_id_str in idiomas and user_id_str in idiomas[chat_id_str]:
        del idiomas[chat_id_str][user_id_str]
        
        # Si no quedan usuarios en el chat, eliminar el chat completo
        if not idiomas[chat_id_str]:
            del idiomas[chat_id_str]
            print(f"🗑️ Chat {chat_id} eliminado completamente (sin usuarios)")
        else:
            print(f"🗑️ Usuario {user_id} eliminado del chat {chat_id}")
        
        guardar_idiomas()
        return True
    return False

async def verificar_y_limpiar_usuarios_inactivos(context, chat_id):
    """
    Verifica qué usuarios del JSON siguen siendo miembros del grupo y elimina los que no
    """
    chat_id_str = str(chat_id)
    
    if chat_id_str not in idiomas:
        return
    
    usuarios_a_eliminar = []
    
    for user_id in idiomas[chat_id_str].keys():
        try:
            # Intentar obtener información del miembro del chat
            chat_member = await context.bot.get_chat_member(chat_id, int(user_id))
            
            # Si el usuario no es miembro activo, agregarlo a la lista de eliminación
            if chat_member.status in ['left', 'kicked', 'banned']:
                usuarios_a_eliminar.append(user_id)
                print(f"❌ Usuario {user_id} no es miembro activo (status: {chat_member.status})")
                
        except Exception as e:
            # Si no se puede obtener información del usuario, probablemente ya no está en el grupo
            print(f"❌ No se pudo verificar usuario {user_id}: {e}")
            usuarios_a_eliminar.append(user_id)
    
    # Eliminar usuarios que ya no están en el grupo
    for user_id in usuarios_a_eliminar:
        limpiar_usuario_del_json(chat_id, user_id)
    
    if usuarios_a_eliminar:
        print(f"🧹 Limpiados {len(usuarios_a_eliminar)} usuarios inactivos del chat {chat_id}")

def agrupar_usuarios_por_idioma(participantes, idioma_detectado):
    """
    Agrupa usuarios por idioma, excluyendo aquellos que ya tienen el idioma detectado
    """
    usuarios_por_idioma = {}
    
    for uid, lang in participantes.items():
        if lang != idioma_detectado:
            if lang not in usuarios_por_idioma:
                usuarios_por_idioma[lang] = []
            usuarios_por_idioma[lang].append(uid)
    
    return usuarios_por_idioma

async def obtener_nombres_usuarios(context, chat_id, user_ids):
    """
    Obtiene los nombres de los usuarios para mencionar
    """
    nombres = []
    for uid in user_ids:
        try:
            chat_member = await context.bot.get_chat_member(chat_id, int(uid))
            nombre = chat_member.user.first_name
            # Agregar @ para mención si el usuario tiene username
            if chat_member.user.username:
                nombres.append(f"@{chat_member.user.username}")
            else:
                nombres.append(nombre)
        except Exception as e:
            print(f"❌ Error al obtener nombre de usuario {uid}: {e}")
            nombres.append(f"Usuario {uid}")
    
    return nombres

async def traducir_texto(texto, idioma_origen, idioma_destino):
    """
    Traduce texto usando Ollama
    """
    try:
        print(f"🔄 Traduciendo de {idioma_origen} a {idioma_destino}")
        print(f"📝 Texto original: {texto}")
        
        # Convertir códigos de idioma a nombres completos
        nombre_origen = NOMBRES_IDIOMAS.get(idioma_origen, idioma_origen)
        nombre_destino = NOMBRES_IDIOMAS.get(idioma_destino, idioma_destino)
        
        print(f"🌐 Idiomas: {nombre_origen} → {nombre_destino}")
        
        # Crear prompt para traducción
        prompt = f"""Translate the following text from {nombre_origen} to {nombre_destino}. 
        Only provide the translation, no additional text or explanations.
        The text you'll receive comes from an automatic transcription, so it has errors. Please translate it without any mistakes.
        Remember you will only say the translation from the input. No more explanation.

        Text to translate: "{texto}"

        Translation:"""
        
        print(f"🤖 Enviando a Ollama...")
        
        # Generar traducción con Ollama
        response = ollama.generate(
            model=OLLAMA_MODEL,
            prompt=prompt,
            stream=False
        )
        
        traduccion = response['response'].strip()
        print(f"✅ Traducción recibida: {traduccion}")
        
        return traduccion
        
    except Exception as e:
        print(f"❌ Error en traducción: {e}")
        return f"[Error de traducción] {texto}"

async def verificar_miembros_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Verifica si el bot se quedó solo en un grupo y limpia el JSON
    """
    try:
        chat_id = update.effective_chat.id
        
        # Solo verificar en grupos (no en chats privados)
        if update.effective_chat.type not in ['group', 'supergroup']:
            return
        
        # Obtener número de miembros del chat
        member_count = await context.bot.get_chat_member_count(chat_id)
        
        print(f"👥 Verificando miembros en chat {chat_id}: {member_count} miembros")
        
        # Si solo hay 1 miembro (el bot), limpiar del JSON
        if member_count <= 1:
            limpiar_chat_del_json(chat_id)
            print(f"🏃‍♂️ Bot se quedó solo en chat {chat_id}, datos eliminados")
            
            # Opcional: intentar salir del grupo
            try:
                await context.bot.leave_chat(chat_id)
                print(f"👋 Bot salió del chat {chat_id}")
            except Exception as e:
                print(f"❌ No se pudo salir del chat {chat_id}: {e}")
                
    except Exception as e:
        print(f"❌ Error verificando miembros del chat: {e}")

async def manejar_cambio_miembros(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Maneja cambios en la membresía del chat (usuarios que se unen/salen)
    """
    try:
        chat_id = update.effective_chat.id
        
        # Obtener información del cambio - FIX: chat_member es un objeto, no una lista
        chat_member_update = update.chat_member
        if not chat_member_update:
            return
            
        user_id = chat_member_update.new_chat_member.user.id
        old_status = chat_member_update.old_chat_member.status
        new_status = chat_member_update.new_chat_member.status
        
        print(f"🔄 Cambio de miembro en chat {chat_id}: Usuario {user_id} {old_status} → {new_status}")
        
        # Si el usuario salió/fue expulsado/baneado
        if new_status in ['left', 'kicked', 'banned']:
            # Limpiar usuario del JSON
            limpiar_usuario_del_json(chat_id, user_id)
            
            # Verificar si el bot se quedó solo después de esta salida
            await verificar_miembros_chat(update, context)
            
        # Si el bot fue expulsado del grupo
        elif chat_member_update.new_chat_member.user.id == context.bot.id and new_status in ['left', 'kicked', 'banned']:
            print(f"🚫 Bot expulsado del chat {chat_id}")
            limpiar_chat_del_json(chat_id)
                
    except Exception as e:
        print(f"❌ Error manejando cambio de miembros: {e}")

async def manejar_migracion_grupo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Maneja cuando un grupo se convierte en supergrupo (migración)
    """
    try:
        if update.message.migrate_from_chat_id:
            old_chat_id = str(update.message.migrate_from_chat_id)
            new_chat_id = str(update.effective_chat.id)
            
            print(f"🔄 Migración de grupo: {old_chat_id} → {new_chat_id}")
            
            # Migrar datos del JSON
            if old_chat_id in idiomas:
                idiomas[new_chat_id] = idiomas[old_chat_id]
                del idiomas[old_chat_id]
                guardar_idiomas()
                print(f"✅ Datos migrados exitosamente")
                
    except Exception as e:
        print(f"❌ Error en migración de grupo: {e}")

async def comando_limpiar_json(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Comando administrativo para limpiar manualmente el JSON
    """
    try:
        # Solo permitir en chats privados o a administradores
        if update.effective_chat.type == 'private':
            # Limpiar todos los chats inactivos
            chats_eliminados = []
            for chat_id in list(idiomas.keys()):
                try:
                    member_count = await context.bot.get_chat_member_count(int(chat_id))
                    if member_count <= 1:
                        del idiomas[chat_id]
                        chats_eliminados.append(chat_id)
                except:
                    # Chat no existe o bot no tiene acceso
                    del idiomas[chat_id]
                    chats_eliminados.append(chat_id)
            
            if chats_eliminados:
                guardar_idiomas()
                await update.message.reply_text(f"🗑️ Eliminados {len(chats_eliminados)} chats inactivos del JSON")
            else:
                await update.message.reply_text("✅ No hay chats inactivos para limpiar")
        else:
            # En grupos, permitir limpiar solo ese chat específico
            chat_id = update.effective_chat.id
            await verificar_y_limpiar_usuarios_inactivos(context, chat_id)
            await update.message.reply_text("✅ Usuarios inactivos verificados y eliminados")
                
    except Exception as e:
        print(f"❌ Error en comando limpiar: {e}")
        await update.message.reply_text("❌ Error al limpiar el JSON")

# Comandos
async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Muestra un mensaje de ayuda completo con instrucciones de uso.
    """
    texto_ayuda = (
        "🤖 **¡Hola! Soy el bot de traducción por voz.**\n\n"
        "Mi función es transcribir y traducir automáticamente las notas de voz que se envían en este chat para que todos puedan entenderse.\n\n"
        "**¿Cómo funciono?**\n"
        "1. Cada usuario configura su idioma una sola vez.\n"
        "2. Alguien envía un audio.\n"
        "3. Yo lo transcribo y lo envío como texto. Si hay usuarios con otros idiomas configurados, también envío la traducción para ellos.\n\n"
        "--- \n\n"
        "**COMANDOS DISPONIBLES**\n\n"
        "⚙️ `/idioma <código>`\n"
        "Configura tu idioma. ¡Este es el paso más importante! Reemplaza `<código>` por el de tu idioma.\n"
        "*Ejemplos:*\n"
        "`/idioma es` (para español)\n"
        "`/idioma en` (para inglés)\n"
        "`/idioma fr` (para francés)\n\n"
        "🌍 `/idiomas_disponibles`\n"
        "Muestra la lista completa de códigos de idioma que puedes usar.\n\n"
        "ℹ️ `/ayuda`\n"
        "Muestra este mensaje de ayuda."
    )
    await update.message.reply_text(texto_ayuda, parse_mode='Markdown')

# Hacemos que /start sea un alias de /ayuda
start = ayuda

async def idiomas_disponibles(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Muestra una lista formateada de los idiomas disponibles.
    """
    try:
        lista_idiomas = []
        # Agrupar los idiomas en columnas para que sea más legible
        columnas = 3
        items_por_columna = -(-len(NOMBRES_IDIOMAS) // columnas)  # Ceiling division
        nombres_ordenados = sorted(NOMBRES_IDIOMAS.items())
        
        # Crear la lista de texto formateado
        for i in range(items_por_columna):
            linea = []
            for j in range(columnas):
                index = i + j * items_por_columna
                if index < len(nombres_ordenados):
                    codigo, nombre = nombres_ordenados[index]
                    linea.append(f"`{codigo}` - {nombre.capitalize()}")
            lista_idiomas.append("   ".join(linea))

        texto_final = "🌍 **Idiomas Disponibles** 🌍\n\nUsa el código de la izquierda con el comando `/idioma`.\n\n" + "\n".join(lista_idiomas)
        
        # Telegram tiene un límite de 4096 caracteres por mensaje. Si la lista es muy larga, la dividimos.
        if len(texto_final) > 4096:
            await update.message.reply_text("La lista de idiomas es muy larga. Aquí están los más comunes:\n`es` - Español, `en` - Inglés, `fr` - Francés, `de` - Alemán, `pt` - Portugués, `it` - Italiano, `ja` - Japonés, `zh` - Chino, `ru` - Ruso.")
        else:
            await update.message.reply_text(texto_final, parse_mode='Markdown')
            
    except Exception as e:
        print(f"Error en /idiomas_disponibles: {e}")
        await update.message.reply_text("❌ No se pudo mostrar la lista de idiomas.")
        
async def idioma(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("Uso: /idioma <código_idioma> (ej: /idioma en)")
        return

    idioma = context.args[0].lower()
    user_id = str(update.message.from_user.id)
    chat_id = str(update.message.chat_id)

    if chat_id not in idiomas:
        idiomas[chat_id] = {}

    idiomas[chat_id][user_id] = idioma
    guardar_idiomas()
    
    print(f"🔧 Idioma configurado: Usuario {user_id} → {idioma}")
    await update.message.reply_text(f"Idioma registrado: {idioma}")

async def mostrar_idiomas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.message.chat_id)
    if chat_id in idiomas:
        texto = "\n".join(f"{uid}: {lang}" for uid, lang in idiomas[chat_id].items())
    else:
        texto = "No hay idiomas registrados en este grupo."
    await update.message.reply_text(f"Idiomas en este grupo:\n{texto}")

# Manejar audios (voice o audio)
async def manejar_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("🎵 Audio recibido, procesando...")
    
    archivo = update.message.voice or update.message.audio
    if not archivo:
        print("❌ No se encontró archivo de audio")
        await update.message.reply_text("No se encontró archivo de audio.")
        return

    chat_id = str(update.message.chat_id)
    
    if update.effective_chat.type in ['group', 'supergroup']:
        await verificar_y_limpiar_usuarios_inactivos(context, chat_id)

    print("⬇️ Descargando audio...")
    archivo_file = await archivo.get_file()
    with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as temp:
        await archivo_file.download_to_drive(temp.name)
        temp_path = temp.name

    try:
        print("🎯 Transcribiendo con Whisper...")
        resultado = modelo_whisper.transcribe(temp_path)
        texto = resultado["text"]
        idioma_detectado = resultado["language"]

        print(f"📝 Transcripción: {texto}")
        print(f"🌐 Idioma detectado: {idioma_detectado}")

        if chat_id not in idiomas:
            idiomas[chat_id] = {}

        participantes = idiomas.get(chat_id, {})
        usuarios_por_idioma = agrupar_usuarios_por_idioma(participantes, idioma_detectado)

        print(f"👥 Participantes: {participantes}")
        print(f"🗂️ Usuarios agrupados por idioma: {usuarios_por_idioma}")

        if usuarios_por_idioma:
            print("🔄 Hay usuarios que necesitan traducción")
            
            usuario_remitente = update.message.from_user
            
            # Enviar mensaje original
            await update.message.reply_text(f"📝 {usuario_remitente.first_name}: {texto}")
            
            for idioma_destino, user_ids in usuarios_por_idioma.items():
                try:
                    print(f"🔄 Traduciendo para idioma {idioma_destino} ({len(user_ids)} usuarios)")
                    
                    nombres_usuarios = await obtener_nombres_usuarios(context, chat_id, user_ids)
                    texto_traducido = await traducir_texto(texto, idioma_detectado, idioma_destino)
                    
                    mencion = f"Para {', '.join(nombres_usuarios)}"
                    
                    await update.message.reply_text(
                        f"🌐 {mencion} ({NOMBRES_IDIOMAS.get(idioma_destino, idioma_destino)}): {texto_traducido}"
                    )
                    
                    # --- INICIO: FUNCIONALIDAD TTS CORREGIDA ---
                    if tts and tts_speaker and idioma_destino in IDIOMAS_SOPORTADOS_TTS:
                        temp_audio_path = None
                        try:
                            print(f"🎤 Generando audio TTS para el idioma: {idioma_destino}")
                            # Crear un archivo temporal para el audio de salida
                            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
                                temp_audio_path = temp_audio.name
                            
                            # Generar el audio desde el texto traducido CON SPEAKER
                            tts.tts_to_file(
                                text=texto_traducido,
                                language=idioma_destino,
                                speaker=tts_speaker,  # ESTE ERA EL PARÁMETRO FALTANTE
                                file_path=temp_audio_path
                            )
                            print(f"✅ Audio temporal generado en: {temp_audio_path}")
                            
                            # Enviar el audio como un mensaje de voz
                            await context.bot.send_voice(
                                chat_id=chat_id,
                                voice=open(temp_audio_path, 'rb')
                            )
                            print(f"🔊 Audio enviado al chat {chat_id}")
                            
                        except Exception as e:
                            print(f"❌ Error al generar o enviar el audio TTS: {e}")
                        finally:
                            # Asegurarse de eliminar el archivo temporal para no ocupar espacio
                            if temp_audio_path and os.path.exists(temp_audio_path):
                                os.unlink(temp_audio_path)
                                print(f"🧹 Archivo de audio temporal eliminado: {temp_audio_path}")
                    elif tts and idioma_destino not in IDIOMAS_SOPORTADOS_TTS:
                        print(f"⚠️ Idioma {idioma_destino} no soportado por TTS")
                    # --- FIN: FUNCIONALIDAD TTS CORREGIDA ---
                    
                except Exception as e:
                    print(f"❌ Error al traducir para idioma {idioma_destino}: {e}")
                    await update.message.reply_text(f"❌ Error al traducir para idioma {idioma_destino}")
        else:
            print("✅ No se necesita traducción, todos entienden el idioma.")

    except Exception as e:
        print(f"❌ Error general en manejar_audio: {e}")
        await update.message.reply_text("❌ Error al procesar el audio")
    
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
            print("🧹 Archivo de audio entrante temporal eliminado")

async def bienvenida(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Función que se ejecuta cuando se agregan nuevos miembros al grupo
    """
    try:
        # Verificar si el bot es uno de los nuevos miembros
        nuevos_miembros = update.message.new_chat_members
        bot_agregado = any(member.id == context.bot.id for member in nuevos_miembros)
        
        if bot_agregado:
            print(f"🎉 Bot agregado al grupo: {update.effective_chat.title}")
            texto_bienvenida = (
                "¡Hola a todos! 👋 Soy su **asistente de traducción por voz**.\n\n"
                "Mi trabajo es simple: cuando envíen una nota de voz, la transcribiré y la traduciré para aquellos que hablen un idioma diferente.\n\n"
                f"{TEXTO_INSTRUCCIONES_BASICAS}\n\n"
                "¡Estoy listo para romper las barreras del idioma! 🎤🌍"
            )
            await update.message.reply_text(texto_bienvenida, parse_mode='Markdown')
        else:
            # Si otros usuarios se unen al grupo, también mostrar instrucciones básicas
            nombres_nuevos = [member.first_name for member in nuevos_miembros if not member.is_bot]
            if nombres_nuevos:
                # Verificar si estos usuarios ya estaban en el grupo antes
                chat_id = str(update.effective_chat.id)
                usuarios_existentes = set(idiomas.get(chat_id, {}).keys())
                
                # Filtrar solo usuarios realmente nuevos (que no tienen idioma configurado)
                usuarios_nuevos = []
                for member in nuevos_miembros:
                    if not member.is_bot and str(member.id) not in usuarios_existentes:
                        usuarios_nuevos.append(member.first_name)
                
                if usuarios_nuevos:
                    texto_nuevos = (
                        f"¡Bienvenidos {', '.join(usuarios_nuevos)}! 👋\n\n"
                        f"{TEXTO_INSTRUCCIONES_BASICAS}"
                    )
                    await update.message.reply_text(texto_nuevos, parse_mode='Markdown')
                
    except Exception as e:
        print(f"❌ Error en función bienvenida: {e}")     
        
        
# Función adicional para manejar cuando el bot se añade a un grupo (alternativa)
async def bot_agregado_grupo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Función específica para cuando el bot es agregado a un grupo
    """
    try:
        if update.message.new_chat_members:
            for member in update.message.new_chat_members:
                if member.id == context.bot.id:
                    print(f"🎉 Bot agregado al grupo: {update.effective_chat.title} ({update.effective_chat.id})")
                    
                    texto_inicial = (
                        "¡Hola a todos! 👋 Soy su **asistente de traducción por voz**.\n\n"
                        "🎯 **¿Qué hago?**\n"
                        "• Transcribo automáticamente las notas de voz\n"
                        "• Las traduzco para usuarios que hablen otros idiomas\n"
                        "• Genero audio de las traducciones (cuando es posible)\n\n"
                        f"{TEXTO_INSTRUCCIONES_BASICAS}\n\n"
                        "💡 **Tip:** Usen `/ayuda` para ver todos los comandos disponibles.\n\n"
                        "¡Estoy listo para romper las barreras del idioma! 🎤🌍"
                    )
                    
                    await update.message.reply_text(texto_inicial, parse_mode='Markdown')
                    break
                    
    except Exception as e:
        print(f"❌ Error al procesar bot agregado al grupo: {e}")

# Main
def main():
    print("🚀 Iniciando bot...")
    app = ApplicationBuilder().token(TOKEN).build()

    # Comandos básicos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ayuda", ayuda))
    app.add_handler(CommandHandler("idiomas_disponibles", idiomas_disponibles))
    app.add_handler(CommandHandler("idioma", idioma))
    app.add_handler(CommandHandler("mostrar_idiomas", mostrar_idiomas))
    app.add_handler(CommandHandler("limpiar_json", comando_limpiar_json))
    
    # Handlers de mensajes
    app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, manejar_audio))
    
    # IMPORTANTE: Estos handlers deben estar activos para que funcione la bienvenida
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, bienvenida))
    app.add_handler(MessageHandler(filters.StatusUpdate.MIGRATE, manejar_migracion_grupo))
    
    # Handler para cambios de miembros
    app.add_handler(ChatMemberHandler(manejar_cambio_miembros, ChatMemberHandler.CHAT_MEMBER))
    
    print("Bot en marcha...")
    app.run_polling()

if __name__ == "__main__":
    main()