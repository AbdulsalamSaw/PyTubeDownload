import os
import tkinter as tk
from tkinter import filedialog
from threading import Thread
import yt_dlp
import shutil

class YoutubeDownloaderUI:
    def __init__(self, master):
        self.master = master
        master.title("YouTube Downloader (yt-dlp)")

        self.file_type_var = tk.StringVar()
        self.file_type_var.set("mp4")  # Default file type

        # Set up ffmpeg path to local directory
        self.setup_ffmpeg_path()
        
        self.create_widgets()

    def setup_ffmpeg_path(self):
        """Add the current directory to PATH so yt-dlp can find local ffmpeg.exe"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Add script directory to PATH if not already there
        if script_dir not in os.environ['PATH']:
            os.environ['PATH'] = script_dir + os.pathsep + os.environ['PATH']

    def check_ffmpeg(self):
        """Check if ffmpeg is available (local directory or system PATH)"""
        # Check in script directory first
        script_dir = os.path.dirname(os.path.abspath(__file__))
        local_ffmpeg = os.path.join(script_dir, 'ffmpeg.exe')
        
        if os.path.exists(local_ffmpeg):
            print(f"Found local ffmpeg at: {local_ffmpeg}")
            return True
        
        # Check system PATH
        if shutil.which('ffmpeg') is not None:
            print("Found ffmpeg in system PATH")
            return True
        
        print("ffmpeg not found")
        return False

    def create_widgets(self):
        # Frame to hold all widgets
        self.main_frame = tk.Frame(self.master)
        self.main_frame.pack(padx=20, pady=20)

        # URL Entry
        self.url_label = tk.Label(self.main_frame, text="Enter YouTube URL or Playlist URL or Dailymotion URL :")
        self.url_label.grid(row=0, column=0, sticky="w", pady=5)

        self.url_entry = tk.Entry(self.main_frame, width=50)
        self.url_entry.grid(row=0, column=1, pady=5)

        # Paste button
        self.paste_button = tk.Button(self.main_frame, text="Paste", command=self.paste_url)
        self.paste_button.grid(row=0, column=2, pady=5, padx=(0, 20))

        # Quality Selection
        self.quality_label = tk.Label(self.main_frame, text="Select video quality:")
        self.quality_label.grid(row=1, column=0, sticky="w", pady=5)

        self.quality_var = tk.StringVar()
        self.quality_var.set("720p")  # Default quality
        qualities = ["360p", "480p", "720p", "1080p", "1440p", "Highest"]
        self.quality_menu = tk.OptionMenu(self.main_frame, self.quality_var, *qualities)
        self.quality_menu.grid(row=1, column=1, pady=5)

        # File Type Selection
        self.file_type_label = tk.Label(self.main_frame, text="Select file type:")
        self.file_type_label.grid(row=2, column=0, sticky="w", pady=5)

        self.file_type_menu = tk.OptionMenu(self.main_frame, self.file_type_var, "mp3", "mp4")
        self.file_type_menu.grid(row=2, column=1, pady=5)

        # Output Folder Selection
        self.output_label = tk.Label(self.main_frame, text="Choose download folder:")
        self.output_label.grid(row=3, column=0, sticky="w", pady=5)

        self.output_path_var = tk.StringVar()
        self.output_path_var.set(os.path.join(os.path.expanduser("~"), "Downloads"))
        self.output_entry = tk.Entry(self.main_frame, textvariable=self.output_path_var, width=40)
        self.output_entry.grid(row=3, column=1, pady=5)

        self.browse_button = tk.Button(self.main_frame, text="Browse", command=self.browse_folder)
        self.browse_button.grid(row=3, column=2, pady=5, padx=(0, 20))

        # Progress Label
        self.progress_label = tk.Label(self.main_frame, text="", fg="blue")
        self.progress_label.grid(row=4, columnspan=3, pady=10)

        # Download Button
        self.download_button = tk.Button(self.main_frame, text="Download", command=self.start_download)
        self.download_button.grid(row=5, columnspan=3, pady=10)

        # Exit Button
        self.quit_button = tk.Button(self.main_frame, text="Exit", command=self.master.destroy)
        self.quit_button.grid(row=6, columnspan=3, pady=10)


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
                self.show_message(f"Downloading... {percent} (Speed: {speed})")
            except:
                pass
        elif d['status'] == 'finished':
            self.show_message("Processing...")

    def download_video(self, video_url, output_path, quality):
        try:
            # Check for ffmpeg
            has_ffmpeg = self.check_ffmpeg()
            
            # Convert quality format (720p -> 720)
            quality_num = quality.replace('p', '') if quality != 'Highest' else '2160'
            
            print(f"FFmpeg available: {has_ffmpeg}")
            
            ydl_opts = {
                'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
                'progress_hooks': [self.progress_hook],
                'quiet': False,
                'no_warnings': False,
            }

            # Choose format based on ffmpeg availability
            if has_ffmpeg:
                # With ffmpeg: can merge video+audio for high quality
                ydl_opts['format'] = f'bestvideo[height<={quality_num}][ext=mp4]+bestaudio[ext=m4a]/best[height<={quality_num}]/best'
                ydl_opts['merge_output_format'] = 'mp4'
                print(f"Using ffmpeg mode - quality up to {quality}")
            else:
                # Without ffmpeg: use single file (progressive) - usually max 720p
                ydl_opts['format'] = 'best[ext=mp4]/best'
                print("No ffmpeg - using best single file format (max 720p usually)")
                if int(quality_num) > 720:
                    self.show_message("Warning: 1080p+ requires ffmpeg. Downloading best available...")

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                title = info.get('title', 'Video')
                self.show_message(f"Downloaded: {title}")

        except Exception as e:
            error_msg = str(e)
            print(f"Error: {error_msg}")
            if "ffmpeg" in error_msg.lower():
                self.show_message("Error: ffmpeg needed for this quality. Install ffmpeg or choose lower quality.")
            else:
                self.show_message(f"Error: {error_msg}")

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
                self.show_message("Warning: Downloading as m4a (ffmpeg needed for mp3)")

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                title = info.get('title', 'Audio')
                self.show_message(f"Downloaded: {title}")

        except Exception as e:
            self.show_message(f"Error: {str(e)}")

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
                self.show_message("Downloading playlist...")
                ydl.download([playlist_url])
                self.show_message("Playlist downloaded successfully!")

        except Exception as e:
            self.show_message(f"Error: {str(e)}")

    def start_download(self):
        url = self.url_entry.get().strip()
        output_path = self.output_path_var.get()
        quality = self.quality_var.get()
        file_type = self.file_type_var.get()

        if not url or not output_path:
            self.show_message("Please enter a valid URL and output path.")
            return

        # Create output directory if doesn't exist
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        self.show_message("Starting download...")

        # Determine if playlist or single video
        if 'list=' in url:
            Thread(target=self.download_playlist, args=(url, output_path, quality), daemon=True).start()
        elif file_type == "mp3":
            Thread(target=self.download_audio, args=(url, output_path), daemon=True).start()
        else:
            Thread(target=self.download_video, args=(url, output_path, quality), daemon=True).start()

    def show_message(self, message):
        self.progress_label.config(text=message)
        print(message)

if __name__ == "__main__":
    root = tk.Tk()
    app = YoutubeDownloaderUI(root)
    root.mainloop()
