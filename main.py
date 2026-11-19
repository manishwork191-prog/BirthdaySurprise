 import random
from datetime import datetime
from kivy.app import App
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Line, Rectangle, RoundedRectangle
from kivy.metrics import dp
from kivy.properties import NumericProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.screenmanager import FadeTransition, Screen, ScreenManager
from kivy.uix.scrollview import ScrollView
from kivy.uix.stencilview import StencilView
from kivy.uix.widget import Widget
from kivy.utils import platform

# ==============================================================================
# CUSTOMIZATION SECTION (आप यहां अपने मैसेज बदल सकते हैं)
# ==============================================================================
TARGET_DATE = datetime(2026, 12, 23, 0, 0, 0)  # 23 December 2026, 12:00 AM

APP_TITLE = "Birthday Surprise ❤️"
GIRLFRIEND_NAME = "My Love"

MAIN_BIRTHDAY_LETTER = (
    f"Happy Birthday, {GIRLFRIEND_NAME}! ❤️\n\n"
    "Tumhari muskurahat meri har thakan mita deti hai. Aaj ka din sirf tumhara hai—"
    "khush raho, hamesha muskurati raho, aur yaad rakhna ki main hamesha tumhare saath hoon.\n\n"
    "Happy Birthday once again, meri jaan! ❤️"
)

PHOTO_CAPTIONS = [
    "✨ Every moment with you feels like magic",
    "🌙 My favorite smile in the whole world",
    "❤️ Today, tomorrow, and forever with you",
]

SECRET_GIFT_TEXT = (
    "🎁 Your Special Birthday Gift:\n\n"
    "Aaj humari special birthday date hai! Ready rehna, "
    "aur apna haath se likha love letter lena mat bhoolna ❤️"
)

PHOTO_FILES = [
    "assets/photo1.jpg",
    "assets/photo2.jpg",
    "assets/photo3.jpg",
]
MUSIC_FILE = "assets/music.mp3"   # Happy Birthday To You background music
VOICE_FILE = "assets/voice.mp3"   # Aapka personal voice note
# ==============================================================================


def schedule_birthday_notification():
    """Android par 23 Dec 2026 ko exact time par notification schedule karta hai."""
    if platform != "android":
        return
    try:
        from jnius import autoclass
        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        Context = autoclass("android.content.Context")
        Intent = autoclass("android.content.Intent")
        PendingIntent = autoclass("android.app.PendingIntent")
        AlarmManager = autoclass("android.app.AlarmManager")
        NotificationChannel = autoclass("android.app.NotificationChannel")
        NotificationManager = autoclass("android.app.NotificationManager")
        NotificationBuilder = autoclass("android.app.Notification$Builder")
        BuildVersion = autoclass("android.os.Build$VERSION")

        context = PythonActivity.mActivity
        channel_id = "birthday_surprise_channel"

        # Android 8+ ke liye Notification Channel banayein
        if BuildVersion.SDK_INT >= 26:
            nm = context.getSystemService(Context.NOTIFICATION_SERVICE)
            channel = NotificationChannel(
                channel_id,
                "Birthday Surprise Alerts",
                NotificationManager.IMPORTANCE_HIGH,
            )
            nm.createNotificationChannel(channel)

        # Target timestamp in milliseconds
        target_ms = int(TARGET_DATE.timestamp() * 1000)
        now_ms = int(datetime.now().timestamp() * 1000)
        if target_ms <= now_ms:
            return

        # App open karne ka intent
        launch_intent = context.getPackageManager().getLaunchIntentForPackage(context.getPackageName())
        flags = PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE
        pending_intent = PendingIntent.getActivity(context, 101, launch_intent, flags)

        # Notification taiyar karein
        if BuildVersion.SDK_INT >= 26:
            builder = NotificationBuilder(context, channel_id)
        else:
            builder = NotificationBuilder(context)

        builder.setContentTitle("🎉 Happy Birthday! ❤️")
        builder.setContentText("The wait is over! Tap to open your Birthday Surprise ✨")
        builder.setSmallIcon(context.getApplicationInfo().icon)
        builder.setContentIntent(pending_intent)
        builder.setAutoCancel(True)

        # Note: Offline reliable wake-up via AlarmManager exact trigger
        alarm_manager = context.getSystemService(Context.ALARM_SERVICE)
        alarm_manager.setExactAndAllowWhileIdle(
            AlarmManager.RTC_WAKEUP, target_ms, pending_intent
        )
    except Exception:
        pass


