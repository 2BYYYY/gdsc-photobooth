import os, time
from dotenv import load_dotenv
from pydrive.auth import GoogleAuth 
from pydrive.drive import GoogleDrive 
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

IMG_DIR = 'Screenshots/'
ALLOWED_FILE_EXT = ('.png', '.jpg', '.jpeg')

class Watcher:
    def __init__(self):
        self.observer = Observer()
        self.path = IMG_DIR

    def run(self):
        """ Start monitoring images folder for new files. """
        handler = Handler()
        self.observer.schedule(handler, self.path, recursive=False)
        self.observer.start()
        try:
            print(f"[WATCHER_TRIGGER_NOTIF] Currently observing. Current file: {handler.latestImg}")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("[TERMINATE_NOTIF] Process stopped. Please run the script again to monitor recent files.")
            self.observer.stop()
        self.observer.join()

class Handler(FileSystemEventHandler):
    def __init__(self):
        self.latestImg = None

    def on_created(self, event):
        """ Override on_created() method to upload new files detected to Google Drive. """
        if not event.is_directory and event.src_path.endswith(ALLOWED_FILE_EXT):
            self.latestImg = event.src_path
            print(f"[FILE_FOUND_NOTIF] New file [{self.latestImg}] found!")
            time.sleep(2)
        folderID, secretFile, credsPath = load_env()
        drive = google_auth(secretFile, credsPath)
        upload_todrive(drive, folderID, self.latestImg)


def load_env():
    """ Load environment variables from .env """
    load_dotenv()
    folderID = os.getenv('folder_id')
    secretFile = os.getenv('client_secret')
    credsPath = os.getenv('save_path')  
    return folderID, secretFile, credsPath


def google_auth(file, path):
    try:
        """ Authenticate Google Drive using OAuth API. """
        gauth = GoogleAuth() 
        gauth.LoadClientConfigFile(file)
        gauth.LoadCredentialsFile(path)

        if gauth.credentials is None:
            gauth.LocalWebserverAuth()
            gauth.SaveCredentialsFile(path)
        elif gauth.access_token_expired:
            gauth.Refresh()
        else:
            gauth.Authorize()

        drive = GoogleDrive(gauth)
        return drive
    except:
        print("No Internet Connection")


def upload_todrive(drive, folder, file):
    try:
        """ Upload detected files to Drive. """
        gfile = drive.CreateFile({'parents': [{'id': folder}]})
        gfile.SetContentFile(file)
        gfile.Upload()
        print(f"[UPLOAD_SUCCESS_NOTIF] File {file} uploaded successfully.")
    except:
        print("No Internet Connection")

if __name__ == "__main__":
    fileWatcher = Watcher()
    fileWatcher.run()