import asyncio
import random
import tkinter as tk
from tkinter import filedialog
from zipfile import ZipFile
import os
import datetime
import io
import aiofiles
from aiohttp import ClientSession
from colorama import Fore, Style, init
from pystyle import Center, Box

from PIL import Image

# Constants
HEADERS = {'User-Agent': 'YiffScraper V3.0 (by axo!)'}
BASE_URL = "https://e621.net/posts.json?tags=order:random+limit:{}"
FOLDERS_DIR = "Folders"

# Initialize colorama
init(autoreset=True)

# Logging functions
def log(level, color, message, thread_num=None):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    thread_info = f"[Thread {thread_num}]" if thread_num is not None else ""
    print(f"{Fore.LIGHTBLACK_EX}[{timestamp}] {Fore.WHITE}{thread_info} {color}[{level.upper()}]{Style.RESET_ALL} {message}")

log_info = lambda msg, tn=None: log("info", Fore.LIGHTBLUE_EX, msg, tn)
log_error = lambda msg, tn=None: log("error", Fore.LIGHTRED_EX, msg, tn)
log_success = lambda msg, tn=None: log("success", Fore.LIGHTGREEN_EX, msg, tn)
log_input = lambda msg: input(f"{Fore.LIGHTBLACK_EX}[{datetime.datetime.now().strftime('%H:%M:%S')}] {Fore.CYAN}[INPUT] {msg} >> {Fore.WHITE}")
log_debug = lambda msg, dbg, tn=None: log("debug", Fore.LIGHTMAGENTA_EX, msg, tn) if dbg else None

# Utility functions
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def display_title():
    title = """
  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡘⣈⠓⠬⢑⡢⣄⠠⠤⠚⡷⡄⠀⠀                                  
  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢃⡇⢵⠀⠀⠈⠁⠀⠀⠀⠒⢅⠀⠀                                  
  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣷⡔⠥⡃⠀⠀⠀⣤⣤⣼⠋⢢⣤      ■■■■■■■■■■■■■■■■■■■■■■■■■   
  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠦⢟⠄⠀⠀⠀⠀⠀⠀⡬⡠⣤⢾      ■                       ■   
  ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠛⡒⠤⢮⠀⡀⠀⣉⠥⠂⠁      ■  YiffScraper          ■   
  ⡤⣀⡀⠀⠀⠀⠀⠀⢤⠤⠆⠈⠉⠀⠀⠈⠉⠉⠁⠀⠜⠲⠥⠺⠀⠀⠀⠀      ■  V3.0                 ■   
  ⠰⡈⠄⠁⠂⠄⣀⣀⣸⡁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠣⡄⠀⠀⠀      ■  Made by Axo with <3  ■   
  ⠀⢃⠀⠀⠀⠀⠀⠀⠨⠩⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⣎⠀⠀⠀⠀      ■                       ■   
  ⠀⠈⢦⠀⠀⠀⠀⠀⣠⢾⠀⠀⠀⠀⡜⠐⡢⣤⡅⠀⠀⢸⠚⠀⠀⠀⠀⠀      ■■■■■■■■■■■■■■■■■■■■■■■■■   
  ⠀⠀⠀⠈⠁⠐⠀⠉⠁⡜⠀⠀⢀⡞⠀⠀⠇⠀⢣⠀⠀⠈⢸⠀⠀⠀⠀⠀                                  
  ⠀⠀⠀⠀⠀⠀⠀⠀⢰⠀⠀⡠⠃⢸⠀⠀⠇⠀⠀⢂⠀⠀⡾⠀⠀⠀⠀⠀                                  
  ⠀⠀⠀⠀⠀⠀⠀⠀⢸⠀⠀⠁⠀⠘⡄⠈⡄⠀⠀⠈⠄⠀⢡⡆⠀⠀⠀⠀                                  
  ⠀⠀⠀⠀⠀⠀⠀⠀⠘⢤⣠⠄⠀⠀⠘⠴⠼⠀⠀⠀⠘⠤⠰⠖⠀⠀⠀⠀                                  
"""
    print(Center.XCenter(title))

def display_menu():
    display_title()
    print(Center.XCenter(Box.DoubleCube("[1] Start\n[2] Exit")))
    

# Download functions
async def download_file(sem, count, file_url, post_id, session, debug, thread_num, download_folder):
    async with sem:
        log_debug(f"Downloading file {count} from {file_url}", debug, thread_num)
        try:
            async with session.get(file_url, headers=HEADERS) as response:
                if response.status == 200:
                    file_ext = file_url.split('.')[-1]
                    file_name = f"{post_id}.{file_ext}"

                    file_data_in_ram = io.BytesIO(await response.read())

                    if file_ext in ["png", "jpg", "jpeg"] and not is_image_valid(file_data_in_ram):
                        log_error(f"File {count} failed image integrity check", thread_num)
                        return

                    async with aiofiles.open(f"{FOLDERS_DIR}/{download_folder}/{file_name}", 'wb') as f:
                        await f.write(file_data_in_ram.getvalue())

                    log_success(f"Downloaded: {file_name}", thread_num)
                else:
                    log_error(f"HTTP {response.status} for file {count}", thread_num)
        except Exception as e:
            log_error(f"Error downloading file {count}: {e}", thread_num)

