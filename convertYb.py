from pytube import Playlist, YouTube

def download_youtube_video(url, output_path):
    try:
        if 'list=' in url:
            playlist = Playlist(url)
            for video_url in playlist.video_urls:
                yt = YouTube(video_url)
                video_stream = yt.streams.get_highest_resolution()
                video_stream.download(output_path)
                print(f"Video downloaded: {yt.title}")
        else:
            yt = YouTube(url)
            video_stream = yt.streams.get_highest_resolution()
            video_stream.download(output_path)
            print("Video downloaded successfully!")
    except Exception as e:
        print(f"An error occurred while downloading the video: {str(e)}")

if __name__ == "__main__":
    while True :
        url = input("Please enter the YouTube video URL or playlist URL (or 'exit' to quit): ")
        if url.lower() == 'exit':
            print("Exiting the program.")
            break
        else:
            output_path = 'D:\\Movies\\افلام'  # Set the path where you want to save the videos

            download_youtube_video(url, output_path)
