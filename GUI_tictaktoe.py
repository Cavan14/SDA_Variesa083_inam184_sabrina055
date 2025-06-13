import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import copy
import threading
import time
import pygame
import os

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

MENANG = 10
KALAH = -10
SERI = 0

class LogikaPermainan: 
    def __init__(self, level='sulit'): ## Konstruktor untuk inisialisasi AI dengan level kesulitan
        self.level = level # Menyimpan level AI ('mudah' = kedalaman 2, 'sulit' = kedalaman 4

    def cek_menang(self, papan, pemain): # Mengecek apakah pemain tertentu menang di papan
        for i in range(3): # Iterasi baris dan kolom
            if all([sel == pemain for sel in papan[i]]):  # Cek kemenangan horizontal
                return True
            if all([papan[j][i] == pemain for j in range(3)]): # Cek kemenangan vertikal
                return True
        if all([papan[i][i] == pemain for i in range(3)]) or \
           all([papan[i][2 - i] == pemain for i in range(3)]):    # Cek diagonal utama
            return True
        return False  # Tidak ada kemenangan ditemukan

    def papan_penuh(self, papan): # Mengecek apakah papan penuh (tidak ada '-' yang tersisa)
        return all(sel != '-' for baris in papan for sel in baris) 

    def hitung_skor(self, papan): # Menghitung skor dari kondisi papan
        if self.cek_menang(papan, 'O'): # Jika AI ('O') menang, skor positif
            return MENANG
        elif self.cek_menang(papan, 'X'): # Jika pemain ('X') menang, skor negatif
            return KALAH
        else:
            return 0   # Jika seri atau belum selesai

    def semua_langkah(self, papan, pemain): # Menghasilkan semua langkah legal berikutnya untuk pemain
        langkah = []      # Menyimpan semua kemungkinan papan setelah satu langkah
        for i in range(3):
            for j in range(3):
                if papan[i][j] == '-': # Jika sel kosong, lakukan simulasi langkah
                    temp = copy.deepcopy(papan) # Salin papan secara mendalam
                    temp[i][j] = pemain # Tempel langkah pemain
                    langkah.append(temp)  # Simpan ke daftar langkah
        return langkah

    def minimax(self, papan, kedalaman, is_max, level=0): # Fungsi utama Minimax (rekursif) dengan pencetakan ke terminal
        indentasi = '│   ' * level # Buat indentasi visual berdasarkan level dalam tree
        skor = self.hitung_skor(papan) # Hitung skor saat ini untuk evaluasi

        if kedalaman == 0 or abs(skor) == MENANG or self.papan_penuh(papan): # Basis rekursi: mencapai kedalaman maksimal, menang/kalah, atau papan penuh
            print(f"{indentasi}├─ Level {level} {'MAX' if is_max else 'MIN'} (Leaf): Skor = {skor}")  # Cetak kondisi terminal
            self.cetak_papan_terminal(papan, indentasi) # Cetak papan ke terminal
            return skor, papan # Kembalikan skor dan papan final

        if is_max:  # Giliran AI (MAXimizer)
            nilai_maks = -float('inf') # Inisialisasi nilai maksimum
            langkah_terbaik = None
            print(f"{indentasi}├─ Level {level} MAX mencari...") # Info pencarian di terminal
            for langkah in self.semua_langkah(papan, 'O'):  # Semua kemungkinan langkah AI
                evaluasi, _ = self.minimax(langkah, kedalaman - 1, False, level + 1) # Rekursi untuk lawan
                if evaluasi > nilai_maks: 
                    nilai_maks = evaluasi # Simpan nilai maksimum
                    langkah_terbaik = langkah # Simpan langkah terbaik
            return nilai_maks, langkah_terbaik
        else:                                  # Giliran pemain (MINimizer)
            nilai_min = float('inf')       # Inisialisasi nilai minimum
            langkah_terbaik = None
            print(f"{indentasi}├─ Level {level} MIN mencari...") # Info pencarian di terminal
            for langkah in self.semua_langkah(papan, 'X'):  # Semua kemungkinan langkah pemain
                evaluasi, _ = self.minimax(langkah, kedalaman - 1, True, level + 1) # Rekursi untuk AI
                if evaluasi < nilai_min:
                    nilai_min = evaluasi  # Simpan nilai minimum
                    langkah_terbaik = langkah  # Simpan langkah terbai
            return nilai_min, langkah_terbaik

    def cetak_papan_terminal(self, papan, indent=''): # Mencetak papan ke terminal dengan indentasi
        for baris in papan:
            print(f"{indent}    {' '.join(baris)}") # Format: tampilkan isi baris dengan spasi antar sel

    def dapatkan_langkah_terbaik(self, papan, callback_status=None): # Interface utama yang dipanggil dari GUI
        if callback_status:
            callback_status("Komputer sedang berpikir...") # Panggil fungsi GUI untuk status spinner/loading
        print("Komputer sedang menghitung langkah terbaik...") # Cetak status ke terminal
        kedalaman = 2 if self.level == 'mudah' else 4 # Tentukan kedalaman rekursi berdasarkan level AI
        _, langkah = self.minimax(papan, kedalaman, True, 0) # Jalankan algoritma Minimax dari root
        print("Komputer selesai menghitung.") # Cetak notifikasi terminal
        if callback_status:
            callback_status("Komputer selesai.")  # Update status GUI setelah berpikir selesai
        return langkah # Kembalikan langkah papan terbaik untuk dipakai