async def start_scraper(tags, amount, debug, thread_limit, download_folder):
    log_info(f"Starting scraper with {thread_limit} threads")
    sem = asyncio.Semaphore(thread_limit)

    async with ClientSession() as session:
        total = 0
        while total < amount:
            log_info(f"Downloading {total}/{amount}")
            url = f"{BASE_URL.format(amount - total)}+{tags}"
            json_data = await get_json(url, session, debug)

            if not json_data:
                return

            posts = json_data.get("posts", [])
            os.makedirs(f"{FOLDERS_DIR}/{download_folder}", exist_ok=True)

            tasks = [download_file(sem, i, post["file"]["url"], post['id'], session, debug, random.randint(1, thread_limit), download_folder) for i, post in enumerate(posts) if "url" in post["file"]]

            await asyncio.gather(*tasks)
            total += len(posts)
            await asyncio.sleep(3)

        log_info("Finished.")
        await post_download_actions(download_folder, debug)

async def post_download_actions(download_folder, debug):
    if log_input("Zip the downloaded files? (y/n)").lower() == 'y':
        log_debug("Zipping files", debug)
        zip_folder(f"{FOLDERS_DIR}/{download_folder}", f"{FOLDERS_DIR}/{download_folder}.zip")
        log_success("Files zipped")

        if log_input("Encrypt the downloaded files? (y/n)").lower() == 'y':
            passkey = log_input("Enter encryption passkey")
            encrypt_zip_file(download_folder, download_folder, passkey)
            log_success("Files encrypted")

async def get_json(url, session, debug, thread_num=None):
    log_debug(f"Sending GET to {url}", debug, thread_num)
    async with session.get(url, headers=HEADERS) as response:
        if response.status == 200:
            return await response.json()
        log_error(f"HTTP {response.status} for GET {url}", thread_num)
        return None

def zip_folder(src_folder, dest_zip_file):
    with ZipFile(dest_zip_file, 'w') as zipf:
        for foldername, subfolders, filenames in os.walk(src_folder):
            for filename in filenames:
                file_path = os.path.join(foldername, filename)
                zipf.write(file_path, os.path.relpath(file_path, src_folder))

def encrypt_zip_file(src_folder, dest_zip_file, passkey):
    encrypted_folder = f"{FOLDERS_DIR}/{src_folder}_encrypted"
    os.makedirs(encrypted_folder, exist_ok=True)
    for foldername, _, filenames in os.walk(f"{FOLDERS_DIR}/{src_folder}"):
        for filename in filenames:
            file_path = os.path.join(foldername, filename)
            encrypted_file_path = os.path.join(encrypted_folder, filename)
            with open(file_path, 'rb') as file:
                data = file.read()

            # Placeholder for encryption logic
            encrypted_data = data

            with open(encrypted_file_path, 'wb') as encrypted_file:
                encrypted_file.write(encrypted_data)

    for foldername, _, filenames in os.walk(f"{FOLDERS_DIR}/{src_folder}"):
        for filename in filenames:
            file_path = os.path.join(foldername, filename)
            os.remove(file_path)

    os.rename(encrypted_folder, f"{FOLDERS_DIR}/{src_folder}")

def is_image_valid(image_data):
    try:
        image = Image.open(image_data)
        image.verify()
        return True
    except Exception:
        return False

async def check_e621_status(debug):
    log_info("Checking if E621 is up...")
    async with ClientSession() as session:
        try:
            async with session.get("https://e621.net/posts.json", headers=HEADERS) as response:
                log_debug(f"Received response {response.status} from E621", debug)
                return response.status == 200
        except Exception as e:
            log_error(str(e))
            return False

