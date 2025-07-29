import customtkinter as ctk
import yt_dlp
import tkinter.filedialog as fd
import tkinter.messagebox as mb
import threading
import os
import time
from pathlib import Path


class YouTubeDownloaderGUI:
    def __init__(self):
        # Initialize the main window
        self.root = ctk.CTk()
        self.root.title("YouTube Downloader")
        self.root.geometry("600x650")
        self.root.resizable(False, False)
        self.root.iconbitmap('assets\\yt_icon.ico')

        # Set appearance mode and color theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Initialize variables
        self.download_folder = str(Path.home() / "Downloads")
        self.is_downloading = False

        # Create GUI elements
        self.create_widgets()

    def create_widgets(self):
        # Main title
        title_label = ctk.CTkLabel(self.root, text="YouTube Video Downloader",font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=20)

        # URL input frame
        url_frame = ctk.CTkFrame(self.root)
        url_frame.pack(pady=10, padx=20, fill="x")

        url_label = ctk.CTkLabel(url_frame, text="Video URL:")
        url_label.pack(pady=(10, 5))

        self.url_entry = ctk.CTkEntry(url_frame, placeholder_text="Enter YouTube URL here...", width=500, height=35)
        self.url_entry.pack(pady=(0, 10), padx=20)

        # Download folder selection frame
        folder_frame = ctk.CTkFrame(self.root)
        folder_frame.pack(pady=10, padx=20, fill="x")

        folder_label = ctk.CTkLabel(folder_frame, text="Download Folder:")
        folder_label.pack(pady=(10, 5))

        folder_selection_frame = ctk.CTkFrame(folder_frame)
        folder_selection_frame.pack(pady=(0, 10), padx=20, fill="x")

        self.folder_label = ctk.CTkLabel(folder_selection_frame, text=self.download_folder, wraplength=400)
        self.folder_label.pack(side="left", padx=10, pady=10)

        self.browse_button = ctk.CTkButton(folder_selection_frame, text="Browse", command=self.browse_folder, width=80)
        self.browse_button.pack(side="right", padx=10, pady=10)

        # Quality selection frame
        quality_frame = ctk.CTkFrame(self.root)
        quality_frame.pack(pady=10, padx=20, fill="x")

        quality_label = ctk.CTkLabel(quality_frame, text="Video Quality:")
        quality_label.pack(pady=(10, 5))

        self.quality_var = ctk.StringVar(value="--SELECT--")
        quality_menu = ctk.CTkOptionMenu(quality_frame, values=["--SELECT--", "1080p", "720p", "480p", "360p", "Audio Only"],variable=self.quality_var)
        quality_menu.pack(pady=(0, 10))

        # Progress frame
        progress_frame = ctk.CTkFrame(self.root)
        progress_frame.pack(pady=10, padx=20, fill="x")

        progress_label = ctk.CTkLabel(progress_frame, text="Download Progress:")
        progress_label.pack(pady=(10, 5))

        self.progress_bar = ctk.CTkProgressBar(progress_frame, width=500)
        self.progress_bar.pack(pady=5, padx=20)
        self.progress_bar.set(0)

        # Progress info frame
        info_frame = ctk.CTkFrame(progress_frame)
        info_frame.pack(pady=5, padx=20, fill="x")

        self.percentage_label = ctk.CTkLabel(info_frame, text="0%")
        self.percentage_label.pack(side="left", padx=10)

        self.speed_label = ctk.CTkLabel(info_frame, text="Speed: 0 KB/s")
        self.speed_label.pack(side="left", padx=10)

        self.eta_label = ctk.CTkLabel(info_frame, text="ETA: --:--")
        self.eta_label.pack(side="right", padx=10)

        progress_frame.pack_configure(pady=(10, 0))

        # Download button
        self.download_button = ctk.CTkButton(self.root, text="Download", command=self.start_download, width=200, height=40, font=ctk.CTkFont(size=16, weight="bold"))
        self.download_button.pack(pady=20)

        # Status label
        self.status_label = ctk.CTkLabel(
            self.root,
            text="READY",
            font=ctk.CTkFont(size=12), text_color="green"
        )
        self.status_label.pack(pady=5)

    def browse_folder(self):
        """Open folder selection dialog"""
        folder = fd.askdirectory(initialdir=self.download_folder)
        if folder:
            self.download_folder = folder
            self.folder_label.configure(text=folder)

    def get_format_selector(self):
        """Get format selector based on quality selection"""
        quality = self.quality_var.get()
        if quality == "Audio Only":
            return 'bestaudio/best'
        elif quality == "--SELECT--":
            return mb.showwarning("Warning", "Video quality not selected")
        elif quality == "1080p":
            return 'bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/best[height<=1080]'
        elif quality == "720p":
            return 'bestvideo[ext=mp4][height<=720]+bestaudio[ext=m4a]/best[height<=720]'
        elif quality == "480p":
            return 'bestvideo[ext=mp4][height<=480]+bestaudio[ext=m4a]/best[height<=480]'
        elif quality == "360p":
            return 'bestvideo[ext=mp4][height<=360]+bestaudio[ext=m4a]/best[height<=360]'
        else:
            return 'bestvideo+bestaudio/best'

    def progress_hook(self, d):
        """Progress hook for yt-dlp to update GUI"""
        if d['status'] == 'downloading':
            # Calculate percentage
            if 'total_bytes' in d:
                percentage = (d['downloaded_bytes'] / d['total_bytes']) * 100
            elif 'total_bytes_estimate' in d:
                percentage = (d['downloaded_bytes'] / d['total_bytes_estimate']) * 100
            else:
                percentage = 0

            # Update progress bar and percentage label
            self.root.after(0, lambda: self.progress_bar.set(percentage / 100))
            self.root.after(0, lambda: self.percentage_label.configure(text=f"{percentage:.1f}%"))

            # Update speed
            speed = d.get('speed', 0)
            if speed:
                if speed > 1024 * 1024:  # MB/s
                    speed_text = f"Speed: {speed / (1024 * 1024):.1f} MB/s"
                elif speed > 1024:  # KB/s
                    speed_text = f"Speed: {speed / 1024:.1f} KB/s"
                else:  # B/s
                    speed_text = f"Speed: {speed:.0f} B/s"
            else:
                speed_text = "Speed: -- KB/s"

            self.root.after(0, lambda: self.speed_label.configure(text=speed_text))

            # Update ETA
            eta = d.get('eta', 0)
            if eta:
                eta_minutes = eta // 60
                eta_seconds = eta % 60
                eta_text = f"ETA: {eta_minutes:02d}:{eta_seconds:02d}"
            else:
                eta_text = "ETA: --:--"

            self.root.after(0, lambda: self.eta_label.configure(text=eta_text))

        elif d['status'] == 'finished':
            self.root.after(0, lambda: self.progress_bar.set(1.0))
            self.root.after(0, lambda: self.percentage_label.configure(text="100%"))
            self.root.after(0, lambda: self.status_label.configure(text="COMPLETED", text_color="green"))
            self.root.after(0, lambda: self.download_button.configure(text="Download", state="normal"))
            self.is_downloading = False

    def download_video(self, url):
        """Download video using yt-dlp"""
        try:
            # Configure yt-dlp options
            ydl_opts = {
                'format': self.get_format_selector(),
                'outtmpl': os.path.join(self.download_folder, '%(title)s.%(ext)s'),
                'noplaylist': True,
                'progress_hooks': [self.progress_hook],
            }

            # If audio only, add audio format options
            if self.quality_var.get() == "Audio Only":
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]

            # Download the video
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

        except Exception as e:
            # Handle errors
            self.root.after(0, lambda: mb.showerror("Error", f"Download failed: {str(e)}"))
            self.root.after(0, lambda: self.status_label.configure(text="FAILED", text_color="red"))
            self.root.after(0, lambda: self.download_button.configure(text="Download", state="normal"))
            self.is_downloading = False

    def start_download(self):
        quality_1 = self.quality_var.get()
        if quality_1 == "--SELECT--":
            return None
        """Start download in a separate thread"""
        if self.is_downloading:
            return

        url = self.url_entry.get().strip()
        if not url:
            mb.showerror("Error", "Please enter a valid URL")
            return

        # Reset progress indicators
        self.progress_bar.set(0)
        self.percentage_label.configure(text="0%")
        self.speed_label.configure(text="Speed: 0 KB/s")
        self.eta_label.configure(text="ETA: --:--")
        self.status_label.configure(text="Starting download...")

        # Disable download button during download
        self.download_button.configure(text="Downloading...", state="disabled")
        self.is_downloading = True

        # Start download in separate thread to prevent GUI freezing
        download_thread = threading.Thread(target=self.download_video, args=(url,))
        download_thread.daemon = True
        download_thread.start()

    def run(self):
        """Start the GUI application"""
        self.root.mainloop()


# Create and run the application
if __name__ == "__main__":
    app = YouTubeDownloaderGUI()
    app.run()