import os
import tkinter as tk
from tkinter import filedialog
from threading import Thread
from pytube import Playlist, YouTube
import youtube_dl

class YoutubeDownloaderUI:
    def __init__(self, master):
        self.master = master
        master.title("YouTube Downloader")

        self.file_type_var = tk.StringVar()
        self.file_type_var.set("mp4")  # Default file type

        self.create_widgets()

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
        qualities = ["144p", "240p", "360p", "480p", "720p", "1080p", "Highest"]
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
        self.output_path_var.set(os.path.expanduser("~"))
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
        self.output_path_var.set(folder_selected)

    def paste_url(self):
        url_from_clipboard = self.master.clipboard_get()
        self.url_entry.delete(0, tk.END)
        self.url_entry.insert(0, url_from_clipboard)

    def download_audio(self, video_url, output_path):
        try:
            yt = YouTube(video_url)
            audio_stream = yt.streams.filter(only_audio=True).first()
            if not audio_stream:
                self.show_message("No audio stream available for the provided video.")
                return

            audio_stream.download(output_path)
            audio_filename = audio_stream.default_filename
            audio_output_path = os.path.join(output_path, audio_filename)
            
            # Convert to MP3
            mp3_filename = os.path.splitext(audio_filename)[0] + ".mp3"
            mp3_output_path = os.path.join(output_path, mp3_filename)
            os.rename(audio_output_path, mp3_output_path)

            self.show_message(f"Audio downloaded: {mp3_filename}")

        except Exception as e:
            self.show_message(f"An error occurred while downloading the audio: {str(e)}")

    def download_video(self, video_url, output_path, quality):
       try:
            yt = YouTube(video_url)
            video_stream = yt.streams.filter(res=quality, file_extension='mp4').first()
            if not video_stream:
                video_stream = yt.streams.get_highest_resolution()
            video_stream.download(output_path)
            self.show_message(f"Video downloaded: {yt.title}")

            # Open the downloaded video automatically
            video_path = os.path.join(output_path, f"{yt.title}.mp4")

       except Exception as e:
            self.show_message(f"An error occurred while downloading the video: {str(e)}")



    def download_dailymotion_video(self, video_url, output_path, quality):
        ydl_opts = {
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
            self.show_message("Video downloaded successfully")

    def download_playlist(self, playlist_url, output_path, quality, batch_size=5):
        try:
            playlist = Playlist(playlist_url)
            num_videos = len(playlist.video_urls)

            for i in range(0, num_videos, batch_size):
                batch = playlist.video_urls[i:i + batch_size]

                threads = []
                for video_url in batch:
                    thread = Thread(target=self.download, args=(video_url, output_path, quality))
                    threads.append(thread)
                    thread.start()

                for thread in threads:
                    thread.join()

                self.show_message(f"Downloaded {min(batch_size, num_videos - i)} videos out of {num_videos}")

            self.show_message("Playlist downloaded successfully!")

        except Exception as e:
            self.show_message(f"An error occurred while downloading the playlist: {str(e)}")

    def start_download(self):
        url = self.url_entry.get()
        output_path = self.output_path_var.get()
        quality = self.quality_var.get()
        file_type = self.file_type_var.get()

        if not url or not output_path:
            self.show_message("Please enter a valid URL and output path.")
            return

        self.progress_label.config(text="Downloading...")

        if 'dailymotion.com' in url:
            Thread(target=self.download_dailymotion_video, args=(url, output_path, quality)).start()

        elif 'list=' in url:
            Thread(target=self.download_playlist, args=(url, output_path, quality, 2)).start()

        if file_type == "mp3":
            Thread(target=self.download_audio, args=(url, output_path)).start()
        else:
            Thread(target=self.download_video, args=(url, output_path, quality)).start()

    def show_message(self, message):
        self.progress_label.config(text=message)

if __name__ == "__main__":
    root = tk.Tk()
    app = YoutubeDownloaderUI(root)
    root.mainloop()