async def main():
    clear_screen()
    display_title()
    log_info("YiffScraper V3.0 BETA 3.1")

    debug_choice = log_input("Enable debug mode? (y/n)")
    debug = debug_choice.lower() == 'y'

    clear_screen()
    if not await check_e621_status(debug):
        display_title()
        log_error("E621 is currently down or not accessible.")
        proceed_choice = log_input("Would you like to launch anyway? (y/n)")
        if proceed_choice.lower() != 'y':
            return

    while True:
        clear_screen()
        display_menu()
        choice = log_input("Choice")

        if choice == "2":
            clear_screen()
            break

        if choice == "1":
            amount_input = log_input("How many images would you like to download?")
            try:
                amount = int(amount_input)
            except ValueError:
                log_error("Invalid input for amount. Exiting...")
                continue

            thread_input = log_input("How many threads would you like to use for downloading?")
            try:
                thread_limit = int(thread_input)
            except ValueError:
                log_error("Invalid input for threads. Exiting...")
                continue

            def get_tags_from_file():
                root = tk.Tk()
                root.withdraw()
                filepath = filedialog.askopenfilename(title="Select a tag file", filetypes=[("Tag files", "*.tag")])
                if filepath:
                    with open(filepath, 'r') as file:
                        return file.read().strip().split(" ")
                return []

            def save_tags_to_file(tags):
                root = tk.Tk()
                root.withdraw()
                filepath = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Tag files", "*.tags")])
                if filepath:
                    with open(filepath, 'w') as file:
                        file.write(" ".join(tags))

            tags = []
            tag_choice = log_input("Do you want to [1] Enter tags manually, [2] Build tags, or [3] Load tags from a file?")

            if tag_choice == "1":
                tags_input = log_input("Enter your tags (separated by spaces)")
                tags = tags_input.replace(" ", "+")
                log_debug("Tags: " + tags, debug)

            elif tag_choice == "2":
                clear_screen()
                display_title()
                log_info("Welcome to the tag builder!")
                log_info("This will guide you through finding the right tags for your needs.")
                log_info("Let's start!")

                tags_input = ""

                g = log_input("What is your preferred gender? [1] Males only (Gay) [2] Females only (Lesbian) [3] Intersex only (Other) [4] Males and Females (Straight) [5] Other or [blank] no preference")
                try:
                    g = int(g)
                    if g in [1, 2, 3, 4, 5]:
                        gender_subtype_questions = {
                            1: "What type of males? [1] Femboy [2] Transmasc [3] Manly ",
                            2: "What type of females? [1] Tomboy [2] Transfem [3] Girly ",
                        }

                        if g == 1:
                            gen = 'male male/male'
                        elif g == 2:
                            gen = 'female female/female'
                        elif g == 3:
                            gen = 'intersex intersex/intersex'
                        elif g == 4:
                            gen = 'male/female male female'
                        elif g == 5:
                            gen = log_input("Enter the type of genders you want to see (e.g male/female or male/male or intersex/female). or press enter to skip.")

                        if g in gender_subtype_questions:
                            subtype = log_input(gender_subtype_questions[g])
                            try:
                                subtype = int(subtype)
                                if g == 1:
                                    if subtype == 1:
                                        gen = f"{gen} femboy"
                                    elif subtype == 2:
                                        gen = f"{gen} transgender"
                                    elif subtype == 3:
                                        gen = f"{gen} manly"
                                elif g == 2:
                                    if subtype == 1:
                                        gen = f"{gen} tomboy"
                                    elif subtype == 2:
                                        gen = f"{gen} transgender"
                                    elif subtype == 3:
                                        gen = f"{gen} girly"

                            except ValueError:
                                log_info("Using no gender tag.")

                        tags_input += gen + " "
                        log_debug(tags_input, debug)

                except ValueError:
                    log_info("Using no gender tag.")

                s = log_input("What should the minimum score be? (Put 0 if you don't care)")
                tags_input += f"score:>={s} "
                r = log_input("What should the rating be? [1] Explicit [2] Questionable or [3] Safe")
                r = int(r)
                if r in [1, 2, 3]:
                    if r == 1:
                        r = 'e'
                    elif r == 2:
                        r = 'q'
                    else:
                        r = 's'
                tags_input += f"rating:{r} "
                fetishes = log_input("Do you have any fetishes/kinks? If so, put them here, otherwise, leave it blank. (e.g. bondage piss) (This is all local noone else sees this)")
                if fetishes != '':
                    tags_input += fetishes + ' '
                elif fetishes == '':
                    pass
                log_debug(tags_input, debug)
                fetishes = log_input("Is there anything else you want to add?")
                tags_input += fetishes + ' '
                log_debug(tags_input, debug)

                tags = tags_input.replace(' ', '+')
                log_debug(f"Formatted: {tags}", debug)

                save_choice = log_input("Do you want to save these tags for future use? (y/n)")
                if save_choice.lower() == 'y':
                    save_tags_to_file(tags)

            elif tag_choice == "3":
                tags = get_tags_from_file()

            download_folder = log_input("Name the folder for downloaded files:")
            if not download_folder.strip():
                log_error("Invalid folder name. Exiting...")
                continue

            os.makedirs(f"Folders/{download_folder}", exist_ok=True)

            await start_scraper(tags, amount, debug, thread_limit, download_folder)
        
asyncio.run(main())
