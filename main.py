import os
import requests
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import subprocess
import pygame
from pygame.locals import *
from PIL import Image, ImageTk
import time

class GameLauncher:
    def __init__(self, root):
        # Configuração inicial do mixer de áudio
        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.init()
        
        self.root = root
        self.setup_variables()
        self.setup_window()
        self.load_assets()
        self.setup_joystick()
        self.setup_main_menu()
        self.start_control_thread()
        self.game_process = None
        self.play_sound("startup")

    def setup_variables(self):
        """Inicializa todas as variáveis necessárias"""
        self.selected_index = 0
        self.selected_card_index = 0
        self.downloading = False
        self.running = True
        self.current_screen = "main_menu"
        self.game_cards = []
        self.menu_options = []
        self.menu_widgets = []
        self.games = [
            {
                "title": "Target Game",
                "version": "v2.0",
                "size": "45 MB",
                "file": "target_game.exe",
                "repo": "gu2121gg/Projeto-Xemuloter",
                "installed": os.path.exists("TargetGame/target_game.exe"),
                "cover": os.path.join("assets", "games", "game1.jpg")
            },
            {
                "title": "PS2 Emulator",
                "version": "v1.5",
                "size": "15 MB",
                "file": "ps2_emulator.exe",
                "repo": "gu2121gg/Projeto-Xemuloter",
                "installed": False,
                "cover": os.path.join("assets", "icons", "opl_logo.png")
            }
        ]

    def setup_window(self):
        """Configura a janela principal"""
        self.root.title("PS2 Game Launcher")
        self.root.geometry("1280x720")
        self.root.configure(bg="#1a1a1a")
        self.root.resizable(True, True)
        self.root.minsize(1024, 576)
        
        try:
            icon_path = os.path.join("assets", "icons", "game_icon.png")
            icon = Image.open(icon_path)
            photo = ImageTk.PhotoImage(icon)
            self.root.iconphoto(False, photo)
        except Exception as e:
            print(f"Erro ao carregar ícone: {e}")
            
        self.center_window()

    def center_window(self):
        """Centraliza a janela na tela"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def load_assets(self):
        """Carrega recursos visuais e sonoros"""
        self.colors = {
            "bg": "#1a1a1a",
            "card": "#252525",
            "text": "#ffffff",
            "accent": "#4CAF50",
            "secondary": "#3498db",
            "highlight": "#FF5722",
            "disabled": "#777777"
        }
        
        # Configuração dos sons
        self.sounds = {
            "back": os.path.join("assets", "audio", "back.wav"),
            "confirm": os.path.join("assets", "audio", "confirm.wav"),
            "navigate": os.path.join("assets", "audio", "navigate.wav"),
            "select": os.path.join("assets", "audio", "select.wav"),
            "startup": os.path.join("assets", "audio", "startup.wav")
        }

    def play_sound(self, sound_name):
        """Toca um efeito sonoro"""
        try:
            if sound_name in self.sounds:
                sound_path = self.sounds[sound_name]
                if os.path.exists(sound_path):
                    sound = pygame.mixer.Sound(sound_path)
                    sound.set_volume(0.5)
                    sound.play()
                else:
                    print(f"Arquivo de som não encontrado: {sound_path}")
            else:
                print(f"Som não definido: {sound_name}")
        except Exception as e:
            print(f"Erro ao tocar som {sound_name}: {e}")

    def setup_joystick(self):
        """Configura o controle PS2"""
        try:
            pygame.joystick.init()
            
            if pygame.joystick.get_count() > 0:
                self.joystick = pygame.joystick.Joystick(0)
                self.joystick.init()
                print(f"Controle conectado: {self.joystick.get_name()}")
                
                # Configuração dos botões específicos para controles PS2
                self.button_map = {
                    'x': 0,    # Botão X (confirmar)
                    'circle': 1,  # Botão O (voltar)
                    'square': 2,
                    'triangle': 3,
                    'up': (1, 1),    # Eixo do hat (cima)
                    'down': (1, -1), # Eixo do hat (baixo)
                    'left': (0, -1), # Eixo do hat (esquerda)
                    'right': (0, 1)  # Eixo do hat (direita)
                }
            else:
                self.joystick = None
                print("Conecte um controle PS2")
                
        except Exception as e:
            print(f"Erro no controle: {e}")
            self.joystick = None

    def start_control_thread(self):
        """Inicia a thread de controle"""
        self.control_thread = threading.Thread(target=self.control_loop, daemon=True)
        self.control_thread.start()

    def setup_main_menu(self):
        """Configura o menu principal"""
        self.clear_screen()
        self.current_screen = "main_menu"
        self.selected_index = 0
        
        main_frame = tk.Frame(self.root, bg=self.colors["bg"])
        main_frame.pack(fill="both", expand=True)

        try:
            logo_path = os.path.join("assets", "icons", "opl_logo.png")
            logo_img = Image.open(logo_path)
            logo_img = logo_img.resize((300, 150), Image.LANCZOS)
            self.opl_logo = ImageTk.PhotoImage(logo_img)
            logo_label = tk.Label(main_frame, image=self.opl_logo, bg=self.colors["bg"])
            logo_label.pack(pady=(40, 20))
        except Exception as e:
            print(f"Erro ao carregar logo: {e}")
            tk.Label(main_frame, 
                    text="GAME LAUNCHER",
                    font=("Arial", 36, "bold"),
                    bg=self.colors["bg"],
                    fg=self.colors["accent"]).pack(pady=50)

        self.menu_options = ["Jogos", "Extras", "Configurações", "Sair"]
        self.menu_widgets = []
        
        for i, option in enumerate(self.menu_options):
            frame = tk.Frame(main_frame, bg=self.colors["bg"])
            frame.pack(pady=5)
            
            try:
                icon_name = option.lower().replace("ç", "c").replace("õ", "o") + "_icon.png"
                icon_path = os.path.join("assets", "icons", icon_name)
                icon_img = Image.open(icon_path)
                icon_img = icon_img.resize((30, 30), Image.LANCZOS)
                icon = ImageTk.PhotoImage(icon_img)
                icon_label = tk.Label(frame, image=icon, bg=self.colors["bg"])
                icon_label.image = icon
                icon_label.pack(side="left", padx=10)
            except Exception as e:
                print(f"Erro ao carregar ícone {option}: {e}")
                selector = tk.Label(frame, text="▶", 
                                 font=("Arial", 16),
                                 bg=self.colors["bg"],
                                 fg=self.colors["accent"] if i == self.selected_index else self.colors["bg"])
                selector.pack(side="left", padx=10)
            
            option_label = tk.Label(frame, 
                                text=option,
                                font=("Arial", 24),
                                bg=self.colors["bg"],
                                fg=self.colors["text"] if i == self.selected_index else self.colors["disabled"])
            option_label.pack(side="left")
            
            self.menu_widgets.append((frame, option_label))

        tk.Label(main_frame, 
                text="Controle PS2: ▲/▼ Navegar  x Confirmar  ○ Voltar",
                font=("Arial", 12),
                bg=self.colors["bg"],
                fg=self.colors["disabled"]).pack(side="bottom", pady=20)

        self.update_menu_selection()

    def update_menu_selection(self):
        """Atualiza a seleção no menu"""
        for i, (frame, label) in enumerate(self.menu_widgets):
            if i == self.selected_index:
                label.config(fg=self.colors["text"], font=("Arial", 24, "bold"))
                for child in frame.winfo_children():
                    if isinstance(child, tk.Label) and child.cget("text") == "▶":
                        child.config(fg=self.colors["accent"])
            else:
                label.config(fg=self.colors["disabled"], font=("Arial", 24))
                for child in frame.winfo_children():
                    if isinstance(child, tk.Label) and child.cget("text") == "▶":
                        child.config(fg=self.colors["bg"])

    def setup_games_menu(self):
        """Configura o menu de jogos"""
        self.clear_screen()
        self.current_screen = "games"
        self.selected_card_index = 0
        
        main_frame = tk.Frame(self.root, bg=self.colors["bg"])
        main_frame.pack(fill="both", expand=True)

        header = tk.Frame(main_frame, bg="#2a2a2a")
        header.pack(fill="x", pady=(0, 20))

        try:
            back_icon_path = os.path.join("assets", "icons", "back_icon.png")
            back_icon = Image.open(back_icon_path)
            back_icon = back_icon.resize((25, 25), Image.LANCZOS)
            self.back_icon_img = ImageTk.PhotoImage(back_icon)
            back_btn = tk.Button(header, 
                               image=self.back_icon_img,
                               command=self.back_to_main,
                               bg="#2a2a2a",
                               fg=self.colors["text"],
                               bd=0,
                               activebackground="#3a3a3a")
            back_btn.pack(side="left", padx=10, pady=5)
        except Exception as e:
            print(f"Erro ao carregar ícone de voltar: {e}")
            back_btn = tk.Button(header, 
                               text="← Voltar",
                               command=self.back_to_main,
                               font=("Arial", 12),
                               bg="#2a2a2a",
                               fg=self.colors["text"],
                               bd=0)
            back_btn.pack(side="left", padx=20, pady=10)

        tk.Label(header, 
                text="JOGOS DISPONÍVEIS",
                font=("Arial", 20, "bold"),
                bg="#2a2a2a",
                fg=self.colors["text"]).pack(side="left", padx=20, pady=10)

        container = tk.Frame(main_frame, bg=self.colors["bg"])
        container.pack(fill="both", expand=True, padx=20, pady=10)

        canvas = tk.Canvas(container, bg=self.colors["bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors["bg"])

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Guarda referência ao canvas para rolagem
        self.games_canvas = canvas

        self.game_cards = []
        for i, game in enumerate(self.games):
            card = tk.Frame(scrollable_frame,
                          bg=self.colors["card"],
                          highlightthickness=2,
                          highlightbackground=self.colors["highlight"] if i == 0 else self.colors["bg"],
                          padx=20,
                          pady=15)
            card.pack(fill="x", pady=10)
            card.grid_columnconfigure(0, weight=1)
            card.grid_columnconfigure(1, weight=3)

            try:
                cover_path = game["cover"]
                cover_img = Image.open(cover_path)
                cover_img = cover_img.resize((120, 120), Image.LANCZOS)
                if not hasattr(self, 'game_covers'):
                    self.game_covers = {}
                self.game_covers[i] = ImageTk.PhotoImage(cover_img)
                cover_label = tk.Label(card, image=self.game_covers[i], bg=self.colors["card"])
                cover_label.grid(row=0, column=0, rowspan=3, padx=10, pady=5, sticky="nsew")
            except Exception as e:
                print(f"Erro ao carregar capa do jogo {game['title']}: {e}")
                tk.Label(card, 
                        text="Sem Imagem",
                        font=("Arial", 10),
                        bg=self.colors["card"],
                        fg=self.colors["disabled"]).grid(row=0, column=0, rowspan=3, padx=10, pady=5)

            info_frame = tk.Frame(card, bg=self.colors["card"])
            info_frame.grid(row=0, column=1, sticky="nsew", padx=10)

            tk.Label(info_frame, 
                    text=game["title"],
                    font=("Arial", 18, "bold"),
                    bg=self.colors["card"],
                    fg=self.colors["text"]).pack(anchor="w")

            tk.Label(info_frame, 
                    text=f"Versão: {game['version']} | Tamanho: {game['size']}",
                    font=("Arial", 12),
                    bg=self.colors["card"],
                    fg=self.colors["disabled"]).pack(anchor="w", pady=5)

            btn_frame = tk.Frame(card, bg=self.colors["card"])
            btn_frame.grid(row=1, column=1, sticky="e", padx=10)

            btn_text = "JOGAR" if game["installed"] else "INSTALAR"
            btn_color = self.colors["accent"] if game["installed"] else self.colors["secondary"]
            
            action_btn = tk.Button(btn_frame,
                                 text=btn_text,
                                 command=lambda g=game: self.play_or_download(g),
                                 font=("Arial", 12, "bold"),
                                 bg=btn_color,
                                 fg=self.colors["text"],
                                 bd=0,
                                 padx=20,
                                 activebackground=self.colors["highlight"])
            action_btn.pack(pady=10, ipady=5)

            self.game_cards.append(card)

    def play_or_download(self, game):
        """Decide se executa ou baixa o jogo"""
        if game["installed"]:
            self.play_game(game)
        else:
            self.download_game(game)

    def play_game(self, game):
        """Executa o jogo e mostra botão de voltar"""
        try:
            self.clear_screen()
            self.current_screen = "in_game"
            
            game_frame = tk.Frame(self.root, bg=self.colors["bg"])
            game_frame.pack(fill="both", expand=True)
            
            back_btn = tk.Button(game_frame,
                               text="Voltar ao Menu (○)",
                               command=self.back_to_main_from_game,
                               font=("Arial", 14),
                               bg=self.colors["highlight"],
                               fg=self.colors["text"],
                               bd=0,
                               padx=30,
                               pady=10)
            back_btn.place(relx=0.5, rely=0.9, anchor="center")
            
            self.game_process = subprocess.Popen([f"TargetGame/{game['file']}"])
            
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível iniciar o jogo:\n{e}")
            self.setup_games_menu()

    def back_to_main_from_game(self):
        """Volta ao menu principal durante o jogo"""
        if self.game_process:
            self.game_process.terminate()
            self.game_process = None
        self.setup_main_menu()

    def download_game(self, game):
        """Inicia o download do jogo"""
        if self.downloading:
            return
            
        self.downloading = True
        
        download_window = tk.Toplevel(self.root)
        download_window.title(f"Baixando {game['title']}")
        download_window.geometry("500x250")
        
        main_frame = tk.Frame(download_window, padx=30, pady=30)
        main_frame.pack(fill="both", expand=True)

        tk.Label(main_frame, 
                text=f"Baixando {game['title']}",
                font=("Arial", 16, "bold")).pack(pady=(0, 20))

        self.progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(main_frame, 
                                     variable=self.progress_var,
                                     maximum=100,
                                     length=400)
        progress_bar.pack(fill="x")

        self.status_label = tk.Label(main_frame, text="Preparando download...", font=("Arial", 10))
        self.status_label.pack(pady=5)

        self.details_label = tk.Label(main_frame, text="", font=("Arial", 8))
        self.details_label.pack()

        cancel_btn = tk.Button(main_frame, 
                             text="Cancelar",
                             command=lambda: self.cancel_download(download_window),
                             font=("Arial", 12),
                             bg=self.colors["bg"],
                             fg=self.colors["text"],
                             bd=0)
        cancel_btn.pack(pady=20)

        threading.Thread(
            target=self.execute_download,
            args=(game, download_window),
            daemon=True
        ).start()

    def execute_download(self, game, window):
        """Executa o download em segundo plano"""
        try:
            os.makedirs("TargetGame", exist_ok=True)
            destination = f"TargetGame/{game['file']}"
            url = f"https://github.com/{game['repo']}/releases/download/{game['version']}/{game['file']}"
            
            with requests.get(url, stream=True) as response:
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
                            progress = (downloaded / total_size) * 100
                            elapsed = time.time() - start_time
                            speed = (downloaded / (1024 * 1024)) / elapsed if elapsed > 0 else 0
                            
                            window.after(0, self.update_download_ui, progress, downloaded, total_size, speed)
            
            window.after(0, lambda: self.download_complete(window, game))
            
        except Exception as e:
            window.after(0, lambda: self.download_failed(window, str(e)))
        finally:
            self.downloading = False

    def update_download_ui(self, progress, downloaded, total, speed):
        """Atualiza a interface do download"""
        self.progress_var.set(progress)
        self.status_label.config(text=f"Download: {progress:.1f}% completo")
        downloaded_mb = downloaded / (1024 * 1024)
        total_mb = total / (1024 * 1024)
        self.details_label.config(text=f"{downloaded_mb:.1f}MB de {total_mb:.1f}MB | {speed:.2f} MB/s")

    def download_complete(self, window, game):
        """Finaliza o download com sucesso"""
        window.destroy()
        messagebox.showinfo("Sucesso", f"{game['title']} instalado com sucesso!")
        self.games[0]["installed"] = True  # Atualiza status de instalação
        self.setup_games_menu()

    def download_failed(self, window, error):
        """Mostra erro no download"""
        window.destroy()
        messagebox.showerror("Erro", f"Falha no download:\n{error}")

    def cancel_download(self, window):
        """Cancela o download"""
        self.downloading = False
        window.destroy()

    def back_to_main(self):
        """Volta para o menu principal"""
        self.play_sound("back")
        self.current_screen = "main_menu"
        self.setup_main_menu()

    def clear_screen(self):
        """Limpa a tela"""
        for widget in self.root.winfo_children():
            widget.destroy()

    def control_loop(self):
        """Loop principal para controle do PS2"""
        clock = pygame.time.Clock()
        
        while self.running:
            clock.tick(30)
            
            if not self.joystick:
                time.sleep(0.1)
                continue
                
            for event in pygame.event.get():
                if event.type == JOYHATMOTION:
                    if event.value[1] == 1:  # Cima
                        self.move_selection(-1)
                    elif event.value[1] == -1:  # Baixo
                        self.move_selection(1)
                        
                elif event.type == JOYBUTTONDOWN:
                    if event.button == self.button_map['x']:  # Botão X (confirmar)
                        self.select_item()
                    elif event.button == self.button_map['circle']:  # Botão O (voltar)
                        self.back_action()

    def move_selection(self, direction):
        """Move a seleção no menu"""
        if self.current_screen == "main_menu":
            new_index = (self.selected_index + direction) % len(self.menu_options)
            if new_index != self.selected_index:
                self.selected_index = new_index
                self.update_menu_selection()
                self.play_sound("navigate")
                
        elif self.current_screen == "games":
            if not self.game_cards:
                return
                
            new_index = max(0, min(len(self.game_cards) - 1, self.selected_card_index + direction))
            if new_index != self.selected_card_index:
                self.game_cards[self.selected_card_index].config(highlightbackground=self.colors["bg"])
                self.selected_card_index = new_index
                self.game_cards[self.selected_card_index].config(highlightbackground=self.colors["highlight"])
                
                # Rolagem suave para o card selecionado
                self.games_canvas.yview_moveto(self.selected_card_index / len(self.game_cards))
                
                self.play_sound("navigate")

    def select_item(self):
        """Processa a seleção atual"""
        self.play_sound("confirm")
        if self.current_screen == "main_menu":
            if self.menu_options[self.selected_index] == "Jogos":
                self.setup_games_menu()
            elif self.menu_options[self.selected_index] == "Sair":
                self.root.quit()
                
        elif self.current_screen == "games":
            if self.game_cards:
                for child in self.game_cards[self.selected_card_index].winfo_children():
                    if isinstance(child, tk.Button):
                        child.invoke()
                        break

    def back_action(self):
        """Volta para o menu anterior"""
        if self.current_screen == "in_game":
            self.back_to_main_from_game()
        elif self.current_screen == "games":
            self.back_to_main()
        elif self.current_screen == "main_menu":
            self.root.quit()

    def on_closing(self):
        """Lida com o fechamento da janela"""
        if self.game_process:
            self.game_process.terminate()
        self.running = False
        pygame.quit()
        self.root.destroy()

if __name__ == "__main__":
    # Verifica e cria a estrutura de diretórios necessária
    required_dirs = [
        "assets",
        os.path.join("assets", "audio"),
        os.path.join("assets", "games"),
        os.path.join("assets", "icons"),
        "TargetGame"
    ]
    
    for directory in required_dirs:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Diretório criado: {directory}")
    
    root = tk.Tk()
    app = GameLauncher(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()