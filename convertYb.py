import os
import tkinter as tk
from tkinter import filedialog
from threading import Thread
from pytube import Playlist, YouTube


class YoutubeDownloaderUI:
    def __init__(self, master):
        self.master = master
        master.title("YouTube Downloader")

        self.create_widgets()

    def create_widgets(self):
        self.url_label = tk.Label(self.master, text="Enter YouTube URL or Playlist URL:")
        self.url_label.pack(pady=10)

        self.url_entry = tk.Entry(self.master, width=50)
        self.url_entry.pack(pady=10)

        # Paste button
        self.paste_button = tk.Button(self.master, text="Paste", command=self.paste_url)
        self.paste_button.pack(pady=10)

        self.quality_label = tk.Label(self.master, text="Select video quality:")
        self.quality_label.pack(pady=10)

        self.quality_var = tk.StringVar()
        self.quality_var.set("720p")  # Default quality
        qualities = ["144p", "240p", "360p", "480p", "720p", "1080p", "Highest"]
        self.quality_menu = tk.OptionMenu(self.master, self.quality_var, *qualities)
        self.quality_menu.pack(pady=10)

        self.output_label = tk.Label(self.master, text="Choose download folder:")
        self.output_label.pack(pady=10)

        self.output_path_var = tk.StringVar()
        self.output_path_var.set(os.path.expanduser("~"))
        self.output_entry = tk.Entry(self.master, textvariable=self.output_path_var, width=50)
        self.output_entry.pack(pady=10)

        self.browse_button = tk.Button(self.master, text="Browse", command=self.browse_folder)
        self.browse_button.pack(pady=10)

        self.progress_label = tk.Label(self.master, text="")
        self.progress_label.pack(pady=10)

        self.download_button = tk.Button(self.master, text="Download", command=self.start_download)
        self.download_button.pack(pady=10)

        self.quit_button = tk.Button(self.master, text="Exit", command=self.master.destroy)
        self.quit_button.pack(pady=10)

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        self.output_path_var.set(folder_selected)

    def paste_url(self):
        url_from_clipboard = self.master.clipboard_get()
        self.url_entry.delete(0, tk.END)
        self.url_entry.insert(0, url_from_clipboard)

    def download(self, video_url, output_path, quality):
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

        if not url or not output_path:
            self.show_message("Please enter a valid URL and output path.")
            return

        self.progress_label.config(text="Downloading...")

        if 'list=' in url:
            Thread(target=self.download_playlist, args=(url, output_path, quality, 2)).start()
        else:
            Thread(target=self.download, args=(url, output_path, quality)).start()

    def show_message(self, message):
        self.progress_label.config(text=message)

if __name__ == "__main__":
    root = tk.Tk()
    app = YoutubeDownloaderUI(root)
    root.mainloop()
