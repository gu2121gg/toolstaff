import os
import requests
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import hashlib
import subprocess
import pygame
from pygame.locals import *

class GameLauncher:
    def __init__(self, root):
        self.root = root
        self.game_cards = []  # Inicializa a lista de cards de jogo
        self.current_selection = 0
        self.downloading = False
        self.setup_ui()
        self.setup_joystick()
        
        # Configura controles de teclado
        self.root.bind("<Key>", self.handle_keypress)
    
    def setup_joystick(self):
        """Configura o joystick (controle de PS2)"""
        pygame.init()
        pygame.joystick.init()
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            print(f"Controle conectado: {self.joystick.get_name()}")
        else:
            self.joystick = None
            print("Nenhum controle detectado")
        
        self.check_joystick()
    
    def check_joystick(self):
        """Verifica eventos do controle periodicamente"""
        if self.joystick:
            for event in pygame.event.get():
                if event.type == JOYBUTTONDOWN:
                    if event.button == 0 and self.game_cards:  # Botão X (confirmar)
                        self.game_cards[self.current_selection].invoke()
                    elif event.button == 12:  # D-pad up
                        self.navigate(-1)
                    elif event.button == 13:  # D-pad down
                        self.navigate(1)
        
        self.root.after(100, self.check_joystick)
    
    def handle_keypress(self, event):
        """Lida com eventos de teclado"""
        if event.keysym == "Up":
            self.navigate(-1)
        elif event.keysym == "Down":
            self.navigate(1)
        elif event.keysym == "Return" and self.game_cards:
            self.game_cards[self.current_selection].invoke()
    
    def navigate(self, direction):
        """Navega entre os cards de jogos"""
        if not self.game_cards:
            return
            
        new_selection = self.current_selection + direction
        if 0 <= new_selection < len(self.game_cards):
            # Remove destaque do card atual
            self.game_cards[self.current_selection].config(relief=tk.RAISED, bg="#f0f0f0")
            
            # Atualiza seleção
            self.current_selection = new_selection
            
            # Destaca novo card
            self.game_cards[self.current_selection].config(relief=tk.SUNKEN, bg="#d0d0ff")
            
            # Rola a tela para mostrar o card selecionado
            self.canvas.yview_moveto(self.current_selection / len(self.game_cards))
    
    def setup_ui(self):
        self.root.title("Game Launcher")
        self.root.geometry("800x600")
        self.root.config(bg="#2c3e50")
        
        # Frame principal
        main_frame = tk.Frame(self.root, bg="#2c3e50")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Cabeçalho
        header = tk.Frame(main_frame, bg="#34495e")
        header.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(header, 
                text="GAME LAUNCHER",
                font=('Arial', 20, 'bold'),
                bg="#34495e",
                fg="#ecf0f1").pack(pady=10)
        
        # Área de jogos com scrollbar
        game_container = tk.Frame(main_frame, bg="#2c3e50")
        game_container.pack(fill=tk.BOTH, expand=True)
        
        # Canvas e scrollbar
        self.canvas = tk.Canvas(game_container, bg="#2c3e50", highlightthickness=0)
        scrollbar = ttk.Scrollbar(game_container, orient="vertical", command=self.canvas.yview)
        scrollable_frame = tk.Frame(self.canvas, bg="#2c3e50")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        
        self.canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Configura o mouse wheel para scroll
        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        
        # Jogo disponível
        game_info = {
            "title": "Target Game",
            "version": "v2.0",
            "repo": "gu2121gg/Projeto-Xemuloter",
            "file": "target_game.exe",
            "download_url": "https://github.com/gu2121gg/Projeto-Xemuloter/releases/download/v2.0/target_game.exe",
            "installed": os.path.exists(os.path.join("TargetGame", "target_game.exe"))
        }
        
        # Cria card para o jogo
        card = tk.Frame(scrollable_frame, 
                      bg="#34495e",
                      relief=tk.RAISED,
                      bd=2)
        card.pack(fill=tk.X, pady=5, ipady=5)
        
        # Info do jogo
        info_frame = tk.Frame(card, bg="#34495e")
        info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        tk.Label(info_frame, 
                text=game_info["title"],
                font=('Arial', 14, 'bold'),
                bg="#34495e",
                fg="#ecf0f1").pack(anchor=tk.W)
        
        tk.Label(info_frame, 
                text=f"Versão: {game_info['version']}",
                font=('Arial', 10),
                bg="#34495e",
                fg="#bdc3c7").pack(anchor=tk.W)
        
        status_text = "Instalado" if game_info["installed"] else "Não instalado"
        status_color = "#2ecc71" if game_info["installed"] else "#e74c3c"
        
        tk.Label(info_frame, 
                text=status_text,
                font=('Arial', 10, 'bold'),
                bg="#34495e",
                fg=status_color).pack(anchor=tk.W)
        
        # Botão de ação
        btn_frame = tk.Frame(card, bg="#34495e")
        btn_frame.pack(side=tk.RIGHT, padx=10)
        
        if game_info["installed"]:
            btn_text = "Jogar"
            btn_command = lambda: self.play_game(game_info)
            btn_color = "#27ae60"
        else:
            btn_text = "Instalar"
            btn_command = lambda: self.download_game(game_info)
            btn_color = "#3498db"
        
        action_btn = tk.Button(btn_frame,
                             text=btn_text,
                             command=btn_command,
                             font=('Arial', 12, 'bold'),
                             bg=btn_color,
                             fg="white",
                             width=10)
        action_btn.pack(pady=10)
        
        self.game_cards.append(action_btn)
        
        # Destaca o primeiro card
        if self.game_cards:
            self.game_cards[0].config(relief=tk.SUNKEN, bg="#d0d0ff")
    
    def download_game(self, game):
        if self.downloading:
            return
            
        self.downloading = True
        
        # Cria janela de download
        download_window = tk.Toplevel(self.root)
        download_window.title(f"Download - {game['title']}")
        download_window.geometry("500x300")
        
        # Frame principal
        main_frame = tk.Frame(download_window, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Cabeçalho
        tk.Label(main_frame, 
                text=f"Download {game['title']}",
                font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Área de status
        status_frame = tk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=15)
        
        status_label = tk.Label(status_frame, 
                               text="Preparando download...",
                               font=('Arial', 10))
        status_label.pack(anchor=tk.W)
        
        progress_bar = ttk.Progressbar(status_frame, length=450, mode='determinate')
        progress_bar.pack(fill=tk.X, pady=5)
        
        details_label = tk.Label(status_frame,
                                text="Tamanho: Desconhecido",
                                font=('Arial', 8))
        details_label.pack(anchor=tk.W)
        
        # Botão de cancelar
        cancel_btn = tk.Button(main_frame, 
                             text="Cancelar",
                             command=lambda: self.cancel_download(download_window),
                             font=('Arial', 10),
                             bg="#e74c3c",
                             fg='white')
        cancel_btn.pack(pady=10)
        
        # Inicia o download em uma thread separada
        download_thread = threading.Thread(
            target=self.execute_download,
            args=(game, download_window, status_label, progress_bar, details_label),
            daemon=True
        )
        download_thread.start()
    
    def execute_download(self, game, window, status_label, progress_bar, details_label):
        try:
            download_folder = os.path.join(os.getcwd(), "TargetGame")
            os.makedirs(download_folder, exist_ok=True)
            destination = os.path.join(download_folder, game["file"])
            
            def progress_callback(progress, downloaded, total, speed):
                if not self.downloading:
                    raise Exception("Download cancelado")
                
                window.after(0, lambda: self.update_progress(
                    progress, downloaded, total, speed, 
                    status_label, progress_bar, details_label
                ))
            
            headers = {'User-Agent': 'GameLauncher'}
            
            with requests.get(game["download_url"], headers=headers, stream=True) as response:
                response.raise_for_status()
                
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                start_time = time.time()
                
                with open(destination, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        if not self.downloading:
                            file.close()
                            os.remove(destination)
                            raise Exception("Download cancelado")
                            
                        if chunk:
                            file.write(chunk)
                            downloaded += len(chunk)
                            
                            progress = (downloaded / total_size) * 100 if total_size > 0 else 0
                            elapsed = time.time() - start_time
                            speed = (downloaded / (1024 * 1024)) / elapsed if elapsed > 0 else 0
                            progress_callback(progress, downloaded, total_size, speed)
            
            # Verificação de integridade
            if total_size > 0 and os.path.getsize(destination) != total_size:
                raise Exception("Download incompleto")
            
            # Verificação MD5
            md5_hash = self.calculate_md5(destination)
            
            window.after(0, lambda: self.download_complete(
                window, game, destination, total_size
            ))
            
        except Exception as e:
            window.after(0, lambda: self.download_failed(window, str(e)))
        finally:
            self.downloading = False
    
    def update_progress(self, progress, downloaded, total, speed, status_label, progress_bar, details_label):
        progress_bar['value'] = progress
        status_label.config(text=f"Download: {progress:.1f}% completo")
        
        downloaded_mb = downloaded / (1024 * 1024)
        total_mb = total / (1024 * 1024)
        details_label.config(text=f"Tamanho: {downloaded_mb:.1f}MB de {total_mb:.1f}MB | Velocidade: {speed:.2f} MB/s")
    
    def calculate_md5(self, filepath):
        hash_md5 = hashlib.md5()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def download_complete(self, window, game, filepath, file_size):
        messagebox.showinfo("Sucesso", f"Download completo!\n\nArquivo: {filepath}\nTamanho: {file_size/1024/1024:.1f} MB")
        window.destroy()
        self.refresh_ui()
    
    def download_failed(self, window, error):
        messagebox.showerror("Erro", f"Falha no download:\n{error}")
        window.destroy()
    
    def cancel_download(self, window):
        self.downloading = False
        window.destroy()
    
    def play_game(self, game):
        """Executa o jogo instalado"""
        try:
            subprocess.Popen([os.path.join("TargetGame", game["file"])])
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível iniciar o jogo:\n{e}")
    
    def refresh_ui(self):
        """Atualiza a interface após instalação"""
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.game_cards = []  # Reseta a lista de cards
        self.current_selection = 0
        self.setup_ui()

if __name__ == "__main__":
    root = tk.Tk()
    app = GameLauncher(root)
    root.mainloop()