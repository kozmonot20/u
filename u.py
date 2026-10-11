import tkinter as tk
import math
import random

# PUG Motoru Çözünürlük Ayarları
WIDTH = 500
HEIGHT = 500

class LocalPugWarEngine:
    def __init__(self, root):
        self.root = root
        self.root.title("PUG Savaş Motoru v2.0 // Gömülü Grafik Sistemi")
        
        # Ekranı oluştur (Gömülü grafik alanı)
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="#2298DB")
        self.canvas.pack()

        # Uçuş Eksenleri
        self.plane_x = 0.0          
        self.pitch = 0.0            
        
        # Silah ve Düşman Sistemleri
        self.lasers = []            # Atılan lazerler
        self.enemies = []           # Düşman drone'ları
        self.score = 0              # Skor
        self.health = 100           # Uçağın Canı
        self.laser_cooldown = 0     # Ateş hızı sınırı

        # Klavye Tuş Takibini Başlat
        self.pressed_keys = {}
        self.root.bind("<KeyPress>", self.key_down)
        self.root.bind("<KeyRelease>", self.key_up)

        # Oyun Döngüsünü Tetikle (Saniyede 60 Kare Simülasyonu)
        self.game_loop()

    def key_down(self, event):
        self.pressed_keys[event.keysym] = True

    def key_up(self, event):
        self.pressed_keys[event.keysym] = False

    def spawn_enemy(self):
        if len(self.enemies) < 3 and random.random() < 0.02:
            enemy_x = random.randint(50, WIDTH - 50)
            enemy_y = random.randint(50, int(HEIGHT / 2))
            self.enemies.append({'x': enemy_x, 'y': enemy_y, 'size': 5.0})

    def game_loop(self):
        if self.health > 0:
            self.handle_input()
            self.update_physics()
            self.render_world()
            # 16 milisaniye sonra sonraki kareyi hesapla (~60 FPS)
            self.root.after(16, self.game_loop)
        else:
            self.render_game_over()

    def handle_input(self):
        # Ok Tuşları ile Uçuş Eksenlerini Kontrol Et
        if self.pressed_keys.get("Up"):
            if self.pitch < 0.4: self.pitch += 0.015
        if self.pressed_keys.get("Down"):
            if self.pitch > -0.4: self.pitch -= 0.015
        if self.pressed_keys.get("Left"):
            self.plane_x -= 0.4
        if self.pressed_keys.get("Right"):
            self.plane_x += 0.4

        # BOŞLUK (SPACE) ile Lazer Ateşleme
        if self.laser_cooldown > 0:
            self.laser_cooldown -= 1
        elif self.pressed_keys.get("space") or self.pressed_keys.get("Space"):
            # Çift namlulu plazma lazerleri fırlatılıyor
            self.lasers.append({'x': int(WIDTH/2) - 20, 'y': HEIGHT - 120, 'size': 8.0})
            self.lasers.append({'x': int(WIDTH/2) + 20, 'y': HEIGHT - 120, 'size': 8.0})
            self.laser_cooldown = 8 # Ateş sıklığı sınırı

    def update_physics(self):
        self.spawn_enemy()

        # Düşman İHA Hareketleri ve Çarpışma Testi
        for enemy in self.enemies[:]:
            enemy['size'] += 0.35 # Bize yaklaştıkça büyüyor (3D)
            
            # Eğer drone uçağımıza çarptıysa (Çok büyüdüyse)
            if enemy['size'] > 45:
                self.health -= 20
                if enemy in self.enemies: self.enemies.remove(enemy)

        # Lazer Hareketleri ve Düşmanı Vurma Kontrolü
        for laser in self.lasers[:]:
            laser['y'] -= 15 # Lazerler ileri fırlıyor
            if laser['size'] > 2: laser['size'] -= 0.3
            
            if laser['y'] < 0:
                if laser in self.lasers: self.lasers.remove(laser)
                continue

            # Lazer düşmanı tam ortasından yakaladı mı?
            for enemy in self.enemies[:]:
                e_x = int(enemy['x'] - self.plane_x * 10)
                e_y = int(enemy['y'] + self.pitch * 50)
                
                distance = math.hypot(laser['x'] - e_x, laser['y'] - e_y)
                if distance < (enemy['size'] + 12):
                    self.score += 1
                    if enemy in self.enemies: self.enemies.remove(enemy)
                    if laser in self.lasers: self.lasers.remove(laser)
                    break

    def render_world(self):
        # Ekranı temizle
        self.canvas.delete("all")

        # 1. Gökyüzü ve Yeryüzü Ayrımı (Ufuk Çizgisi)
        horizon = int(HEIGHT / 2 + self.pitch * 120)
        self.canvas.create_rectangle(0, 0, WIDTH, horizon, fill="#3498DB", outline="")
        self.canvas.create_rectangle(0, horizon, WIDTH, HEIGHT, fill="#27AE60", outline="")

        # 2. Sanal Perspektif Pisti
        rwy_center = int(WIDTH / 2 - self.plane_x * 20)
        points = [
            rwy_center - 15, horizon,
            rwy_center + 15, horizon,
            int(WIDTH / 2 - self.plane_x * 5) + 160, HEIGHT - 120,
            int(WIDTH / 2 - self.plane_x * 5) - 160, HEIGHT - 120
        ]
        self.canvas.create_polygon(points, fill="#7F8C8D", outline="")

        # 3. Düşman Drone'larını Çiz
        for enemy in self.enemies:
            current_x = int(enemy['x'] - self.plane_x * 10)
            current_y = int(enemy['y'] + self.pitch * 50)
            sz = int(enemy['size'])
            
            # Ana Gövde
            self.canvas.create_oval(current_x - sz, current_y - sz, current_x + sz, current_y + sz, fill="#C0392B", outline="")
            # Pervane barları
            self.canvas.create_line(current_x - int(sz*1.5), current_y, current_x + int(sz*1.5), current_y, fill="black", width=2)

        # 4. Lazerleri Çiz
        for laser in self.lasers:
            sz = int(laser['size'])
            self.canvas.create_oval(laser['x'] - sz, int(laser['y']) - sz, laser['x'] + sz, int(laser['y']) + sz, fill="#FF0000", outline="")

        # 5. Alt Kokpit Paneli ve Savaş Nişangahı (HUD)
        self.canvas.create_rectangle(0, HEIGHT - 120, WIDTH, HEIGHT, fill="#2C3E50", outline="")
        
        # Crosshair (Nişangah)
        cx, cy = int(WIDTH/2), int(HEIGHT/2 - 50)
        self.canvas.create_iter = self.canvas.create_oval(cx - 15, cy - 15, cx + 15, cy + 15, outline="#2ECC71", width=2)
        self.canvas.create_line(cx - 25, cy, cx + 25, cy, fill="#2ECC71")
        self.canvas.create_line(cx, cy - 25, cx, cy + 25, fill="#2ECC71")

        # 6. Skor ve Can Arayüzü
        self.canvas.create_text(60, HEIGHT - 90, text=f"SKOR: {self.score}", fill="#FFFFFF", font=("Arial", 14, "bold"))
        health_color = "#2ECC71" if self.health > 40 else "#FF0000"
        self.canvas.create_text(60, HEIGHT - 50, text=f"CAN: {self.health}%", fill=health_color, font=("Arial", 14, "bold"))

    def render_game_over(self):
        self.canvas.delete("all")
        self.canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill="black", outline="")
        self.canvas.create_text(int(WIDTH/2), int(HEIGHT/2) - 20, text="UÇAK DÜŞTÜ - GAME OVER", fill="#FF0000", font=("Arial", 20, "bold"))
        self.canvas.create_text(int(WIDTH/2), int(HEIGHT/2) + 20, text=f"TOPLAM SKOR: {self.score}", fill="#FFFFFF", font=("Arial", 16, "bold"))

if __name__ == "__main__":
    root = tk.Tk()
    engine = LocalPugWarEngine(root)
    root.mainloop()
