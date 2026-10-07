import pygame
import sys
import time
import random
import math
import os

# Pygame başlatma
pygame.init()
pygame.font.init()
pygame.mixer.init()

# Tam Ekran Ayarları
info_object = pygame.display.Info()
WIDTH, HEIGHT = info_object.current_w, info_object.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("PROJE: UGGKF - Space Station Terminal OS")

# Renkler
BLACK = (5, 8, 12)
GREEN = (40, 255, 120)
DIM_GREEN = (20, 120, 60)
WHITE = (240, 250, 245)
CYAN = (0, 230, 255)
DARK_BLUE = (10, 20, 35)
GRAY = (50, 65, 80)
LIGHT_GRAY = (180, 190, 200)
ALERT_RED = (255, 60, 80)
YELLOW = (255, 220, 50)
ORANGE = (255, 140, 0)
PURPLE = (180, 70, 255)

# Yazı Tipleri
FONT_NAME = "Courier New"
font_large = pygame.font.SysFont(FONT_NAME, 32, bold=True)
font_medium = pygame.font.SysFont(FONT_NAME, 24, bold=True)
font_small = pygame.font.SysFont(FONT_NAME, 18)
font_tiny = pygame.font.SysFont(FONT_NAME, 14)

# Ses Efektleri (Synthesized beeps)
def create_beep_sound(frequency=800, duration=0.05):
    sample_rate = 22050
    n_samples = int(sample_rate * duration)
    buf = bytearray()
    for i in range(n_samples):
        t = float(i) / sample_rate
        val = int(127 + 127 * math.sin(2 * math.pi * frequency * t))
        buf.append(val)
    try:
        sound = pygame.mixer.Sound(buffer=bytes(buf))
        sound.set_volume(0.15)
        return sound
    except:
        return None

key_sound = create_beep_sound(frequency=900, duration=0.03)
enter_sound = create_beep_sound(frequency=400, duration=0.1)
laser_sound = create_beep_sound(frequency=1200, duration=0.08)

# Uzay çöpü fotoğraflarını yükle
DEBRIS_IMAGES = []
debris_dir = os.path.join(os.path.dirname(__file__), "uzaycopufotolari")
if os.path.exists(debris_dir):
    for f in os.listdir(debris_dir):
        if f.lower().endswith(('.jpeg', '.jpg', '.png')):
            img_path = os.path.join(debris_dir, f)
            try:
                img = pygame.image.load(img_path).convert_alpha()
                DEBRIS_IMAGES.append(img)
            except Exception as e:
                print(f"Fotoğraf yüklenemedi: {f}, hata: {e}")

# Retro CRT Efekti Çizimi
crt_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
for y in range(0, HEIGHT, 4):
    pygame.draw.line(crt_surface, (0, 0, 0, 45), (0, y), (WIDTH, y))

def draw_crt_overlay(surface):
    surface.blit(crt_surface, (0, 0))
    pygame.draw.rect(surface, (0, 0, 0, 80), (0, 0, WIDTH, HEIGHT), 20)

# Özel Retro Fare İmleci
def draw_custom_cursor(surface, pos):
    x, y = pos
    points = [(x, y), (x + 16, y + 12), (x + 10, y + 14), (x + 14, y + 22), (x + 10, y + 24), (x + 6, y + 16), (x, y + 18)]
    pygame.draw.polygon(surface, GREEN, points)
    pygame.draw.polygon(surface, BLACK, points, 2)
    pygame.draw.circle(surface, (40, 255, 120, 40), (x+4, y+4), 8)

