"""
Python to download images from e621.net
Takes tags and number of images to download as input
Outputs to ./Folders
"""

# Import packages
import random
import tkinter as tk
from tkinter import filedialog
import aiofiles
import asyncio
from aiohttp import ClientSession
from zipfile import ZipFile
import os
import datetime
from colorama import Fore, Style, init
from pystyle import Center, Box
import io
from PIL import Image


# Initialise colorama for colored output
init(autoreset=True)

HEADERS = {'User-Agent': 'YiffScraper V3.0 (by axo!)'}
BASE_URL = "https://e621.net/posts.json?tags=order:random+limit:{}"

# Function to log messages with color and timestamp
def log(level, color, message, thread_num=None):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    thread_info = f"[Thread {thread_num}]" if thread_num is not None else ""
    print(f"{Fore.LIGHTBLACK_EX}[{timestamp}] {Fore.WHITE}{thread_info} {color}[{level.upper()}]{Style.RESET_ALL} {message}")

# Log Info blue
def log_info(message, thread_num=None):
    log("info", Fore.LIGHTBLUE_EX, message, thread_num)

# Log Error red
def log_error(message, thread_num=None):
    log("error", Fore.LIGHTRED_EX, message, thread_num)

# Log Input cyan
def log_input(message):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    return input(f"{Fore.LIGHTBLACK_EX}[{timestamp}] {Fore.CYAN}[INPUT] {message} {Fore.CYAN}>> {Fore.WHITE}")

# Log Success green
def log_success(message, thread_num=None):
    log("success", Fore.LIGHTGREEN_EX, message, thread_num)

# Log Debug magenta
def log_debug(message, debug, thread_num=None):
    if debug:
        log("debug", Fore.LIGHTMAGENTA_EX, message, thread_num)

