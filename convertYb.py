import os
import tkinter as tk
from tkinter import filedialog, ttk
from threading import Thread
import yt_dlp
import shutil

class ModernButton(tk.Canvas):
    """Custom modern button with gradient effect"""
    def __init__(self, parent, text, command, bg_color="#4A90E2", hover_color="#357ABD", **kwargs):
        super().__init__(parent, height=45, bd=0, highlightthickness=0, **kwargs)
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text = text
        
        self.draw_button(bg_color)
        self.bind("<Enter>", lambda e: self.draw_button(self.hover_color))
        self.bind("<Leave>", lambda e: self.draw_button(self.bg_color))
        self.bind("<Button-1>", lambda e: self.on_click())
        
    def draw_button(self, color):
        self.delete("all")
        width = self.winfo_reqwidth() or 200
        self.create_rectangle(0, 0, width, 45, fill=color, outline="", tags="button")
        self.create_text(width//2, 22, text=self.text, fill="white", 
                        font=("Segoe UI", 11, "bold"), tags="text")
        
    def on_click(self):
        if self.command:
            self.command()

class YoutubeDownloaderUI:
    def __init__(self, master):
        self.master = master
        master.title("YouTube Downloader")
        master.geometry("750x600")
        master.configure(bg="#1a1a2e")
        
        # Make window non-resizable for consistent design
        master.resizable(False, False)
        
        # Center window on screen
        self.center_window()

        self.file_type_var = tk.StringVar()
        self.file_type_var.set("mp4")

        # Set up ffmpeg path to local directory
        self.setup_ffmpeg_path()
        
        self.create_widgets()

    def center_window(self):
        """Center the window on screen"""
        self.master.update_idletasks()
        width = 750
        height = 600
        x = (self.master.winfo_screenwidth() // 2) - (width // 2)
        y = (self.master.winfo_screenheight() // 2) - (height // 2)
        self.master.geometry(f'{width}x{height}+{x}+{y}')

    def setup_ffmpeg_path(self):
        """Add the current directory to PATH so yt-dlp can find local ffmpeg.exe"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        if script_dir not in os.environ['PATH']:
            os.environ['PATH'] = script_dir + os.pathsep + os.environ['PATH']

    def check_ffmpeg(self):
        """Check if ffmpeg is available (local directory or system PATH)"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        local_ffmpeg = os.path.join(script_dir, 'ffmpeg.exe')
        
        if os.path.exists(local_ffmpeg):
            print(f"Found local ffmpeg at: {local_ffmpeg}")
            return True
        
        if shutil.which('ffmpeg') is not None:
            print("Found ffmpeg in system PATH")
            return True
        
        print("ffmpeg not found")
        return False

    def create_widgets(self):
        # Main container with gradient effect
        self.main_frame = tk.Frame(self.master, bg="#1a1a2e")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header with gradient
        header_frame = tk.Frame(self.main_frame, bg="#16213e", height=80)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        # Title
        title_label = tk.Label(header_frame, text="🎬 YouTube Downloader", 
                              font=("Segoe UI", 24, "bold"), 
                              fg="#4A90E2", bg="#16213e")
        title_label.pack(pady=20)
        
        # Content area
        content_frame = tk.Frame(self.main_frame, bg="#1a1a2e")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)
        
        # URL Section
        url_frame = tk.Frame(content_frame, bg="#1a1a2e")
        url_frame.pack(fill=tk.X, pady=(0, 20))
        
        url_label = tk.Label(url_frame, text="📎 Video URL", 
                            font=("Segoe UI", 11, "bold"), 
                            fg="#e8e8e8", bg="#1a1a2e")
        url_label.pack(anchor="w", pady=(0, 8))
        
        url_input_frame = tk.Frame(url_frame, bg="#16213e", highlightthickness=1, 
                                  highlightbackground="#4A90E2")
        url_input_frame.pack(fill=tk.X)
        
        self.url_entry = tk.Entry(url_input_frame, font=("Segoe UI", 11), 
                                 bg="#16213e", fg="#ffffff", 
                                 bd=0, insertbackground="#4A90E2")
        self.url_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15, pady=12)
        
        paste_btn = tk.Button(url_input_frame, text="📋 Paste", 
                            command=self.paste_url,
                            font=("Segoe UI", 10, "bold"),
                            bg="#4A90E2", fg="white", 
                            bd=0, padx=20, pady=8,
                            cursor="hand2",
                            activebackground="#357ABD")
        paste_btn.pack(side=tk.RIGHT, padx=8, pady=8)
        
        # Options Section
        options_frame = tk.Frame(content_frame, bg="#1a1a2e")
        options_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Quality and Type in same row
        row1_frame = tk.Frame(options_frame, bg="#1a1a2e")
        row1_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Quality
        quality_container = tk.Frame(row1_frame, bg="#1a1a2e")
        quality_container.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        quality_label = tk.Label(quality_container, text="🎥 Quality", 
                                font=("Segoe UI", 11, "bold"), 
                                fg="#e8e8e8", bg="#1a1a2e")
        quality_label.pack(anchor="w", pady=(0, 8))
        
        self.quality_var = tk.StringVar()
        self.quality_var.set("720p")
        
        quality_frame = tk.Frame(quality_container, bg="#16213e", highlightthickness=1, 
                                highlightbackground="#4A90E2")
        quality_frame.pack(fill=tk.X)
        
        qualities = ["360p", "480p", "720p", "1080p", "1440p", "Highest"]
        self.quality_menu = ttk.Combobox(quality_frame, textvariable=self.quality_var,
                                        values=qualities, state="readonly",
                                        font=("Segoe UI", 11))
        self.quality_menu.pack(fill=tk.X, padx=10, pady=10)
        
        # File Type
        type_container = tk.Frame(row1_frame, bg="#1a1a2e")
        type_container.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
        
        type_label = tk.Label(type_container, text="📁 Format", 
                             font=("Segoe UI", 11, "bold"), 
                             fg="#e8e8e8", bg="#1a1a2e")
        type_label.pack(anchor="w", pady=(0, 8))
        
        type_frame = tk.Frame(type_container, bg="#16213e", highlightthickness=1, 
                             highlightbackground="#4A90E2")
        type_frame.pack(fill=tk.X)
        
        self.file_type_menu = ttk.Combobox(type_frame, textvariable=self.file_type_var,
                                          values=["mp4", "mp3"], state="readonly",
                                          font=("Segoe UI", 11))
        self.file_type_menu.pack(fill=tk.X, padx=10, pady=10)
        
        # Output Folder
        folder_label = tk.Label(options_frame, text="💾 Download Location", 
                               font=("Segoe UI", 11, "bold"), 
                               fg="#e8e8e8", bg="#1a1a2e")
        folder_label.pack(anchor="w", pady=(0, 8))
        
        folder_frame = tk.Frame(options_frame, bg="#16213e", highlightthickness=1, 
                               highlightbackground="#4A90E2")
        folder_frame.pack(fill=tk.X)
        
        self.output_path_var = tk.StringVar()
        self.output_path_var.set(os.path.join(os.path.expanduser("~"), "Downloads"))
        
        self.output_entry = tk.Entry(folder_frame, textvariable=self.output_path_var,
                                    font=("Segoe UI", 11), 
                                    bg="#16213e", fg="#ffffff", 
                                    bd=0, insertbackground="#4A90E2")
        self.output_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15, pady=12)
        
        browse_btn = tk.Button(folder_frame, text="📂 Browse", 
                             command=self.browse_folder,
                             font=("Segoe UI", 10, "bold"),
                             bg="#4A90E2", fg="white", 
                             bd=0, padx=20, pady=8,
                             cursor="hand2",
                             activebackground="#357ABD")
        browse_btn.pack(side=tk.RIGHT, padx=8, pady=8)
        
        # Progress Section
        progress_container = tk.Frame(content_frame, bg="#16213e", 
                                     highlightthickness=1, highlightbackground="#2d2d44")
        progress_container.pack(fill=tk.X, pady=(0, 25))
        
        self.progress_label = tk.Label(progress_container, text="Ready to download", 
                                      font=("Segoe UI", 10), 
                                      fg="#b8b8b8", bg="#16213e",
                                      pady=15)
        self.progress_label.pack()
        
        # Buttons
        buttons_frame = tk.Frame(content_frame, bg="#1a1a2e")
        buttons_frame.pack(fill=tk.X)
        
        # Download Button
        download_btn = tk.Button(buttons_frame, text="⬇️  Download", 
                               command=self.start_download,
                               font=("Segoe UI", 13, "bold"),
                               bg="#4ECDC4", fg="white", 
                               bd=0, padx=30, pady=15,
                               cursor="hand2",
                               activebackground="#45b8b0")
        download_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Exit Button
        exit_btn = tk.Button(buttons_frame, text="✖️  Exit", 
                           command=self.master.destroy,
                           font=("Segoe UI", 13, "bold"),
                           bg="#e74c3c", fg="white", 
                           bd=0, padx=30, pady=15,
                           cursor="hand2",
                           activebackground="#c0392b")
        exit_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
        
        # Apply ttk styling
        self.apply_ttk_style()

    def apply_ttk_style(self):
        """Apply custom styling to ttk widgets"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Combobox styling
        style.configure('TCombobox', 
                       fieldbackground='#16213e',
                       background='#16213e',
                       foreground='#ffffff',
                       borderwidth=0,
                       arrowcolor='#4A90E2')
        
        style.map('TCombobox',
                 fieldbackground=[('readonly', '#16213e')],
                 selectbackground=[('readonly', '#16213e')],
                 selectforeground=[('readonly', '#ffffff')])

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.output_path_var.set(folder_selected)

    def paste_url(self):
        try:
            url_from_clipboard = self.master.clipboard_get()
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, url_from_clipboard)
        except:
            pass

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            try:
                percent = d.get('_percent_str', 'N/A')
                speed = d.get('_speed_str', 'N/A')
                self.show_message(f"⏬ Downloading... {percent} • Speed: {speed}", "#4ECDC4")
            except:
                pass
        elif d['status'] == 'finished':
            self.show_message("⚙️ Processing...", "#4A90E2")

    def download_video(self, video_url, output_path, quality):
        try:
            has_ffmpeg = self.check_ffmpeg()
            quality_num = quality.replace('p', '') if quality != 'Highest' else '2160'
            
            print(f"FFmpeg available: {has_ffmpeg}")
            
            ydl_opts = {
                'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
                'progress_hooks': [self.progress_hook],
                'quiet': False,
                'no_warnings': False,
            }

            if has_ffmpeg:
                ydl_opts['format'] = f'bestvideo[height<={quality_num}][ext=mp4]+bestaudio[ext=m4a]/best[height<={quality_num}]/best'
                ydl_opts['merge_output_format'] = 'mp4'
                print(f"Using ffmpeg mode - quality up to {quality}")
            else:
                ydl_opts['format'] = 'best[ext=mp4]/best'
                print("No ffmpeg - using best single file format (max 720p usually)")
                if int(quality_num) > 720:
                    self.show_message("⚠️ 1080p+ requires ffmpeg. Downloading best available...", "#f39c12")

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                title = info.get('title', 'Video')
                self.show_message(f"✅ Downloaded: {title}", "#4ECDC4")

        except Exception as e:
            error_msg = str(e)
            print(f"Error: {error_msg}")
            if "ffmpeg" in error_msg.lower():
                self.show_message("❌ Error: ffmpeg needed for this quality. Install ffmpeg or choose lower quality.", "#e74c3c")
            else:
                self.show_message(f"❌ Error: {error_msg[:50]}...", "#e74c3c")

    def download_audio(self, video_url, output_path):
        try:
            has_ffmpeg = self.check_ffmpeg()
            
            ydl_opts = {
                'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
                'progress_hooks': [self.progress_hook],
                'format': 'bestaudio/best',
                'quiet': False,
            }

            if has_ffmpeg:
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
                print("Downloading and converting to MP3...")
            else:
                print("Warning: ffmpeg not found. Downloading as m4a instead of mp3.")
                self.show_message("⚠️ Downloading as m4a (ffmpeg needed for mp3)", "#f39c12")

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                title = info.get('title', 'Audio')
                self.show_message(f"✅ Downloaded: {title}", "#4ECDC4")

        except Exception as e:
            self.show_message(f"❌ Error: {str(e)[:50]}...", "#e74c3c")

    def download_playlist(self, playlist_url, output_path, quality):
        try:
            has_ffmpeg = self.check_ffmpeg()
            quality_num = quality.replace('p', '') if quality != 'Highest' else '2160'
            
            ydl_opts = {
                'outtmpl': os.path.join(output_path, '%(playlist_index)s - %(title)s.%(ext)s'),
                'progress_hooks': [self.progress_hook],
                'quiet': False,
            }

            if has_ffmpeg:
                ydl_opts['format'] = f'bestvideo[height<={quality_num}][ext=mp4]+bestaudio[ext=m4a]/best'
                ydl_opts['merge_output_format'] = 'mp4'
            else:
                ydl_opts['format'] = 'best[ext=mp4]/best'

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.show_message("📋 Downloading playlist...", "#4A90E2")
                ydl.download([playlist_url])
                self.show_message("✅ Playlist downloaded successfully!", "#4ECDC4")

        except Exception as e:
            self.show_message(f"❌ Error: {str(e)[:50]}...", "#e74c3c")

    def start_download(self):
        url = self.url_entry.get().strip()
        output_path = self.output_path_var.get()
        quality = self.quality_var.get()
        file_type = self.file_type_var.get()

        if not url or not output_path:
            self.show_message("⚠️ Please enter a valid URL and output path.", "#f39c12")
            return

        if not os.path.exists(output_path):
            os.makedirs(output_path)

        self.show_message("🚀 Starting download...", "#4A90E2")

        if 'list=' in url:
            Thread(target=self.download_playlist, args=(url, output_path, quality), daemon=True).start()
        elif file_type == "mp3":
            Thread(target=self.download_audio, args=(url, output_path), daemon=True).start()
        else:
            Thread(target=self.download_video, args=(url, output_path, quality), daemon=True).start()

    def show_message(self, message, color="#b8b8b8"):
        self.progress_label.config(text=message, fg=color)
        print(message)

if __name__ == "__main__":
    root = tk.Tk()
    app = YoutubeDownloaderUI(root)
    root.mainloop()