class HalamanRetro:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic Tac Toe Retro")
        self.root.geometry("800x600")
        self.level_ai = tk.StringVar(value="sulit")

        self.canvas = tk.Canvas(self.root, bg="#0d0d0d", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.frame_layar = ctk.CTkFrame(self.root, fg_color="#111111", corner_radius=20, border_color="green", border_width=3,
                                        width=600, height=400)
        self.frame_layar.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        self.label_judul = ctk.CTkLabel(self.frame_layar, text="TIC TAC TOE", font=("Press Start 2P", 26), text_color="hot pink")
        self.label_judul.pack(pady=20)

        self.option_level = ctk.CTkOptionMenu(self.frame_layar, values=["mudah", "sulit"], variable=self.level_ai)
        self.option_level.pack(pady=10)

        self.btn_start = ctk.CTkButton(self.frame_layar, text="START", fg_color="green", hover_color="#66ff66",
                                       font=("Press Start 2P", 14), width=160, command=self.mulai_permainan)
        self.btn_start.pack(pady=10)

        self.btn_menu = ctk.CTkButton(self.frame_layar, text="TENTANG", fg_color="#3366ff", hover_color="#6699ff",
                                      font=("Press Start 2P", 14), width=160, command=self.tampilkan_pesan_menu)
        self.btn_menu.pack(pady=10)

        self.canvas.create_text(100, 30, text="REMAIN 1", fill="white", font=("Courier", 10))
        self.canvas.create_text(700, 30, text="REMAIN 2", fill="white", font=("Courier", 10))
        self.canvas.create_text(400, 30, text="SKOR TERTINGGI: 25000", fill="white", font=("Courier", 10))
        self.canvas.create_text(400, 580, text="S1-Sains Data - Universitas Negeri Surabaya", fill="white", font=("Courier", 9))

        self.load_karakter()
        self.putar_musik()

    def load_karakter(self):
        try:
            gambar = Image.open("karakter_pixel.png")
            gambar = gambar.resize((60, 60), Image.NEAREST)
            self.karakter_img = ImageTk.PhotoImage(gambar)
            self.canvas.create_image(70, 530, image=self.karakter_img, anchor=tk.NW)
        except:
            print("Gagal memuat gambar karakter pixel.")

    def putar_musik(self):
        try:
            pygame.mixer.init()
            pygame.mixer.music.load("videoplayback.mp3")
            pygame.mixer.music.play(-1)
        except:
            print("Musik gagal dimuat.")

    def tampilkan_pesan_menu(self):
        messagebox.showinfo("Tentang", "Aplikasi Tic Tac Toe retro ini dibuat untuk tugas akhir SDA.")

    def mulai_permainan(self):
        self.canvas.destroy()
        self.frame_layar.destroy()
        PermainanGUI(self.root, self.level_ai.get())

class PermainanGUI:
    def __init__(self, root, level_ai):
        self.root = root
        self.papan = [['-' for _ in range(3)] for _ in range(3)]
        self.giliran = 'X'
        self.skor = {'Menang': 0, 'Kalah': 0, 'Seri': 0}
        self.logika = LogikaPermainan(level=level_ai)

        self.frame = ctk.CTkFrame(root)
        self.frame.pack(pady=20)

        self.label_info = ctk.CTkLabel(self.frame, text="Giliran: X", font=("Arial", 20))
        self.label_info.grid(row=0, column=0, columnspan=3, pady=10)

        self.tombol = [[None for _ in range(3)] for _ in range(3)]
        for i in range(3):
            for j in range(3):
                btn = ctk.CTkButton(self.frame, text="", width=100, height=100, font=("Arial", 24),
                                    command=lambda x=i, y=j: self.langkah_pemain(x, y))
                btn.grid(row=i+1, column=j, padx=5, pady=5)
                self.tombol[i][j] = btn

        self.label_status = ctk.CTkLabel(self.frame, text="", font=("Arial", 14))
        self.label_status.grid(row=4, column=0, columnspan=3, pady=10)

        self.btn_kembali = ctk.CTkButton(self.frame, text="Kembali ke Menu", command=self.kembali_ke_menu)
        self.btn_kembali.grid(row=5, column=0, columnspan=3, pady=10)

    def langkah_pemain(self, i, j):
        if self.papan[i][j] == '-':
            self.papan[i][j] = 'X'
            self.tombol[i][j].configure(text='X', state='disabled')
            if self.logika.cek_menang(self.papan, 'X'):
                self.skor['Menang'] += 1
                self.akhiri_permainan("Kamu Menang!")
            elif self.logika.papan_penuh(self.papan):
                self.skor['Seri'] += 1
                self.akhiri_permainan("Seri!")
            else:
                self.giliran = 'O'
                self.label_info.configure(text="Giliran: O")
                threading.Thread(target=self.langkah_komputer).start()

    def langkah_komputer(self):
        langkah = self.logika.dapatkan_langkah_terbaik(self.papan, self.ubah_status)
        self.papan = langkah
        self.perbarui_tampilan()
        if self.logika.cek_menang(self.papan, 'O'):
            self.skor['Kalah'] += 1
            self.akhiri_permainan("Komputer Menang!")
        elif self.logika.papan_penuh(self.papan):
            self.skor['Seri'] += 1
            self.akhiri_permainan("Seri!")
        else:
            self.giliran = 'X'
            self.label_info.configure(text="Giliran: X")

    def perbarui_tampilan(self):
        for i in range(3):
            for j in range(3):
                self.tombol[i][j].configure(text=self.papan[i][j])
                if self.papan[i][j] != '-':
                    self.tombol[i][j].configure(state='disabled')

    def ubah_status(self, teks):
        self.label_status.configure(text=teks)

    def akhiri_permainan(self, pesan):
        self.label_info.configure(text=pesan)
        for i in range(3):
            for j in range(3):
                self.tombol[i][j].configure(state='disabled')

    def kembali_ke_menu(self):
        self.frame.destroy()
        HalamanRetro(self.root)

if __name__ == "__main__":
    root = ctk.CTk()
    HalamanRetro(root)
    root.mainloop()

# import customtkinter as ctk
# import tkinter as tk
# from tkinter import messagebox
# from PIL import Image, ImageTk
# import copy
# import threading
# import time
# import pygame

# ctk.set_appearance_mode("dark")
# ctk.set_default_color_theme("green")

# # Konstanta skor
# MENANG = 10
# KALAH = -10
# SERi = 0

# class LogikaPermainan:
#     def __init__(self, level='sulit'):
#         self.level = level

#     def cek_menang(self, papan, pemain):
#         for i in range(3):
#             if all([sel == pemain for sel in papan[i]]):
#                 return True
#             if all([papan[j][i] == pemain for j in range(3)]):
#                 return True
#         if all([papan[i][i] == pemain for i in range(3)]) or \
#            all([papan[i][2 - i] == pemain for i in range(3)]):
#             return True
#         return False

#     def papan_penuh(self, papan):
#         return all(sel != '-' for baris in papan for sel in baris)

#     def hitung_skor(self, papan):
#         if self.cek_menang(papan, 'O'):
#             return MENANG
#         elif self.cek_menang(papan, 'X'):
#             return KALAH
#         else:
#             return 0

#     def semua_langkah(self, papan, pemain):
#         langkah = []
#         for i in range(3):
#             for j in range(3):
#                 if papan[i][j] == '-':
#                     temp = copy.deepcopy(papan)
#                     temp[i][j] = pemain
#                     langkah.append(temp)
#         return langkah

#     def minimax(self, papan, kedalaman, is_max, level=0):
#         indentasi = '│   ' * level
#         skor = self.hitung_skor(papan)

#         if kedalaman == 0 or abs(skor) == MENANG or self.papan_penuh(papan):
#             print(f"{indentasi}├─ Level {level} {'MAX' if is_max else 'MIN'} (Leaf): Skor = {skor}")
#             self.cetak_papan_terminal(papan, indentasi)
#             return skor, papan

#         if is_max:
#             nilai_maks = -float('inf')
#             langkah_terbaik = None
#             print(f"{indentasi}├─ Level {level} MAX mencari...")
#             for langkah in self.semua_langkah(papan, 'O'):
#                 evaluasi, _ = self.minimax(langkah, kedalaman - 1, False, level + 1)
#                 if evaluasi > nilai_maks:
#                     nilai_maks = evaluasi
#                     langkah_terbaik = langkah
#             return nilai_maks, langkah_terbaik
#         else:
#             nilai_min = float('inf')
#             langkah_terbaik = None
#             print(f"{indentasi}├─ Level {level} MIN mencari...")
#             for langkah in self.semua_langkah(papan, 'X'):
#                 evaluasi, _ = self.minimax(langkah, kedalaman - 1, True, level + 1)
#                 if evaluasi < nilai_min:
#                     nilai_min = evaluasi
#                     langkah_terbaik = langkah
#             return nilai_min, langkah_terbaik

#     def cetak_papan_terminal(self, papan, indent=''):
#         for baris in papan:
#             print(f"{indent}    {' '.join(baris)}")

#     def dapatkan_langkah_terbaik(self, papan, callback_status=None):
#         if callback_status:
#             callback_status("Komputer sedang berpikir...")
#         print("Komputer sedang menghitung langkah terbaik...")
#         kedalaman = 2 if self.level == 'mudah' else 4
#         _, langkah = self.minimax(papan, kedalaman, True, 0)
#         print("Komputer selesai menghitung.")
#         if callback_status:
#             callback_status("Komputer selesai.")
#         return langkah

# class HalamanRetro:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("Tic Tac Toe Retro")
#         self.root.geometry("800x600")

#         self.canvas = tk.Canvas(self.root, bg="#0d0d0d", highlightthickness=0)
#         self.canvas.pack(fill=tk.BOTH, expand=True)

#         # Background kotak neon
#         self.frame_layar = ctk.CTkFrame(self.root, fg_color="#111111", corner_radius=20, border_color="green", border_width=3)
#         self.frame_layar.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=600, height=400)

#         # Judul game
#         self.label_judul = ctk.CTkLabel(self.frame_layar, text="TIC TAC TOE", font=("Press Start 2P", 26), text_color="hot pink")
#         self.label_judul.pack(pady=40)

#         # Tombol retro
#         self.btn_start = ctk.CTkButton(self.frame_layar, text="START", fg_color="green", hover_color="#66ff66", font=("Press Start 2P", 14), width=160)
#         self.btn_start.pack(pady=10)

#         self.btn_menu = ctk.CTkButton(self.frame_layar, text="MENU", fg_color="#3366ff", hover_color="#6699ff", font=("Press Start 2P", 14), width=160)
#         self.btn_menu.pack(pady=10)

#         self.btn_signin = ctk.CTkButton(self.frame_layar, text="SIGN IN", fg_color="deeppink", hover_color="#ff99cc", font=("Press Start 2P", 14), width=160)
#         self.btn_signin.pack(pady=10)

#         # Label atas skor dan nyawa
#         self.canvas.create_text(100, 30, text="REMAIN 1", fill="white", font=("Courier", 10))
#         self.canvas.create_text(700, 30, text="REMAIN 2", fill="white", font=("Courier", 10))
#         self.canvas.create_text(400, 30, text="SKOR TERTINGGI: 25000", fill="white", font=("Courier", 10))

#         # Footer
#         self.canvas.create_text(400, 580, text="S1-Sains Data - Universitas Negeri Surabaya", fill="white", font=("Courier", 9))

#         # Tambahan dekor karakter
#         self.load_karakter()

#     def load_karakter(self):
#         try:
#             gambar = Image.open("karakter_pixel.png")  # ganti nama file sesuai file kamu
#             gambar = gambar.resize((60, 60), Image.NEAREST)
#             self.karakter_img = ImageTk.PhotoImage(gambar)
#             self.canvas.create_image(70, 530, image=self.karakter_img, anchor=tk.NW)
#         except:
#             print("Gagal memuat gambar karakter pixel.")

# if __name__ == "__main__":
#     root = ctk.CTk()
#     app = HalamanRetro(root)
#     root.mainloop()


# class TicTacToeGUI:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("Tic Tac Toe")
#         self.ukuran_window = "600x700"
#         self.root.geometry(self.ukuran_window)

#         # Inisialisasi skor
#         self.skor_menang = 0
#         self.skor_seri = 0
#         self.skor_kalah = 0

#         # Musik background
#         pygame.init()
#         pygame.mixer.init()
#         try:
#             pygame.mixer.music.load("videoplayback.mp3")
#             pygame.mixer.music.play(-1)
#         except:
#             print("Gagal memuat musik background.")

#         # Load gambar background halaman awal
#         self.bg_awal_img_orig = Image.open("poto brina.png")
#         self.bg_main_img_orig = Image.open("poto variesa.png")

#         self.mode_pilihan = None  # vs Teman atau vs Komputer
#         self.level_ai = "sulit"   # Default level

#         # Setup halaman awal
#         self.buat_halaman_awal()

#         # Bind resize window untuk resize gambar background
#         self.root.bind("<Configure>", self.resize_background)

#     def buat_halaman_awal(self):
#         self.frame_awal = ctk.CTkFrame(self.root)
#         self.frame_awal.pack(fill=tk.BOTH, expand=True)

#         self.canvas_awal = tk.Canvas(self.frame_awal, highlightthickness=0)
#         self.canvas_awal.pack(fill=tk.BOTH, expand=True)

#         # Pasang gambar bg awal (sementara, nanti diresize saat event configure)
#         self.bg_awal_img = ImageTk.PhotoImage(self.bg_awal_img_orig)
#         self.bg_awal_id = self.canvas_awal.create_image(0, 0, anchor=tk.NW, image=self.bg_awal_img)

#         # Tombol mulai main
#         self.btn_mulai = ctk.CTkButton(self.frame_awal, text="Mulai", command=self.ke_pilihan_mode)
#         self.btn_mulai.place(relx=0.5, rely=0.85, anchor=tk.CENTER)

#     def resize_background(self, event):
#         # Resize background halaman awal jika aktif
#         if hasattr(self, 'canvas_awal') and self.canvas_awal.winfo_exists():
#             w = self.canvas_awal.winfo_width()
#             h = self.canvas_awal.winfo_height()
#             if w > 0 and h > 0:
#                 resized_awal = self.bg_awal_img_orig.resize((w, h), Image.LANCZOS)
#                 self.bg_awal_img = ImageTk.PhotoImage(resized_awal)
#                 self.canvas_awal.itemconfig(self.bg_awal_id, image=self.bg_awal_img)

#         # Resize background halaman main game jika aktif
#         if hasattr(self, 'canvas_main') and self.canvas_main.winfo_exists():
#             w = self.canvas_main.winfo_width()
#             h = self.canvas_main.winfo_height()
#             if w > 0 and h > 0:
#                 resized_main = self.bg_main_img_orig.resize((w, h), Image.LANCZOS)
#                 self.bg_main_img = ImageTk.PhotoImage(resized_main)
#                 self.canvas_main.itemconfig(self.bg_main_id, image=self.bg_main_img)

#     def ke_pilihan_mode(self):
#         self.frame_awal.destroy()
#         self.buat_frame_pilihan_mode()

#     def buat_frame_pilihan_mode(self):
#         self.frame_mode = ctk.CTkFrame(self.root)
#         self.frame_mode.pack(fill=tk.BOTH, expand=True)

#         label = ctk.CTkLabel(self.frame_mode, text="Pilih Mode Permainan", font=("Arial", 20))
#         label.pack(pady=20)

#         btn_vs_teman = ctk.CTkButton(self.frame_mode, text="VS Teman", command=lambda: self.mulai_permainan('teman'))
#         btn_vs_teman.pack(pady=10)

#         btn_vs_komputer = ctk.CTkButton(self.frame_mode, text="VS Komputer", command=self.ke_pilihan_level)
#         btn_vs_komputer.pack(pady=10)

#         btn_kembali = ctk.CTkButton(self.frame_mode, text="Kembali", command=self.kembali_ke_awal)
#         btn_kembali.pack(pady=30)

#     def ke_pilihan_level(self):
#         self.frame_mode.destroy()
#         self.buat_frame_pilihan_level()

#     def buat_frame_pilihan_level(self):
#         self.frame_level = ctk.CTkFrame(self.root)
#         self.frame_level.pack(fill=tk.BOTH, expand=True)

#         label = ctk.CTkLabel(self.frame_level, text="Pilih Level AI", font=("Arial", 20))
#         label.pack(pady=20)

#         btn_mudah = ctk.CTkButton(self.frame_level, text="Mudah", command=lambda: self.mulai_permainan('komputer', 'mudah'))
#         btn_mudah.pack(pady=10)

#         btn_sulit = ctk.CTkButton(self.frame_level, text="Sulit", command=lambda: self.mulai_permainan('komputer', 'sulit'))
#         btn_sulit.pack(pady=10)

#         btn_kembali = ctk.CTkButton(self.frame_level, text="Kembali", command=self.ke_pilihan_mode)
#         btn_kembali.pack(pady=30)

#     def kembali_ke_awal(self):
#         if hasattr(self, 'frame_mode'):
#             self.frame_mode.destroy()
#         if hasattr(self, 'frame_level'):
#             self.frame_level.destroy()
#         self.buat_halaman_awal()

#     def mulai_permainan(self, mode, level=None):
#         self.mode_pilihan = mode
#         self.level_ai = level if level else 'sulit'

#         # Bersihkan frame yg ada
#         if hasattr(self, 'frame_mode'):
#             self.frame_mode.destroy()
#         if hasattr(self, 'frame_level'):
#             self.frame_level.destroy()
#         if hasattr(self, 'frame_awal'):
#             self.frame_awal.destroy()

#         # Setup frame permainan utama
#         self.frame_main = ctk.CTkFrame(self.root)
#         self.frame_main.pack(fill=tk.BOTH, expand=True)

#         # Canvas untuk background game
#         self.canvas_main = tk.Canvas(self.frame_main, highlightthickness=0)
#         self.canvas_main.pack(fill=tk.BOTH, expand=True)

#         # Pasang gambar background main game (sementara, nanti diresize saat configure)
#         self.bg_main_img = ImageTk.PhotoImage(self.bg_main_img_orig)
#         self.bg_main_id = self.canvas_main.create_image(0, 0, anchor=tk.NW, image=self.bg_main_img)

#         # Frame di atas canvas untuk tombol dan info
#         self.frame_controls = ctk.CTkFrame(self.frame_main)
#         self.frame_controls.place(relx=0.5, rely=0.05, anchor=tk.N)

#         # Label status giliran
#         self.label_status = ctk.CTkLabel(self.frame_controls, text="Giliran: X", font=("Arial", 16))
#         self.label_status.pack(padx=10, pady=5)

#         # Frame papan permainan tombol
#         self.frame_papan = ctk.CTkFrame(self.frame_main)
#         self.frame_papan.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

#         # Skor
#         self.frame_skor = ctk.CTkFrame(self.frame_main)
#         self.frame_skor.place(relx=0.5, rely=0.9, anchor=tk.CENTER)

#         self.label_skor = ctk.CTkLabel(self.frame_skor, text=self.ambil_teks_skor(), font=("Arial", 14))
#         self.label_skor.pack()

#         # Inisialisasi papan dan tombol
#         self.papan = [['-' for _ in range(3)] for _ in range(3)]
#         self.tombol = [[None for _ in range(3)] for _ in range(3)]
#         self.logika = LogikaPermainan(self.level_ai)
#         self.giliran_pemain = 'X'

#         for i in range(3):
#             for j in range(3):
#                 btn = ctk.CTkButton(self.frame_papan, text=' ', width=80, height=80,
#                                     font=("Arial", 24),
#                                     command=lambda i=i, j=j: self.ketika_diklik(i, j))
#                 btn.grid(row=i, column=j, padx=5, pady=5)
#                 self.tombol[i][j] = btn

#         # Jika mode vs komputer dan giliran pertama komputer (bisa disesuaikan)
#         if self.mode_pilihan == 'komputer' and self.giliran_pemain == 'O':
#             self.giliran_komputer()

#     def ambil_teks_skor(self):
#         return f"Menang: {self.skor_menang}  Seri: {self.skor_seri}  Kalah: {self.skor_kalah}"

#     def perbarui_skor(self, hasil):
#         if hasil == 'menang':
#             self.skor_menang += 1
#         elif hasil == 'seri':
#             self.skor_seri += 1
#         elif hasil == 'kalah':
#             self.skor_kalah += 1
#         self.label_skor.configure(text=self.ambil_teks_skor())

#     def ketika_diklik(self, i, j):
#         if self.papan[i][j] != '-' or (self.mode_pilihan == 'komputer' and self.giliran_pemain == 'O'):
#             return

#         self.papan[i][j] = self.giliran_pemain
#         self.tombol[i][j].configure(text=self.giliran_pemain)

#         if self.logika.cek_menang(self.papan, self.giliran_pemain):
#             hasil = 'menang' if self.giliran_pemain == 'X' else 'kalah'
#             self.perbarui_skor(hasil)
#             self.label_status.configure(text=f"Pemain {self.giliran_pemain} menang!")
#             self.nonaktifkan_tombol()
#             return
#         elif self.logika.papan_penuh(self.papan):
#             self.perbarui_skor('seri')
#             self.label_status.configure(text="Permainan seri!")
#             return

#         # Ganti giliran
#         self.giliran_pemain = 'O' if self.giliran_pemain == 'X' else 'X'
#         self.label_status.configure(text=f"Giliran: {self.giliran_pemain}")

#         if self.mode_pilihan == 'komputer' and self.giliran_pemain == 'O':
#             self.giliran_komputer()

#     def giliran_komputer(self):
#         self.mulai_loading()
#         threading.Thread(target=self.proses_giliran_komputer, daemon=True).start()

#     def proses_giliran_komputer(self):
#         langkah = self.logika.dapatkan_langkah_terbaik(self.papan, callback_status=self.perbarui_status)
#         self.hentikan_loading()

#         for i in range(3):
#             for j in range(3):
#                 if self.papan[i][j] != langkah[i][j]:
#                     self.papan[i][j] = 'O'
#                     self.tombol[i][j].configure(text='O')

#         if self.logika.cek_menang(self.papan, 'O'):
#             self.perbarui_skor('kalah')
#             self.label_status.configure(text="Komputer menang!")
#             self.nonaktifkan_tombol()
#         elif self.logika.papan_penuh(self.papan):
#             self.perbarui_skor('seri')
#             self.label_status.configure(text="Permainan seri!")
#         else:
#             self.giliran_pemain = 'X'
#             self.label_status.configure(text="Giliran: X")

#     def nonaktifkan_tombol(self):
#         for baris in self.tombol:
#             for tombol in baris:
#                 tombol.configure(state='disabled')

#     def perbarui_status(self, pesan):
#         self.label_status.configure(text=pesan)

#     def mulai_loading(self):
#         self.animasi_loading_jalan = True
#         threading.Thread(target=self.animasi_loading, daemon=True).start()

#     def hentikan_loading(self):
#         self.animasi_loading_jalan = False

#     def animasi_loading(self):
#         spinner = ["|", "/", "-", "\\"]
#         i = 0
#         while self.animasi_loading_jalan:
#             self.perbarui_status(f"Komputer sedang berpikir... {spinner[i % len(spinner)]}")
#             time.sleep(0.2)
#             i += 1

# if __name__ == "__main__":
#     root = ctk.CTk()
#     app = TicTacToeGUI(root)
#     root.mainloop()