# Daktilo Efektli Metin Girişi Sınıfı
class IntroIntroSequence:
    def __init__(self):
        self.texts = [
            "proje: uggkf",
            "uzaya giden geliştirilmiş kirlilik fikri",
            "çokta uzak olmayan bir gelecekte uzay istasyonunda çalışıyorsun...",
            "Laikler projesi."
        ]
        self.current_text_index = 0
        self.char_index = 0
        self.displayed_text = ""
        self.last_char_time = time.time()
        self.typing_speed = 0.05
        self.state = "TYPING"
        self.wait_start_time = 0
        self.hold_duration = 1.8

    def update(self):
        current_time = time.time()
        if self.state == "TYPING":
            if current_time - self.last_char_time >= self.typing_speed:
                target_text = self.texts[self.current_text_index]
                if self.char_index < len(target_text):
                    self.displayed_text += target_text[self.char_index]
                    self.char_index += 1
                    self.last_char_time = current_time
                    if key_sound:
                        key_sound.play()
                else:
                    self.state = "WAITING"
                    self.wait_start_time = current_time

        elif self.state == "WAITING":
            if current_time - self.wait_start_time >= self.hold_duration:
                self.state = "ERASING"
                self.last_char_time = current_time

        elif self.state == "ERASING":
            if current_time - self.last_char_time >= 0.02:
                if len(self.displayed_text) > 0:
                    self.displayed_text = self.displayed_text[:-1]
                    self.last_char_time = current_time
                else:
                    self.current_text_index += 1
                    if self.current_text_index >= len(self.texts):
                        self.state = "COMPLETED"
                    else:
                        self.char_index = 0
                        self.state = "TYPING"
                        if enter_sound:
                            enter_sound.play()

    def draw(self, surface):
        surface.fill(BLACK)
        prompt = "SYS_BOOT:\\> "
        prompt_surf = font_medium.render(prompt, True, DIM_GREEN)
        surface.blit(prompt_surf, (80, HEIGHT // 2 - 20))
        
        text_surf = font_medium.render(self.displayed_text, True, GREEN)
        surface.blit(text_surf, (80 + prompt_surf.get_width(), HEIGHT // 2 - 20))
        
        if int(time.time() * 2) % 2 == 0:
            cursor_x = 80 + prompt_surf.get_width() + text_surf.get_width() + 4
            pygame.draw.rect(surface, GREEN, (cursor_x, HEIGHT // 2 - 18, 12, 24))
            
        skip_surf = font_tiny.render("[ESC] Geç", True, GRAY)
        surface.blit(skip_surf, (WIDTH - 120, HEIGHT - 40))

# Ekonomi ve Personel Sistemi Sınıfı
class EconomySystem:
    def __init__(self):
        self.base_monthly_revenue = 454000  # $454,000 Aylık Gelir
        self.total_vault = 1250000          # Başlangıç Kasa Bütçesi
        self.current_month = 1
        self.debris_target_for_month = 17
        self.current_month_debris = 0
        
        # Personel Kadrosu ve Satın Alma (İşe Alım) Durumları
        self.personnel = [
            {"id": 0, "role": "Makine Mühendisi", "name": "Efe kocagöz", "profit_pct": 14, "comm_pct": 16, "salary": 28000, "hire_cost": 85000, "is_hired": False},
            {"id": 1, "role": "Makine Mühendisi", "name": "Aley ceviz", "profit_pct": 5, "comm_pct": 9, "salary": 18000, "hire_cost": 45000, "is_hired": False},
            {"id": 2, "role": "Yazılım Mühendisi", "name": "Burak Kahya", "profit_pct": 16, "comm_pct": 15, "salary": 32000, "hire_cost": 110000, "is_hired": True},
            {"id": 3, "role": "Yazılım Mühendisi", "name": "North elmasstone", "profit_pct": 4, "comm_pct": 9, "salary": 16000, "hire_cost": 40000, "is_hired": False},
            {"id": 4, "role": "Uzay Mühendisi", "name": "Çağan Özcan", "profit_pct": 14, "comm_pct": 15, "salary": 30000, "hire_cost": 95000, "is_hired": False},
            {"id": 5, "role": "Uzay Mühendisi", "name": "baarkiyn copper", "profit_pct": 8, "comm_pct": 10, "salary": 22000, "hire_cost": 60000, "is_hired": False},
            {"id": 6, "role": "Astronot", "name": "Deniz Güler", "profit_pct": 15, "comm_pct": 18, "salary": 35000, "hire_cost": 125000, "is_hired": False}
        ]
        
        self.last_month_stats = None
        self.calc_monthly_finance()

    def hire_personnel(self, p_id):
        for p in self.personnel:
            if p["id"] == p_id and not p["is_hired"]:
                if self.total_vault >= p["hire_cost"]:
                    self.total_vault -= p["hire_cost"]
                    p["is_hired"] = True
                    self.calc_monthly_finance()
                    return True, f"TEBRİKLER! {p['name']} (${p['hire_cost']:,}) BAŞARIYLA İŞE ALINDI!"
                else:
                    return False, f"YETERSIZ BAKİYE! GEREKLİ BÜTÇE: ${p['hire_cost']:,}"
        return False, "İşlem gerçekleştirilemedi."

    def fire_personnel(self, p_id):
        for p in self.personnel:
            if p["id"] == p_id and p["is_hired"]:
                p["is_hired"] = False
                self.calc_monthly_finance()
                return True, f"{p['name']} İŞTEN ÇIKARILDI."
        return False, "İşlem gerçekleştirilemedi."

    def calc_monthly_finance(self):
        total_comm_payout = 0
        total_base_salaries = 0
        total_added_revenue = 0
        
        staff_details = []
        for p in self.personnel:
            if p.get("is_hired", False):
                revenue_contrib = self.base_monthly_revenue * (p["profit_pct"] / 100.0)
                total_added_revenue += revenue_contrib
                
                comm_bonus = p["salary"] * (p["comm_pct"] / 100.0)
                total_pay = p["salary"] + comm_bonus
                
                total_comm_payout += comm_bonus
                total_base_salaries += p["salary"]
                
                staff_details.append({
                    "id": p["id"],
                    "name": p["name"],
                    "role": p["role"],
                    "base": p["salary"],
                    "revenue_contrib": revenue_contrib,
                    "comm_bonus": comm_bonus,
                    "total": total_pay,
                    "prof_pct": p["profit_pct"],
                    "comm_pct": p["comm_pct"],
                    "hire_cost": p["hire_cost"],
                    "is_hired": True
                })
            
        total_expenses = total_base_salaries + total_comm_payout
        total_monthly_revenue = self.base_monthly_revenue + total_added_revenue
        net_profit = total_monthly_revenue - total_expenses
        
        self.last_month_stats = {
            "revenue": total_monthly_revenue,
            "base_revenue": self.base_monthly_revenue,
            "added_revenue": total_added_revenue,
            "expenses": total_expenses,
            "net": net_profit,
            "staff": staff_details
        }
        return self.last_month_stats

    def advance_month(self):
        stats = self.calc_monthly_finance()
        self.total_vault += stats["net"]
        self.current_month += 1
        self.current_month_debris = 0

# STATİK BALON ELEKTROSTATİK ÇÖP TOPLAMA OYUNU
class BalloonSim:
    def __init__(self, rect, economy):
        self.rect = rect
        self.economy = economy
        self.reset()

    def reset(self):
        self.balloon_x = 400.0
        self.balloon_y = 300.0
        self.balloon_radius = 28
        self.charge_surge = False
        self.surge_time = 0
        self.debris_list = []
        self.attached_debris = []
        self.particles = []
        self.score = 0
        self.total_burned = 0
        self.total_earned = 0
        self.is_reentering = False
        self.reentry_y = 0
        self.reentry_start_time = 0
        self.max_capacity = 7  # Her seferde 7 çöp kapasitesi
        self.is_cooling = False
        self.cooldown_start_time = 0
        self.cooldown_duration = 180.0  # 3 Dakika Cooldown (180 saniye)
        self.last_spawn = time.time()
        self.spawn_interval = 0.9

    def handle_event(self, event):
        if self.is_cooling:
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            tx, ty, tw, th = self.rect.x, self.rect.y, self.rect.width, self.rect.height
            play_area = pygame.Rect(tx + 15, ty + 35, tw - 30, th - 50)
            if play_area.collidepoint(event.pos):
                if not self.is_reentering and (time.time() - self.surge_time > 1.2):
                    self.charge_surge = True
                    self.surge_time = time.time()
                    if enter_sound:
                        enter_sound.play()

    def update(self):
        tx, ty, tw, th = self.rect.x, self.rect.y, self.rect.width, self.rect.height
        play_area = pygame.Rect(tx + 15, ty + 35, tw - 30, th - 50)

        # 3 Dakikalık Soğuma Süresi Kontrolü
        if self.is_cooling:
            elapsed = time.time() - self.cooldown_start_time
            if elapsed >= self.cooldown_duration:
                self.is_cooling = False
                self.attached_debris = []
                self.debris_list = []
            return

        # Fare ile balonu hareket ettir
        m_x, m_y = pygame.mouse.get_pos()
        if play_area.collidepoint(m_x, m_y) and not self.is_reentering:
            self.balloon_x = float(m_x)
            self.balloon_y = float(m_y)

        # Surge zaman aşımı
        if self.charge_surge and time.time() - self.surge_time > 0.6:
            self.charge_surge = False

        # Atmosfere giriş aşaması
        if self.is_reentering:
            self.reentry_y += 7.0
            # Alev parçacıkları
            self.particles.append({
                "x": self.balloon_x + random.uniform(-20, 20),
                "y": self.balloon_y + self.reentry_y + random.uniform(-10, 30),
                "vx": random.uniform(-2, 2),
                "vy": random.uniform(-5, -1),
                "life": 1.0,
                "color": random.choice([ORANGE, ALERT_RED, YELLOW, WHITE])
            })
            
            if self.reentry_y > th + 50:
                # Atmosferik yanma tamamlandı!
                count = len(self.attached_debris)
                earned = count * 1000 + 4000
                self.score += count * 300 + 800
                self.total_burned += count
                self.total_earned += earned
                self.economy.total_vault += earned
                self.economy.current_month_debris += count
                if self.economy.current_month_debris >= self.economy.debris_target_for_month:
                    self.economy.advance_month()
                
                # 3 Dakikalık Cooldown Başlat
                self.attached_debris = []
                self.debris_list = []
                self.is_reentering = False
                self.reentry_y = 0
                self.is_cooling = True
                self.cooldown_start_time = time.time()
            return

        # Kapasite 7 çöp olunca imhaya başla
        if len(self.attached_debris) >= self.max_capacity:
            self.is_reentering = True
            self.reentry_start_time = time.time()
            self.reentry_y = 0

        # Yeni çöp üretimi
        if time.time() - self.last_spawn > self.spawn_interval:
            self.last_spawn = time.time()
            if len(self.debris_list) < 15:
                side = random.choice(["left", "right", "top", "bottom"])
                if side == "left":
                    dx, dy = play_area.x - 10, random.randint(play_area.y, play_area.y + play_area.height)
                elif side == "right":
                    dx, dy = play_area.x + play_area.width + 10, random.randint(play_area.y, play_area.y + play_area.height)
                elif side == "top":
                    dx, dy = random.randint(play_area.x, play_area.x + play_area.width), play_area.y - 10
                else:
                    dx, dy = random.randint(play_area.x, play_area.x + play_area.width), play_area.y + play_area.height + 10

                vx = random.uniform(-1.5, 1.5)
                vy = random.uniform(-1.5, 1.5)
                dtype = random.choice(["boya", "vida", "metal", "toz"])
                self.debris_list.append({"x": float(dx), "y": float(dy), "vx": vx, "vy": vy, "type": dtype})

        # Çekim yarıçapı
        attract_radius = 190 if self.charge_surge else 115
        attract_force = 4.8 if self.charge_surge else 1.9

        # Çöpleri güncelle
        for d in self.debris_list[:]:
            d["x"] += d["vx"]
            d["y"] += d["vy"]

            dist = math.hypot(self.balloon_x - d["x"], self.balloon_y - d["y"])
            
            # Elektromanyetik Çekim Kuvveti
            if dist < attract_radius and dist > 5:
                angle = math.atan2(self.balloon_y - d["y"], self.balloon_x - d["x"])
                force = attract_force * (1.0 - dist / attract_radius)
                d["vx"] += math.cos(angle) * force
                d["vy"] += math.sin(angle) * force

            # Balona yapışma
            if dist <= self.balloon_radius + 6:
                offset_angle = random.uniform(0, 2 * math.pi)
                offset_r = random.uniform(5, self.balloon_radius - 2)
                self.attached_debris.append({
                    "rel_x": math.cos(offset_angle) * offset_r,
                    "rel_y": math.sin(offset_angle) * offset_r,
                    "type": d["type"]
                })
                self.debris_list.remove(d)
                self.score += 50

                # Kıvılcım parçacığı
                for _ in range(5):
                    self.particles.append({
                        "x": self.balloon_x, "y": self.balloon_y,
                        "vx": random.uniform(-3, 3), "vy": random.uniform(-3, 3),
                        "life": 0.5, "color": CYAN
                    })

        # Parçacık güncellemeleri
        for p in self.particles[:]:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["life"] -= 0.04
            if p["life"] <= 0:
                self.particles.remove(p)

    def draw(self, surface):
        tx, ty, tw, th = self.rect.x, self.rect.y, self.rect.width, self.rect.height
        play_area = pygame.Rect(tx + 15, ty + 35, tw - 30, th - 50)

        pygame.draw.rect(surface, (4, 10, 22), play_area)
        pygame.draw.rect(surface, DIM_GREEN, play_area, 1)

        old_clip = surface.get_clip()
        surface.set_clip(play_area)

        # 3 Dakikalık Cooldown Ekranı
        if self.is_cooling:
            elapsed = time.time() - self.cooldown_start_time
            rem_sec = max(0, int(self.cooldown_duration - elapsed))
            mins = rem_sec // 60
            secs = rem_sec % 60
            
            c_title = font_medium.render("⏳ STATİK BALON ŞARJ OLUYOR (SOĞUMA SÜRESİ)", True, YELLOW)
            c_timer = font_large.render(f"KALAN SÜRE: {mins:02d}:{secs:02d} / 03:00", True, CYAN)
            
            info1 = font_small.render("7 Adet Statik Yüklü Çöp Atmosfere İndirilip Yanma Reaksiyonuyla Yok Edildi.", True, WHITE)
            info2 = font_tiny.render(f"İstasyon Bütçesine Katkı: +${self.total_earned:,.0f} | Toplam Yanıtılan Çöp: {self.total_burned} Adet", True, GREEN)
            info3 = font_tiny.render(f"Aylık Hedef (17 Çöp) İlerlemesi: {self.economy.current_month_debris}/17", True, LIGHT_GRAY)

            surface.blit(c_title, (tx + tw//2 - c_title.get_width()//2, ty + 100))
            surface.blit(c_timer, (tx + tw//2 - c_timer.get_width()//2, ty + 145))
            
            # İlerleme Çubuğu
            p_box = pygame.Rect(tx + 80, ty + 200, tw - 160, 26)
            pygame.draw.rect(surface, (20, 35, 50), p_box, border_radius=5)
            progress_ratio = min(1.0, elapsed / self.cooldown_duration)
            pygame.draw.rect(surface, CYAN, (p_box.x, p_box.y, int(p_box.width * progress_ratio), p_box.height), border_radius=5)
            pygame.draw.rect(surface, DIM_GREEN, p_box, 2, border_radius=5)
            
            pct_t = font_tiny.render(f"%{int(progress_ratio * 100)} ELEKTROSTATİK ŞARJ DOLDU", True, WHITE)
            surface.blit(pct_t, (p_box.centerx - pct_t.get_width()//2, p_box.centery - pct_t.get_height()//2))

            surface.blit(info1, (tx + tw//2 - info1.get_width()//2, ty + 260))
            surface.blit(info2, (tx + tw//2 - info2.get_width()//2, ty + 295))
            surface.blit(info3, (tx + tw//2 - info3.get_width()//2, ty + 320))

            surface.set_clip(old_clip)
            return

        # Arka plan yörünge çizgileri
        for r in range(40, 320, 55):
            pygame.draw.circle(surface, (10, 24, 40), (tx + tw//2, ty + th//2), r, 1)

        # Elektromanyetik Alan Halkaları (Pulse)
        bx = int(self.balloon_x)
        by = int(self.balloon_y) + (int(self.reentry_y) if self.is_reentering else 0)
        
        pulse_r = 175 if self.charge_surge else 105
        aura_c = CYAN if self.charge_surge else (30, 90, 150)
        
        pygame.draw.circle(surface, aura_c, (bx, by), pulse_r, 1 if not self.charge_surge else 2)
        pygame.draw.circle(surface, (20, 60, 100), (bx, by), pulse_r // 2, 1)

        # Parçacıklar
        for p in self.particles:
            alpha_r = max(1, int(4 * p["life"]))
            pygame.draw.circle(surface, p["color"], (int(p["x"]), int(p["y"])), alpha_r)

        # Serbest Çöpler (Boya pikselleri, vidalar, metaller)
        for d in self.debris_list:
            dx, dy = int(d["x"]), int(d["y"])
            if d["type"] == "vida":
                pygame.draw.rect(surface, LIGHT_GRAY, (dx - 3, dy - 3, 6, 6))
            elif d["type"] == "boya":
                pygame.draw.circle(surface, YELLOW, (dx, dy), 3)
            elif d["type"] == "metal":
                pygame.draw.polygon(surface, ORANGE, [(dx, dy - 4), (dx + 4, dy + 4), (dx - 4, dy + 4)])
            else:
                pygame.draw.circle(surface, WHITE, (dx, dy), 2)

        # Dev Şişirilebilir Statik Balon
        b_color = (80, 180, 255) if not self.is_reentering else (255, 100, 30)
        pygame.draw.circle(surface, b_color, (bx, by), self.balloon_radius)
        pygame.draw.circle(surface, WHITE, (bx - 8, by - 8), 8)  # Parlama
        pygame.draw.circle(surface, PURPLE if not self.charge_surge else CYAN, (bx, by), self.balloon_radius, 2)

        # Balona yapışan çöpler
        for att in self.attached_debris:
            ax = int(bx + att["rel_x"])
            ay = int(by + att["rel_y"])
            pygame.draw.circle(surface, DARK_BLUE, (ax, ay), 3)
            pygame.draw.circle(surface, WHITE, (ax, ay), 1)

        # Atmosfere giriş efekti
        if self.is_reentering:
            fire_txt = font_medium.render("🔥 ATMOSFERE İNİŞ VE YANMA REAKSİYONU AKTİF!", True, ALERT_RED)
            surface.blit(fire_txt, (tx + tw//2 - fire_txt.get_width()//2, ty + 55))

        # HUD ve Bilgiler
        m_deb = self.economy.current_month_debris
        m_tgt = self.economy.debris_target_for_month
        hud_str = f"STATİK BALON KAPAN | Skor: {self.score} | Kapasite: {len(self.attached_debris)}/{self.max_capacity} | Aylık Çöp Sayaç: [{m_deb}/{m_tgt}]"
        surface.blit(font_tiny.render(hud_str, True, GREEN if not self.charge_surge else CYAN), (tx + 25, ty + 42))

        surge_msg = "ELEKTROMANYETİK ŞOK (TIKLA / ATEŞ)" if not self.charge_surge else "⚡ ELEKTROSTATİK ŞOK AKTİF!"
        surface.blit(font_tiny.render(surge_msg, True, YELLOW if not self.charge_surge else CYAN), (tx + tw - 240, ty + 42))

        surface.set_clip(old_clip)

# Arşimet Güneş Odaklayıcı Mini Game Sınıfı
class ArchimedesSim:
    def __init__(self, rect, economy):
        self.rect = rect
        self.economy = economy
        self.slider_angle = 0.5
        self.slider_height = 0.5
        
        self.drag_angle = False
        self.drag_height = False
        
        self.destroyed_count = 0
        self.debris_since_cooldown = 0
        self.max_debris_limit = 5
        
        self.is_cooling = False
        self.cooling_start_time = 0
        self.cooling_duration = 120.0
        
        # Web Mağazası Yükseltmeleri (Shop Upgrades)
        self.auto_ai_unlocked = False
        self.damage_multiplier = 1.0
        self.auto_drone_unlocked = False
        self.last_drone_time = time.time()
        
        # Statik Balon Kapanı Yükseltmesi
        self.static_balloon_unlocked = False
        self.last_balloon_time = time.time()
        
        # Yörüngedeki Aktif Çöp Raporu
        self.total_orbital_debris = 543000
        
        self.rel_debris_x = 0.5
        self.rel_debris_y = 0.5
        self.debris_size = 70
        self.debris_hp = 100.0
        self.current_img = None
        self.month_advanced_popup_time = 0
        self.respawn_debris()

    def respawn_debris(self):
        self.rel_debris_x = random.uniform(0.15, 0.75)
        self.rel_debris_y = random.uniform(0.25, 0.70)
        self.debris_size = random.randint(55, 75)
        self.debris_hp = 100.0
        
        if DEBRIS_IMAGES:
            raw_img = random.choice(DEBRIS_IMAGES)
            self.current_img = pygame.transform.scale(raw_img, (self.debris_size, self.debris_size))
        else:
            self.current_img = None

    def handle_event(self, event):
        tx, ty, tw, th = self.rect.x, self.rect.y, self.rect.width, self.rect.height
        
        sb_h_x = tx + 80
        sb_h_y = ty + th - 40
        sb_h_w = tw - 180
        sb_h_rect = pygame.Rect(sb_h_x - 10, sb_h_y - 15, sb_h_w + 20, 30)

        sb_v_x = tx + tw - 40
        sb_v_y = ty + 60
        sb_v_h = th - 140
        sb_v_rect = pygame.Rect(sb_v_x - 15, sb_v_y - 10, 30, sb_v_h + 20)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            m_pos = event.pos
            if sb_h_rect.collidepoint(m_pos):
                self.drag_angle = True
                self.update_angle_slider(m_pos[0], sb_h_x, sb_h_w)
            elif sb_v_rect.collidepoint(m_pos):
                self.drag_height = True
                self.update_height_slider(m_pos[1], sb_v_y, sb_v_h)

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.drag_angle = False
            self.drag_height = False

        elif event.type == pygame.MOUSEMOTION:
            if self.drag_angle:
                self.update_angle_slider(event.pos[0], sb_h_x, sb_h_w)
            if self.drag_height:
                self.update_height_slider(event.pos[1], sb_v_y, sb_v_h)

    def update_angle_slider(self, mouse_x, sb_x, sb_w):
        rel_x = mouse_x - sb_x
        self.slider_angle = max(0.0, min(1.0, rel_x / sb_w))

    def update_height_slider(self, mouse_y, sb_y, sb_h):
        rel_y = mouse_y - sb_y
        self.slider_height = max(0.0, min(1.0, rel_y / sb_h))

    def update(self):
        if self.auto_drone_unlocked:
            if time.time() - self.last_drone_time >= 10.0:
                self.last_drone_time = time.time()
                self.destroyed_count += 1
                self.debris_since_cooldown += 1
                self.economy.current_month_debris += 1
                self.total_orbital_debris = max(0, self.total_orbital_debris - 25)
                if self.economy.current_month_debris >= self.economy.debris_target_for_month:
                    self.economy.advance_month()
                    self.month_advanced_popup_time = time.time()
                self.respawn_debris()

        if self.static_balloon_unlocked:
            if time.time() - self.last_balloon_time >= 6.0:
                self.last_balloon_time = time.time()
                self.destroyed_count += 1
                self.economy.current_month_debris += 1
                self.total_orbital_debris = max(0, self.total_orbital_debris - 50)
                if self.economy.current_month_debris >= self.economy.debris_target_for_month:
                    self.economy.advance_month()
                    self.month_advanced_popup_time = time.time()
                self.respawn_debris()

        if self.is_cooling:
            elapsed = time.time() - self.cooling_start_time
            if elapsed >= self.cooling_duration:
                self.is_cooling = False
                self.debris_since_cooldown = 0
            else:
                return

        if self.auto_ai_unlocked and not self.is_cooling:
            self.slider_angle += (self.rel_debris_x - self.slider_angle) * 0.08
            self.slider_height += (self.rel_debris_y - self.slider_height) * 0.08

        tx, ty, tw, th = self.rect.x, self.rect.y, self.rect.width, self.rect.height
        screen_rect = pygame.Rect(tx + 15, ty + 35, tw - 70, th - 95)
        
        deb_x = screen_rect.x + self.rel_debris_x * (screen_rect.width - self.debris_size)
        deb_y = screen_rect.y + self.rel_debris_y * (screen_rect.height - self.debris_size)

        sun_x = tx + (tw - 70) // 2
        sun_y = ty + 70
        
        beam_target_x = screen_rect.x + 30 + self.slider_angle * (screen_rect.width - 60)
        beam_target_y = screen_rect.y + 40 + self.slider_height * (screen_rect.height - 50)
        
        deb_cx = deb_x + self.debris_size / 2.0
        deb_cy = deb_y + self.debris_size / 2.0

        ab_x = beam_target_x - sun_x
        ab_y = beam_target_y - sun_y
        ap_x = deb_cx - sun_x
        ap_y = deb_cy - sun_y

        ab2 = ab_x * ab_x + ab_y * ab_y
        if ab2 > 0:
            t = max(0.0, min(1.0, (ap_x * ab_x + ap_y * ab_y) / ab2))
            closest_x = sun_x + t * ab_x
            closest_y = sun_y + t * ab_y
            
            dist = math.hypot(deb_cx - closest_x, deb_cy - closest_y)
            end_dist = math.hypot(deb_cx - beam_target_x, deb_cy - beam_target_y)

            hit_radius = (self.debris_size / 2.0) + 12
            if dist <= hit_radius or end_dist <= hit_radius:
                self.debris_hp -= 2.2 * self.damage_multiplier
                if laser_sound and random.random() < 0.2:
                    laser_sound.play()
                if self.debris_hp <= 0:
                    self.destroyed_count += 1
                    self.debris_since_cooldown += 1
                    self.economy.current_month_debris += 1
                    self.total_orbital_debris = max(0, self.total_orbital_debris - 15)
                    
                    if self.economy.current_month_debris >= self.economy.debris_target_for_month:
                        self.economy.advance_month()
                        self.month_advanced_popup_time = time.time()
                    
                    if self.debris_since_cooldown >= self.max_debris_limit:
                        self.is_cooling = True
                        self.cooling_start_time = time.time()
                    
                    self.respawn_debris()

    def draw(self, surface):
        tx, ty, tw, th = self.rect.x, self.rect.y, self.rect.width, self.rect.height
        
        screen_rect = pygame.Rect(tx + 15, ty + 35, tw - 70, th - 95)
        pygame.draw.rect(surface, (4, 8, 16), screen_rect)
        pygame.draw.rect(surface, DIM_GREEN, screen_rect, 1)

        old_clip = surface.get_clip()
        surface.set_clip(screen_rect)

        deb_x = screen_rect.x + self.rel_debris_x * (screen_rect.width - self.debris_size)
        deb_y = screen_rect.y + self.rel_debris_y * (screen_rect.height - self.debris_size)

        if self.current_img:
            current_alpha = int(255 * (self.debris_hp / 100.0))
            temp_img = self.current_img.copy()
            temp_img.set_alpha(current_alpha)
            surface.blit(temp_img, (deb_x, deb_y))
            pygame.draw.rect(surface, ALERT_RED if self.debris_hp < 100 else CYAN, 
                             (deb_x - 4, deb_y - 4, self.debris_size + 8, self.debris_size + 8), 1)
        else:
            pygame.draw.rect(surface, GRAY, (deb_x, deb_y, self.debris_size, self.debris_size))

        sun_x = tx + (tw - 70) // 2
        sun_y = ty + 70
        
        sun_color_1 = ALERT_RED if self.is_cooling else ORANGE
        sun_color_2 = ALERT_RED if self.is_cooling else YELLOW
        
        pygame.draw.circle(surface, sun_color_1, (sun_x, sun_y), 25)
        pygame.draw.circle(surface, sun_color_2, (sun_x, sun_y), 18)
        pygame.draw.circle(surface, WHITE, (sun_x, sun_y), 10)
        
        beam_target_x = screen_rect.x + 30 + self.slider_angle * (screen_rect.width - 60)
        beam_target_y = screen_rect.y + 40 + self.slider_height * (screen_rect.height - 50)
        
        if self.is_cooling:
            overlay_surf = pygame.Surface((screen_rect.width, screen_rect.height), pygame.SRCALPHA)
            overlay_surf.fill((255, 30, 30, 40))
            surface.blit(overlay_surf, (screen_rect.x, screen_rect.y))
            
            remaining = max(0, int(self.cooling_duration - (time.time() - self.cooling_start_time)))
            mins = remaining // 60
            secs = remaining % 60
            
            warn_t1 = font_medium.render("! AŞIRI ISINMA - AYNALAR SOĞUTULUYOR !", True, ALERT_RED)
            warn_t2 = font_large.render(f"KALAN SÜRE: {mins:02d}:{secs:02d}", True, YELLOW)
            
            surface.blit(warn_t1, (screen_rect.x + screen_rect.width//2 - warn_t1.get_width()//2, screen_rect.y + screen_rect.height//2 - 30))
            surface.blit(warn_t2, (screen_rect.x + screen_rect.width//2 - warn_t2.get_width()//2, screen_rect.y + screen_rect.height//2 + 10))
        else:
            pygame.draw.line(surface, (255, 255, 150, 100), (sun_x, sun_y), (beam_target_x, beam_target_y), 8)
            pygame.draw.line(surface, YELLOW, (sun_x, sun_y), (beam_target_x, beam_target_y), 4)
            pygame.draw.line(surface, WHITE, (sun_x, sun_y), (beam_target_x, beam_target_y), 2)
            
            pygame.draw.circle(surface, ORANGE, (int(beam_target_x), int(beam_target_y)), 12)
            pygame.draw.circle(surface, WHITE, (int(beam_target_x), int(beam_target_y)), 4)
            pygame.draw.circle(surface, CYAN, (int(beam_target_x), int(beam_target_y)), 18, 1)

        if time.time() - self.month_advanced_popup_time < 3.5:
            pop_txt = font_medium.render(f"🎉 17 ÇÖP TEMİZLENDİ! YENİ AY #{self.economy.current_month} BAŞLADI!", True, GREEN)
            pygame.draw.rect(surface, BLACK, (screen_rect.x + 20, screen_rect.y + 70, screen_rect.width - 40, 40))
            pygame.draw.rect(surface, GREEN, (screen_rect.x + 20, screen_rect.y + 70, screen_rect.width - 40, 40), 2)
            surface.blit(pop_txt, (screen_rect.x + screen_rect.width//2 - pop_txt.get_width()//2, screen_rect.y + 80))

        surface.set_clip(old_clip)

        m_debris = self.economy.current_month_debris
        m_target = self.economy.debris_target_for_month
        heat_level = f"{self.debris_since_cooldown}/{self.max_debris_limit}"
        info_str = f"Toplam: {self.destroyed_count} | Ay Çöp Hedefi: [{m_debris}/{m_target}] | Isı: [{heat_level}]"
        surface.blit(font_small.render(info_str, True, ALERT_RED if self.is_cooling else GREEN), (tx + 25, ty + 42))

        sb_h_x = tx + 80
        sb_h_y = ty + th - 40
        sb_h_w = tw - 180
        pygame.draw.rect(surface, GRAY, (sb_h_x, sb_h_y - 4, sb_h_w, 8), border_radius=4)
        pygame.draw.rect(surface, DIM_GREEN, (sb_h_x, sb_h_y - 4, sb_h_w, 8), 1, border_radius=4)
        
        h_handle_x = sb_h_x + self.slider_angle * sb_h_w
        h_handle_rect = pygame.Rect(h_handle_x - 12, sb_h_y - 12, 24, 24)
        pygame.draw.rect(surface, ALERT_RED if self.is_cooling else (CYAN if self.drag_angle else GREEN), h_handle_rect, border_radius=4)
        pygame.draw.rect(surface, WHITE, h_handle_rect, 2, border_radius=4)
        
        lbl_h = font_tiny.render("AÇI", True, WHITE)
        surface.blit(lbl_h, (sb_h_x - 45, sb_h_y - 8))

        sb_v_x = tx + tw - 40
        sb_v_y = ty + 60
        sb_v_h = th - 140
        pygame.draw.rect(surface, GRAY, (sb_v_x - 4, sb_v_y, 8, sb_v_h), border_radius=4)
        pygame.draw.rect(surface, DIM_GREEN, (sb_v_x - 4, sb_v_y, 8, sb_v_h), 1, border_radius=4)
        
        v_handle_y = sb_v_y + self.slider_height * sb_v_h
        v_handle_rect = pygame.Rect(sb_v_x - 12, v_handle_y - 12, 24, 24)
        pygame.draw.rect(surface, ALERT_RED if self.is_cooling else (CYAN if self.drag_height else GREEN), v_handle_rect, border_radius=4)
        pygame.draw.rect(surface, WHITE, v_handle_rect, 2, border_radius=4)

        lbl_v = font_tiny.render("YÜKS", True, WHITE)
        surface.blit(lbl_v, (sb_v_x - 15, sb_v_y - 20))

# Masaüstü Pencere Sınıfı
class Window:
    def __init__(self, title, x, y, width, height, content_type):
        self.title = title
        self.rect = pygame.Rect(x, y, width, height)
        self.is_open = True
        self.content_type = content_type
        self.dragging = False
        self.drag_offset = (0, 0)
        self.close_btn_rect = pygame.Rect(x + width - 26, y + 5, 18, 18)

    def update_close_btn(self):
        self.close_btn_rect = pygame.Rect(self.rect.x + self.rect.width - 26, self.rect.y + 5, 18, 18)

    def draw_header(self, surface):
        pygame.draw.rect(surface, (0, 0, 0, 150), (self.rect.x + 8, self.rect.y + 8, self.rect.width, self.rect.height))
        pygame.draw.rect(surface, (8, 12, 18), self.rect)
        pygame.draw.rect(surface, GREEN, self.rect, 2)
        pygame.draw.rect(surface, DIM_GREEN, (self.rect.x, self.rect.y, self.rect.width, 28))
        title_text = font_small.render(self.title, True, WHITE)
        surface.blit(title_text, (self.rect.x + 12, self.rect.y + 5))
        
        self.update_close_btn()
        pygame.draw.rect(surface, ALERT_RED, self.close_btn_rect, border_radius=2)
        x_text = font_tiny.render("X", True, WHITE)
        surface.blit(x_text, (self.close_btn_rect.x + 4, self.close_btn_rect.y + 1))

# Masaüstü Modu (Desktop OS)
class DesktopOS:
    def __init__(self):
        w_width = min(850, WIDTH - 100)
        w_height = min(560, HEIGHT - 120)
        
        self.economy = EconomySystem()
        self.economy_tab = "market"
        self.economy_msg = ""
        self.economy_msg_time = 0
        
        # Web Tarayıcısı Durumu
        self.current_web_url = "http://shop.uggkf.space"
        self.web_msg = ""
        self.web_msg_time = 0
        self.web_scroll_y = 0

        # Statik Balon Uygulaması Satın Alma Durumu
        self.balloon_unlocked = False
        self.balloon_sim = None

        self.windows = {
            "terminal": Window("COMMAND INTERFACE [UGGKF-CMD]", 80, 60, w_width, w_height, "terminal"),
            "archimedes": Window("ARŞİMET GÜNEŞ ODAKLAYICI SIMULATOR", 160, 100, 780, 520, "archimedes"),
            "bilgiler": Window("BELGELER VE ARAŞTIRMALAR", 200, 120, 750, 480, "bilgiler"),
            "ekonomi": Window("İSTASYON EKONOMİ VE PERSONEL MERKEZİ", 140, 80, 840, 540, "ekonomi"),
            "web": Window("UGGKF WEB BROWSER v1.0", 110, 70, 820, 540, "web")
        }
        
        self.archimedes_sim = ArchimedesSim(self.windows["archimedes"].rect, self.economy)

        self.docs_dir = os.path.join(os.path.dirname(__file__), "belgeler_arastırmalar")
        self.doc_files = []
        if os.path.exists(self.docs_dir):
            self.doc_files = [f for f in os.listdir(self.docs_dir) if f.lower().endswith('.txt')]
        
        self.selected_doc_file = self.doc_files[0] if self.doc_files else None
        self.doc_scroll_y = 0
        self.doc_scroll_x = 0

        self.windows["archimedes"].is_open = False
        self.windows["bilgiler"].is_open = False
        self.windows["ekonomi"].is_open = False
        self.windows["web"].is_open = False

        self.active_window = "terminal"
        
        self.command_history = [
            "UGGKF OS v4.09 [Uzay İstasyonu Alpha-7]",
            "Arşimet Güneş Odaklayıcı Modülü Yüklendi.",
            "Ekonomi & Personel Mağazası Bağlandı ($454,000/Ay).",
            "Yardım almak için 'yardım' veya 'help' yazın.",
            ""
        ]
        self.current_input = ""
        
        # Masaüstü İkonları (Sadece temel sistem uygulamaları)
        self.icons = [
            {"name": "Terminal.sys", "x": 40, "y": 50, "action": "terminal"},
            {"name": "Arsimet.exe", "x": 40, "y": 140, "action": "archimedes"},
            {"name": "Ekonomi.exe", "x": 40, "y": 230, "action": "ekonomi"},
            {"name": "Web.exe", "x": 40, "y": 320, "action": "web"},
            {"name": "Bilgiler", "x": 40, "y": 410, "action": "bilgiler"}
        ]
        self.rearrange_icons()
        self.selected_icon = None

    def install_app(self, app_name, app_action, window_title):
        if not any(icon["action"] == app_action for icon in self.icons):
            self.icons.append({"name": app_name, "x": 0, "y": 0, "action": app_action})
            self.rearrange_icons()
        if app_action not in self.windows:
            self.windows[app_action] = Window(window_title, 180, 90, 780, 500, app_action)
            self.windows[app_action].is_open = False

    def rearrange_icons(self):
        for i, icon in enumerate(self.icons):
            col = i // 6
            row = i % 6
            icon["x"] = 40 + col * 105
            icon["y"] = 50 + row * 85

    def handle_event(self, event):
        if self.windows["archimedes"].is_open:
            self.archimedes_sim.handle_event(event)

        if "balloon_trap" in self.windows and self.windows["balloon_trap"].is_open and self.balloon_unlocked and self.balloon_sim:
            self.balloon_sim.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            if event.button == 1:
                self.selected_icon = None
                for icon in self.icons:
                    rect = pygame.Rect(icon["x"], icon["y"], 90, 80)
                    if rect.collidepoint(mouse_pos):
                        self.selected_icon = icon["name"]
                        win_key = icon["action"]
                        if win_key in self.windows:
                            self.windows[win_key].is_open = True
                            self.active_window = win_key

                # Web Browser Tıklamaları
                web_win = self.windows["web"]
                if web_win.is_open and web_win.rect.collidepoint(mouse_pos):
                    wx, wy, ww, wh = web_win.rect.x, web_win.rect.y, web_win.rect.width, web_win.rect.height
                    
                    tab_shop = pygame.Rect(wx + 15, wy + 35, 180, 26)
                    if tab_shop.collidepoint(mouse_pos):
                        self.current_web_url = "http://shop.uggkf.space"
                        if key_sound: key_sound.play()

                    tab_nasa = pygame.Rect(wx + 200, wy + 35, 240, 26)
                    if tab_nasa.collidepoint(mouse_pos):
                        self.current_web_url = "http://nasa.gov/orbital-debris"
                        if key_sound: key_sound.play()

                    if self.current_web_url == "http://shop.uggkf.space":
                        sy = self.web_scroll_y
                        
                        # Tek Ürün: Statik Balon Kapanı (Elektrostatik Çöp Toplayıcı Oyunu)
                        b_balloon = pygame.Rect(wx + ww - 180, wy + 172 + sy, 140, 36)
                        if b_balloon.collidepoint(mouse_pos) and not self.balloon_unlocked:
                            if self.economy.total_vault >= 140000:
                                self.economy.total_vault -= 140000
                                self.balloon_unlocked = True
                                self.balloon_sim = BalloonSim(pygame.Rect(180, 90, 780, 500), self.economy)
                                self.install_app("Balloon.exe", "balloon_trap", "STATİK BALON KAPAN OYUNU [Balloon.exe]")
                                self.web_msg = "Balloon.exe Yüklendi! Masaüstüne Eklendi."
                                self.web_msg_time = time.time()
                                if enter_sound: enter_sound.play()
                            else:
                                self.web_msg = "Yetersiz Bakiye! Gereken: $140,000"
                                self.web_msg_time = time.time()

                bilgiler_win = self.windows["bilgiler"]
                if bilgiler_win.is_open and bilgiler_win.rect.collidepoint(mouse_pos):
                    bx, by = bilgiler_win.rect.x + 20, bilgiler_win.rect.y + 45
                    file_item_y = by
                    for docname in self.doc_files:
                        item_rect = pygame.Rect(bx, file_item_y, 160, 30)
                        if item_rect.collidepoint(mouse_pos):
                            self.selected_doc_file = docname
                            self.doc_scroll_y = 0
                            self.doc_scroll_x = 0
                            if key_sound:
                                key_sound.play()
                        file_item_y += 35

                ekonomi_win = self.windows["ekonomi"]
                if ekonomi_win.is_open and ekonomi_win.rect.collidepoint(mouse_pos):
                    tx, ty, tw, th = ekonomi_win.rect.x, ekonomi_win.rect.y, ekonomi_win.rect.width, ekonomi_win.rect.height
                    
                    tab_hired_rect = pygame.Rect(tx + 15, ty + 108, 220, 32)
                    tab_market_rect = pygame.Rect(tx + 245, ty + 108, 380, 32)
                    
                    if tab_hired_rect.collidepoint(mouse_pos):
                        self.economy_tab = "hired"
                        if key_sound:
                            key_sound.play()
                    elif tab_market_rect.collidepoint(mouse_pos):
                        self.economy_tab = "market"
                        if key_sound:
                            key_sound.play()
                    else:
                        if self.economy_tab == "market":
                            row_y = ty + 180
                            for p in self.economy.personnel:
                                btn_rect = pygame.Rect(tx + tw - 200, row_y + 4, 185, 34)
                                if btn_rect.collidepoint(mouse_pos):
                                    if not p["is_hired"]:
                                        success, msg = self.economy.hire_personnel(p["id"])
                                        self.economy_msg = msg
                                        self.economy_msg_time = time.time()
                                        if success and enter_sound:
                                            enter_sound.play()
                                        elif not success and key_sound:
                                            key_sound.play()
                                row_y += 44
                        elif self.economy_tab == "hired":
                            row_y = ty + 180
                            st = self.economy.last_month_stats
                            for p in st["staff"]:
                                btn_rect = pygame.Rect(tx + tw - 150, row_y + 4, 135, 34)
                                if btn_rect.collidepoint(mouse_pos):
                                    success, msg = self.economy.fire_personnel(p["id"])
                                    self.economy_msg = msg
                                    self.economy_msg_time = time.time()
                                    if key_sound:
                                        key_sound.play()
                                row_y += 44

                for win_key, win in self.windows.items():
                    if win.is_open:
                        if win.close_btn_rect.collidepoint(mouse_pos):
                            win.is_open = False
                            if key_sound:
                                key_sound.play()
                            return
                        
                        title_bar = pygame.Rect(win.rect.x, win.rect.y, win.rect.width, 28)
                        if title_bar.collidepoint(mouse_pos):
                            win.dragging = True
                            win.drag_offset = (mouse_pos[0] - win.rect.x, mouse_pos[1] - win.rect.y)
                            self.active_window = win_key

            elif event.button in (4, 5):
                bilgiler_win = self.windows["bilgiler"]
                if bilgiler_win.is_open and bilgiler_win.rect.collidepoint(mouse_pos):
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                        if event.button == 4:
                            self.doc_scroll_x = min(0, self.doc_scroll_x + 40)
                        else:
                            self.doc_scroll_x -= 40
                    else:
                        if event.button == 4:
                            self.doc_scroll_y = min(0, self.doc_scroll_y + 30)
                        else:
                            self.doc_scroll_y -= 30

                web_win = self.windows["web"]
                if web_win.is_open and web_win.rect.collidepoint(mouse_pos):
                    if event.button == 4:
                        self.web_scroll_y = min(0, self.web_scroll_y + 30)
                    else:
                        self.web_scroll_y = max(-250, self.web_scroll_y - 30)

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            for win in self.windows.values():
                win.dragging = False

        elif event.type == pygame.MOUSEMOTION:
            for win in self.windows.values():
                if win.dragging:
                    win.rect.x = event.pos[0] - win.drag_offset[0]
                    win.rect.y = event.pos[1] - win.drag_offset[1]
                    if win.content_type == "archimedes":
                        self.archimedes_sim.rect = win.rect
                    elif win.content_type == "empty":
                        self.artemis_sim.rect = win.rect

        elif event.type == pygame.KEYDOWN:
            bilgiler_win = self.windows["bilgiler"]
            if bilgiler_win.is_open and self.active_window == "bilgiler":
                if event.key == pygame.K_LEFT:
                    self.doc_scroll_x = min(0, self.doc_scroll_x + 40)
                elif event.key == pygame.K_RIGHT:
                    self.doc_scroll_x -= 40
                elif event.key == pygame.K_UP:
                    self.doc_scroll_y = min(0, self.doc_scroll_y + 30)
                elif event.key == pygame.K_DOWN:
                    self.doc_scroll_y -= 30

            term_win = self.windows["terminal"]
            if term_win.is_open and self.active_window == "terminal":
                if event.key == pygame.K_RETURN:
                    if key_sound:
                        key_sound.play()
                    self.process_command(self.current_input)
                    self.current_input = ""
                elif event.key == pygame.K_BACKSPACE:
                    self.current_input = self.current_input[:-1]
                else:
                    if len(event.unicode) > 0 and event.unicode.isprintable():
                        self.current_input += event.unicode
                        if key_sound:
                            key_sound.play()

    def process_command(self, cmd):
        cmd_clean = cmd.strip().lower()
        self.command_history.append(f"> {cmd}")
        
        if cmd_clean in ["yardim", "help"]:
            self.command_history.append("Mevcut Komutlar:")
            self.command_history.append("  arsimet  - Arşimet Güneş Odaklayıcı simülatörünü açar")
            self.command_history.append("  ekonomi  - Bütçe ve personel mağazası / işe alım merkezini açar")
            self.command_history.append("  web      - Web tarayıcısını açar (Yazılım Mağazası)")
            self.command_history.append("  bilgiler - Araştırma belgeleri klasörünü açar")
            self.command_history.append("  durum    - İstasyon ve kirlilik durumunu gösterir")
            self.command_history.append("  aylikcop - Bu ay toplanan toplam çöp sayısını ve kalan hedefi gösterir")
            self.command_history.append("  credits  - Oyun geliştiricisi ve fikir sahiplerini gösterir")
            self.command_history.append("  temizle  - Terminal ekranını temizler")
            self.command_history.append("  cikis    - Terminal penceresini kapatır")
        elif cmd_clean in ["arsimet", "archimedes"]:
            self.windows["archimedes"].is_open = True
            self.active_window = "archimedes"
            self.command_history.append("Arşimet simülatörü başlatıldı.")
        elif cmd_clean in ["ekonomi", "bütçe", "butce"]:
            self.windows["ekonomi"].is_open = True
            self.active_window = "ekonomi"
            self.command_history.append("Ekonomi ve personel yönetim merkezi açıldı.")
        elif cmd_clean in ["web", "browser", "internet", "shop"]:
            self.windows["web"].is_open = True
            self.active_window = "web"
            self.command_history.append("Web tarayıcısı açıldı.")
        elif cmd_clean in ["bilgiler", "belgeler", "docs"]:
            self.windows["bilgiler"].is_open = True
            self.active_window = "bilgiler"
            self.command_history.append("Belgeler klasörü açıldı.")
        elif cmd_clean in ["durum", "status"]:
            st = self.economy.last_month_stats
            self.command_history.append("[SİSTEM DURUMU]")
            self.command_history.append(f"  Mevcut Ay     : Ay #{self.economy.current_month}")
            self.command_history.append(f"  Kasa Bütçesi  : ${self.economy.total_vault:,.2f}")
            self.command_history.append(f"  Aylık Gelir   : ${self.economy.base_monthly_revenue:,.2f}")
            self.command_history.append(f"  Net Kar       : ${st['net']:,.2f}")
            self.command_history.append(f"  Aktif Çalışan : {len(st['staff'])}/7")
        elif cmd_clean in ["aylikcop", "aylıkçöp", "aylik_cop", "cop"]:
            collected = self.economy.current_month_debris
            target = self.economy.debris_target_for_month
            remaining = max(0, target - collected)
            self.command_history.append("[AYLIK ÇÖP TOPLAMA SAYAÇ SİSTEMİ]")
            self.command_history.append(f"  Mevcut Ay         : Ay #{self.economy.current_month}")
            self.command_history.append(f"  Bu Ay Toplanan    : {collected} / {target} Adet Çöp")
            self.command_history.append(f"  1 Ay Geçmesi İçin  : Kalan {remaining} Adet Çöp")
            if remaining == 0:
                self.command_history.append("  SAYAÇ DURUMU      : Hedef doldu! Yeni aya geçildi ve sayaç 0'landı.")
            else:
                self.command_history.append(f"  SAYAÇ DURUMU      : {remaining} çöp daha toplanınca 1 ay geçecek ve sayaç 0'lanacak.")
        elif cmd_clean in ["credits", "krediler", "kredi", "jenerik", "yapimclar", "yapımcılar"]:
            self.command_history.append("Oyun geliştiricisi: Burak Kahya,")
            self.command_history.append("Fikirler:Deniz Güler,Efe Kocagöz,Çağan Özcan")
        elif cmd_clean in ["temizle", "clear"]:
            self.command_history = []
        elif cmd_clean in ["cikis", "exit"]:
            self.windows["terminal"].is_open = False
        elif cmd_clean != "":
            self.command_history.append(f"Hata: '{cmd}' komutu tanınmadı. 'yardim' yazabilirsiniz.")
            
        self.command_history.append("")

    def draw(self, surface):
        surface.fill(DARK_BLUE)
        
        for x in range(0, WIDTH, 50):
            pygame.draw.line(surface, (15, 30, 50), (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, 50):
            pygame.draw.line(surface, (15, 30, 50), (0, y), (WIDTH, y))

        pygame.draw.rect(surface, BLACK, (0, 0, WIDTH, 32))
        pygame.draw.line(surface, DIM_GREEN, (0, 32), (WIDTH, 32))
        sys_info = font_tiny.render(f"PROJE: UGGKF OS | AY #{self.economy.current_month} | KASA: ${self.economy.total_vault:,.0f} | [ESC: Çıkış]", True, GREEN)
        surface.blit(sys_info, (15, 8))

        # Masaüstü İkonları
        for icon in self.icons:
            ix, iy = icon["x"], icon["y"]
            is_selected = (self.selected_icon == icon["name"])
            box_color = CYAN if is_selected else DIM_GREEN
            pygame.draw.rect(surface, (15, 35, 45) if is_selected else (10, 25, 35), (ix, iy, 74, 58), border_radius=4)
            pygame.draw.rect(surface, box_color, (ix, iy, 74, 58), 2, border_radius=4)
            
            if icon["action"] == "bilgiler":
                pygame.draw.rect(surface, YELLOW, (ix + 18, iy + 14, 38, 28), border_radius=2)
                pygame.draw.rect(surface, (200, 160, 20), (ix + 18, iy + 14, 38, 28), 2, border_radius=2)
                pygame.draw.rect(surface, ORANGE, (ix + 22, iy + 10, 16, 6))
            elif icon["action"] == "ekonomi":
                pygame.draw.rect(surface, GREEN, (ix + 18, iy + 14, 38, 28), border_radius=3)
                pygame.draw.rect(surface, WHITE, (ix + 18, iy + 14, 38, 28), 1, border_radius=3)
                dol_t = font_medium.render("$", True, BLACK)
                surface.blit(dol_t, (ix + 31, iy + 15))
            elif icon["action"] == "web":
                pygame.draw.circle(surface, CYAN, (ix + 37, iy + 28), 16, 2)
                pygame.draw.ellipse(surface, YELLOW, (ix + 27, iy + 22, 20, 12), 2)
            elif icon["action"] == "auto_ai":
                pygame.draw.rect(surface, (10, 40, 50), (ix + 18, iy + 14, 38, 28), border_radius=3)
                pygame.draw.rect(surface, CYAN, (ix + 18, iy + 14, 38, 28), 1, border_radius=3)
                surface.blit(font_tiny.render("AI", True, CYAN), (ix + 30, iy + 20))
            elif icon["action"] == "laser_power":
                pygame.draw.rect(surface, (50, 30, 10), (ix + 18, iy + 14, 38, 28), border_radius=3)
                pygame.draw.rect(surface, ORANGE, (ix + 18, iy + 14, 38, 28), 1, border_radius=3)
                surface.blit(font_tiny.render("PWR", True, ORANGE), (ix + 22, iy + 20))
            elif icon["action"] == "drone_ctrl":
                pygame.draw.rect(surface, (10, 40, 20), (ix + 18, iy + 14, 38, 28), border_radius=3)
                pygame.draw.rect(surface, GREEN, (ix + 18, iy + 14, 38, 28), 1, border_radius=3)
                surface.blit(font_tiny.render("DRN", True, GREEN), (ix + 23, iy + 20))
            elif icon["action"] == "balloon_trap":
                pygame.draw.rect(surface, (40, 10, 50), (ix + 18, iy + 14, 38, 28), border_radius=3)
                pygame.draw.rect(surface, PURPLE, (ix + 18, iy + 14, 38, 28), 1, border_radius=3)
                surface.blit(font_tiny.render("BAL", True, PURPLE), (ix + 24, iy + 20))
            else:
                pygame.draw.rect(surface, GREEN, (ix + 25, iy + 14, 24, 28), 2)

            name_surf = font_tiny.render(icon["name"], True, WHITE if is_selected else LIGHT_GRAY)
            surface.blit(name_surf, (ix - 5, iy + 65))

        # Pencereler
        for win_key, win in self.windows.items():
            if win.is_open:
                win.draw_header(surface)
                tx, ty, tw, th = win.rect.x, win.rect.y, win.rect.width, win.rect.height

                if win.content_type == "terminal":
                    max_lines = int((th - 70) / 22)
                    visible_lines = self.command_history[-max_lines:]
                    start_y = ty + 38
                    for line in visible_lines:
                        line_surf = font_small.render(line, True, GREEN)
                        surface.blit(line_surf, (tx + 15, start_y))
                        start_y += 22
                        
                    input_prompt = font_small.render("> " + self.current_input, True, CYAN)
                    surface.blit(input_prompt, (tx + 15, ty + th - 30))
                    
                    if int(time.time() * 3) % 2 == 0:
                        cursor_x = tx + 15 + input_prompt.get_width() + 2
                        pygame.draw.rect(surface, CYAN, (cursor_x, ty + th - 28, 8, 16))

                elif win.content_type == "archimedes":
                    self.archimedes_sim.rect = win.rect
                    self.archimedes_sim.update()
                    self.archimedes_sim.draw(surface)

                elif win.content_type == "web":
                    pygame.draw.rect(surface, (15, 25, 38), (tx + 10, ty + 32, tw - 20, 32))
                    
                    is_s1 = (self.current_web_url == "http://shop.uggkf.space")
                    tab_shop = pygame.Rect(tx + 15, ty + 35, 180, 26)
                    pygame.draw.rect(surface, (25, 55, 85) if is_s1 else (10, 20, 30), tab_shop, border_top_left_radius=4, border_top_right_radius=4)
                    pygame.draw.rect(surface, CYAN if is_s1 else GRAY, tab_shop, 1, border_top_left_radius=4, border_top_right_radius=4)
                    surface.blit(font_tiny.render("🛒 Software Shop", True, WHITE if is_s1 else LIGHT_GRAY), (tx + 25, ty + 40))

                    is_s2 = (self.current_web_url == "http://nasa.gov/orbital-debris")
                    tab_nasa = pygame.Rect(tx + 200, ty + 35, 240, 26)
                    pygame.draw.rect(surface, (25, 55, 85) if is_s2 else (10, 20, 30), tab_nasa, border_top_left_radius=4, border_top_right_radius=4)
                    pygame.draw.rect(surface, CYAN if is_s2 else GRAY, tab_nasa, 1, border_top_left_radius=4, border_top_right_radius=4)
                    surface.blit(font_tiny.render("🚀 NASA Debris Portal", True, WHITE if is_s2 else LIGHT_GRAY), (tx + 210, ty + 40))

                    pygame.draw.rect(surface, (8, 14, 22), (tx + 10, ty + 68, tw - 20, 28))
                    pygame.draw.rect(surface, DIM_GREEN, (tx + 10, ty + 68, tw - 20, 28), 1)
                    url_t = font_tiny.render("URL: " + self.current_web_url, True, GREEN)
                    surface.blit(url_t, (tx + 20, ty + 74))

                    web_content_rect = pygame.Rect(tx + 10, ty + 100, tw - 20, th - 110)
                    pygame.draw.rect(surface, (6, 10, 18), web_content_rect)
                    pygame.draw.rect(surface, DIM_GREEN, web_content_rect, 1)

                    if self.web_msg and (time.time() - self.web_msg_time < 3.5):
                        msg_s = font_tiny.render(self.web_msg, True, YELLOW)
                        surface.blit(msg_s, (tx + tw - msg_s.get_width() - 30, ty + 74))

                    # MAĞAZA İÇERİĞİ
                    if self.current_web_url == "http://shop.uggkf.space":
                        old_c = surface.get_clip()
                        surface.set_clip(web_content_rect)

                        sy = self.web_scroll_y

                        header_s = font_medium.render("UGGKF ISTASYON YAZILIM VE OYUN MAĞAZASI", True, YELLOW)
                        surface.blit(header_s, (tx + 30, ty + 110 + sy))
                        
                        sub_s = font_tiny.render("Yörünge Temizliği ve İstasyon İçin Özel Yazılım ve Oyun Modülleri", True, LIGHT_GRAY)
                        surface.blit(sub_s, (tx + 30, ty + 135 + sy))

                        # Tek Ürün: Statik Balon Kapanı (Elektrostatik Çöp Toplayıcı)
                        card_box = pygame.Rect(tx + 25, ty + 165 + sy, tw - 50, 310)
                        pygame.draw.rect(surface, (12, 22, 36), card_box, border_radius=6)
                        pygame.draw.rect(surface, CYAN if self.balloon_unlocked else DIM_GREEN, card_box, 1, border_radius=6)
                        
                        title_str = "1. \"Statik Balon\" Kapanı (Elektrostatik Çöp Toplayıcı Oyunu)"
                        surface.blit(font_small.render(title_str, True, WHITE), (tx + 38, ty + 178 + sy))
                        
                        # Satın al butonu
                        btn_bal = pygame.Rect(tx + tw - 180, ty + 175 + sy, 140, 36)
                        if self.balloon_unlocked:
                            pygame.draw.rect(surface, (20, 50, 30), btn_bal, border_radius=4)
                            surface.blit(font_tiny.render("✓ YÜKLENDİ", True, GREEN), (btn_bal.x + 25, btn_bal.y + 10))
                        else:
                            can_aff = self.economy.total_vault >= 140000
                            pygame.draw.rect(surface, (20, 80, 40) if can_aff else (60, 20, 20), btn_bal, border_radius=4)
                            surface.blit(font_tiny.render("SATIN AL ($140K)", True, WHITE), (btn_bal.x + 12, btn_bal.y + 10))

                        # Açıklama Metinleri (Kullanıcının tam açıklaması)
                        p1 = "Uzaydaki küçük çöplerin (boya pikselleri, vida parçaları vb.) neredeyse tamamı uzay radyasyonu"
                        p2 = "nedeniyle statik elektrikle (pozitif veya negatif) yüklüdür."
                        b1 = "• Fikir: Yörüngeye, üzeri tamamen zıt elektrik yüküyle (örneğin tamamen negatif) kaplanmış,"
                        b1_sub = "  devasa ama ultra hafif, şişirilebilir bir balon fırlatmak."
                        b2_1 = "• Nasıl Çalışır? Tıpkı kazağımıza sürttüğümüz balonun saçımızı veya küçük kağıt parçalarını kendine"
                        b2_2 = "  çekmesi gibi, bu dev balon da yörüngedeki küçük metal ve boya tozlarını elektromanyetik olarak üstüne çeker."
                        b2_3 = "  Balon çöple dolup ağırlaştıkça yavaşlar ve kendini atmosfere bırakarak çöplerle birlikte yanar."
                        b3_1 = "• Neden Basit ve Özgün? Yakalamak için robotik kollara, kameralara veya yakıta gerek yoktur."
                        b3_2 = "  Sadece fiziksel çekim gücünü kullanır."

                        curr_y = ty + 215 + sy
                        surface.blit(font_tiny.render(p1, True, LIGHT_GRAY), (tx + 38, curr_y))
                        curr_y += 18
                        surface.blit(font_tiny.render(p2, True, LIGHT_GRAY), (tx + 38, curr_y))
                        curr_y += 24
                        
                        surface.blit(font_tiny.render(b1, True, YELLOW), (tx + 38, curr_y))
                        curr_y += 18
                        surface.blit(font_tiny.render(b1_sub, True, LIGHT_GRAY), (tx + 38, curr_y))
                        curr_y += 24

                        surface.blit(font_tiny.render(b2_1, True, CYAN), (tx + 38, curr_y))
                        curr_y += 18
                        surface.blit(font_tiny.render(b2_2, True, LIGHT_GRAY), (tx + 38, curr_y))
                        curr_y += 18
                        surface.blit(font_tiny.render(b2_3, True, GREEN), (tx + 38, curr_y))
                        curr_y += 24

                        surface.blit(font_tiny.render(b3_1, True, ORANGE), (tx + 38, curr_y))
                        curr_y += 18
                        surface.blit(font_tiny.render(b3_2, True, LIGHT_GRAY), (tx + 38, curr_y))

                        surface.set_clip(old_c)

                    elif self.current_web_url == "http://nasa.gov/orbital-debris":
                        nasa_h = font_medium.render("NASA ORBITAL DEBRIS PROGRAM OFFICE", True, CYAN)
                        surface.blit(nasa_h, (tx + 30, ty + 110))
                        
                        line_div = pygame.Rect(tx + 30, ty + 138, tw - 60, 2)
                        pygame.draw.rect(surface, CYAN, line_div)

                        deb_count_str = f"TAHMİNİ AKTİF MİKRO-ÇÖP: {self.archimedes_sim.total_orbital_debris:,} ADET"
                        surface.blit(font_small.render(deb_count_str, True, ALERT_RED), (tx + 30, ty + 150))

                        info1 = "Dünya yörüngesinde 1 cm'den büyük 500.000'den fazla insan yapımı çöp bulunmaktadır."
                        info2 = "Bu parçalar 28.000 km/s hıza ulaşarak uzay istasyonlarına ve uydulara büyük tehdit oluşturur."
                        info3 = "UGGKF Projesi, Arşimet Aynaları ile bu çöpleri yörüngede buharlaştırarak yok etmeyi hedefler."

                        surface.blit(font_tiny.render(info1, True, WHITE), (tx + 30, ty + 190))
                        surface.blit(font_tiny.render(info2, True, WHITE), (tx + 30, ty + 215))
                        surface.blit(font_tiny.render(info3, True, GREEN), (tx + 30, ty + 240))

                        stat_card = pygame.Rect(tx + 30, ty + 280, tw - 60, 110)
                        pygame.draw.rect(surface, (10, 20, 35), stat_card)
                        pygame.draw.rect(surface, DIM_GREEN, stat_card, 1)

                        surface.blit(font_small.render("KİRLİLİK İSTATİSTİKLERİ VE TEHDİT ANOMALİSİ", True, YELLOW), (tx + 45, ty + 292))
                        surface.blit(font_tiny.render("• LEO (Alçak Dünya Yörüngesi): %68 Yoğunluk (Yüksek Risk)", True, LIGHT_GRAY), (tx + 45, ty + 320))
                        surface.blit(font_tiny.render("• GEO (Yer Eşzamanlı Yörünge): %22 Yoğunluk (Orta Risk)", True, LIGHT_GRAY), (tx + 45, ty + 342))
                        surface.blit(font_tiny.render("• Temizleme İlerlemesi: Proje UGGKF Arşimet Odaklayıcısı Aktif", True, GREEN), (tx + 45, ty + 364))

                elif win.content_type == "ekonomi":
                    st = self.economy.last_month_stats
                    
                    pygame.draw.rect(surface, (12, 24, 36), (tx + 15, ty + 38, tw - 30, 65))
                    pygame.draw.rect(surface, DIM_GREEN, (tx + 15, ty + 38, tw - 30, 65), 1)
                    
                    c_txt = font_medium.render(f"İSTASYON KASASI: ${self.economy.total_vault:,.2f}", True, GREEN)
                    m_txt = font_small.render(f"Mevcut Ay: Ay #{self.economy.current_month} | 17 Çöp Temizlenince Yeni Aya Geçilir", True, CYAN)
                    fin_txt = font_tiny.render(f"Aylık Gelir: ${st['revenue']:,.0f} (+${st['added_revenue']:,.0f} Kadro Katkısı) | Giderler: ${st['expenses']:,.0f} | Net Kâr: ${st['net']:,.0f}", True, WHITE)
                    
                    surface.blit(c_txt, (tx + 25, ty + 44))
                    surface.blit(m_txt, (tx + 25, ty + 68))
                    surface.blit(fin_txt, (tx + 25, ty + 86))

                    hired_count = len(st["staff"])
                    unhired_count = sum(1 for p in self.economy.personnel if not p["is_hired"])
                    
                    tab_hired_rect = pygame.Rect(tx + 15, ty + 108, 220, 32)
                    tab_market_rect = pygame.Rect(tx + 245, ty + 108, 380, 32)
                    
                    is_t1 = (self.economy_tab == "hired")
                    pygame.draw.rect(surface, (20, 50, 75) if is_t1 else (10, 20, 30), tab_hired_rect, border_top_left_radius=6, border_top_right_radius=6)
                    pygame.draw.rect(surface, CYAN if is_t1 else GRAY, tab_hired_rect, 2, border_top_left_radius=6, border_top_right_radius=6)
                    t1_txt = font_tiny.render(f"👥 AKTİF KADRO ({hired_count}/7)", True, WHITE if is_t1 else LIGHT_GRAY)
                    surface.blit(t1_txt, (tx + 30, ty + 116))

                    is_t2 = (self.economy_tab == "market")
                    pygame.draw.rect(surface, (20, 50, 75) if is_t2 else (10, 20, 30), tab_market_rect, border_top_left_radius=6, border_top_right_radius=6)
                    pygame.draw.rect(surface, CYAN if is_t2 else GRAY, tab_market_rect, 2, border_top_left_radius=6, border_top_right_radius=6)
                    t2_txt = font_tiny.render(f"🛒 PERSONEL MAĞAZASI / İŞE AL ({unhired_count} ALINABİLİR)", True, YELLOW if is_t2 else LIGHT_GRAY)
                    surface.blit(t2_txt, (tx + 260, ty + 116))

                    if self.economy_msg and (time.time() - self.economy_msg_time < 3.0):
                        msg_surf = font_tiny.render(self.economy_msg, True, YELLOW)
                        surface.blit(msg_surf, (tx + 635, ty + 116))

                    tb_hdr_y = ty + 144
                    pygame.draw.rect(surface, (20, 40, 60), (tx + 15, tb_hdr_y, tw - 30, 28))
                    
                    if self.economy_tab == "hired":
                        surface.blit(font_tiny.render("UNVAN / MESLEK", True, CYAN), (tx + 25, tb_hdr_y + 6))
                        surface.blit(font_tiny.render("PERSONEL İSMİ", True, CYAN), (tx + 170, tb_hdr_y + 6))
                        surface.blit(font_tiny.render("MAAŞ", True, CYAN), (tx + 320, tb_hdr_y + 6))
                        surface.blit(font_tiny.render("+GELİR KATKISI", True, GREEN), (tx + 410, tb_hdr_y + 6))
                        surface.blit(font_tiny.render("% KOMİSYON", True, CYAN), (tx + 545, tb_hdr_y + 6))
                        surface.blit(font_tiny.render("MAAŞ ÖDEMESİ", True, CYAN), (tx + 655, tb_hdr_y + 6))
                        
                        row_y = tb_hdr_y + 32
                        if not st["staff"]:
                            no_staff_msg = font_small.render("Henüz kadroda personel yok! 'PERSONEL MAĞAZASI' sekmesinden satın alın.", True, ALERT_RED)
                            surface.blit(no_staff_msg, (tx + tw//2 - no_staff_msg.get_width()//2, row_y + 40))
                        else:
                            for p in st["staff"]:
                                pygame.draw.rect(surface, (10, 18, 26), (tx + 15, row_y, tw - 30, 40))
                                pygame.draw.rect(surface, (25, 45, 65), (tx + 15, row_y, tw - 30, 40), 1)
                                
                                surface.blit(font_tiny.render(p["role"], True, WHITE), (tx + 25, row_y + 12))
                                surface.blit(font_tiny.render(p["name"], True, GREEN), (tx + 170, row_y + 12))
                                surface.blit(font_tiny.render(f"${p['base']:,}", True, LIGHT_GRAY), (tx + 320, row_y + 12))
                                surface.blit(font_tiny.render(f"+%{p['prof_pct']} (+$${p['revenue_contrib']:,.0f})", True, GREEN), (tx + 410, row_y + 12))
                                surface.blit(font_tiny.render(f"%{p['comm_pct']}", True, CYAN), (tx + 545, row_y + 12))
                                surface.blit(font_medium.render(f"${p['total']:,.0f}", True, YELLOW), (tx + 655, row_y + 8))
                                
                                btn_fire = pygame.Rect(tx + tw - 150, row_y + 4, 135, 32)
                                pygame.draw.rect(surface, (80, 20, 20), btn_fire, border_radius=4)
                                pygame.draw.rect(surface, ALERT_RED, btn_fire, 1, border_radius=4)
                                btn_fire_txt = font_tiny.render("İŞTEN ÇIKAR", True, WHITE)
                                surface.blit(btn_fire_txt, (btn_fire.x + 18, btn_fire.y + 8))
                                
                                row_y += 44

                    elif self.economy_tab == "market":
                        surface.blit(font_tiny.render("UNVAN / MESLEK", True, CYAN), (tx + 25, tb_hdr_y + 6))
                        surface.blit(font_tiny.render("PERSONEL İSMİ", True, CYAN), (tx + 170, tb_hdr_y + 6))
                        surface.blit(font_tiny.render("SAĞLADIĞI GELİR KATKISI", True, GREEN), (tx + 320, tb_hdr_y + 6))
                        surface.blit(font_tiny.render("SATIN ALMA FİYATI", True, YELLOW), (tx + 500, tb_hdr_y + 6))
                        surface.blit(font_tiny.render("SATIN AL / İŞE AL", True, GREEN), (tx + 645, tb_hdr_y + 6))
                        
                        row_y = tb_hdr_y + 32
                        for p in self.economy.personnel:
                            pygame.draw.rect(surface, (10, 18, 26), (tx + 15, row_y, tw - 30, 40))
                            pygame.draw.rect(surface, (25, 45, 65), (tx + 15, row_y, tw - 30, 40), 1)
                            
                            rev_boost = self.economy.base_monthly_revenue * (p["profit_pct"] / 100.0)
                            
                            surface.blit(font_tiny.render(p["role"], True, WHITE), (tx + 25, row_y + 12))
                            surface.blit(font_tiny.render(p["name"], True, GREEN if p["is_hired"] else LIGHT_GRAY), (tx + 170, row_y + 12))
                            surface.blit(font_tiny.render(f"+%{p['profit_pct']} (+$${rev_boost:,.0f}/ay)", True, GREEN), (tx + 320, row_y + 12))
                            surface.blit(font_medium.render(f"${p['hire_cost']:,}", True, YELLOW), (tx + 500, row_y + 8))
                            
                            btn_buy = pygame.Rect(tx + tw - 200, row_y + 4, 185, 34)
                            if p["is_hired"]:
                                pygame.draw.rect(surface, (20, 40, 30), btn_buy, border_radius=4)
                                pygame.draw.rect(surface, DIM_GREEN, btn_buy, 1, border_radius=4)
                                btn_t = font_tiny.render("✓ SATIN ALINDI", True, DIM_GREEN)
                                surface.blit(btn_t, (btn_buy.x + 25, btn_buy.y + 9))
                            else:
                                can_afford = (self.economy.total_vault >= p["hire_cost"])
                                bg_c = (20, 80, 40) if can_afford else (70, 20, 20)
                                border_c = GREEN if can_afford else ALERT_RED
                                text_c = WHITE if can_afford else ALERT_RED
                                
                                pygame.draw.rect(surface, bg_c, btn_buy, border_radius=4)
                                pygame.draw.rect(surface, border_c, btn_buy, 1, border_radius=4)
                                
                                label = f"🛒 İŞE AL (${p['hire_cost']//1000}K)" if can_afford else "❌ YETERSIZ BAKİYE"
                                btn_t = font_tiny.render(label, True, text_c)
                                surface.blit(btn_t, (btn_buy.x + 12, btn_buy.y + 9))
                                
                            row_y += 44

                elif win.content_type == "bilgiler":
                    left_panel = pygame.Rect(tx + 15, ty + 38, 180, th - 52)
                    pygame.draw.rect(surface, (12, 18, 28), left_panel)
                    pygame.draw.rect(surface, DIM_GREEN, left_panel, 1)

                    file_item_y = ty + 45
                    for docname in self.doc_files:
                        is_sel = (self.selected_doc_file == docname)
                        item_box = pygame.Rect(tx + 20, file_item_y, 170, 30)
                        pygame.draw.rect(surface, (25, 45, 65) if is_sel else (15, 25, 35), item_box, border_radius=3)
                        pygame.draw.rect(surface, CYAN if is_sel else GRAY, item_box, 1, border_radius=3)
                        
                        f_text = font_tiny.render(docname, True, WHITE if is_sel else LIGHT_GRAY)
                        surface.blit(f_text, (tx + 30, file_item_y + 7))
                        file_item_y += 35

                    right_panel = pygame.Rect(tx + 205, ty + 38, tw - 220, th - 52)
                    pygame.draw.rect(surface, (4, 8, 14), right_panel)
                    pygame.draw.rect(surface, DIM_GREEN, right_panel, 1)

                    if self.selected_doc_file:
                        file_path = os.path.join(self.docs_dir, self.selected_doc_file)
                        if os.path.exists(file_path):
                            try:
                                with open(file_path, "r", encoding="utf-8") as f:
                                    lines = f.readlines()
                            except:
                                lines = ["Dosya okunamadı!"]
                        else:
                            lines = ["Dosya bulunamadı."]

                        # Maksimum satır genişliği ve satır sayısı hesabı
                        max_line_width = 0
                        for l in lines:
                            w = font_tiny.size(l.rstrip("\n"))[0]
                            if w > max_line_width:
                                max_line_width = w

                        panel_content_w = right_panel.width - 30
                        min_x_scroll = min(0, panel_content_w - max_line_width)
                        self.doc_scroll_x = max(min_x_scroll, min(0, self.doc_scroll_x))

                        total_text_h = len(lines) * 20
                        panel_content_h = right_panel.height - 25
                        min_y_scroll = min(0, panel_content_h - total_text_h)
                        self.doc_scroll_y = max(min_y_scroll, min(0, self.doc_scroll_y))

                        old_c = surface.get_clip()
                        surface.set_clip(right_panel)

                        text_y = ty + 48 + self.doc_scroll_y
                        for line in lines:
                            line_str = line.rstrip("\n")
                            line_surf = font_tiny.render(line_str, True, GREEN if line_str.startswith("PROJE:") else WHITE)
                            surface.blit(line_surf, (tx + 215 + self.doc_scroll_x, text_y))
                            text_y += 20

                        # Yönlendirme İpucu ve Scroll Göstergesi
                        if max_line_width > panel_content_w:
                            sb_w = max(30, int(panel_content_w * (panel_content_w / max_line_width)))
                            scroll_ratio = 0 if min_x_scroll == 0 else (self.doc_scroll_x / min_x_scroll)
                            sb_x = tx + 215 + int(scroll_ratio * (panel_content_w - sb_w))
                            pygame.draw.rect(surface, (15, 30, 45), (tx + 210, ty + th - 20, tw - 230, 10), border_radius=4)
                            pygame.draw.rect(surface, CYAN, (sb_x, ty + th - 20, sb_w, 10), border_radius=4)
                            
                            hint_txt = font_tiny.render("↔ Kaydırmak için Yön Tuşları (← →) veya Shift+Sürükle/Tekerlek kullanın", True, YELLOW)
                            surface.blit(hint_txt, (tx + tw - hint_txt.get_width() - 25, ty + th - 36))

                        surface.set_clip(old_c)

                elif win.content_type == "balloon_trap":
                    if self.balloon_unlocked and self.balloon_sim:
                        self.balloon_sim.rect = win.rect
                        self.balloon_sim.update()
                        self.balloon_sim.draw(surface)
                    else:
                        err_t1 = font_medium.render("❌ UYGULAMA YÜKLENEMEDİ!", True, ALERT_RED)
                        err_t2 = font_small.render("'Balloon.exe' henüz Web Mağazasından satın alınmadı.", True, WHITE)
                        err_t3 = font_tiny.render("Web Tarayıcısı (Web.exe) -> Software Shop üzerinden $140,000'e satın alın.", True, YELLOW)
                        
                        surface.blit(err_t1, (tx + tw//2 - err_t1.get_width()//2, ty + th//2 - 40))
                        surface.blit(err_t2, (tx + tw//2 - err_t2.get_width()//2, ty + th//2 + 5))
                        surface.blit(err_t3, (tx + tw//2 - err_t3.get_width()//2, ty + th//2 + 35))

# Ana Oyun Döngüsü
def main():
    clock = pygame.time.Clock()
    pygame.mouse.set_visible(False)
    
    intro = IntroIntroSequence()
    desktop = DesktopOS()
    
    game_state = "INTRO"

    running = True
    while running:
        dt = clock.tick(60)
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game_state == "INTRO":
                        game_state = "DESKTOP"
                    else:
                        running = False

            if game_state == "DESKTOP":
                desktop.handle_event(event)

        if game_state == "INTRO":
            intro.update()
            if intro.state == "COMPLETED":
                game_state = "DESKTOP"

        if game_state == "INTRO":
            intro.draw(screen)
        elif game_state == "DESKTOP":
            desktop.draw(screen)

        draw_crt_overlay(screen)
        draw_custom_cursor(screen, mouse_pos)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()