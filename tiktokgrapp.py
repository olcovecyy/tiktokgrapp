import importlib.util
import subprocess
import sys

# Kontrola knihovny tkinter
tkinter_spec = importlib.util.find_spec("tkinter")
tkinter_installed = tkinter_spec is not None

# Kontrola knihovny pydrive
pydrive_spec = importlib.util.find_spec("pydrive")
pydrive_installed = pydrive_spec is not None

if not tkinter_installed:
    print("Knihovna 'tkinter' není nainstalována. Probíhá instalace...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "tkinter"])
    print("Knihovna 'tkinter' byla úspěšně nainstalována.")

if not pydrive_installed:
    print("Knihovna 'pydrive' není nainstalována. Probíhá instalace...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pydrive"])
    print("Knihovna 'pydrive' byla úspěšně nainstalována.")

# Pokračovat se zbytkem kódu
from tkinter import *
from tkinter import filedialog, messagebox
import os
import requests
import shutil
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

def download_tiktok_video(video_url, output_dir):
    response = requests.get(video_url, stream=True)
    total_size = int(response.headers.get("Content-Length", 0))
    downloaded_size = 0

    file_name = video_url.split("/")[-1]
    output_file_name = os.path.join(output_dir, file_name)

    with open(output_file_name, "wb") as file:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                file.write(chunk)
                downloaded_size += len(chunk)
                progress = int((downloaded_size / total_size) * 100)
                status_label.config(text=f"Stahování: {progress}% dokončeno")
                status_label.update()

    messagebox.showinfo("Stažení dokončeno", f"Video bylo úspěšně staženo: {video_url}")
    return output_file_name

def upload_to_google_drive(file_path):
    gauth = GoogleAuth()
    gauth.LoadCredentialsFile("mycreds.txt")

    if gauth.credentials is None:
        messagebox.showerror("Chyba", "Není nastaven přístupový klíč pro Google Disk.")
        return

    if gauth.access_token_expired:
        gauth.Refresh()
        gauth.SaveCredentialsFile("mycreds.txt")

    drive = GoogleDrive(gauth)

    file_name = os.path.basename(file_path)
    gfile = drive.CreateFile({"title": file_name})
    gfile.SetContentFile(file_path)
    gfile.Upload()

    messagebox.showinfo("Nahráno na Google Disk", f"Soubor byl úspěšně nahrán na Google Disk: {gfile['alternateLink']}")

    os.remove(file_path)

def save_copy_to_desktop(file_path):
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    file_name = os.path.basename(file_path)
    destination_path = os.path.join(desktop_path, file_name)

    shutil.copy2(file_path, destination_path)

    messagebox.showinfo("Kopie na ploše", f"Kopie souboru byla úspěšně uložena na plochu: {destination_path}")

def browse_output_dir():
    output_dir = filedialog.askdirectory()
    output_dir_entry.delete(0, "end")
    output_dir_entry.insert(0, output_dir)

def login_to_google_drive():
    gauth = GoogleAuth()

    if not os.path.isfile("mycreds.txt"):
        gauth.LocalWebserverAuth()
        gauth.SaveCredentialsFile("mycreds.txt")

    messagebox.showinfo("Přihlášení k Google Disk", "Byli jste úspěšně přihlášeni k Google Disk.")

def download_and_upload():
    urls = url_entry.get().split()
    output_dir = output_dir_entry.get()

    if not output_dir:
        output_dir = "videos"

    for i, url in enumerate(urls, 1):
        status_label.config(text=f"Stahování videa {i}/{len(urls)}")
        status_label.update()
        video_path = download_tiktok_video(url, output_dir)

        if upload_to_drive.get():
            status_label.config(text=f"Nahrávání videa {i}/{len(urls)} na Google Disk")
            status_label.update()
            upload_to_google_drive(video_path)

        if save_to_desktop.get():
            status_label.config(text=f"Ukládání kopie videa {i}/{len(urls)} na plochu")
            status_label.update()
            save_copy_to_desktop(video_path)

    status_label.config(text="Stahování a nahrávání videí dokončeno")

root = Tk()
root.title("TikTok Downloader")
root.configure(background="#F0F0F0")

# Logo
logo_label = Label(root, text="TIKTOK GRABER", font=("Arial", 18, "bold"), background="#F0F0F0")
logo_label.pack(pady=10)

# URL vstupní pole
url_frame = Frame(root, background="#F0F0F0")
url_frame.pack(pady=10)

url_label = Label(url_frame, text="URL videa:", background="#F0F0F0")
url_label.pack(side="left")

url_entry = Entry(url_frame, width=50)
url_entry.pack(side="left")

# Výstupní složka vstupní pole
output_dir_frame = Frame(root, background="#F0F0F0")
output_dir_frame.pack(pady=10)

output_dir_label = Label(output_dir_frame, text="Výstupní složka:", background="#F0F0F0")
output_dir_label.pack(side="left")

output_dir_entry = Entry(output_dir_frame, width=50)
output_dir_entry.pack(side="left")

browse_button = Button(output_dir_frame, text="Procházet", command=browse_output_dir, background="white")
browse_button.pack(side="left")

# Možnost přihlášení k Google Disk
login_frame = Frame(root, background="#F0F0F0")
login_frame.pack(pady=10)

login_label = Label(login_frame, text="Přihlášení k Google Disk:", background="#F0F0F0")
login_label.pack(side="left")

upload_to_drive = BooleanVar()
drive_checkbox = Checkbutton(login_frame, text="Nahrát na Google Disk", variable=upload_to_drive, background="#F0F0F0")
drive_checkbox.pack(side="left")

# Možnost uložení kopie na ploše
desktop_frame = Frame(root, background="#F0F0F0")
desktop_frame.pack(pady=10)

save_to_desktop = BooleanVar()
desktop_checkbox = Checkbutton(desktop_frame, text="Uložit kopii na plochu", variable=save_to_desktop, background="#F0F0F0")
desktop_checkbox.pack()

# Tlačítko pro stahování a nahrávání
download_button = Button(root, text="Stáhnout a nahrát", command=download_and_upload, background="white")
download_button.pack(pady=10)

# Statusový label
status_label = Label(root, text="", background="#F0F0F0")
status_label.pack()

root.mainloop()