class HeartParticle:
    def __init__(self, width, height):
        self.reset(width, height, random_y=True)

    def reset(self, width, height, random_y=False):
        self.x = random.uniform(20, max(40, width - 20))
        self.y = random.uniform(0, height) if random_y else -20
        self.size = random.uniform(dp(9), dp(19))
        self.speed = random.uniform(dp(28), dp(68))
        alpha = random.uniform(0.30, 0.78)
        self.color = random.choice([
            (1.0, 0.32, 0.62, alpha),
            (0.84, 0.28, 0.88, alpha),
            (1.0, 0.52, 0.74, alpha),
        ])


class FlowerPetalParticle:
    """Upar se girne wali gulab ki pankhudiyan aur confetti."""
    def __init__(self, width, height):
        self.reset(width, height, random_y=True)

    def reset(self, width, height, random_y=False):
        self.x = random.uniform(0, max(50, width))
        self.y = random.uniform(0, height * 1.2) if random_y else height + random.uniform(10, 60)
        self.w = random.uniform(dp(8), dp(15))
        self.h = random.uniform(dp(12), dp(20))
        self.vy = random.uniform(dp(55), dp(135))
        self.vx = random.uniform(-dp(30), dp(30))
        self.sway_phase = random.uniform(0, 6.28)
        self.is_petal = random.choice([True, True, False])
        if self.is_petal:
            self.color = random.choice([
                (0.96, 0.18, 0.45, 0.88),  # Rose red-pink
                (1.00, 0.42, 0.68, 0.88),  # Soft rose pink
                (0.88, 0.14, 0.38, 0.85),  # Deep rose
            ])
        else:
            self.color = random.choice([
                (1.0, 0.84, 0.30, 0.92),   # Gold sparkle
                (0.75, 0.40, 1.0, 0.90),   # Lavender
            ])


class RomanticBackground(Widget):
    def __init__(self, celebration_mode=False, **kwargs):
        super().__init__(**kwargs)
        self.celebration_mode = celebration_mode
        self.hearts = [HeartParticle(400, 800) for _ in range(22)]
        self.petals = [FlowerPetalParticle(400, 800) for _ in range(42)] if celebration_mode else []
        self.bind(size=self._reinit_particles)
        Clock.schedule_interval(self.update_animation, 1.0 / 30.0)

    def _reinit_particles(self, *args):
        if self.width > 0 and self.height > 0:
            for h in self.hearts:
                h.reset(self.width, self.height, random_y=True)
            for p in self.petals:
                p.reset(self.width, self.height, random_y=True)

    def update_animation(self, dt):
        if self.width <= 0 or self.height <= 0:
            return
        for h in self.hearts:
            h.y += h.speed * dt
            if h.y > self.height + 20:
                h.reset(self.width, self.height, random_y=False)

        for p in self.petals:
            p.sway_phase += dt * 2.5
            p.y -= p.vy * dt
            p.x += (p.vx + dp(18) * (1 if int(p.sway_phase) % 2 == 0 else -1)) * dt
            if p.y < -25:
                p.reset(self.width, self.height, random_y=False)

        self.redraw()

    def redraw(self):
        self.canvas.clear()
        with self.canvas:
            steps = 28
            for i in range(steps):
                t = i / float(steps)
                r = 0.08 + 0.15 * (1 - abs(t - 0.35))
                g = 0.03 + 0.04 * t
                b = 0.13 + 0.17 * (1 - t)
                Color(r, g, b, 1)
                Rectangle(pos=(self.x, self.y + i * (self.height / steps)), size=(self.width, self.height / steps + 1))

            for h in self.hearts:
                Color(*h.color)
                r = h.size * 0.32
                Ellipse(pos=(h.x - r * 1.4, h.y), size=(r * 2, r * 2))
                Ellipse(pos=(h.x - r * 0.2, h.y), size=(r * 2, r * 2))
                Ellipse(pos=(h.x - r * 0.85, h.y - r * 0.9), size=(r * 2.1, r * 2.1))

            for p in self.petals:
                Color(*p.color)
                if p.is_petal:
                    Ellipse(pos=(p.x, p.y), size=(p.w, p.h))
                else:
                    RoundedRectangle(pos=(p.x, p.y), size=(p.w * 0.7, p.h * 0.7), radius=[dp(3)])


