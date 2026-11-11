# engine/sound_effects.py
import pygame
import math
import array

class SoundManager:
    """Procedurally synthesizes crisp arcade SFX and dynamic retro background music with volume controls."""
    def __init__(self):
        self.enabled = False
        self.sfx_volume = 0.8
        self.bgm_volume = 0.4
        self.bgm_playing = False
        self.bgm_channel = None
        self.bgm_sound = None
        
        try:
            if pygame.mixer.get_init():
                self.sample_rate = pygame.mixer.get_init()[0]
                self.enabled = True
                
                # Dedicated sound effect dictionary
                self.sounds = {
                    "punch_launch": self._make_punch_launch_sound(),
                    "punch_impact": self._make_punch_impact_sound(),
                    "special_launch": self._make_special_launch_sound(),
                    "special_impact": self._make_special_impact_sound(),
                    "special_ready": self._make_ready_sound(),
                    "shield_up": self._make_shield_up_sound(),
                    "shield_absorb": self._make_shield_absorb_sound(),
                    "dodge": self._make_dodge_sound(),
                    "boss_telegraph": self._make_telegraph_sound(),
                    "boss_hit": self._make_boss_hit_sound(),
                    "victory": self._make_victory_sound(),
                    "defeat": self._make_defeat_sound()
                }
                
                # Pre-generate chiptune battle theme loop
                self.bgm_sound = self._make_chiptune_bgm()
                self._update_all_volumes()
        except Exception as e:
            print(f"Sound initialization note: {e}")
            self.enabled = False

    def _generate_sound(self, generator_func, duration_sec):
        sample_rate = self.sample_rate
        total_samples = int(sample_rate * duration_sec)
        samples = array.array('h')
        for i in range(total_samples):
            t = i / sample_rate
            val = generator_func(t, duration_sec)
            val = max(-1.0, min(1.0, val))
            samples.append(int(val * 28000))
        return pygame.mixer.Sound(buffer=samples)

    def _make_punch_launch_sound(self):
        # Whoosh / energy blast launch
        def gen(t, dur):
            freq = 480 * (1.0 - t / dur) + 120
            env = max(0.0, 1.0 - (t / dur) ** 0.5)
            noise = (math.sin(t * 70000 % 10) * 0.3)
            return (math.sin(2 * math.pi * freq * t) * 0.7 + noise) * env
        return self._generate_sound(gen, 0.12)

    def _make_punch_impact_sound(self):
        # Heavy explosive impact thud
        def gen(t, dur):
            freq = 180 * (1.0 - t / dur) + 50
            env = max(0.0, 1.0 - t / dur)
            noise = (math.sin(t * 90000 % 15) * 0.45)
            return (math.sin(2 * math.pi * freq * t) * 0.6 + noise) * env
        return self._generate_sound(gen, 0.16)

    def _make_special_launch_sound(self):
        # High power beam surge
        def gen(t, dur):
            freq = 200 + 750 * (t / dur) ** 0.5
            env = max(0.0, 1.0 - t / dur)
            vibrato = math.sin(2 * math.pi * 30 * t) * 45
            return (math.sin(2 * math.pi * (freq + vibrato) * t) * 0.8) * env
        return self._generate_sound(gen, 0.38)

    def _make_special_impact_sound(self):
        # Mega explosion
        def gen(t, dur):
            freq = 110 * (1.0 - t / dur) + 30
            env = max(0.0, 1.0 - (t / dur) ** 0.4)
            noise = (math.sin(t * 120000 % 12) * 0.6)
            return (math.sin(2 * math.pi * freq * t) * 0.5 + noise) * env
        return self._generate_sound(gen, 0.5)

    def _make_ready_sound(self):
        def gen(t, dur):
            freq = 523.25 if t < dur / 2 else 659.25
            env = max(0.0, 1.0 - (t % (dur / 2)) / (dur / 2))
            return math.sin(2 * math.pi * freq * t) * env * 0.5
        return self._generate_sound(gen, 0.22)

    def _make_shield_up_sound(self):
        # Sci-fi forcefield hum rising
        def gen(t, dur):
            freq = 300 + 550 * (t / dur)
            harmonics = math.sin(2 * math.pi * freq * t) + 0.4 * math.sin(2 * math.pi * freq * 2.0 * t)
            env = min(1.0, t * 15) * max(0.0, 1.0 - t / dur)
            return harmonics * 0.5 * env
        return self._generate_sound(gen, 0.24)

    def _make_shield_absorb_sound(self):
        # Deflection / ricochet pulse
        def gen(t, dur):
            freq = 920 * (1.0 - t / dur) + 200
            env = math.exp(-14 * t)
            harmonics = math.sin(2 * math.pi * freq * t) + 0.6 * math.sin(2 * math.pi * freq * 1.5 * t)
            return harmonics * 0.7 * env
        return self._generate_sound(gen, 0.22)

    def _make_dodge_sound(self):
        def gen(t, dur):
            freq = 500 + 400 * math.sin(math.pi * t / dur)
            env = math.sin(math.pi * t / dur)
            return math.sin(2 * math.pi * freq * t) * env * 0.5
        return self._generate_sound(gen, 0.16)

    def _make_telegraph_sound(self):
        def gen(t, dur):
            freq = 220 + 20 * math.sin(2 * math.pi * 15 * t)
            env = min(1.0, t * 5) * max(0.0, 1.0 - t / dur)
            return math.sin(2 * math.pi * freq * t) * env * 0.5
        return self._generate_sound(gen, 0.25)

    def _make_boss_hit_sound(self):
        def gen(t, dur):
            freq = 120 * (1.0 - t / dur)
            env = max(0.0, 1.0 - (t / dur) ** 0.3)
            return math.sin(2 * math.pi * freq * t) * env * 0.8
        return self._generate_sound(gen, 0.28)

    def _make_victory_sound(self):
        def gen(t, dur):
            notes = [392.0, 523.25, 659.25, 783.99]
            note_idx = min(3, int(t / (dur / 4)))
            freq = notes[note_idx]
            sub_t = t % (dur / 4)
            env = max(0.0, 1.0 - sub_t / (dur / 4))
            return math.sin(2 * math.pi * freq * t) * env * 0.6
        return self._generate_sound(gen, 0.65)

    def _make_defeat_sound(self):
        def gen(t, dur):
            freq = max(40, 220 - 180 * (t / dur))
            env = max(0.0, 1.0 - t / dur)
            return math.sin(2 * math.pi * freq * t) * env * 0.7
        return self._generate_sound(gen, 0.6)

    def _make_chiptune_bgm(self):
        """Generates a looping 4-bar 130 BPM arcade cyberpunk battle track"""
        bpm = 130
        beat_len = 60.0 / bpm
        dur = beat_len * 16  # 4 bars of 4/4 = ~7.38 seconds seamless loop
        
        # Bass progression: A minor (A2, F2, C3, G2)
        bass_notes = [110.0, 87.31, 130.81, 98.0]
        # Arpeggio notes (Am, F, C, G)
        arps = [
            [220.0, 261.63, 329.63, 440.0],
            [174.61, 220.0, 261.63, 349.23],
            [261.63, 329.63, 392.0, 523.25],
            [196.0, 246.94, 293.66, 392.0]
        ]
        
        def gen(t, total_dur):
            # Bar index (0 to 3)
            bar = int((t / (beat_len * 4))) % 4
            beat_in_bar = (t / beat_len) % 4
            sixteenth = int((t / (beat_len / 4))) % 16
            
            # 1. Bassline (8th notes pulse)
            bass_freq = bass_notes[bar]
            bass_env = max(0.0, 1.0 - ((t / (beat_len / 2)) % 1.0) * 1.5)
            # Square wave bass
            bass_wave = 1.0 if math.sin(2 * math.pi * bass_freq * t) > 0 else -1.0
            bass_sig = bass_wave * 0.28 * bass_env
            
            # 2. Arp lead (16th notes fast arcade sweep)
            note_idx = sixteenth % 4
            lead_freq = arps[bar][note_idx]
            sub_t = (t % (beat_len / 4)) / (beat_len / 4)
            lead_env = max(0.0, 1.0 - sub_t * 1.2)
            lead_wave = math.sin(2 * math.pi * lead_freq * t) + 0.3 * (1.0 if math.sin(2 * math.pi * lead_freq * 2 * t) > 0 else -1.0)
            lead_sig = lead_wave * 0.22 * lead_env
            
            # 3. Hi-hat noise on every offbeat
            hat_env = max(0.0, 1.0 - ((t / (beat_len / 2)) % 1.0) * 5.0)
            hat_noise = (math.sin(t * 150000 % 10) * 0.15) * hat_env
            
            return bass_sig + lead_sig + hat_noise
            
        return self._generate_sound(gen, dur)

    def _update_all_volumes(self):
        for s in self.sounds.values():
            s.set_volume(self.sfx_volume)
        if self.bgm_sound:
            self.bgm_sound.set_volume(self.bgm_volume)

    def start_bgm(self):
        if not self.enabled or not self.bgm_sound or self.bgm_playing:
            return
        try:
            self.bgm_channel = self.bgm_sound.play(loops=-1)
            self.bgm_playing = True
        except Exception:
            pass

    def stop_bgm(self):
        if self.bgm_channel:
            self.bgm_channel.stop()
            self.bgm_playing = False

    def toggle_bgm(self):
        if self.bgm_playing:
            self.stop_bgm()
        else:
            self.start_bgm()

    def set_sfx_volume(self, vol):
        self.sfx_volume = max(0.0, min(1.0, vol))
        self._update_all_volumes()

    def set_bgm_volume(self, vol):
        self.bgm_volume = max(0.0, min(1.0, vol))
        self._update_all_volumes()

    def adjust_volume(self, delta):
        new_vol = max(0.0, min(1.0, self.sfx_volume + delta))
        self.set_sfx_volume(new_vol)
        self.set_bgm_volume(new_vol * 0.6)

    def play(self, name):
        if not self.enabled:
            return
        sound = self.sounds.get(name)
        if sound:
            try:
                sound.play()
            except Exception:
                pass
