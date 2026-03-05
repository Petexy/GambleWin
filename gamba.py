#!/usr/bin/env python3
import sys
import random
import time
import os
import subprocess
import atexit
import gi
import crypto

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
gi.require_version('Gst', '1.0')

from gi.repository import Gtk, Adw, GLib, GObject, Gdk, Gst


Gst.init(None)

import gettext
import builtins
import argparse


parser = argparse.ArgumentParser(description="Gamba - Slot Machine")
parser.add_argument("--debug", action="store_true", help="Enable debug mode (bypass file encryption/decryption)")
parser.add_argument("--force-language", type=str, help="Force the application language (e.g., 'pl' for Polish)")
args, unknown = parser.parse_known_args()

DEBUG_MODE = args.debug
if DEBUG_MODE:
    print("DEBUG MODE ENABLED: Bypassing Windows mounting and encryption.")
    sys.argv = [sys.argv[0]] + unknown                           


APP_NAME = "gamba"
LOCALE_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "locales")

if args.force_language:
    os.environ["LANGUAGE"] = args.force_language
    os.environ["LANG"] = args.force_language
    os.environ["LC_ALL"] = args.force_language

try:
    locale_lang = gettext.translation(APP_NAME, localedir=LOCALE_DIR, fallback=True)
    locale_lang.install()
    builtins._ = locale_lang.gettext
except Exception as e:
    print(f"Localization failed to load: {e}")
    builtins._ = gettext.gettext