class PulsingPadlock(Widget):
    pulse = NumericProperty(0.0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._dir = 1
        Clock.schedule_interval(self._animate, 1.0 / 30.0)
        self.bind(pos=self._draw, size=self._draw, pulse=self._draw)

    def _animate(self, dt):
        self.pulse += dt * 1.6 * self._dir
        if self.pulse >= 1.0:
            self.pulse = 1.0
            self._dir = -1
        elif self.pulse <= 0.0:
            self.pulse = 0.0
            self._dir = 1

    def _draw(self, *args):
        self.canvas.clear()
        cx, cy = self.center_x, self.center_y
        glow_r = dp(46) + dp(8) * self.pulse
        with self.canvas:
            Color(1.0, 0.32, 0.65, 0.18 + 0.12 * self.pulse)
            Ellipse(pos=(cx - glow_r, cy - glow_r), size=(glow_r * 2, glow_r * 2))
            Color(1.0, 0.72, 0.88, 0.95)
            Line(circle=(cx, cy + dp(10), dp(14), -90, 90), width=dp(3.2))
            Color(0.95, 0.30, 0.62, 1.0)
            RoundedRectangle(pos=(cx - dp(20), cy - dp(18)), size=(dp(40), dp(30)), radius=[dp(8)])
            Color(0.10, 0.04, 0.16, 1.0)
            Ellipse(pos=(cx - dp(3.5), cy - dp(5)), size=(dp(7), dp(7)))
            RoundedRectangle(pos=(cx - dp(2), cy - dp(12)), size=(dp(4), dp(9)), radius=[dp(2)])


class AnimatedPhotoSlideshow(StencilView):
    """Smooth Ken Burns Zoom + Crossfade Photo Showcase."""
    def __init__(self, photos, captions, **kwargs):
        super().__init__(**kwargs)
        self.photos = photos
        self.captions = captions
        self.index = 0

        with self.canvas.before:
            Color(1, 1, 1, 0.10)
            self.bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(18)])
        self.bind(pos=self._update_bg, size=self._update_bg)

        self.img = Image(
            source=self.photos[0],
            allow_stretch=True,
            keep_ratio=True,
            size_hint=(None, None),
            opacity=1.0,
        )
        self.caption_lbl = Label(
            text=self.captions[0],
            font_size=dp(13),
            bold=True,
            color=(1, 0.92, 0.96, 0.95),
            size_hint=(None, None),
            height=dp(34),
        )
        self.add_widget(self.img)
        self.add_widget(self.caption_lbl)
        self.bind(pos=self._layout_children, size=self._layout_children)

        Clock.schedule_once(lambda dt: self._start_zoom_animation(), 0.2)
        Clock.schedule_interval(self._next_slide, 4.5)

    def _update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size

    def _layout_children(self, *args):
        self.img.size = (self.width * 0.94, self.height * 0.80)
        self.img.center = (self.center_x, self.center_y + dp(12))
        self.caption_lbl.size = (self.width - dp(20), dp(32))
        self.caption_lbl.pos = (self.x + dp(10), self.y + dp(6))

    def _start_zoom_animation(self):
        base_w, base_h = self.width * 0.94, self.height * 0.80
        self.img.size = (base_w, base_h)
        self.img.center = (self.center_x, self.center_y + dp(12))
        anim = Animation(
            size=(base_w * 1.10, base_h * 1.10),
            center=(self.center_x, self.center_y + dp(12)),
            duration=4.2,
            t="in_out_sine",
        )
        anim.start(self.img)

    def _next_slide(self, dt):
        fade_out = Animation(opacity=0.0, duration=0.45)

        def switch_photo(*args):
            self.index = (self.index + 1) % len(self.photos)
            self.img.source = self.photos[self.index]
            self.caption_lbl.text = self.captions[self.index % len(self.captions)]
            self._start_zoom_animation()
            Animation(opacity=1.0, duration=0.55).start(self.img)

        fade_out.bind(on_complete=switch_photo)
        fade_out.start(self.img)


