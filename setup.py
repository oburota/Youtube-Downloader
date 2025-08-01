from cx_Freeze import setup, Executable

build_exe_options = {
    "packages": ["customtkinter", "tkinter", "yt_dlp"],
    "includes": ["customtkinter", "tkinter", "yt_dlp"]
}

setup(
    name="Youtube Downloader",
    version = "1.0",
    options={"build_exe": build_exe_options},
    executables=[Executable("yt_downloader_3.py", base="Win32GUI", icon="assets\\yt_icon.ico")]  # Use Win32GUI for GUI apps
)