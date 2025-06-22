from telethon import TelegramClient, events
import re
import json
import os
import asyncio
from datetime import datetime

# ==== CONFIGURAÇÕES INICIAIS ====
api_id = 23565949
api_hash = '5ffa446ffd412847ac9ffd654c88e6cd'
session_name = 'Botdos1000'
grupo_origem = 'FTVIPLucasTyLty'  # Nome ou ID do grupo origem
grupo_destino = 'https://t.me/linkeyeudy'  # Grupo destino

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

# ==== FUNÇÃO PRINCIPAL ====

async def main():
    client = TelegramClient(session_name, api_id, api_hash)
    await client.start()

    @client.on(events.NewMessage(chats=grupo_origem))
    async def handler(event):
        if not dentro_do_horario():
            return

        mensagem = event.message.message
        msg_id = event.message.id

        # === NOVO FORMATO: TIP ENCONTRADA ===
        if "TIP ENCONTRADA" in mensagem.upper():
            links = re.findall(r'(https?://[^\s,]+)', mensagem)
            unidades_match = re.search(r'Unidade[s]*[:：]\s*(\d+)', mensagem)
            tipo_match = re.search(r'Tipo de Aposta[:：]\s*(.*)', mensagem)

            if links and unidades_match and tipo_match:
                unidades = float(unidades_match.group(1))
                tipo = tipo_match.group(1).strip()
                banca = carregar_banca()
                valor_aposta = calcular_valor_aposta(unidades, banca)

                texto = f"🎯 Tip detectada\n\n"
                texto += f"💰 Stake: {unidades} unidade(s) (R${valor_aposta:.2f})\n"
                texto += f"⚽ Tipo: {tipo}\n\n"
                texto += "🔗 Link(s):\n"
                for link in links:
                    texto += f"- {link}\n"
                texto += "\n*Jogue com responsabilidade ✅*"

                await client.send_message(grupo_destino, texto)
                salvar_tip(msg_id, valor_aposta)
                return

        # === ANTIGO FORMATO: texto com unidade + link ===
        if 'unidade' in mensagem.lower():
            match_link = re.search(r'(https?://[^\s]+)', mensagem)
            match_unidades = re.search(r'(\d+(?:,\d+)?)\s*unidade', mensagem.lower())

            if match_link and match_unidades:
                link = match_link.group(1)
                unidades = float(match_unidades.group(1).replace(',', '.'))
                banca = carregar_banca()
                valor_aposta = calcular_valor_aposta(unidades, banca)

                texto = f"""💸 *TIP IDENTIFICADA!*

🎯 Link: {link}
📌 Unidades: {unidades}
📊 Banca: R${banca:.2f}
💰 Apostar: *R${valor_aposta:.2f}*

⏱ Aguarde o resultado...
"""
                await client.send_message(grupo_destino, texto, parse_mode='markdown')
                salvar_tip(msg_id, valor_aposta)

        elif any(resultado in mensagem.lower() for resultado in ['green', 'red', 'reembolso']):
            resultado = mensagem.lower()
            valor_apostado = carregar_tip(msg_id)
            if valor_apostado is None:
                return

            banca = carregar_banca()

            if 'green' in resultado:
                lucro = valor_apostado * 0.8
                banca += lucro
                msg = f'✅ GREEN — +R${lucro:.2f}\n💰 Nova banca: R${banca:.2f}'
            elif 'red' in resultado:
                banca -= valor_apostado
                msg = f'❌ RED — -R${valor_apostado:.2f}\n💰 Nova banca: R${banca:.2f}'
            elif 'reembolso' in resultado:
                msg = f'🔄 REEMBOLSO — sem alteração\n💰 Banca: R${banca:.2f}'
            else:
                return

            await client.send_message(grupo_destino, msg)
            salvar_banca(banca)
            remover_tip(msg_id)

    print("🤖 Bot em tempo real iniciado.")
    await client.run_until_disconnected()

# ==== INICIAR ====
asyncio.run(main())