CSS = """
.slot-image {
    transition: all 0.2s ease-in-out;
}

@keyframes reel-motion {
    0% { transform: translateY(-20px); filter: blur(4px); }
    100% { transform: translateY(20px); filter: blur(4px); }
}

.spinning {
    animation: reel-motion 0.1s linear infinite;
    opacity: 0.8;
}

@keyframes win-pulse {
    0% { transform: scale(1); filter: drop-shadow(0 0 0px rgba(255,215,0,0)); }
    50% { transform: scale(1.3) rotate(5deg); filter: drop-shadow(0 0 20px rgba(255,215,0,1)) brightness(1.3); }
    100% { transform: scale(1); filter: drop-shadow(0 0 0px rgba(255,215,0,0)); }
}

.winning-image {
    animation: win-pulse 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275) infinite;
}

@keyframes lose-shake {
    0% { transform: translate(1px, 1px) rotate(0deg); filter: grayscale(0%); }
    20% { transform: translate(-3px, 0px) rotate(-2deg); }
    40% { transform: translate(3px, 2px) rotate(2deg); filter: grayscale(40%); }
    60% { transform: translate(-3px, 2px) rotate(0deg); }
    80% { transform: translate(3px, -1px) rotate(2deg); filter: grayscale(80%); opacity: 0.7;}
    100% { transform: translate(0px, 0px) rotate(0deg); filter: grayscale(100%); opacity: 0.5; }
}

.losing-image {
    animation: lose-shake 0.4s forwards;
}

@keyframes rainbow-bg {
    0%   { background-color: #ff0000; }
    5%   { background-color: #ff4000; }
    10%  { background-color: #ff8000; }
    15%  { background-color: #ffbf00; }
    20%  { background-color: #ffff00; }
    25%  { background-color: #bfff00; }
    30%  { background-color: #80ff00; }
    35%  { background-color: #40ff00; }
    40%  { background-color: #00ff00; }
    45%  { background-color: #00ff80; }
    50%  { background-color: #00ffff; }
    55%  { background-color: #00bfff; }
    60%  { background-color: #0080ff; }
    65%  { background-color: #0040ff; }
    70%  { background-color: #0000ff; }
    75%  { background-color: #4000ff; }
    80%  { background-color: #8000ff; }
    85%  { background-color: #bf00ff; }
    90%  { background-color: #ff00ff; }
    95%  { background-color: #ff0080; }
    100% { background-color: #ff0000; }
}

.rainbow-bg-layer {
    background-image: radial-gradient(circle at center, rgba(255,255,255,0.6) 0%, rgba(255,255,255,0) 80%);
    animation: rainbow-bg 0.8s linear infinite;
    opacity: 0;
    transition: opacity 1.5s ease;
}

.rainbow-active {
    opacity: 1;
}

@keyframes jackpot-explosion {
    0% { transform: scale(1) rotate(0deg); filter: brightness(1) drop-shadow(0 0 0px #fff); }
    10% { transform: scale(1.5) rotate(-15deg); filter: brightness(2) drop-shadow(0 0 50px #ff0); }
    20% { transform: scale(1.2) rotate(10deg); filter: brightness(1.5) drop-shadow(0 0 30px #f00); }
    30% { transform: scale(1.6) rotate(-5deg); filter: brightness(2.5) drop-shadow(0 0 60px #0f0); }
    40% { transform: scale(1.3) rotate(15deg); filter: brightness(1.2) drop-shadow(0 0 20px #00f); }
    50% { transform: scale(1.8) rotate(-10deg); filter: brightness(3) drop-shadow(0 0 80px #f0f); }
    60% { transform: scale(1.1) rotate(5deg); filter: brightness(1) drop-shadow(0 0 10px #0ff); }
    70% { transform: scale(1.5) rotate(-20deg); filter: brightness(2) drop-shadow(0 0 50px #ff0); }
    80% { transform: scale(1.3) rotate(10deg); filter: brightness(1.5) drop-shadow(0 0 30px #f00); }
    90% { transform: scale(1.7) rotate(-5deg); filter: brightness(2.5) drop-shadow(0 0 70px #fff); }
    100% { transform: scale(1) rotate(0deg); filter: brightness(1) drop-shadow(0 0 0px #fff); }
}

.jackpot-image {
    animation: jackpot-explosion 1s ease-in-out infinite;
}

@keyframes spin-ready-pulse {
    0% { transform: scale(1); background-color: #3584e4; box-shadow: 0 0 15px rgba(53, 132, 228, 0.5); text-shadow: 0 0 0px transparent; border: 2px solid transparent;}
    50% { transform: scale(1.05); background-color: #f1c40f; box-shadow: 0 0 50px #f39c12, inset 0 0 15px #fff; color: #000; text-shadow: 0 0 10px #fff; border: 2px solid #fff; }
    100% { transform: scale(1); background-color: #3584e4; box-shadow: 0 0 15px rgba(53, 132, 228, 0.5); text-shadow: 0 0 0px transparent; border: 2px solid transparent;}
}

.spin-ready {
    animation: spin-ready-pulse 0.8s infinite ease-in-out;
}

.win-text {
    color: #f1c40f;
    font-size: 32px;
    font-weight: 900;
    text-shadow: 0 0 15px #f39c12;
}

.lose-text {
    color: #e74c3c;
    font-size: 24px;
    font-weight: 900;
    text-shadow: 0 0 15px #c0392b;
}

.result-message {
    transition: all 0.3s ease;
}

/* UI Overhaul Styles */
.slot-reel {
    background-color: rgba(0, 0, 0, 0.6);
    background-image: linear-gradient(to bottom, rgba(0,0,0,0.8) 0%, rgba(20,20,20,0) 20%, rgba(20,20,20,0) 80%, rgba(0,0,0,0.8) 100%);
    border-radius: 12px;
    border: 2px solid #333;
    box-shadow: inset 0 0 20px rgba(0,0,0,0.9);
    padding: 10px;
}

.spin-button-giant {
    font-size: 42px;
    font-weight: 900;
    letter-spacing: 4px;
    border-radius: 50px;
    padding: 25px 80px;
    margin-top: 10px;
    transition: all 0.4s ease-out;
}

.control-deck {
    background-color: rgba(30, 30, 30, 0.7);
    border-radius: 16px;
    padding: 20px;
    border: 1px solid #444;
    box-shadow: 0 10px 30px rgba(0,0,0,0.5);
}

.main-box-bg {
    transition: background-color 1.5s ease, filter 1.5s ease, transform 0.1s ease;
}

@keyframes shake {
    0% { transform: translate(2px, 2px) rotate(0deg); }
    10% { transform: translate(-2px, -4px) rotate(-1deg); }
    20% { transform: translate(-6px, 0px) rotate(2deg); }
    30% { transform: translate(6px, 4px) rotate(0deg); }
    40% { transform: translate(2px, -2px) rotate(2deg); }
    50% { transform: translate(-2px, 4px) rotate(-1deg); }
    60% { transform: translate(-6px, 2px) rotate(0deg); }
    70% { transform: translate(6px, 2px) rotate(-1deg); }
    80% { transform: translate(-2px, -2px) rotate(2deg); }
    90% { transform: translate(2px, 4px) rotate(0deg); }
    100% { transform: translate(2px, -4px) rotate(-1deg); }
}

.shake-screen {
    animation: shake 0.5s cubic-bezier(.36,.07,.19,.97) both;
}

.spin-running {
    animation: spin-pulse 0.5s infinite alternate;
    background-color: #555;
    color: #ffd700;
    box-shadow: 0 0 10px #777;
    border-color: #666;
}

@keyframes spin-pulse {
    from { opacity: 0.8; transform: scale(0.98); }
    to { opacity: 1; transform: scale(1.02); }
}
"""




WIN_MOUNT_POINT = "/tmp/gamba_win_mount"
_win_mounted = False
SUDO_PASSWORD = ""

def find_windows_partition():
    import json
    try:
        result = subprocess.run(
            ["/usr/bin/lsblk", "-J", "-b", "-l", "-o", "NAME,FSTYPE,SIZE"],
            capture_output=True, text=True, timeout=10
        )
        data = json.loads(result.stdout)
        best = None
        best_size = 0
        for dev in data.get("blockdevices", []):

            fstype = dev.get("fstype") or ""
            if fstype.lower() in ["ntfs", "ntfs3", "ntfs-3g"]:
                name = dev.get("name", "")
                size = dev.get("size", 0)
                try:
                    size = int(size)
                except (ValueError, TypeError):
                    size = 0

                if size > best_size and name:
                    best_size = size
                    if name.startswith("/dev/"):
                        best = name
                    else:
                        best = f"/dev/{name}"
        return best
    except Exception as e:
        print(f"Error finding Windows partition: {e}")
        return None

