from telethon.sync import TelegramClient, events
import re
import json
import os
from datetime import datetime

# ==== CONFIGURAÇÕES INICIAIS ====
api_id = 23565949
api_hash = '5ffa446ffd412847ac9ffd654c88e6cd'
session_name = 'Botdos1000'
grupo_origem = '[FT] VIP LUCAS TYLTY 🐍'
grupo_destino = 'https://t.me/linkeyeudy'

# ==== FUNÇÕES AUXILIARES ====

def carregar_banca():
    if os.path.exists('banca.json'):
        with open('banca.json', 'r') as f:
            return json.load(f)['banca']
    else:
        return 1000.0

def salvar_banca(nova_banca):
    with open('banca.json', 'w') as f:
        json.dump({'banca': nova_banca}, f)

def calcular_valor_aposta(unidades, banca):
    unidade_valor = banca / 100
    return round(unidades * unidade_valor, 2)

def salvar_tip(msg_id, valor_apostado):
    tips = {}
    if os.path.exists('tips_ativas.json'):
        with open('tips_ativas.json', 'r') as f:
            tips = json.load(f)
    tips[str(msg_id)] = valor_apostado
    with open('tips_ativas.json', 'w') as f:
        json.dump(tips, f)

def carregar_tip(msg_id):
    if os.path.exists('tips_ativas.json'):
        with open('tips_ativas.json', 'r') as f:
            tips = json.load(f)
        return tips.get(str(msg_id))
    return None

def remover_tip(msg_id):
    if os.path.exists('tips_ativas.json'):
        with open('tips_ativas.json', 'r') as f:
            tips = json.load(f)
        if str(msg_id) in tips:
            del tips[str(msg_id)]
        with open('tips_ativas.json', 'w') as f:
            json.dump(tips, f)

def dentro_do_horario():
    agora = datetime.now().hour
    return 9 <= agora <= 23

# ==== BOT INICIADO ====

client = TelegramClient('Botdos1000', api_id, api_hash)
client.start()

@client.on(events.NewMessage(chats=grupo_origem))
async def handler(event):
    if not dentro_do_horario():
        return

    mensagem = event.message.message
    msg_id = event.message.id

    # === NOVO FORMATO: TIP ENCONTRADA ===
    if "TIP ENCONTRADA" in mensagem.upper():
        links = re.findall(r'(https?://[^\s,]+)', mensagem)
        unidades_match = re.search(r'Unidades:\s*(\d+)', mensagem)
        tipo_match = re.search(r'Tipo de Aposta:\s*(.*)', mensagem)

        if links and unidades_match and tipo_match:
            unidades = float(unidades_match.group(1))
          
