#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Program Upload Otomatis ke GitHub dengan Tema Hacker - VERSION 3.1
Mendukung GitHub Token Authentication & Deployment Fix - UPDATED
"""

import os
import sys
import subprocess
import time
import json
import getpass
import requests
from datetime import datetime
import re
import base64
from urllib.parse import urlparse

# Fungsi untuk membersihkan layar terminal
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# Kelas untuk animasi loading dengan tema hacker
class HackerLoading:
    def __init__(self, total=100, width=50):
        self.total = total
        self.width = width
        self.progress = 0
        self.chars = ["█", "▓", "▒", "░", "▄", "▀", "■", "□", "◼", "◻"]
        self.hacker_colors = ["\033[92m", "\033[96m", "\033[94m", "\033[95m"]
    
    def update(self, progress, message=""):
        self.progress = progress
        percent = self.progress / self.total
        bar_width = int(self.width * percent)
        bar = self.hacker_colors[1] + "█" * bar_width + "\033[0m"
        empty = self.hacker_colors[3] + "░" * (self.width - bar_width) + "\033[0m"
        
        percent_str = f"{self.progress}%"
        if self.progress < 30:
            percent_color = "\033[91m"
        elif self.progress < 70:
            percent_color = "\033[93m"
        else:
            percent_color = "\033[92m"
            
        hacker_text = ""
        if message:
            hacker_text = self.hacker_colors[0] + "[" + self.hacker_colors[2] + ">>>" + self.hacker_colors[0] + "] " + message + "\033[0m"
        
        sys.stdout.write(f"\r[{bar}{empty}] {percent_color}{percent_str:>4}\033[0m {hacker_text}")
        sys.stdout.flush()
    
    def complete(self, message=""):
        self.update(self.total, message)
        print()

# Fungsi untuk tampilan header bertema hacker
def display_hacker_header():
    clear_screen()
    
    hacker_art = """
    \033[92m╔══════════════════════════════════════════════════════════════════════╗
    ║   ██████╗ ██╗  ██╗ ██████╗ ██╗  ██╗███████╗██████╗   ██████╗ ██╗   ██╗██████╗  ║
    ║  ██╔════╝ ██║  ██║██╔════╝ ██║  ██║██╔════╝██╔══██╗██╔═══██╗██║   ██║██╔══██╗ ║
    ║  ███████╗ ███████║██║  ███╗███████║█████╗  ██████╔╝██║   ██║██║   ██║██████╔╝ ║
    ║  ╚════██║ ██╔══██║██║   ██║██╔══██║██╔══╝  ██╔══██╗██║   ██║██║   ██║██╔═══╝  ║
    ║  ███████║ ██║  ██║╚██████╔╝██║  ██║███████╗██║  ██║╚██████╔╝╚██████╔╝██║      ║
    ║  ╚══════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝  ╚═════╝ ╚═╝      ║
    ║                                                                                ║
    ║            [ GITHUB UPLOADER v3.1 - DEPLOYMENT FIXED ]                        ║
    ║            [ SECURE UPLOAD WITH PERSONAL ACCESS TOKEN ]                       ║
    ╚══════════════════════════════════════════════════════════════════════╝\033[0m
    """
    
    print(hacker_art)
    print("\033[96m" + "=" * 78 + "\033[0m")
    print("\033[93m[!] PERINGATAN: GitHub tidak lagi menerima password untuk Git operations")
    print("[!] Gunakan Personal Access Token (PAT) sebagai pengganti password")
    print("[!] Dapatkan token di: https://github.com/settings/tokens")
    print("[!] Berikan token permissions: repo, workflow, write:packages\033[0m")
    print("\033[96m" + "=" * 78 + "\033[0m\n")

# Fungsi untuk efek mengetik
def typewriter_effect(text, delay=0.02):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

# Fungsi untuk validasi folder
def validate_folder(path):
    if not os.path.exists(path):
        return False, f"Folder tidak ditemukan: {path}"
    
    if not os.path.isdir(path):
        return False, f"Path bukan folder: {path}"
    
    git_path = os.path.join(path, '.git')
    if os.path.exists(git_path):
        return True, "Folder sudah merupakan repository Git"
    
    return True, "Folder valid"

# Fungsi untuk menampilkan menu
def display_menu():
    print("\n\033[94m" + "═" * 78 + "\033[0m")
    print("\033[95m[ GITHUB UPLOAD MENU ]\033[0m")
    print("\033[94m" + "═" * 78 + "\033[0m")
    print("\033[96m1. Upload proyek baru ke GitHub")
    print("2. Update proyek yang sudah ada")
    print("3. Buat repository baru di GitHub")
    print("4. Lihat status repository lokal")
    print("5. Konfigurasi Git credentials")
    print("6. Setup GitHub Pages (Static Site)")
    print("7. Cek status deployment")
    print("8. Keluar dari program\033[0m")
    print("\033[94m" + "═" * 78 + "\033[0m")
    
    while True:
        try:
            choice = input("\033[93m[?] Pilih opsi (1-8): \033[0m").strip()
            if choice in ["1", "2", "3", "4", "5", "6", "7", "8"]:
                return int(choice)
            else:
                print("\033[91m[!] Pilihan tidak valid. Silakan pilih 1-8.\033[0m")
        except KeyboardInterrupt:
            print("\n\033[91m[!] Operasi dibatalkan.\033[0m")
            sys.exit(0)

# Fungsi untuk mendapatkan kredensial GitHub (dengan token)
def get_github_credentials():
    print("\n\033[95m[ GITHUB AUTHENTICATION ]\033[0m")
    print("\033[96m" + "─" * 60 + "\033[0m")
    
    username = input("\033[93m[?] Masukkan username GitHub: \033[0m").strip()
    
    print("\n\033[93m[!] GitHub mengharuskan penggunaan Personal Access Token (PAT)")
    print("[!] Jika belum memiliki token, buat di: https://github.com/settings/tokens")
    print("[!] Token harus memiliki permission: 'repo' (full control of private repositories)\033[0m")
    
    token = getpass.getpass("\033[93m[?] Masukkan GitHub Personal Access Token: \033[0m").strip()
    
    if not username or not token:
        print("\033[91m[!] Username dan token tidak boleh kosong.\033[0m")
        return None, None
    
    # Validasi token dengan API call
    if not validate_github_token(username, token):
        return None, None
    
    return username, token

# Fungsi untuk validasi token GitHub
def validate_github_token(username, token):
    print("\n\033[93m[!] Memvalidasi token...\033[0m")
    
    url = "https://api.github.com/user"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            user_data = response.json()
            if user_data.get('login') == username:
                print(f"\033[92m[+] Token valid untuk user: {username}\033[0m")
                
                # Cek scope token
                if 'X-OAuth-Scopes' in response.headers:
                    scopes = response.headers['X-OAuth-Scopes']
                    print(f"\033[92m[+] Token scopes: {scopes}\033[0m")
                    if 'repo' not in scopes:
                        print("\033[91m[!] PERINGATAN: Token tidak memiliki scope 'repo'!\033[0m")
                        print("\033[91m[!] Upload mungkin gagal. Buat token baru dengan scope repo.\033[0m")
                
                return True
            else:
                print(f"\033[91m[!] Token tidak sesuai dengan username {username}\033[0m")
                return False
        elif response.status_code == 401:
            print("\033[91m[!] Token tidak valid atau kadaluarsa.\033[0m")
            return False
        else:
            print(f"\033[91m[!] Gagal validasi token. Status code: {response.status_code}\033[0m")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"\033[91m[!] Gagal terhubung ke GitHub API: {e}\033[0m")
        return False

# Fungsi untuk membuat repository baru di GitHub menggunakan API
def create_github_repository(username, token, repo_name, is_private=False, description=""):
    print(f"\n\033[93m[!] Membuat repository '{repo_name}' di GitHub...\033[0m")
    
    url = "https://api.github.com/user/repos"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    if not description:
        description = f"Repository created by GitHub Uploader on {datetime.now().strftime('%Y-%m-%d')}"
    
    data = {
        "name": repo_name,
        "description": description,
        "private": is_private,
        "auto_init": True,  # Initialize with README.md
        "gitignore_template": "Python",
        "license_template": "mit"
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 201:
            print(f"\033[92m[+] Repository '{repo_name}' berhasil dibuat di GitHub!\033[0m")
            repo_data = response.json()
            repo_url = repo_data.get("html_url")
            clone_url = repo_data.get("clone_url")
            print(f"\033[92m[+] URL Repository: {repo_url}\033[0m")
            print(f"\033[92m[+] Clone URL: {clone_url}\033[0m")
            return repo_url, clone_url
        elif response.status_code == 401:
            print("\033[91m[!] Token tidak valid atau tidak memiliki permission yang cukup.\033[0m")
            return None, None
        elif response.status_code == 422:
            print(f"\033[93m[!] Repository '{repo_name}' sudah ada di akun Anda.\033[0m")
            repo_url = f"https://github.com/{username}/{repo_name}"
            clone_url = f"https://github.com/{username}/{repo_name}.git"
            return repo_url, clone_url
        else:
            print(f"\033[91m[!] Gagal membuat repository. Status code: {response.status_code}\033[0m")
            print(f"\033[91m[!] Response: {response.text}\033[0m")
            return None, None
            
    except requests.exceptions.RequestException as e:
        print(f"\033[91m[!] Gagal terhubung ke GitHub API: {e}\033[0m")
        return None, None

# Fungsi untuk setup GitHub Pages
def setup_github_pages(username, token, repo_name):
    print(f"\n\033[95m[ SETUP GITHUB PAGES ]\033[0m")
    
    url = f"https://api.github.com/repos/{username}/{repo_name}/pages"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    data = {
        "source": {
            "branch": "main",
            "path": "/"
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        if response.status_code in [201, 204]:
            print(f"\033[92m[+] GitHub Pages berhasil diaktifkan!\033[0m")
            pages_url = f"https://{username}.github.io/{repo_name}"
            print(f"\033[92m[+] URL Pages: {pages_url}\033[0m")
            return pages_url
        elif response.status_code == 409:
            print("\033[93m[!] GitHub Pages mungkin sudah aktif atau repository kosong.\033[0m")
            # Coba cek status
            return check_pages_status(username, token, repo_name)
        else:
            print(f"\033[91m[!] Gagal setup GitHub Pages: {response.status_code}\033[0m")
            print(f"\033[91m[!] Response: {response.text}\033[0m")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"\033[91m[!] Gagal terhubung ke GitHub API: {e}\033[0m")
        return None

# Fungsi untuk cek status GitHub Pages
def check_pages_status(username, token, repo_name):
    url = f"https://api.github.com/repos/{username}/{repo_name}/pages"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            pages_data = response.json()
            status = pages_data.get('status', 'unknown')
            pages_url = pages_data.get('html_url', f"https://{username}.github.io/{repo_name}")
            
            print(f"\033[92m[+] GitHub Pages Status: {status}\033[0m")
            print(f"\033[92m[+] URL Pages: {pages_url}\033[0m")
            
            if status == 'built':
                print("\033[92m[+] Deployment BERHASIL! Site sudah live.\033[0m")
            elif status == 'building':
                print("\033[93m[!] Deployment sedang dalam proses...\033[0m")
            else:
                print(f"\033[93m[!] Status deployment: {status}\033[0m")
            
            return pages_url
        else:
            print(f"\033[91m[!] GitHub Pages belum diaktifkan untuk repository ini.\033[0m")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"\033[91m[!] Gagal cek status Pages: {e}\033[0m")
        return None

# Fungsi untuk animasi hacker terminal
def hacker_terminal_effect(stage="upload"):
    loading = HackerLoading()
    
    print("\033[92m")
    
    if stage == "upload":
        messages = [
            "Mengkoneksikan ke GitHub API...",
            "Memvalidasi Personal Access Token...",
            "Menganalisis struktur file...",
            "Mempersiapkan upload batch...",
            "Mengunggah ke GitHub...",
            "Memverifikasi upload...",
            "Mengkonfigurasi deployment..."
        ]
    elif stage == "create":
        messages = [
            "Mengkoneksikan ke GitHub API...",
            "Memvalidasi token...",
            "Membuat repository baru...",
            "Menginisialisasi dengan README...",
            "Mengatur repository settings...",
            "Menyelesaikan setup..."
        ]
    elif stage == "pages":
        messages = [
            "Mengkoneksikan ke GitHub API...",
            "Mengaktifkan GitHub Pages...",
            "Mengkonfigurasi build settings...",
            "Memulai deployment...",
            "Menunggu build selesai...",
            "Memverifikasi deployment..."
        ]
    
    for i, message in enumerate(messages):
        progress = int((i + 1) * 100 / len(messages))
        loading.update(progress, message)
        time.sleep(0.5)
    
    loading.complete("Operasi selesai!")
    print("\033[0m")

# Fungsi untuk konfigurasi Git credentials secara permanen
def configure_git_credentials():
    print("\n\033[95m[ KONFIGURASI GIT CREDENTIALS ]\033[0m")
    
    username = input("\033[93m[?] Masukkan username GitHub: \033[0m").strip()
    email = input("\033[93m[?] Masukkan email GitHub: \033[0m").strip()
    
    try:
        # Konfigurasi global Git
        subprocess.run(["git", "config", "--global", "user.name", username], check=True)
        subprocess.run(["git", "config", "--global", "user.email", email], check=True)
        
        print("\033[92m[+] Git username dan email berhasil dikonfigurasi.\033[0m")
        
        # Set default branch ke main
        subprocess.run(["git", "config", "--global", "init.defaultBranch", "main"], check=True)
        print("\033[92m[+] Default branch diatur ke 'main'.\033[0m")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"\033[91m[!] Gagal mengkonfigurasi Git: {e}\033[0m")
        return False

# Fungsi untuk inisialisasi Git
def init_git_repository(folder_path):
    try:
        if os.path.exists(os.path.join(folder_path, '.git')):
            print("\033[93m[!] Repository Git sudah ada di folder ini.\033[0m")
            return True
        
        subprocess.run(["git", "init"], cwd=folder_path, check=True, capture_output=True)
        
        # Set branch ke main
        subprocess.run(["git", "branch", "-M", "main"], cwd=folder_path, check=True, capture_output=True)
        
        print("\033[92m[+] Repository Git berhasil diinisialisasi dengan branch 'main'.\033[0m")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\033[91m[!] Gagal menginisialisasi Git: {e}\033[0m")
        return False

# Fungsi untuk membuat file .gitignore jika belum ada
def create_gitignore(folder_path):
    gitignore_path = os.path.join(folder_path, '.gitignore')
    
    if os.path.exists(gitignore_path):
        print("\033[93m[!] File .gitignore sudah ada.\033[0m")
        return True
    
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.env
.venv
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# PyInstaller
*.manifest
*.spec

# Unit test / coverage reports
htmlcov/
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/

# Jupyter Notebook
.ipynb_checkpoints

# pyenv
.python-version

# celery beat schedule
celerybeat-schedule

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# macOS
.DS_Store
.AppleDouble
.LSOverride
Icon
._*

# Windows
Thumbs.db
ehthumbs.db
Desktop.ini
$RECYCLE.BIN/

# Project specific
*.log
*.bak
*.tmp
"""
    
    try:
        with open(gitignore_path, 'w') as f:
            f.write(gitignore_content)
        print("\033[92m[+] File .gitignore berhasil dibuat.\033[0m")
        return True
    except Exception as e:
        print(f"\033[91m[!] Gagal membuat .gitignore: {e}\033[0m")
        return False

# Fungsi untuk membuat README.md jika belum ada
def create_readme(folder_path, repo_name, description=""):
    readme_path = os.path.join(folder_path, 'README.md')
    
    if os.path.exists(readme_path):
        print("\033[93m[!] File README.md sudah ada.\033[0m")
        return True
    
    if not description:
        description = f"Repository {repo_name} created with GitHub Uploader"
    
    readme_content = f"""# {repo_name}

{description}

## Deskripsi
Repository ini dibuat menggunakan GitHub Uploader v3.0 dengan token authentication.

## Struktur Proyek
```
.
├── README.md
├── .gitignore
└── ...
```

## Cara Menggunakan
1. Clone repository ini
2. Jalankan program sesuai kebutuhan
3. Lakukan perubahan dan update

## Lisensi
MIT License

## Kontak
- GitHub: [@YOUR_USERNAME](https://github.com/YOUR_USERNAME)
- Dibuat: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    try:
        with open(readme_path, 'w') as f:
            f.write(readme_content)
        print("\033[92m[+] File README.md berhasil dibuat.\033[0m")
        return True
    except Exception as e:
        print(f"\033[91m[!] Gagal membuat README.md: {e}\033[0m")
        return False

# Fungsi untuk menambahkan file ke staging
def add_files_to_git(folder_path):
    try:
        # Buat .gitignore jika belum ada
        create_gitignore(folder_path)
        
        # Add all files
        result = subprocess.run(["git", "add", "."], cwd=folder_path, 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("\033[92m[+] Semua file berhasil ditambahkan ke staging area.\033[0m")
            
            # Cek file yang diadd
            status = subprocess.run(["git", "status", "--short"], cwd=folder_path,
                                  capture_output=True, text=True)
            if status.stdout:
                print("\033[96m[+] File yang akan di-commit:\033[0m")
                for line in status.stdout.split('\n'):
                    if line.strip():
                        print(f"  \033[92m{line}\033[0m")
            
            return True
        else:
            print(f"\033[91m[!] Gagal menambahkan file: {result.stderr}\033[0m")
            return False
    except subprocess.CalledProcessError as e:
        print(f"\033[91m[!] Gagal menambahkan file ke Git: {e}\033[0m")
        return False

# Fungsi untuk membuat commit
def create_commit(folder_path, message="Initial commit"):
    try:
        # Cek apakah ada perubahan untuk di-commit
        result = subprocess.run(["git", "status", "--porcelain"], cwd=folder_path, 
                              capture_output=True, text=True)
        
        if not result.stdout.strip():
            print("\033[93m[!] Tidak ada perubahan untuk di-commit.\033[0m")
            return True
        
        # Commit dengan message
        subprocess.run(["git", "commit", "-m", message], cwd=folder_path, 
                     check=True, capture_output=True)
        print(f"\033[92m[+] Commit berhasil dibuat: '{message}'\033[0m")
        return True
    except subprocess.CalledProcessError as e:
        # Cek apakah karena perlu konfigurasi user
        if "user.email" in str(e.stderr) or "user.name" in str(e.stderr):
            print("\033[91m[!] Git user belum dikonfigurasi.\033[0m")
            # Set user sementara
            email = input("\033[93m[?] Masukkan email untuk commit ini: \033[0m").strip()
            name = input("\033[93m[?] Masukkan nama untuk commit ini: \033[0m").strip()
            
            subprocess.run(["git", "config", "user.email", email], cwd=folder_path, check=True)
            subprocess.run(["git", "config", "user.name", name], cwd=folder_path, check=True)
            
            # Coba commit lagi
            subprocess.run(["git", "commit", "-m", message], cwd=folder_path, 
                         check=True, capture_output=True)
            print(f"\033[92m[+] Commit berhasil dibuat: '{message}'\033[0m")
            return True
        else:
            print(f"\033[91m[!] Gagal membuat commit: {e}\033[0m")
            print(f"\033[91m[!] Error detail: {e.stderr}\033[0m")
            return False

# Fungsi untuk menambahkan remote repository
def add_remote(folder_path, repo_url):
    try:
        # Cek remote yang sudah ada
        result = subprocess.run(["git", "remote", "-v"], cwd=folder_path, 
                              capture_output=True, text=True)
        
        if "origin" in result.stdout:
            # Update existing remote
            subprocess.run(["git", "remote", "set-url", "origin", repo_url], 
                         cwd=folder_path, check=True)
            print("\033[93m[!] Remote origin sudah diperbarui.\033[0m")
        else:
            # Add new remote
            subprocess.run(["git", "remote", "add", "origin", repo_url], 
                         cwd=folder_path, check=True)
            print("\033[92m[+] Remote origin berhasil ditambahkan.\033[0m")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"\033[91m[!] Gagal menambahkan remote: {e}\033[0m")
        return False

# ============== FUNGSI PUSH YANG SUDAH DIPERBAIKI ==============
def push_to_github(folder_path, token, username=None, branch="main"):
    """
    Push ke GitHub dengan autentikasi token
    
    Args:
        folder_path: Path folder repository
        token: GitHub Personal Access Token
        username: GitHub username (opsional, akan diekstrak dari URL jika tidak diberikan)
        branch: Branch tujuan (default: main)
    """
    try:
        print(f"\033[93m[!] Mengupload ke branch '{branch}'...\033[0m")
        
        # Dapatkan URL remote saat ini
        remote_result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=folder_path,
            capture_output=True,
            text=True
        )
        
        if remote_result.returncode != 0:
            print("\033[91m[!] Tidak dapat mengambil URL remote.\033[0m")
            return False
        
        remote_url = remote_result.stdout.strip()
        
        # Ekstrak username dari remote URL jika tidak diberikan
        if username is None:
            # Coba ekstrak username dari remote URL
            if 'github.com/' in remote_url:
                # Format: https://github.com/username/repo.git atau git@github.com:username/repo.git
                if remote_url.startswith('https://'):
                    path_part = remote_url.replace('https://github.com/', '')
                elif remote_url.startswith('git@'):
                    path_part = remote_url.replace('git@github.com:', '')
                else:
                    path_part = remote_url
                
                # Ambil username (bagian pertama sebelum '/')
                username = path_part.split('/')[0]
                print(f"\033[93m[!] Menggunakan username dari URL: {username}\033[0m")
            else:
                # Minta username dari user
                username = input("\033[93m[?] Masukkan username GitHub untuk push: \033[0m").strip()
                if not username:
                    print("\033[91m[!] Username diperlukan untuk autentikasi.\033[0m")
                    return False
        
        # Buat URL dengan token untuk autentikasi
        if remote_url.startswith('https://'):
            # Hapus https:// dari URL
            base_url = remote_url.replace('https://', '')
            
            # Format: github.com/username/repo.git
            if 'github.com/' in base_url:
                # Ambil bagian setelah github.com/
                repo_path = base_url.split('github.com/')[-1]
                
                # Buat URL dengan token
                auth_url = f"https://{username}:{token}@github.com/{repo_path}"
                print(f"\033[92m[+] Menggunakan autentikasi token untuk user: {username}\033[0m")
            else:
                print("\033[91m[!] Format URL remote tidak dikenal.\033[0m")
                return False
        else:
            # URL bukan HTTPS (mungkin SSH)
            print("\033[93m[!] Remote menggunakan SSH. Menggunakan autentikasi default.\033[0m")
            auth_url = remote_url
        
        # Simpan URL asli untuk dikembalikan nanti
        original_url = remote_url
        
        # Set remote sementara dengan token
        subprocess.run(
            ["git", "remote", "set-url", "origin", auth_url],
            cwd=folder_path,
            check=True,
            capture_output=True
        )
        
        # Lakukan push
        result = subprocess.run(
            ["git", "push", "-u", "origin", branch, "--force"],
            cwd=folder_path,
            capture_output=True,
            text=True
        )
        
        # Kembalikan remote URL ke semula (tanpa token)
        subprocess.run(
            ["git", "remote", "set-url", "origin", original_url],
            cwd=folder_path,
            check=True,
            capture_output=True
        )
        
        if result.returncode == 0:
            print("\033[92m[+] Push ke GitHub berhasil!\033[0m")
            
            # Tampilkan URL repository (tanpa token)
            clean_url = re.sub(r'https://[^@]*@', 'https://', auth_url)
            print(f"\033[92m[+] Repository URL: {clean_url}\033[0m")
            
            return True
        else:
            print(f"\033[91m[!] Gagal push ke GitHub:\033[0m")
            print(f"\033[91m{result.stderr}\033[0m")
            
            # Handle specific errors
            if "remote: Repository not found" in result.stderr:
                print("\033[91m[!] Repository tidak ditemukan di GitHub.\033[0m")
                print("\033[93m[!] Pastikan repository sudah dibuat dan Anda memiliki akses.\033[0m")
            elif "403" in result.stderr:
                print("\033[91m[!] Akses ditolak. Token mungkin tidak memiliki permission yang cukup.\033[0m")
            elif "Authentication failed" in result.stderr:
                print("\033[91m[!] Autentikasi gagal. Token mungkin tidak valid.\033[0m")
            
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"\033[91m[!] Gagal push ke GitHub: {e}\033[0m")
        
        # Pastikan remote URL dikembalikan
        try:
            subprocess.run(
                ["git", "remote", "set-url", "origin", original_url],
                cwd=folder_path,
                capture_output=True
            )
        except:
            pass
            
        return False

# Fungsi untuk upload proyek baru
def upload_new_project(folder_path, username, token):
    print(f"\n\033[95m[ UPLOAD PROYEK BARU ]\033[0m")
    print(f"\033[96mFolder: {os.path.basename(folder_path)}\033[0m")
    
    # Validasi folder
    is_valid, message = validate_folder(folder_path)
    if not is_valid:
        print(f"\033[91m[!] {message}\033[0m")
        return False
    
    # Minta nama repository
    default_name = os.path.basename(folder_path).lower().replace(' ', '-')
    repo_name = input(f"\033[93m[?] Nama repository GitHub (default: '{default_name}'): \033[0m").strip()
    if not repo_name:
        repo_name = default_name
    
    # Bersihkan nama repository (hanya huruf kecil, angka, -, _)
    repo_name = re.sub(r'[^a-z0-9_.-]', '-', repo_name.lower())
    
    # Tanya apakah repository private
    is_private = input("\033[93m[?] Buat repository private? (y/n): \033[0m").strip().lower() == 'y'
    
    # Minta deskripsi
    description = input("\033[93m[?] Deskripsi repository (opsional): \033[0m").strip()
    
    # Tanya apakah setup GitHub Pages
    setup_pages = input("\033[93m[?] Setup GitHub Pages? (y/n): \033[0m").strip().lower() == 'y'
    
    # Buat repository di GitHub
    hacker_terminal_effect("create")
    repo_url, clone_url = create_github_repository(username, token, repo_name, is_private, description)
    
    if not repo_url:
        print("\033[91m[!] Gagal membuat repository. Upload dibatalkan.\033[0m")
        return False
    
    # Inisialisasi Git lokal
    if not init_git_repository(folder_path):
        return False
    
    # Buat README jika belum ada
    create_readme(folder_path, repo_name, description)
    
    # Tambahkan file
    if not add_files_to_git(folder_path):
        return False
    
    # Minta pesan commit
    commit_msg = input("\033[93m[?] Pesan commit (default: 'Initial commit'): \033[0m").strip()
    if not commit_msg:
        commit_msg = "Initial commit"
    
    # Buat commit
    if not create_commit(folder_path, commit_msg):
        return False
    
    # Tambahkan remote
    if not add_remote(folder_path, clone_url):
        return False
    
    # Tampilkan animasi upload
    hacker_terminal_effect("upload")
    
    # Push ke GitHub (dengan username)
    if not push_to_github(folder_path, token, username):
        return False
    
    # Setup GitHub Pages jika diminta
    pages_url = None
    if setup_pages:
        print("\n\033[93m[!] Setup GitHub Pages...\033[0m")
        hacker_terminal_effect("pages")
        pages_url = setup_github_pages(username, token, repo_name)
    
    # Tampilkan sukses
    print("\n\033[92m" + "═" * 78 + "\033[0m")
    print("\033[92m[ UPLOAD BERHASIL! ]\033[0m")
    print(f"\033[96mRepository: {repo_url}")
    print(f"Clone URL: {clone_url}")
    print(f"Folder: {folder_path}")
    print(f"Branch: main")
    print(f"Waktu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\033[0m")
    
    if pages_url:
        print(f"\033[92mGitHub Pages: {pages_url}\033[0m")
    
    print("\033[92m" + "═" * 78 + "\033[0m")
    
    return True

# Fungsi untuk update proyek yang sudah ada
def update_existing_project(folder_path, username, token):
    print(f"\n\033[95m[ UPDATE PROYEK ]\033[0m")
    
    # Validasi folder
    is_valid, message = validate_folder(folder_path)
    if not is_valid:
        print(f"\033[91m[!] {message}\033[0m")
        return False
    
    # Cek apakah ini repository Git
    if not os.path.exists(os.path.join(folder_path, '.git')):
        print("\033[91m[!] Folder ini bukan repository Git.\033[0m")
        return False
    
    # Pull dulu untuk update
    try:
        print("\033[93m[!] Mengambil update terbaru dari remote...\033[0m")
        subprocess.run(["git", "pull", "origin", "main"], cwd=folder_path, 
                     capture_output=True, text=True)
    except:
        pass
    
    # Tambahkan file
    if not add_files_to_git(folder_path):
        return False
    
    # Minta pesan commit
    commit_msg = input("\033[93m[?] Pesan commit: \033[0m").strip()
    if not commit_msg:
        commit_msg = f"Update {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    # Buat commit
    if not create_commit(folder_path, commit_msg):
        return False
    
    # Tampilkan animasi
    hacker_terminal_effect("upload")
    
    # Push ke GitHub (dengan username)
    if not push_to_github(folder_path, token, username):
        return False
    
    print("\n\033[92m[+] Update proyek berhasil!\033[0m")
    return True

# Fungsi untuk melihat status repository
def view_repository_status(folder_path):
    print(f"\n\033[95m[ STATUS REPOSITORY ]\033[0m")
    
    try:
        # Cek apakah folder Git
        if not os.path.exists(os.path.join(folder_path, '.git')):
            print("\033[91m[!] Bukan repository Git.\033[0m")
            return
        
        # Git status
        print("\033[93m[ GIT STATUS ]\033[0m")
        result = subprocess.run(["git", "status"], cwd=folder_path,
                              capture_output=True, text=True)
        print("\033[96m" + result.stdout + "\033[0m")
        
        # Git branch
        result = subprocess.run(["git", "branch", "-a"], cwd=folder_path,
                              capture_output=True, text=True)
        if result.stdout:
            print("\033[93m[ BRANCHES ]\033[0m")
            print("\033[96m" + result.stdout + "\033[0m")
        
        # Log commit terakhir
        result = subprocess.run(["git", "log", "--oneline", "-5"], cwd=folder_path,
                              capture_output=True, text=True)
        if result.stdout:
            print("\033[93m[ 5 COMMIT TERAKHIR ]\033[0m")
            print("\033[96m" + result.stdout + "\033[0m")
        
        # Remote info
        result = subprocess.run(["git", "remote", "-v"], cwd=folder_path,
                              capture_output=True, text=True)
        if result.stdout:
            print("\033[93m[ REMOTE INFO ]\033[0m")
            for line in result.stdout.split('\n'):
                if line.strip():
                    # Sembunyikan token jika ada
                    line = re.sub(r'https://[^@]*@', 'https://', line)
                    print("\033[96m" + line + "\033[0m")
        
        # Cek GitHub Pages
        try:
            remote_url = subprocess.run(["git", "remote", "get-url", "origin"],
                                      cwd=folder_path, capture_output=True, text=True).stdout.strip()
            match = re.search(r'github\.com[/:]([^/]+)/([^/.]+)', remote_url)
            if match:
                repo_owner, repo_name = match.groups()
                check_pages_status(repo_owner, None, repo_name)
        except:
            pass
            
    except subprocess.CalledProcessError as e:
        print(f"\033[91m[!] Gagal mendapatkan status: {e}\033[0m")

# Fungsi untuk membuat repository baru saja (tanpa upload)
def create_repository_only(username, token):
    print("\n\033[95m[ BUAT REPOSITORY BARU ]\033[0m")
    
    repo_name = input("\033[93m[?] Nama repository: \033[0m").strip()
    if not repo_name:
        print("\033[91m[!] Nama repository tidak boleh kosong.\033[0m")
        return False
    
    repo_name = re.sub(r'[^a-z0-9_.-]', '-', repo_name.lower())
    
    is_private = input("\033[93m[?] Repository private? (y/n): \033[0m").strip().lower() == 'y'
    description = input("\033[93m[?] Deskripsi repository (opsional): \033[0m").strip()
    
    hacker_terminal_effect("create")
    repo_url, clone_url = create_github_repository(username, token, repo_name, is_private, description)
    
    if repo_url:
        print(f"\n\033[92m[+] Repository berhasil dibuat!")
        print(f"\033[92m[+] URL: {repo_url}")
        print(f"\033[92m[+] Clone: {clone_url}\033[0m")
        
        # Tanya apakah mau clone
        clone_now = input("\n\033[93m[?] Clone repository sekarang? (y/n): \033[0m").strip().lower()
        if clone_now == 'y':
            target_dir = input("\033[93m[?] Target folder (default: ./{repo_name}): \033[0m").strip()
            if not target_dir:
                target_dir = f"./{repo_name}"
            
            try:
                subprocess.run(["git", "clone", clone_url, target_dir], check=True)
                print(f"\033[92m[+] Repository berhasil di-clone ke: {target_dir}\033[0m")
            except subprocess.CalledProcessError as e:
                print(f"\033[91m[!] Gagal clone: {e}\033[0m")
        
        return True
    else:
        return False

# Fungsi untuk setup GitHub Pages
def setup_pages_only(username, token):
    print("\n\033[95m[ SETUP GITHUB PAGES ]\033[0m")
    
    repo_name = input("\033[93m[?] Nama repository: \033[0m").strip()
    if not repo_name:
        print("\033[91m[!] Nama repository tidak boleh kosong.\033[0m")
        return False
    
    hacker_terminal_effect("pages")
    pages_url = setup_github_pages(username, token, repo_name)
    
    if pages_url:
        print(f"\n\033[92m[+] GitHub Pages berhasil diaktifkan!")
        print(f"\033[92m[+] URL: {pages_url}\033[0m")
        return True
    else:
        return False

# Fungsi untuk cek status deployment
def check_deployment_status(username, token):
    print("\n\033[95m[ CEK STATUS DEPLOYMENT ]\033[0m")
    
    repo_name = input("\033[93m[?] Nama repository: \033[0m").strip()
    if not repo_name:
        print("\033[91m[!] Nama repository tidak boleh kosong.\033[0m")
        return False
    
    # Cek GitHub Pages
    pages_url = check_pages_status(username, token, repo_name)
    
    # Cek deployment status via API
    url = f"https://api.github.com/repos/{username}/{repo_name}/deployments"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            deployments = response.json()
            if deployments:
                print("\n\033[93m[ DEPLOYMENT HISTORY ]\033[0m")
                for dep in deployments[:5]:
                    print(f"\033[96m- {dep.get('created_at')}: {dep.get('environment')} - {dep.get('state')}\033[0m")
            else:
                print("\033[93m[!] Belum ada deployment history.\033[0m")
                
    except Exception as e:
        print(f"\033[91m[!] Gagal cek deployment: {e}\033[0m")
    
    return True

# Fungsi utama
def main():
    # Tampilkan header
    display_hacker_header()
    
    # Pesan selamat datang
    welcome_msg = "\033[92m[+] GitHub Uploader v3.1 - Deployment Fixed"
    typewriter_effect(welcome_msg, 0.01)
    
    # Minta input folder
    folder_path = input("\033[93m[?] Masukkan path folder proyek (enter untuk folder saat ini): \033[0m").strip()
    
    if not folder_path:
        folder_path = os.getcwd()
        print(f"\033[93m[!] Menggunakan folder saat ini: {folder_path}\033[0m")
        use_current_folder = True
    elif os.path.exists(folder_path):
        print(f"\033[92m[+] Folder ditemukan: {folder_path}\033[0m")
        use_current_folder = True
    else:
        print("\033[91m[!] Folder tidak ditemukan.\033[0m")
        use_current_folder = False
    
    # Dapatkan kredensial GitHub
    username, token = get_github_credentials()
    if not username or not token:
        print("\033[91m[!] Autentikasi gagal.\033[0m")
        sys.exit(1)
    
    print(f"\033[92m[+] Autentikasi berhasil sebagai: {username}\033[0m")
    
    # Loop menu utama
    while True:
        choice = display_menu()
        
        if choice == 1:
            # Upload proyek baru
            if use_current_folder:
                upload_new_project(folder_path, username, token)
            else:
                print("\033[91m[!] Folder tidak valid.\033[0m")
        
        elif choice == 2:
            # Update proyek yang sudah ada
            if use_current_folder:
                update_existing_project(folder_path, username, token)
            else:
                print("\033[91m[!] Folder tidak valid.\033[0m")
        
        elif choice == 3:
            # Buat repository baru
            create_repository_only(username, token)
        
        elif choice == 4:
            # Lihat status repository
            if use_current_folder:
                view_repository_status(folder_path)
            else:
                print("\033[91m[!] Folder tidak valid.\033[0m")
        
        elif choice == 5:
            # Konfigurasi Git
            configure_git_credentials()
        
        elif choice == 6:
            # Setup GitHub Pages
            setup_pages_only(username, token)
        
        elif choice == 7:
            # Cek status deployment
            check_deployment_status(username, token)
        
        elif choice == 8:
            # Keluar
            print("\n\033[92m[+] Program selesai. Terima kasih!\033[0m")
            break
        
        # Tanya apakah ingin melanjutkan
        if choice != 8:
            continue_choice = input("\n\033[93m[?] Lanjutkan? (y/n): \033[0m").strip().lower()
            if continue_choice != 'y':
                print("\n\033[92m[+] Program selesai.\033[0m")
                break

# Eksekusi program
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n\033[91m[!] Program dihentikan.\033[0m")
        sys.exit(0)
    except Exception as e:
        print(f"\n\033[91m[!] Error: {e}\033[0m")
        import traceback
        traceback.print_exc()
        sys.exit(1)
