import os
import requests
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import hashlib

class GitHubGameDownloader:
    REPO = "gu2121gg/Projeto-Xemuloter"
    RELEASE_TAG = "v2.0"
    FILE_NAME = "target_game.exe"
    DOWNLOAD_URL = f"https://github.com/{REPO}/releases/download/{RELEASE_TAG}/{FILE_NAME}"

    @staticmethod
    def download_file(destination, progress_callback=None):
        """Faz download do arquivo do GitHub"""
        headers = {
            'Accept': 'application/octet-stream',
            'User-Agent': 'Game-Downloader'
        }
        
        with requests.get(GitHubGameDownloader.DOWNLOAD_URL, headers=headers, stream=True) as response:
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            start_time = time.time()
            
            with open(destination, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
                        downloaded += len(chunk)
                        
                        if progress_callback:
                            progress = (downloaded / total_size) * 100 if total_size > 0 else 0
                            elapsed = time.time() - start_time
                            speed = (downloaded / (1024 * 1024)) / elapsed if elapsed > 0 else 0
                            progress_callback(progress, downloaded, total_size, speed)
        
        # Verificação de integridade
        if total_size > 0 and os.path.getsize(destination) != total_size:
            raise Exception("Download incompleto - tamanho do arquivo não corresponde")

class GameDownloadApp:
    def __init__(self, root):
        self.root = root
        self.setup_ui()
        self.downloading = False
        
    def setup_ui(self):
        self.root.title("Download do Target Game")
        self.root.geometry("500x350")
        self.root.resizable(False, False)
        
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Cabeçalho
        tk.Label(main_frame, 
                text="Target Game Downloader",
                font=('Arial', 14, 'bold')).pack(pady=10)
        
        tk.Label(main_frame, 
                text=f"Versão: {GitHubGameDownloader.RELEASE_TAG}",
                font=('Arial', 10)).pack()
        
        # Área de status
        status_frame = tk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=15)
        
        self.status_label = tk.Label(status_frame, 
                                   text="Pronto para baixar o jogo",
                                   font=('Arial', 10))
        self.status_label.pack(anchor=tk.W)
        
        self.progress_bar = ttk.Progressbar(status_frame, length=450, mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        self.details_label = tk.Label(status_frame,
                                    text="Tamanho: Desconhecido",
                                    font=('Arial', 8))
        self.details_label.pack(anchor=tk.W)
        
        # Botão de download
        self.download_btn = tk.Button(main_frame, 
                                    text="Baixar Jogo",
                                    command=self.start_download,
                                    font=('Arial', 12, 'bold'),
                                    bg='#4CAF50',
                                    fg='white',
                                    width=20)
        self.download_btn.pack(pady=20)
        
        # Rodapé
        tk.Label(main_frame,
                text=f"Repositório: {GitHubGameDownloader.REPO}",
                font=('Arial', 8)).pack(side=tk.BOTTOM)
    
    def start_download(self):
        if self.downloading:
            return
            
        self.downloading = True
        self.download_btn.config(state=tk.DISABLED, text="Baixando...")
        self.status_label.config(text="Iniciando download...")
        self.progress_bar['value'] = 0
        self.details_label.config(text="Tamanho: Calculando...")
        
        download_folder = os.path.join(os.getcwd(), "TargetGame")
        os.makedirs(download_folder, exist_ok=True)
        destination = os.path.join(download_folder, GitHubGameDownloader.FILE_NAME)
        
        threading.Thread(
            target=self.execute_download,
            args=(destination,),
            daemon=True
        ).start()
    
    def execute_download(self, destination):
        try:
            def progress_callback(progress, downloaded, total, speed):
                self.root.after(0, lambda: self.update_progress(progress, downloaded, total, speed))
            
            GitHubGameDownloader.download_file(
                destination=destination,
                progress_callback=progress_callback
            )
            
            self.root.after(0, lambda: self.status_label.config(text="Verificando arquivo..."))
            md5_hash = self.calculate_md5(destination)
            file_size = os.path.getsize(destination)
            
            self.root.after(0, lambda: self.download_complete(destination, md5_hash, file_size))
            
        except Exception as e:
            self.root.after(0, lambda: self.download_failed(str(e)))
        finally:
            self.root.after(0, self.reset_download_button)
            self.downloading = False
    
    def update_progress(self, progress, downloaded, total, speed):
        self.progress_bar['value'] = progress
        self.status_label.config(text=f"Download: {progress:.1f}% completo")
        
        downloaded_mb = downloaded / (1024 * 1024)
        total_mb = total / (1024 * 1024)
        self.details_label.config(text=f"Tamanho: {downloaded_mb:.1f}MB de {total_mb:.1f}MB | Velocidade: {speed:.2f} MB/s")
    
    def calculate_md5(self, filepath):
        hash_md5 = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def download_complete(self, filepath, md5_hash, file_size):
        messagebox.showinfo("Sucesso", 
                          f"Download completo!\n\n"
                          f"Arquivo: {filepath}\n"
                          f"Tamanho: {file_size/1024/1024:.1f} MB\n"
                          f"MD5: {md5_hash}")
        
        self.status_label.config(text="Download concluído com sucesso!")
        self.details_label.config(text=f"MD5: {md5_hash}")
    
    def download_failed(self, error):
        messagebox.showerror("Erro", f"Falha no download:\n{error}")
        self.status_label.config(text="Erro no download")
        self.progress_bar['value'] = 0
        self.details_label.config(text="Tente novamente mais tarde")
    
    def reset_download_button(self):
        self.download_btn.config(state=tk.NORMAL, text="Baixar Novamente")

if __name__ == "__main__":
    root = tk.Tk()
    app = GameDownloadApp(root)
    root.mainloop()