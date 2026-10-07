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
                        
                        # Ürün 1: AI Auto-Aim
                        b1 = pygame.Rect(wx + ww - 180, wy + 172 + sy, 140, 34)
                        if b1.collidepoint(mouse_pos) and not self.archimedes_sim.auto_ai_unlocked:
                            if self.economy.total_vault >= 150000:
                                self.economy.total_vault -= 150000
                                self.archimedes_sim.auto_ai_unlocked = True
                                self.install_app("AutoAim.exe", "auto_ai", "YAPAY ZEKA OTO-ODAKLAYICI [AutoAim.exe]")
                                self.web_msg = "AutoAim.exe Yüklendi! Masaüstüne Eklendi."
                                self.web_msg_time = time.time()
                                if enter_sound: enter_sound.play()
                            else:
                                self.web_msg = "Yetersiz Bakiye! Gereken: $150,000"
                                self.web_msg_time = time.time()

                        # Ürün 2: Focus Multiplier
                        b2 = pygame.Rect(wx + ww - 180, wy + 262 + sy, 140, 34)
                        if b2.collidepoint(mouse_pos) and self.archimedes_sim.damage_multiplier < 1.5:
                            if self.economy.total_vault >= 90000:
                                self.economy.total_vault -= 90000
                                self.archimedes_sim.damage_multiplier = 1.5
                                self.install_app("LaserPower.exe", "laser_power", "LAZER GÜÇ OPTİMİZATÖRÜ [LaserPower.exe]")
                                self.web_msg = "LaserPower.exe Yüklendi! Masaüstüne Eklendi."
                                self.web_msg_time = time.time()
                                if enter_sound: enter_sound.play()
                            else:
                                self.web_msg = "Yetersiz Bakiye! Gereken: $90,000"
                                self.web_msg_time = time.time()

                        # Ürün 3: Auto Clean Drones
                        b3 = pygame.Rect(wx + ww - 180, wy + 352 + sy, 140, 34)
                        if b3.collidepoint(mouse_pos) and not self.archimedes_sim.auto_drone_unlocked:
                            if self.economy.total_vault >= 250000:
                                self.economy.total_vault -= 250000
                                self.archimedes_sim.auto_drone_unlocked = True
                                self.install_app("DroneCtrl.exe", "drone_ctrl", "YÖRÜNGE DRON KONTROL MERKEZİ [DroneCtrl.exe]")
                                self.web_msg = "DroneCtrl.exe Yüklendi! Masaüstüne Eklendi."
                                self.web_msg_time = time.time()
                                if enter_sound: enter_sound.play()
                            else:
                                self.web_msg = "Yetersiz Bakiye! Gereken: $250,000"
                                self.web_msg_time = time.time()

                        # Ürün 4: Statik Balon Kapanı
                        b4 = pygame.Rect(wx + ww - 180, wy + 442 + sy, 140, 34)
                        if b4.collidepoint(mouse_pos) and not self.archimedes_sim.static_balloon_unlocked:
                            if self.economy.total_vault >= 180000:
                                self.economy.total_vault -= 180000
                                self.archimedes_sim.static_balloon_unlocked = True
                                self.install_app("Balloon.exe", "balloon_trap", "STATİK BALON KAPAN YÖNETİMİ [Balloon.exe]")
                                self.web_msg = "Balloon.exe Yüklendi! Masaüstüne Eklendi."
                                self.web_msg_time = time.time()
                                if enter_sound: enter_sound.play()
                            else:
                                self.web_msg = "Yetersiz Bakiye! Gereken: $180,000"
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

                        header_s = font_medium.render("UGGKF ISTASYON YAZILIM MAĞAZASI", True, YELLOW)
                        surface.blit(header_s, (tx + 30, ty + 110 + sy))
                        
                        sub_s = font_tiny.render("Arşimet Güneş Odaklayıcı ve İstasyon için Gelişmiş Yazılım Yükseltmeleri", True, LIGHT_GRAY)
                        surface.blit(sub_s, (tx + 30, ty + 135 + sy))

                        # Ürün 1: AI Auto Aim
                        item1_box = pygame.Rect(tx + 25, ty + 160 + sy, tw - 50, 75)
                        pygame.draw.rect(surface, (12, 22, 34), item1_box, border_radius=4)
                        pygame.draw.rect(surface, CYAN if self.archimedes_sim.auto_ai_unlocked else GRAY, item1_box, 1, border_radius=4)
                        
                        surface.blit(font_small.render("1. Yapay Zeka Otomatik Odaklayıcı Modülü (Auto-Aim AI)", True, WHITE), (tx + 35, ty + 168 + sy))
                        surface.blit(font_tiny.render("Aynaların açı ve yükseklik ayarını uzay çöplerine otomatik kilitler.", True, LIGHT_GRAY), (tx + 35, ty + 192 + sy))
                        
                        btn1 = pygame.Rect(tx + tw - 180, ty + 172 + sy, 140, 34)
                        if self.archimedes_sim.auto_ai_unlocked:
                            pygame.draw.rect(surface, (20, 50, 30), btn1, border_radius=4)
                            surface.blit(font_tiny.render("✓ YÜKLENDİ", True, GREEN), (btn1.x + 25, btn1.y + 9))
                        else:
                            can_aff = self.economy.total_vault >= 150000
                            pygame.draw.rect(surface, (20, 80, 40) if can_aff else (60, 20, 20), btn1, border_radius=4)
                            surface.blit(font_tiny.render("SATIN AL ($150K)", True, WHITE), (btn1.x + 12, btn1.y + 9))

                        # Ürün 2: Focus Multiplier
                        item2_box = pygame.Rect(tx + 25, ty + 250 + sy, tw - 50, 75)
                        pygame.draw.rect(surface, (12, 22, 34), item2_box, border_radius=4)
                        pygame.draw.rect(surface, CYAN if self.archimedes_sim.damage_multiplier > 1.0 else GRAY, item2_box, 1, border_radius=4)
                        
                        surface.blit(font_small.render("2. Lazer Odaklama & Güç Çarpanı (+%50 Hasar)", True, WHITE), (tx + 35, ty + 258 + sy))
                        surface.blit(font_tiny.render("Güneş ışınlarını sıkıştırarak çöp imha hızını %50 artırır.", True, LIGHT_GRAY), (tx + 35, ty + 282 + sy))
                        
                        btn2 = pygame.Rect(tx + tw - 180, ty + 262 + sy, 140, 34)
                        if self.archimedes_sim.damage_multiplier > 1.0:
                            pygame.draw.rect(surface, (20, 50, 30), btn2, border_radius=4)
                            surface.blit(font_tiny.render("✓ YÜKLENDİ", True, GREEN), (btn2.x + 25, btn2.y + 9))
                        else:
                            can_aff = self.economy.total_vault >= 90000
                            pygame.draw.rect(surface, (20, 80, 40) if can_aff else (60, 20, 20), btn2, border_radius=4)
                            surface.blit(font_tiny.render("SATIN AL ($90K)", True, WHITE), (btn2.x + 16, btn2.y + 9))

                        # Ürün 3: Auto Drone System
                        item3_box = pygame.Rect(tx + 25, ty + 340 + sy, tw - 50, 75)
                        pygame.draw.rect(surface, (12, 22, 34), item3_box, border_radius=4)
                        pygame.draw.rect(surface, CYAN if self.archimedes_sim.auto_drone_unlocked else GRAY, item3_box, 1, border_radius=4)
                        
                        surface.blit(font_small.render("3. Otomatik Temizlik Dronu Filosu (Auto-Drone)", True, WHITE), (tx + 35, ty + 348 + sy))
                        surface.blit(font_tiny.render("Her 10 saniyede bir yörüngedeki 1 uzay çöpünü otonom yok eder.", True, LIGHT_GRAY), (tx + 35, ty + 372 + sy))
                        
                        btn3 = pygame.Rect(tx + tw - 180, ty + 352 + sy, 140, 34)
                        if self.archimedes_sim.auto_drone_unlocked:
                            pygame.draw.rect(surface, (20, 50, 30), btn3, border_radius=4)
                            surface.blit(font_tiny.render("✓ YÜKLENDİ", True, GREEN), (btn3.x + 25, btn3.y + 9))
                        else:
                            can_aff = self.economy.total_vault >= 250000
                            pygame.draw.rect(surface, (20, 80, 40) if can_aff else (60, 20, 20), btn3, border_radius=4)
                            surface.blit(font_tiny.render("SATIN AL ($250K)", True, WHITE), (btn3.x + 12, btn3.y + 9))

                        # Ürün 4: Statik Balon Kapanı
                        item4_box = pygame.Rect(tx + 25, ty + 430 + sy, tw - 50, 80)
                        pygame.draw.rect(surface, (12, 22, 34), item4_box, border_radius=4)
                        pygame.draw.rect(surface, CYAN if self.archimedes_sim.static_balloon_unlocked else GRAY, item4_box, 1, border_radius=4)
                        
                        surface.blit(font_small.render("4. \"Statik Balon\" Kapanı (Elektrostatik Çöp Toplayıcı)", True, WHITE), (tx + 35, ty + 438 + sy))
                        surface.blit(font_tiny.render("Statik yüklü dev balon ile mikro çöpleri çeker, atmosfere girip yakar.", True, LIGHT_GRAY), (tx + 35, ty + 460 + sy))
                        
                        btn4 = pygame.Rect(tx + tw - 180, ty + 442 + sy, 140, 34)
                        if self.archimedes_sim.static_balloon_unlocked:
                            pygame.draw.rect(surface, (20, 50, 30), btn4, border_radius=4)
                            surface.blit(font_tiny.render("✓ YÜKLENDİ", True, GREEN), (btn4.x + 25, btn4.y + 9))
                        else:
                            can_aff = self.economy.total_vault >= 180000
                            pygame.draw.rect(surface, (20, 80, 40) if can_aff else (60, 20, 20), btn4, border_radius=4)
                            surface.blit(font_tiny.render("SATIN AL ($180K)", True, WHITE), (btn4.x + 12, btn4.y + 9))

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

                        old_c = surface.get_clip()
                        surface.set_clip(right_panel)

                        text_y = ty + 48 + self.doc_scroll_y
                        for line in lines:
                            line_str = line.rstrip("\n")
                            line_surf = font_tiny.render(line_str, True, GREEN if line_str.startswith("PROJE:") else WHITE)
                            surface.blit(line_surf, (tx + 215, text_y))
                            text_y += 20

                        surface.set_clip(old_c)

                elif win.content_type == "auto_ai":
                    h_surf = font_medium.render("🤖 YAPAY ZEKA OTOMATİK ODAKLAYICI (AutoAim.exe)", True, CYAN)
                    surface.blit(h_surf, (tx + 25, ty + 45))
                    pygame.draw.line(surface, DIM_GREEN, (tx + 25, ty + 75), (tx + tw - 25, ty + 75))
                    
                    st_t = font_small.render("SİSTEM DURUMU: AKTİF & YÖRÜNGEYE KİLİTLENMİŞ", True, GREEN)
                    surface.blit(st_t, (tx + 25, ty + 90))
                    
                    desc1 = font_tiny.render("• Arşimet aynaları uzay çöplerine otomatik kilitlenir.", True, WHITE)
                    desc2 = font_tiny.render("• Manuel açı ve yükseklik ayarı yapmadan çöpleri tam merkezden vurur.", True, LIGHT_GRAY)
                    desc3 = font_tiny.render("• Kilitlenme Hassasiyeti: %100 | Otomatik Takip: DEVREDE", True, YELLOW)
                    surface.blit(desc1, (tx + 25, ty + 125))
                    surface.blit(desc2, (tx + 25, ty + 150))
                    surface.blit(desc3, (tx + 25, ty + 175))

                    radar_box = pygame.Rect(tx + 25, ty + 210, tw - 50, 240)
                    pygame.draw.rect(surface, (8, 16, 26), radar_box, border_radius=6)
                    pygame.draw.rect(surface, CYAN, radar_box, 1, border_radius=6)
                    
                    rcx, rcy = radar_box.centerx, radar_box.centery
                    pygame.draw.circle(surface, (15, 40, 50), (rcx, rcy), 90, 1)
                    pygame.draw.circle(surface, (15, 60, 70), (rcx, rcy), 60, 1)
                    pygame.draw.circle(surface, (15, 80, 90), (rcx, rcy), 30, 1)
                    
                    sweep_angle = (time.time() * 3) % (2 * math.pi)
                    sx = rcx + int(math.cos(sweep_angle) * 90)
                    sy = rcy + int(math.sin(sweep_angle) * 90)
                    pygame.draw.line(surface, GREEN, (rcx, rcy), (sx, sy), 2)
                    pygame.draw.circle(surface, GREEN, (rcx + 35, rcy - 20), 5)
                    surface.blit(font_tiny.render("HEDEF KİLİTLENDİ [CH-09]", True, GREEN), (rcx + 45, rcy - 25))

                elif win.content_type == "laser_power":
                    h_surf = font_medium.render("⚡ LAZER GÜÇ OPTİMİZATÖRÜ (LaserPower.exe)", True, ORANGE)
                    surface.blit(h_surf, (tx + 25, ty + 45))
                    pygame.draw.line(surface, DIM_GREEN, (tx + 25, ty + 75), (tx + tw - 25, ty + 75))
                    
                    st_t = font_small.render("LAZER GÜÇ ÇARPANI: 1.5x (+%50 EKSTRA HASAR)", True, GREEN)
                    surface.blit(st_t, (tx + 25, ty + 90))
                    
                    desc1 = font_tiny.render("• Güneş ışınlarını sıkıştırarak termal imha hızını %50 artırır.", True, WHITE)
                    desc2 = font_tiny.render("• Çöp imha süresi yarıya iner, enerji verimliliği artar.", True, LIGHT_GRAY)
                    surface.blit(desc1, (tx + 25, ty + 125))
                    surface.blit(desc2, (tx + 25, ty + 150))

                    gauge_box = pygame.Rect(tx + 25, ty + 190, tw - 50, 240)
                    pygame.draw.rect(surface, (18, 12, 8), gauge_box, border_radius=6)
                    pygame.draw.rect(surface, ORANGE, gauge_box, 1, border_radius=6)
                    
                    p_bar = pygame.Rect(tx + 50, ty + 250, tw - 100, 30)
                    pygame.draw.rect(surface, (40, 20, 10), p_bar, border_radius=4)
                    fill_w = int((tw - 100) * (1.5 / 2.0))
                    pygame.draw.rect(surface, ORANGE, (p_bar.x, p_bar.y, fill_w, 30), border_radius=4)
                    surface.blit(font_medium.render("GÜÇ KAPASİTESİ: %150", True, WHITE), (p_bar.x + 10, p_bar.y + 4))

                elif win.content_type == "drone_ctrl":
                    h_surf = font_medium.render("🛸 OTONOM DRON FİLOSU (DroneCtrl.exe)", True, GREEN)
                    surface.blit(h_surf, (tx + 25, ty + 45))
                    pygame.draw.line(surface, DIM_GREEN, (tx + 25, ty + 75), (tx + tw - 25, ty + 75))
                    
                    st_t = font_small.render("FİLO DURUMU: OTONOM DEVRİYE AKTİF (4 DRON)", True, GREEN)
                    surface.blit(st_t, (tx + 25, ty + 90))
                    
                    desc1 = font_tiny.render("• Her 10 saniyede bir yörüngedeki 1 uzay çöpünü otonom yok eder.", True, WHITE)
                    desc2 = font_tiny.render("• İstasyon bütçesine ve kirlilik hedefine otonom katkı sağlar.", True, LIGHT_GRAY)
                    surface.blit(desc1, (tx + 25, ty + 125))
                    surface.blit(desc2, (tx + 25, ty + 150))

                    d_box = pygame.Rect(tx + 25, ty + 190, tw - 50, 240)
                    pygame.draw.rect(surface, (8, 20, 14), d_box, border_radius=6)
                    pygame.draw.rect(surface, GREEN, d_box, 1, border_radius=6)
                    
                    rem_time = max(0, 10.0 - (time.time() - self.archimedes_sim.last_drone_time))
                    surface.blit(font_medium.render(f"SONRAKİ OTONOM TARAMA: {rem_time:.1f} s", True, YELLOW), (tx + 45, ty + 230))
                    surface.blit(font_small.render("• Dron 1: Devriyede [Sektör Alpha]", True, LIGHT_GRAY), (tx + 45, ty + 270))
                    surface.blit(font_small.render("• Dron 2: Devriyede [Sektör Beta]", True, LIGHT_GRAY), (tx + 45, ty + 300))
                    surface.blit(font_small.render("• Dron 3: Şarj Oluyor [Sektör Gamma]", True, LIGHT_GRAY), (tx + 45, ty + 330))
                    surface.blit(font_small.render("• Dron 4: Devriyede [Sektör Delta]", True, LIGHT_GRAY), (tx + 45, ty + 360))

                elif win.content_type == "balloon_trap":
                    h_surf = font_medium.render("🎈 STATİK BALON KAPAN YÖNETİMİ (Balloon.exe)", True, PURPLE)
                    surface.blit(h_surf, (tx + 25, ty + 45))
                    pygame.draw.line(surface, DIM_GREEN, (tx + 25, ty + 75), (tx + tw - 25, ty + 75))
                    
                    st_t = font_small.render("KAPAN DURUMU: ELEKTROSTATİK ALAN AKTİF", True, GREEN)
                    surface.blit(st_t, (tx + 25, ty + 90))
                    
                    desc1 = font_tiny.render("• Elektrostatik dev balon mikro çöpleri çekerek atmosfere sürükler.", True, WHITE)
                    desc2 = font_tiny.render("• Her 15 saniyede bir mikro çöpler atmosfere girip sürtünmeyle yanar.", True, LIGHT_GRAY)
                    surface.blit(desc1, (tx + 25, ty + 125))
                    surface.blit(desc2, (tx + 25, ty + 150))

                    b_box = pygame.Rect(tx + 25, ty + 190, tw - 50, 240)
                    pygame.draw.rect(surface, (18, 10, 24), b_box, border_radius=6)
                    pygame.draw.rect(surface, PURPLE, b_box, 1, border_radius=6)
                    
                    rem_time_b = max(0, 15.0 - (time.time() - self.archimedes_sim.last_balloon_time))
                    surface.blit(font_medium.render(f"ATMOSFERİK TEMİZLİK DÖNGÜSÜ: {rem_time_b:.1f} s", True, YELLOW), (tx + 45, ty + 230))
                    surface.blit(font_small.render("• Statik Yük Potansiyeli: +15,000 V", True, LIGHT_GRAY), (tx + 45, ty + 270))
                    surface.blit(font_small.render("• Çap: 120 Metre (Kevlar Mylar Filmi)", True, LIGHT_GRAY), (tx + 45, ty + 300))
                    surface.blit(font_small.render("• Çekilen Mikro Parçacık Sayısı: 1,420 Adet/Ay", True, LIGHT_GRAY), (tx + 45, ty + 330))

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