def mount_windows_partition(device, password):
    global _win_mounted
    os.makedirs(WIN_MOUNT_POINT, exist_ok=True)
    uid = os.getuid()
    gid = os.getgid()


    cmd_ntfs3g = ["/usr/bin/sudo", "-S", "/usr/bin/mount", "-t", "ntfs-3g", "-o", f"rw,uid={uid},gid={gid},umask=000,remove_hiberfile", device, WIN_MOUNT_POINT]

    try:
        subprocess.run(
            cmd_ntfs3g,
            input=password + "\n", text=True, check=True, timeout=30, capture_output=True
        )
        _win_mounted = True
        print(f"Mounted {device} at {WIN_MOUNT_POINT} (ntfs-3g)")
        return True
    except subprocess.CalledProcessError as e:
        print(f"ntfs-3g mount failed: {e.stderr}")
        return False

def unmount_windows_partition():
    global _win_mounted
    global SUDO_PASSWORD
    if not _win_mounted:
        return
    try:
        subprocess.run(
            ["/usr/bin/sudo", "-S", "/usr/bin/umount", WIN_MOUNT_POINT],
            input=SUDO_PASSWORD + "\n", text=True, check=True, timeout=15, capture_output=True
        )
        print(f"Unmounted {WIN_MOUNT_POINT}")
        _win_mounted = False
    except subprocess.CalledProcessError as e:
        print(f"Failed to unmount: {e.stderr}")

WIN_FILES = []                                         

def count_files_on_partition(mount_point):
    global WIN_FILES
    WIN_FILES = []
    count = 0
    try:
        for root, dirs, files in os.walk(mount_point):
            for file in files:
                WIN_FILES.append(os.path.join(root, file))
                count += 1
    except Exception as e:
        print(f"Error counting files: {e}")
    return count


atexit.register(unmount_windows_partition)




class GamblingRiskDialog(Adw.Window):
    def __init__(self, parent_window, on_accept_callback):
        super().__init__(transient_for=parent_window, modal=True)
        self.set_title(_("Terms of Decryption"))
        self.set_default_size(500, 600)
        self.on_accept_callback = on_accept_callback

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(main_box)


        header = Adw.HeaderBar()
        header.set_show_end_title_buttons(False)                                     
        header.set_show_start_title_buttons(False)
        main_box.append(header)


        self.scroll = Gtk.ScrolledWindow()
        self.scroll.set_vexpand(True)
        self.scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        main_box.append(self.scroll)

        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        content_box.set_margin_top(20)
        content_box.set_margin_bottom(20)
        content_box.set_margin_start(20)
        content_box.set_margin_end(20)
        self.scroll.set_child(content_box)

        warning_icon = Gtk.Image.new_from_icon_name("dialog-warning-symbolic")
        warning_icon.set_pixel_size(64)
        warning_icon.add_css_class("error")
        content_box.append(warning_icon)

        title_label = Gtk.Label(label=_("WARNING"))
        title_label.add_css_class("title-1")
        title_label.add_css_class("error")
        content_box.append(title_label)

        eula_text = _(
            "You are about to decrypt your files, recovering your data and effectively ending this gambling session.\n\n"
            "However, by doing so, you acknowledge the extreme theoretical and practical risks associated with gambling, including but not limited to:\n\n"
            "1. THE DOPAMINE LOOP\n"
            "Gambling creates artificial spikes in dopamine, hijacking the brain's reward system. This EULA confirms you understand that the flashing lights and sounds were designed to psychologically manipulate you into betting your own files.\n\n"
            "2. THE SUNK COST FALLACY\n"
            "Quitting now means accepting any losses you have accrued. Gambling preys upon the irrational desire to \"win back\" what was lost, which mathematically leads to absolute ruin. This software takes no responsibility for financial, emotional, or data-related destruction.\n\n"
            "3. ILLUSION OF CONTROL\n"
            "You acknowledge that the outcomes are strictly pseudo-random and heavily rigged by house edge algorithms to prevent overflowing the starting coin cap. You never had control.\n\n"
            "4. ESCALATION OF COMMITMENT\n"
            "This is a small simulation, but real gambling leads to escalated betting, chased losses, and severe real-world consequences.\n\n"
            "By pressing Accept, you legally acknowledge that you have read this entire warning, understand the psychological traps of the casino, and accept full responsibility for clicking the spinning reels.\n\n"
            "Scroll to the absolute bottom to accept."
        )
        text_label = Gtk.Label(label=eula_text)
        text_label.set_wrap(True)
        text_label.set_justify(Gtk.Justification.LEFT)
        content_box.append(text_label)


        action_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        action_box.set_margin_top(15)
        action_box.set_margin_bottom(15)
        action_box.set_margin_start(20)
        action_box.set_margin_end(20)
        action_box.set_halign(Gtk.Align.END)
        main_box.append(action_box)

        self.decline_btn = Gtk.Button(label=_("Decline & Keep Gambling"))
        self.decline_btn.connect("clicked", self.on_decline)
        action_box.append(self.decline_btn)

        self.accept_btn = Gtk.Button(label=_("I Understand, Decrypt My Files"))
        self.accept_btn.add_css_class("destructive-action")
        self.accept_btn.set_sensitive(False)                          
        self.accept_btn.connect("clicked", self.on_accept)
        action_box.append(self.accept_btn)


        vadj = self.scroll.get_vadjustment()
        vadj.connect("value-changed", self.on_scroll_changed)


        GLib.idle_add(self.check_initial_scroll)

    def check_initial_scroll(self):
        vadj = self.scroll.get_vadjustment()
        upper = vadj.get_upper()
        page_size = vadj.get_page_size()
        if upper <= page_size:
             self.accept_btn.set_sensitive(True)
        return False

    def on_scroll_changed(self, vadj):
        value = vadj.get_value()
        upper = vadj.get_upper()
        page_size = vadj.get_page_size()


        if value >= (upper - page_size - 5):
            self.accept_btn.set_sensitive(True)

    def on_decline(self, widget):
        self.close()

    def on_accept(self, widget):
        self.on_accept_callback()
        self.close()