# Function to clear the screen
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# Function to display the title
def display_title():
    title = """

    ⠀
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

# Display menu
def display_menu():
    display_title()
    print("\n\n") 
    table = Box.DoubleCube("[1] Start\n[2] Exit")
    print(Center.XCenter(table))

def is_image_valid(file_path):
    try:
        with Image.open(file_path) as img:
            img.verify()
        return True
    except (IOError, SyntaxError):
        return False
    return False

async def download_file(sem, count, file_url, post_id, session, debug, thread_num, download_folder):
    async with sem:
        log_debug(f"Attempting to download file {count} from {file_url}", debug, thread_num)
        try:
            async with session.get(file_url, headers=HEADERS) as response:
                log_debug(f"Received response with status code {response.status} for file {count}", debug, thread_num)
                if response.status == 200:
                    file_ext = file_url.split('.')[-1]
                    file_name = f"{post_id}.{file_ext}"
                    log_debug(f"File name determined: {file_name}", debug, thread_num)

                    file_data_in_ram = io.BytesIO(await response.read())
                    log_debug(f"File data stored in RAM", debug, thread_num)

                    if file_ext in ["png", "jpg", "jpeg"]:
                        log_debug("Checking image integrity...", debug, thread_num)
                        if not is_image_valid(file_data_in_ram):
                            log_error(f"File {count} failed image integrity check", thread_num)
                            return
                        else:
                            log_debug("Integrity check passed, writing to disk...", debug, thread_num)
                    else:
                        log_debug("Skipping debug check due to video content.", debug)
                        log_debug("Writing to disk...", debug, thread_num)

                    async with aiofiles.open(f"Folders/{download_folder}/{file_name}", mode='wb') as f:
                        await f.write(file_data_in_ram.getvalue())
                        log_debug(f"File {file_name} written to disk", debug, thread_num)

                    log_success(f"File {count} downloaded: {file_name}", thread_num)
                else:
                    log_error(f"No file {count} to download. Server replied HTTP code: {response.status}", thread_num)
        except Exception as e:
            log_error(str(e), thread_num)

async def start_scraper(tags, amount, debug, thread_limit, download_folder):
    log_info(f"Starting scraper with {thread_limit} threads")
    sem = asyncio.Semaphore(thread_limit)

    async with ClientSession() as session:
        total = 0
        while total < amount:
            log_info(f"Downloading {total}/{amount}")
            url = BASE_URL.format(amount - total) + "+" + tags
            json_data = await get_json(url, session, debug, None)

            if not json_data:
                return

            posts = json_data["posts"]
            if not os.path.exists(f"Folders/{download_folder}"):
                log_debug(f"Creating directory Folders/{download_folder}", debug)
                os.makedirs(f"Folders/{download_folder}")

            tasks = []
            for i, post in enumerate(posts):
                file_data = post["file"]
                file_url = file_data.get("url")
                if file_url:
                    task = asyncio.ensure_future(download_file(sem, i, file_url, post['id'], session, debug, random.randint(1, thread_limit), download_folder))
                    tasks.append(task)

            await asyncio.gather(*tasks)
            log_info(f"Downloaded {len(posts)} files")
            total += len(posts)
            await asyncio.sleep(3)
        log_info("Finished.")
        asyncio.sleep(2)
        clear_screen()
        display_title()
        zip_choice = log_input("Would you like to zip the downloaded files? (y/n)")

        if zip_choice.lower() == 'y':
            encrypt_choice = log_input("Would you like to encrypt the downloaded files? (y/n)")
            log_debug("Zipping downloaded files", debug)
            zip_folder(f"Folders/{download_folder}", f"Folders/{download_folder}.zip")
            log_success("Zipped")
            if encrypt_choice.lower() == 'y':
                log_debug("Encrypting downloaded files", debug)
                passkey = log_input("Enter a passkey for encryption")
                encrypt_zip_file(download_folder, download_folder, passkey)
                log_success("Encrypted")

async def get_json(url, session, debug, thread_num):
    log_debug(f"Sending GET request to {url}", debug, thread_num)
    async with session.get(url, headers=HEADERS) as response:
        log_debug(f"Received response with status code {response.status}", debug, thread_num)
        if response.status == 200:
            log_debug("Response 200: Data received", debug, thread_num)
            return await response.json()
        else:
            log_error(f"Response code: {response.status}", thread_num)
            return None

def zip_folder(src_folder, dest_zip_file):
    log_debug(f"Zipping folder {src_folder} to {dest_zip_file}", debug=True)
    with ZipFile(dest_zip_file, 'w') as zipf:
        for foldername, subfolders, filenames in os.walk(src_folder):
            for filename in filenames:
                zipf.write(os.path.join(foldername, filename), os.path.relpath(os.path.join(foldername, filename), src_folder))

def encrypt_zip_file(src_folder, dest_zip_file, passkey):
    # Step 2: Encrypt the downloaded files
    encrypted_folder = f"Folders/{src_folder}_encrypted"
    os.makedirs(encrypted_folder, exist_ok=True)
    for foldername, subfolders, filenames in os.walk(f"Folders/{src_folder}"):
        for filename in filenames:
            file_path = os.path.join(foldername, filename)
            encrypted_file_path = os.path.join(encrypted_folder, filename)
            with open(file_path, 'rb') as file:
                data = file.read()

            # replace with actual encryption
            encrypted_data = data

            with open(encrypted_file_path, 'wb') as encrypted_file:
                encrypted_file.write(encrypted_data)

    # Step 3: Delete the original downloaded files
    for foldername, subfolders, filenames in os.walk(f"Folders/{src_folder}"):
        for filename in filenames:
            file_path = os.path.join(foldername, filename)
            os.remove(file_path)

    # Step 4: Rename the encrypted folder to the original download folder name
    os.rename(encrypted_folder, f"Folders/{src_folder}")
    # Step 5: Zip the encrypted folder
    zip_folder(f"Folders/{src_folder}", f"Folders/{dest_zip_file}.zip")

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