class CountdownTile(BoxLayout):
    value_text = StringProperty("00")

    def __init__(self, unit, **kwargs):
        super().__init__(orientation="vertical", padding=[dp(6), dp(10)], spacing=dp(2), **kwargs)
        with self.canvas.before:
            Color(1, 1, 1, 0.09)
            self.bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(14)])
            Color(1.0, 0.45, 0.75, 0.35)
            self.border = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, dp(14)), width=1.1)
        self.bind(pos=self._update_rect, size=self._update_rect)

        self.num_lbl = Label(text="00", font_size=dp(28), bold=True, color=(1, 0.88, 0.95, 1))
        self.unit_lbl = Label(text=unit, font_size=dp(10), bold=True, color=(0.95, 0.55, 0.78, 0.9))
        self.add_widget(self.num_lbl)
        self.add_widget(self.unit_lbl)
        self.bind(value_text=lambda inst, val: setattr(self.num_lbl, "text", val))

    def _update_rect(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size
        self.border.rounded_rectangle = (self.x, self.y, self.width, self.height, dp(14))


class LockedScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root = FloatLayout()
        root.add_widget(RomanticBackground(celebration_mode=False))

        content = BoxLayout(orientation="vertical", padding=[dp(22), dp(36), dp(22), dp(32)], spacing=dp(14))
        content.add_widget(Label(text=APP_TITLE, font_size=dp(26), bold=True, color=(1, 0.85, 0.94, 1), size_hint_y=None, height=dp(40)))

        lock_holder = BoxLayout(size_hint_y=None, height=dp(115))
        lock_holder.add_widget(PulsingPadlock())
        content.add_widget(lock_holder)

        headline = Label(
            text="A Special Surprise Is Waiting For You!",
            font_size=dp(20),
            bold=True,
            halign="center",
            valign="middle",
            color=(1, 1, 1, 0.96),
            size_hint_y=None,
            height=dp(56),
        )
        headline.bind(size=lambda inst, val: setattr(inst, "text_size", (val[0], None)))
        content.add_widget(headline)

        content.add_widget(Label(text="Unlocks on 23 December 2026", font_size=dp(13), color=(0.96, 0.62, 0.82, 1), size_hint_y=None, height=dp(26)))

        timer_row = BoxLayout(orientation="horizontal", spacing=dp(10), size_hint_y=None, height=dp(88))
        self.days_tile = CountdownTile("DAYS")
        self.hours_tile = CountdownTile("HOURS")
        self.mins_tile = CountdownTile("MINUTES")
        self.secs_tile = CountdownTile("SECONDS")
        for tile in (self.days_tile, self.hours_tile, self.mins_tile, self.secs_tile):
            timer_row.add_widget(tile)
        content.add_widget(timer_row)

        content.add_widget(Label(text="Counting Every Second For You ❤️", font_size=dp(15), italic=True, color=(1, 0.78, 0.90, 0.95), size_hint_y=None, height=dp(44)))
        content.add_widget(Label(text="🔒 Surprise Content Safely Locked Until Midnight", font_size=dp(12), color=(0.82, 0.72, 0.86, 0.75), size_hint_y=None, height=dp(30)))

        root.add_widget(content)
        self.add_widget(root)

    def update_tiles(self, days, hours, minutes, seconds):
        self.days_tile.value_text = f"{days:02d}"
        self.hours_tile.value_text = f"{hours:02d}"
        self.mins_tile.value_text = f"{minutes:02d}"
        self.secs_tile.value_text = f"{seconds:02d}"


class BirthdaySurpriseScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bg_music = None
        self.voice_note = None
        self.is_muted = False
        self.is_voice_playing = False

        root = FloatLayout()
        root.add_widget(RomanticBackground(celebration_mode=True))

        scroll = ScrollView(do_scroll_x=False)
        self.container = BoxLayout(orientation="vertical", padding=[dp(20), dp(26), dp(20), dp(40)], spacing=dp(15), size_hint_y=None)
        self.container.bind(minimum_height=self.container.setter("height"))

        # Top Bar with Background Music Mute Button
        top_bar = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(40))
        top_bar.add_widget(Label(text="🎉 23 December 2026 🎉", font_size=dp(13), bold=True, color=(1, 0.78, 0.90, 1), halign="left"))
        self.mute_btn = Button(
            text="🎵 Music On",
            size_hint=(None, None),
            size=(dp(105), dp(34)),
            background_normal="",
            background_color=(0.85, 0.25, 0.58, 0.88),
            font_size=dp(12),
            bold=True,
        )
        self.mute_btn.bind(on_release=self.toggle_bg_music)
        top_bar.add_widget(self.mute_btn)
        self.container.add_widget(top_bar)

        # Instant Happy Birthday Header
        self.container.add_widget(
            Label(
                text="Happy Birthday! ❤️",
                font_size=dp(34),
                bold=True,
                color=(1, 0.92, 0.97, 1),
                size_hint_y=None,
                height=dp(52),
            )
        )

        # Voice Note Button (Plays ONLY when clicked!)
        self.voice_btn = Button(
            text="🎙️ Tap To Hear My Voice Message ❤️",
            size_hint_y=None,
            height=dp(52),
            background_normal="",
            background_color=(0.94, 0.24, 0.58, 1),
            font_size=dp(15),
            bold=True,
        )
        self.voice_btn.bind(on_release=self.toggle_voice_note)
        self.container.add_widget(self.voice_btn)

        # Animated Photo Slideshow (Ken Burns Zoom + Fade)
        self.container.add_widget(
            AnimatedPhotoSlideshow(
                photos=PHOTO_FILES,
                captions=PHOTO_CAPTIONS,
                size_hint_y=None,
                height=dp(280),
            )
        )

        # Personalized Birthday Letter
        self.container.add_widget(self._make_card(MAIN_BIRTHDAY_LETTER, height=dp(195)))

        # Surprise Gift Button
        gift_btn = Button(
            text="🎁 Open Your Secret Birthday Gift",
            size_hint_y=None,
            height=dp(52),
            background_normal="",
            background_color=(0.66, 0.24, 0.88, 1),
            font_size=dp(15),
            bold=True,
        )
        gift_btn.bind(on_release=self.open_gift_popup)
        self.container.add_widget(gift_btn)

        scroll.add_widget(self.container)
        root.add_widget(scroll)
        self.add_widget(root)

    def _make_card(self, text, height=dp(150)):
        box = BoxLayout(padding=[dp(16), dp(14)], size_hint_y=None, height=height)
        with box.canvas.before:
            Color(1, 1, 1, 0.11)
            rect = RoundedRectangle(pos=box.pos, size=box.size, radius=[dp(16)])
        box.bind(pos=lambda inst, v: setattr(rect, "pos", v), size=lambda inst, v: setattr(rect, "size", v))
        lbl = Label(text=text, font_size=dp(14), halign="left", valign="middle", color=(1, 0.95, 0.98, 0.96))
        lbl.bind(size=lambda inst, val: setattr(inst, "text_size", (val[0], None)))
        box.add_widget(lbl)
        return box

    def on_enter(self):
        # Unlock hote hi 'Happy Birthday To You' music start karein
        if not self.bg_music:
            try:
                self.bg_music = SoundLoader.load(MUSIC_FILE)
                if self.bg_music:
                    self.bg_music.loop = True
                    self.bg_music.volume = 0.75
                    self.bg_music.play()
            except Exception:
                self.bg_music = None

    def toggle_bg_music(self, *args):
        if not self.bg_music:
            self.mute_btn.text = "🔇 No Music"
            return
        if self.is_muted:
            self.bg_music.volume = 0.20 if self.is_voice_playing else 0.75
            self.mute_btn.text = "🎵 Music On"
            self.is_muted = False
        else:
            self.bg_music.volume = 0.0
            self.mute_btn.text = "🔇 Muted"
            self.is_muted = True

    def toggle_voice_note(self, *args):
        if not self.voice_note:
            try:
                self.voice_note = SoundLoader.load(VOICE_FILE)
                if self.voice_note:
                    self.voice_note.bind(on_stop=self._on_voice_finished)
            except Exception:
                self.voice_note = None

        if not self.voice_note:
            self.voice_btn.text = "⚠️ Voice file not found"
            return

        if self.is_voice_playing:
            self.voice_note.stop()
            self._on_voice_finished()
        else:
            # Voice note bajne par background music dheema karein
            if self.bg_music and not self.is_muted:
                self.bg_music.volume = 0.15
            self.voice_note.volume = 1.0
            self.voice_note.play()
            self.is_voice_playing = True
            self.voice_btn.text = "⏸️ Playing My Voice... (Tap to Stop)"
            self.voice_btn.background_color = (0.75, 0.18, 0.45, 1)

    def _on_voice_finished(self, *args):
        self.is_voice_playing = False
        self.voice_btn.text = "🎙️ Replay My Voice Message ❤️"
        self.voice_btn.background_color = (0.94, 0.24, 0.58, 1)
        if self.bg_music and not self.is_muted:
            self.bg_music.volume = 0.75

    def open_gift_popup(self, *args):
        modal = ModalView(size_hint=(0.86, 0.42), background_color=(0, 0, 0, 0.75))
        card = BoxLayout(orientation="vertical", padding=dp(22), spacing=dp(14))
        with card.canvas.before:
            Color(0.18, 0.06, 0.24, 0.98)
            rect = RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(20)])
        card.bind(pos=lambda inst, v: setattr(rect, "pos", v), size=lambda inst, v: setattr(rect, "size", v))

        msg = Label(text=SECRET_GIFT_TEXT, font_size=dp(15), halign="center", valign="middle", color=(1, 0.92, 0.96, 1))
        msg.bind(size=lambda inst, val: setattr(inst, "text_size", (val[0], None)))
        card.add_widget(msg)

        close_btn = Button(text="Close ❤️", size_hint_y=None, height=dp(44), background_normal="", background_color=(0.92, 0.28, 0.62, 1), bold=True)
        close_btn.bind(on_release=modal.dismiss)
        card.add_widget(close_btn)
        modal.add_widget(card)
        modal.open()


class BirthdaySurpriseApp(App):
    def build(self):
        self.title = APP_TITLE
        schedule_birthday_notification()
        self.sm = ScreenManager(transition=FadeTransition(duration=0.85))
        self.locked_screen = LockedScreen(name="locked")
        self.surprise_screen = BirthdaySurpriseScreen(name="surprise")
        self.sm.add_widget(self.locked_screen)
        self.sm.add_widget(self.surprise_screen)

        self.check_countdown(0)
        Clock.schedule_interval(self.check_countdown, 1.0)
        return self.sm

    def check_countdown(self, dt):
        now = datetime.now()
        remaining = TARGET_DATE - now

        if remaining.total_seconds() <= 0:
            if self.sm.current != "surprise":
                self.sm.current = "surprise"
            return

        if self.sm.current != "locked":
            self.sm.current = "locked"

        total_secs = int(remaining.total_seconds())
        days = total_secs // 86400
        hours = (total_secs % 86400) // 3600
        minutes = (total_secs % 3600) // 60
        seconds = total_secs % 60
        self.locked_screen.update_tiles(days, hours, minutes, seconds)


if __name__ == "__main__":
    BirthdaySurpriseApp().run()