class GambaWindow(Adw.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.set_title(_("Slots"))
        self.set_default_size(700, 850)                               


        style_manager = Adw.StyleManager.get_default()
        style_manager.set_color_scheme(Adw.ColorScheme.FORCE_DARK)


        self.game_dir = os.path.dirname(os.path.realpath(__file__))
        self.test_file_path = os.path.join(self.game_dir, "test.txt")
        self.check_test_file()


        self.starting_coins = 0
        self.coins = 0
        self.current_bet_amount = 1

        if DEBUG_MODE:
            GLib.idle_add(self._on_mount_done, 10000)
        else:

            GLib.idle_add(self.prompt_sudo)


        self.icons_dir = os.path.join(self.game_dir, "spins_icons")
        self.sounds_dir = os.path.join(self.game_dir, "sounds")


        self.player_spin = Gst.ElementFactory.make("playbin", "player_spin")
        self.player_win = Gst.ElementFactory.make("playbin", "player_win")
        self.player_lose = Gst.ElementFactory.make("playbin", "player_lose")

        self.player_spin.set_property("uri", "file://" + os.path.join(self.sounds_dir, "spin.ogg"))
        self.player_win.set_property("uri", "file://" + os.path.join(self.sounds_dir, "win.ogg"))
        self.player_lose.set_property("uri", "file://" + os.path.join(self.sounds_dir, "lose.ogg"))



        REGULAR_WEIGHT = 20
        REGULAR_MULTIPLIER = 5

        self.SYMBOLS = {
            "massivewin": {"file": "massivewin.png", "weight": 2, "special": "max_coins"},
            "massivelose": {"file": "massivelose.png", "weight": 2, "special": "zero_coins"},
            "bigwin": {"file": "bigwin.png", "weight": 5, "multiplier": 50},
            "icon6": {"file": "icon6.png", "weight": REGULAR_WEIGHT, "multiplier": REGULAR_MULTIPLIER},
            "icon5": {"file": "icon5.png", "weight": REGULAR_WEIGHT, "multiplier": REGULAR_MULTIPLIER},
            "icon4": {"file": "icon4.png", "weight": REGULAR_WEIGHT, "multiplier": REGULAR_MULTIPLIER},
            "icon3": {"file": "icon3.png", "weight": REGULAR_WEIGHT, "multiplier": REGULAR_MULTIPLIER},
            "icon2": {"file": "icon2.png", "weight": REGULAR_WEIGHT, "multiplier": REGULAR_MULTIPLIER},
            "icon1": {"file": "icon1.png", "weight": REGULAR_WEIGHT, "multiplier": REGULAR_MULTIPLIER},
        }

        self.symbol_keys = list(self.SYMBOLS.keys())
        self.symbol_weights = [self.SYMBOLS[k]["weight"] for k in self.symbol_keys]

        self.grid_widgets = []
        self.total_spins = 0
        self.consecutive_wins = 0
        self.WIN_CHANCE = 0.2
        self.is_muted = False


        self.is_spinning = False
        self.final_grid = []
        self.spin_start_time = 0
        self.row_stop_times = []
        self.result_sound_triggered = False

        self.overlay = Gtk.Overlay()
        self.set_content(self.overlay)

        self.rainbow_bg = Gtk.Box()
        self.rainbow_bg.add_css_class("rainbow-bg-layer")
        self.overlay.set_child(self.rainbow_bg)

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.main_box.add_css_class("main-box-bg")
        self.overlay.add_overlay(self.main_box)
        self.overlay.set_measure_overlay(self.main_box, True)

        header = Adw.HeaderBar()
        self.main_box.append(header)


        self.mute_btn = Gtk.Button.new_from_icon_name("audio-volume-high-symbolic")
        self.mute_btn.connect("clicked", self.toggle_mute)


        self.decrypt_all_btn = Gtk.Button(label=_("Decrypt all files"))
        self.decrypt_all_btn.add_css_class("suggested-action")
        self.decrypt_all_btn.connect("clicked", self.on_decrypt_all)


        header_actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        header_actions.append(self.mute_btn)
        header_actions.append(self.decrypt_all_btn)



        settings = Gtk.Settings.get_default()
        layout = settings.get_property("gtk-decoration-layout")


        place_at_start = True

        if layout:
            parts = layout.split(":")
            if len(parts) >= 2:
                start_controls = parts[0].strip()




                if start_controls:
                    place_at_start = False

        if place_at_start:
            header.pack_start(header_actions)
        else:
            header.pack_end(header_actions)


        main_clamp = Adw.Clamp()
        main_clamp.set_maximum_size(700)
        main_clamp.set_vexpand(True)
        self.main_box.append(main_clamp)


        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=30)
        content_box.set_margin_top(30)
        content_box.set_margin_bottom(30)
        content_box.set_margin_start(20)
        content_box.set_margin_end(20)
        content_box.set_halign(Gtk.Align.FILL)
        main_clamp.set_child(content_box)

        self.status_label = Gtk.Label(label=_("Current: {coins}").format(coins=self.coins))
        self.status_label.add_css_class("title-1")
        self.status_label.add_css_class("numeric")
        self.status_label.set_halign(Gtk.Align.CENTER)
        content_box.append(self.status_label)


        clamp = Adw.Clamp()
        clamp.set_maximum_size(500)
        content_box.append(clamp)

        deck_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        deck_box.add_css_class("control-deck")
        clamp.set_child(deck_box)

        controls_group = Adw.PreferencesGroup()
        deck_box.append(controls_group)

        amount_row = Adw.ActionRow()
        amount_row.set_title(_("Bet Amount"))
        controls_group.add(amount_row)

        self.amount_spin = Gtk.SpinButton.new_with_range(1, 100, 1)
        self.amount_spin.set_value(self.current_bet_amount)
        self.amount_spin.connect("value-changed", self.on_amount_changed)
        amount_row.add_suffix(self.amount_spin)

        grid = Gtk.Grid()
        grid.set_column_homogeneous(True)
        grid.set_row_homogeneous(True)
        grid.set_column_spacing(15)
        grid.set_row_spacing(15)
        grid.set_halign(Gtk.Align.FILL)
        grid.set_hexpand(True)
        grid.set_vexpand(True)
        content_box.append(grid)


        for i in range(9):

            initial_symbol = random.choice(self.symbol_keys)
            image_path = os.path.join(self.icons_dir, self.SYMBOLS[initial_symbol]["file"])

            image = Gtk.Picture.new_for_filename(image_path)
            image.set_can_shrink(True)
            image.set_content_fit(Gtk.ContentFit.CONTAIN)
            image.set_halign(Gtk.Align.CENTER)
            image.set_valign(Gtk.Align.CENTER)
            image.set_hexpand(True)
            image.set_vexpand(True)
            image.add_css_class("slot-image")

            frame = Gtk.Box()
            frame.add_css_class("slot-reel")
            frame.append(image)

            col = i % 3
            row = i // 3
            grid.attach(frame, col, row, 1, 1)
            self.grid_widgets.append(image)

        self.result_label = Gtk.Label(label=_("Ready to Spin"))
        self.result_label.add_css_class("title-2")
        self.result_label.add_css_class("result-message")
        self.result_label.set_halign(Gtk.Align.CENTER)
        self.result_label.set_size_request(-1, 80)
        content_box.append(self.result_label)

        self.spin_btn = Gtk.Button(label=_("SPIN"))
        self.spin_btn.add_css_class("spin-button-giant")
        self.spin_btn.add_css_class("spin-ready")
        self.spin_btn.connect("clicked", self.on_spin)


        spin_btn_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        spin_btn_container.set_size_request(-1, 130)                                                       
        spin_btn_container.set_halign(Gtk.Align.CENTER)
        spin_btn_container.set_valign(Gtk.Align.CENTER)
        spin_btn_container.append(self.spin_btn)

        deck_box.append(spin_btn_container)

        self.load_css()
        self.update_ui_state()

    def load_css(self):
        provider = Gtk.CssProvider()
        provider.load_from_data(CSS.encode())
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def on_amount_changed(self, widget):
        self.current_bet_amount = int(widget.get_value())
        self.update_ui_state()

    def toggle_mute(self, widget):
        self.is_muted = not self.is_muted
        icon_name = "audio-volume-muted-symbolic" if self.is_muted else "audio-volume-high-symbolic"
        self.mute_btn.set_icon_name(icon_name)

        target_vol = 0.0 if self.is_muted else 1.0

        for p in [self.player_spin, self.player_win, self.player_lose]:
            p.set_property("volume", target_vol)

    def play_sound(self, player):
        player.set_state(Gst.State.NULL)
        vol = 0.0 if self.is_muted else 1.0
        player.set_property("volume", vol) 
        player.set_state(Gst.State.PLAYING)


    def stop_sound(self, player):
        player.set_state(Gst.State.NULL)

    def fade_out_sound(self, player, duration_ms=300, interval_ms=30):

        steps = int(duration_ms / interval_ms)
        if steps <= 0:
            player.set_state(Gst.State.NULL)
            return

        initial_vol = player.get_property("volume")
        step_count = 0

        def _step():
            nonlocal step_count
            step_count += 1

            if step_count > steps or player.get_state(0)[1] != Gst.State.PLAYING:
                player.set_state(Gst.State.NULL)
                return False             



            factor = 1.0 - (step_count / steps)
            new_vol = initial_vol * (factor * factor * factor)

            player.set_property("volume", max(0.0, new_vol))

            if new_vol <= 0.01:
                player.set_state(Gst.State.NULL)
                return False

            return True

        GLib.timeout_add(interval_ms, _step)

    def generate_grid(self, force_win=False, force_lose=False):



        max_attempts = 100
        for _unused_loop in range(max_attempts):
            grid_values = random.choices(self.symbol_keys, weights=self.symbol_weights, k=9)
            winnings, _unused = self.calculate_winnings_logic(grid_values)

            if force_win:
                if winnings > 0:
                    return grid_values
            elif force_lose:
                if winnings == 0:
                    return grid_values
            else:
                return grid_values


        if force_lose:


            return ["icon1", "icon2", "icon3", "icon4", "icon5", "icon6", "icon1", "icon2", "icon3"]


        return random.choices(self.symbol_keys, weights=self.symbol_weights, k=9)

    def on_spin(self, widget):
        if self.coins < self.current_bet_amount:
            self.result_label.set_text(_("Not enough files!"))
            return

        if self.is_spinning:
            return

        self.coins -= self.current_bet_amount
        self.update_ui_state() 


        self.result_label.remove_css_class("win-text")
        self.result_label.remove_css_class("lose-text")
        self.rainbow_bg.add_css_class("rainbow-active")                 

        for image in self.grid_widgets:
            image.remove_css_class("winning-image")
            image.remove_css_class("jackpot-image")
            image.remove_css_class("losing-image")
            image.add_css_class("spinning")


        should_win = False


        if self.consecutive_wins >= 3:
            should_win = False
        else:
             should_win = (random.random() < self.WIN_CHANCE)


        self.final_grid = self.generate_grid(force_win=should_win, force_lose=not should_win)



        winnings, _unused = self.calculate_winnings_logic(self.final_grid)

        future_coins = self.coins + winnings

        if future_coins > self.starting_coins:
            print(f"DEBUG: Cap Check Triggered. Future: {future_coins} > Start: {self.starting_coins}")






            if winnings > 0:

                 print("DEBUG: Forcing LOSS to prevent cap overflow.")
                 self.final_grid = self.generate_grid(force_lose=True)


        self.is_spinning = True
        self.result_sound_triggered = False             
        self.spin_btn.set_sensitive(False)
        self.spin_btn.remove_css_class("spin-ready")
        self.spin_btn.add_css_class("spin-running")
        self.spin_btn.set_label(_("SPINNING..."))
        self.amount_spin.set_sensitive(False)
        self.result_label.set_text("Spinning...")

        self.spin_start_time = time.time()


        self.play_sound(self.player_spin)

        base_time = 2.5
        self.row_stop_times = []
        for i in range(3):
            self.row_stop_times.append(base_time + random.random() * 0.5)
            base_time += 1.0

        GLib.timeout_add(80, self.animate_spin)

    def animate_spin(self):
        current_time = time.time()
        elapsed = current_time - self.spin_start_time

        all_stopped = True



        if not self.result_sound_triggered:

            if elapsed >= self.row_stop_times[1] + 0.2:                                   

                 self.fade_out_sound(self.player_spin, duration_ms=500)

                 self.result_sound_triggered = True


                 winnings, _unused = self.calculate_winnings_logic(self.final_grid)




                 special_hit = False


                 has_special = False
                 _unused, winning_indices = self.calculate_winnings_logic(self.final_grid)
                 if winning_indices:
                     has_special = True                                    

                 if winnings > 0 or has_special:
                     self.play_sound(self.player_win)
                 else:
                     self.play_sound(self.player_lose)

        for row in range(3):
            is_row_stopped = elapsed >= self.row_stop_times[row]

            if not is_row_stopped:
                all_stopped = False
                for col in range(3):
                    idx = row * 3 + col

                    random_symbol = random.choice(self.symbol_keys)
                    path = os.path.join(self.icons_dir, self.SYMBOLS[random_symbol]["file"])
                    self.grid_widgets[idx].set_filename(path)
            else:
                for col in range(3):
                    idx = row * 3 + col
                    self.grid_widgets[idx].remove_css_class("spinning")

                    symbol_key = self.final_grid[idx]
                    path = os.path.join(self.icons_dir, self.SYMBOLS[symbol_key]["file"])
                    self.grid_widgets[idx].set_filename(path)

        if all_stopped:
            self.finalize_spin()
            return False 

        return True 

    def on_decrypt_all(self, widget):
        if not WIN_FILES and not DEBUG_MODE:
            self.result_label.set_text(_("No Windows files array loaded."))
            return

        dialog = GamblingRiskDialog(self, self._execute_decrypt_all)
        dialog.present()

    def _execute_decrypt_all(self):
        self.result_label.set_text(_("Decrypting all files..."))
        self.decrypt_all_btn.set_sensitive(False)
        self.spin_btn.set_sensitive(False)

        def _do_decrypt():
            if not DEBUG_MODE:
                count = crypto.decrypt_all_files(WIN_FILES)
            else:
                time.sleep(1)
                count = 10000
            GLib.idle_add(self._on_decrypt_all_done, count)

        import threading
        threading.Thread(target=_do_decrypt, daemon=True).start()

    def _on_decrypt_all_done(self, count):
        self.result_label.set_text(_("Decrypted {count} files completely!").format(count=count))
        self.decrypt_all_btn.set_sensitive(True)
        self.update_ui_state()

    def do_screen_shake(self, duration_ms=500):
        self.main_box.add_css_class("shake-screen")
        def stop_shake():
            self.main_box.remove_css_class("shake-screen")
            return False
        GLib.timeout_add(duration_ms, stop_shake)

    def tick_up_coins(self, target_coins, step=1, interval_ms=30):
        def _tick():
            if self.coins < target_coins:
                self.coins = min(self.coins + step, target_coins)
                self.status_label.set_text(_("Current: {coins}").format(coins=self.coins))
                return True           
            return False       
        GLib.timeout_add(interval_ms, _tick)

    def check_test_file(self):
        if not os.path.exists(self.test_file_path):
            try:
                with open(self.test_file_path, "w") as f:
                    f.write("This is your precious data. Win to keep it safe. Lose and it gets encrypted!")
                print(f"Created test file: {self.test_file_path}")
            except Exception as e:
                print(f"Error creating test file: {e}")

    def finalize_spin(self):
        self.is_spinning = False

        self.rainbow_bg.remove_css_class("rainbow-active")

        winnings, winning_indices = self.calculate_winnings_logic(self.final_grid)

        self.total_spins += 1


        special_event = self.check_special_event(winning_indices)

        import threading


        self.spin_btn.set_sensitive(False)
        self.decrypt_all_btn.set_sensitive(False)
        self.amount_spin.set_sensitive(False)

        if special_event == "max_coins":
            self.do_screen_shake(1000)
            target = self.starting_coins
            step = max(1, int((target - self.coins) / 60))           
            self.tick_up_coins(target, step)

            self.result_label.set_text(_("MASSIVE WIN! Decrypting all files..."))
            self.consecutive_wins += 1 

            for idx_set in winning_indices:
                for idx in idx_set:
                    self.grid_widgets[idx].add_css_class("jackpot-image")

            def _massive_win_thread():
                if not DEBUG_MODE:
                    crypto.decrypt_all_files(WIN_FILES)
                else:
                    time.sleep(1)
                GLib.idle_add(self._on_crypto_done, _("MASSIVE WIN! All files have been decrypted!"), True)

            threading.Thread(target=_massive_win_thread, daemon=True).start()
            return                  

        elif special_event == "zero_coins":
            self.coins = 0
            self.result_label.set_text(_("MASSIVE LOSE! Encrypting everything..."))
            self.consecutive_wins = 0

            def _massive_lose_thread():
                if not DEBUG_MODE:
                    crypto.encrypt_random_files(WIN_FILES, len(WIN_FILES))
                else:
                    time.sleep(1)
                GLib.idle_add(self._on_crypto_done, _("MASSIVE LOSE! Say goodbye to your files!"), False)

            threading.Thread(target=_massive_lose_thread, daemon=True).start()
            return                  

        elif winnings > 0:
            target = self.coins + winnings
            step = max(1, int(winnings / 30))
            self.tick_up_coins(target, step)
            self.do_screen_shake()

            for idx_set in winning_indices:
                for idx in idx_set:

                    if random.random() < 0.3:
                        self.grid_widgets[idx].add_css_class("jackpot-image")
                    else:
                        self.grid_widgets[idx].add_css_class("winning-image")

            self.result_label.set_text(_("WINNER! +{winnings} (Decrypting...)").format(winnings=winnings))
            self.consecutive_wins += 1

            def _win_thread():
                if not DEBUG_MODE:
                    decrypted_count = crypto.decrypt_random_files(WIN_FILES, winnings)
                else:
                    time.sleep(1)
                    decrypted_count = winnings
                GLib.idle_add(self._on_crypto_done, _("WINNER! +{winnings} (Decrypted {decrypted_count} files!)").format(winnings=winnings, decrypted_count=decrypted_count), True)

            threading.Thread(target=_win_thread, daemon=True).start()
            return                  

        else:
            self.consecutive_wins = 0
            self.result_label.set_text(_("Try Again! (Encrypting {amount} files...)").format(amount=self.current_bet_amount))

            def _lose_thread():
                if not DEBUG_MODE:
                    encrypted_count = crypto.encrypt_random_files(WIN_FILES, self.current_bet_amount)
                else:
                    time.sleep(1)
                    encrypted_count = self.current_bet_amount
                GLib.idle_add(self._on_crypto_done, _("Try Again! (Encrypted {count} files!)").format(count=encrypted_count), False)

            threading.Thread(target=_lose_thread, daemon=True).start()
            return                  

    def _on_crypto_done(self, message, is_win):
        self.result_label.set_text(message)


        if is_win:
            self.result_label.add_css_class("win-text")
        else:
            self.result_label.add_css_class("lose-text")

            for w in self.grid_widgets:
                w.add_css_class("losing-image")

        self.update_ui_state()
        self.amount_spin.set_sensitive(True)
        self.decrypt_all_btn.set_sensitive(True)

        if self.coins <= 0:
            self.show_game_over()
        return False

    def check_special_event(self, winning_indices):
        if not winning_indices:
            return None

        for idx_set in winning_indices:

             first_idx = list(idx_set)[0]
             symbol_key = self.final_grid[first_idx]

             if "special" in self.SYMBOLS[symbol_key]:
                 return self.SYMBOLS[symbol_key]["special"]

        return None

    def calculate_winnings_logic(self, grid):
        lines = [

            [0, 1, 2], [3, 4, 5], [6, 7, 8],

            [0, 3, 6], [1, 4, 7], [2, 5, 8],

            [0, 4, 8], [2, 4, 6]
        ]

        total_win = 0
        winning_indices = []

        for indices in lines:
            s1 = grid[indices[0]]
            s2 = grid[indices[1]]
            s3 = grid[indices[2]]

            if s1 == s2 == s3:
                symbol_key = s1
                multiplier = self.SYMBOLS[symbol_key].get("multiplier", 0)


                if multiplier > 0:
                    total_win += self.current_bet_amount * multiplier

                winning_indices.append(set(indices))

        return total_win, winning_indices

    def update_ui_state(self):
        self.status_label.set_text(_("Current: {coins}").format(coins=self.coins))
        self.spin_btn.remove_css_class("spin-running")

        if self.coins < self.current_bet_amount:
             self.spin_btn.set_sensitive(False)
             self.spin_btn.remove_css_class("spin-ready")
             self.spin_btn.set_label(_("SPIN"))
        else:
             if not self.is_spinning:
                 self.spin_btn.set_sensitive(True)
                 self.spin_btn.add_css_class("spin-ready")
                 self.spin_btn.set_label(_("SPIN"))
        self.amount_spin.set_sensitive(not getattr(self, 'is_spinning', False))

        self.decrypt_all_btn.set_sensitive(not getattr(self, 'is_spinning', False) and (bool(WIN_FILES) or DEBUG_MODE))

    def show_game_over(self):
        dialog = Adw.AlertDialog(
            heading=_("Game Over"),
            body=_("You ran out of files! Better luck next time."),
        )
        dialog.add_response("close", _("Close"))
        dialog.set_default_response("close")
        dialog.set_close_response("close")
        dialog.present(self)

    def prompt_sudo(self):
        dialog = Adw.AlertDialog(
            heading=_("Root Permissions Required"),
            body=_("Gambling with Windows files requires root permissions to securely read and write to the partition.\nPlease enter your sudo password."),
        )
        self.password_entry = Gtk.PasswordEntry()
        self.password_entry.set_show_peek_icon(True)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.append(self.password_entry)
        dialog.set_extra_child(box)

        dialog.add_response("quit", _("Quit"))
        dialog.add_response("submit", _("Authorize"))
        dialog.set_response_appearance("submit", Adw.ResponseAppearance.SUGGESTED)
        dialog.set_default_response("submit")
        dialog.set_close_response("quit")

        dialog.connect("response", self.on_sudo_response)
        dialog.present(self)
        return False

    def on_sudo_response(self, dialog, response):
        if response == "submit":
            global SUDO_PASSWORD
            SUDO_PASSWORD = self.password_entry.get_text()
            self.status_label.set_text("Mounting and scanning files...")
            self.spin_btn.set_sensitive(False)
            self.decrypt_all_btn.set_sensitive(False)

            import threading
            threading.Thread(target=self._mount_and_count_thread, daemon=True).start()
        else:
            self.close()

    def _mount_and_count_thread(self):
        win_dev = find_windows_partition()
        file_count = 0
        if win_dev:
            print(f"Found Windows partition: {win_dev}")
            if mount_windows_partition(win_dev, SUDO_PASSWORD):
                file_count = count_files_on_partition(WIN_MOUNT_POINT)
            else:
                print("Could not mount Windows partition. Using default coins.")
                file_count = 10000
        else:
            print("No Windows partition found. Using default coins.")
            file_count = 10000

        GLib.idle_add(self._on_mount_done, file_count)

    def _on_mount_done(self, file_count):
        self.starting_coins = file_count if file_count > 0 else 10000
        self.coins = self.starting_coins
        self.update_ui_state()
        self.decrypt_all_btn.set_sensitive(True)
        return False


class GambaApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)
        self.connect('shutdown', self.on_shutdown)

    def on_activate(self, app):
        self.win = GambaWindow(application=app)
        self.win.present()

    def on_shutdown(self, app):
        unmount_windows_partition()

if __name__ == "__main__":
    app = GambaApp(application_id="com.petexy.gamba.slots.animated")
    app.run(None)
