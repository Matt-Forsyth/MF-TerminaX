import curses
import subprocess
import json
import os
import sys
import time
import threading
import socket

def check_online_status():
    """Check internet connectivity by attempting to connect to a known server."""
    try:
        # Attempt to connect to Google's public DNS server
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

# Utility to run tasks from dynamically configured programs
def run_task(stdscr, task_name, script_path, config_file):
    try:
        command = ["sudo python3", script_path]
        if hasattr(script_path, 'launch_args') and script_path.launch_args:
            command.extend(script_path.launch_args.split())
        
        # Launch the program in a new terminal
        subprocess.Popen([
            "gnome-terminal", "--", "bash", "-c",
            f"{' '.join(command)}; echo 'Press Enter to close...'; read"
        ])
    except Exception as e:
        stdscr.addstr(f"Error running {task_name}: {e}\nPress any key to return to the menu.\n")
    stdscr.getch()

class MFProgram:
    def __init__(self, name, script_path, launch_args=None):
        self.name = name
        self.script_path = script_path
        self.launch_args = launch_args or ""

class MFMenu:
    def __init__(self):
        self.ping_times = []  # Stores ping times for calculating average
        self.menus = {"Main": [MFProgram("Settings", None)]}
        self.current_menu = "Main"
        self.config_file = "config.json"
        self.banner = self.load_banner()
        self.load_programs()
        self.online_status = check_online_status()
        self.refresh_interval = self.load_refresh_interval()
        self.stop_refresh = False

    def load_refresh_interval(self):
        """Load the refresh interval from the config file."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r") as f:
                    config_data = json.load(f)
                    return config_data.get("refresh_interval", 5)  # Default to 5 seconds
        except Exception as e:
            print(f"Error loading refresh interval: {e}")
        return 5

    def load_programs(self):
        programs_dir = "programs"
        if not os.path.exists(programs_dir):
            os.makedirs(programs_dir)

        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r") as f:
                    config_data = json.load(f)
                    self.menus.update({
                        menu: [MFProgram(p["name"], p["script_path"]) for p in programs]
                        for menu, programs in config_data.get("menus", {}).items()
                    })
        except Exception as e:
            print(f"Error loading programs: {e}")

    def load_banner(self):
        default_banner = "Error Loading Banner!"
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r") as f:
                    config_data = json.load(f)
                    return config_data.get("banner", default_banner)
        except Exception:
            pass
        return default_banner

    def update_online_status(self):
        """Continuously update the online status and record ping times."""
        while not self.stop_refresh:
            start_time = time.time()
            self.online_status = check_online_status()
            if self.online_status:
                ping_time = (time.time() - start_time) * 1000  # Convert to milliseconds
                if len(self.ping_times) >= 60:  # Keep only the last 60 pings (1 minute)
                    self.ping_times.pop(0)
                self.ping_times.append(ping_time)
            time.sleep(self.refresh_interval)
        """Continuously update the online status in a separate thread."""
        while not self.stop_refresh:
            self.online_status = check_online_status()
            time.sleep(self.refresh_interval)

    def add_program(self, menu, name, script_path):
        if menu not in self.menus:
            self.menus[menu] = []
        self.menus[menu].append(MFProgram(name, script_path))

    def export_config(self):
        config_data = {
            "menus": {menu: [{"name": p.name, "script_path": p.script_path} for p in programs] for menu, programs in self.menus.items()},
            "banner": self.banner,
            "refresh_interval": self.refresh_interval
        }
        with open(self.config_file, "w") as f:
            json.dump(config_data, f, indent=4)

    def import_config(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r") as f:
                    config_data = json.load(f)
                    self.banner = config_data.get("banner", self.banner)
                    self.refresh_interval = config_data.get("refresh_interval", self.refresh_interval)
                    self.menus = {
                        menu: [MFProgram(p["name"], p["script_path"], p.get("launch_args", "")) 
                              for p in programs]
                        for menu, programs in config_data.get("menus", {}).items()
                    }
        except Exception as e:
            print(f"Error loading configuration: {e}")

    def render_banner(self, stdscr):
        if hasattr(self, 'banner') and self.banner:
            for idx, line in enumerate(self.banner.split('\n')):
                stdscr.addstr(idx, 0, line)

    def get_ping_color(self, ping):
        if ping >= 200:
            return curses.color_pair(5)  # Red
        elif ping >= 150:
            return curses.color_pair(4)  # Red-Purple
        elif ping >= 100:
            return curses.color_pair(3)  # Purple
        elif ping >= 50:
            return curses.color_pair(2)  # Blue-Purple
        else:
            return curses.color_pair(1)  # Blue

    def render_status_bar(self, stdscr):
        banner_height = len(self.banner.split('\n')) if hasattr(self, 'banner') and self.banner else 0
        online_status = "Online" if self.online_status else "Offline"
        online_color = curses.color_pair(6) if self.online_status else curses.color_pair(7)
        avg_ping = sum(self.ping_times) / len(self.ping_times) if self.ping_times else 0
        
        # Render status with its color
        stdscr.addstr(banner_height, 0, f"Status: {online_status}", online_color)
        # Render ping with its gradient color
        stdscr.addstr(banner_height, 30, f"Ping: {avg_ping:.2f}", self.get_ping_color(avg_ping))
        stdscr.addstr(banner_height + 1, 0, "\n")

    def render_menu_items(self, stdscr, options, current_row):
        banner_height = len(self.banner.split('\n')) if hasattr(self, 'banner') and self.banner else 0
        stdscr.addstr(banner_height + 2, 0, f"Current Menu: {self.current_menu}", curses.A_BOLD)
        for idx, program in enumerate(options):
            prefix = "> " if idx == current_row else "  "
            style = curses.A_REVERSE if idx == current_row else 0
            stdscr.addstr(banner_height + 3 + idx, 0, f"{prefix}{program.name}", style)

    def get_menu_options(self):
        # Cache menu options to prevent regeneration
        if not hasattr(self, '_cached_options') or self._cached_options_menu != self.current_menu:
            base_options = self.menus.get(self.current_menu, []).copy()  # Create a copy
            if self.current_menu != "Main":
                base_options.append(MFProgram("Back", None))
            if self.current_menu == "Main":
                base_options.append(MFProgram("Settings", None))
            self._cached_options = base_options
            self._cached_options_menu = self.current_menu
        return self._cached_options

    def handle_menu_selection(self, stdscr, selected_program, current_row):
        if selected_program.name == "Settings":
            self.settings_menu(stdscr)
        elif selected_program.script_path:
            run_task(stdscr, selected_program.name, selected_program.script_path, self.config_file)
        elif selected_program.name in self.menus:
            self.current_menu = selected_program.name
            self._cached_options_menu = None  # Reset cache on menu change
            return 0
        elif selected_program.name == "Back":
            self.current_menu = "Main"
            self._cached_options_menu = None  # Reset cache on menu change
            return 0
        return current_row

    def main_loop(self, stdscr):
        current_row = 0
        try:
            while True:
                stdscr.clear()
                options = self.get_menu_options()
                current_row = max(0, min(current_row, len(options) - 1))
                
                self.render_banner(stdscr)
                self.render_status_bar(stdscr)
                self.render_menu_items(stdscr, options, current_row)
                
                key = stdscr.getch()
                
                if key == curses.KEY_UP:
                    current_row = max(0, current_row - 1)
                elif key == curses.KEY_DOWN:
                    current_row = min(len(options) - 1, current_row + 1)
                elif key == curses.KEY_ENTER or key in [10, 13]:
                    if 0 <= current_row < len(options):
                        selected_program = options[current_row]
                        current_row = self.handle_menu_selection(stdscr, selected_program, current_row)
                
                stdscr.refresh()
        finally:
            self.stop_refresh = True

    def display(self, stdscr):
        curses.curs_set(0)

        # Start the online status updater thread
        refresh_thread = threading.Thread(target=self.update_online_status, daemon=True)
        refresh_thread.start()

        self.main_loop(stdscr)

    def install_dependencies(self, stdscr):
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            apt_deps = config.get('apt_install', [])
            pip_deps = config.get('pip_install', [])
            
            stdscr.clear()
            stdscr.addstr(0, 0, "Installing dependencies...\n\n")
            
            if apt_deps:
                stdscr.addstr("Installing APT packages...\n")
                stdscr.refresh()
                subprocess.run(['sudo', 'apt-get', 'update'], check=True)
                subprocess.run(['sudo', 'apt-get', 'install', '-y'] + apt_deps, check=True)
            
            if pip_deps:
                stdscr.addstr("Installing PIP packages...\n")
                stdscr.refresh()
                pip_command = [sys.executable, '-m', 'pip', 'install', '--break-system-packages']
                pip_command.extend(pip_deps)
                subprocess.run(pip_command, check=True)
            
            stdscr.addstr("\nDependencies installed successfully. Press any key to continue.")
            stdscr.refresh()
            stdscr.getch()
        except Exception as e:
            stdscr.clear()
            stdscr.addstr(0, 0, f"Error installing dependencies: {str(e)}\n\nPress any key to continue.")
            stdscr.refresh()
            stdscr.getch()

    def settings_menu(self, stdscr):
        current_row = 0
        settings_options = ["Export Config", "Import Config", "Install Dependencies", "Back"]
        
        while True:
            stdscr.clear()
            self.render_banner(stdscr)
            
            stdscr.addstr("\nSettings Menu:\n\n")
            for idx, option in enumerate(settings_options):
                if idx == current_row:
                    stdscr.addstr(f"> {option}\n", curses.A_REVERSE)
                else:
                    stdscr.addstr(f"  {option}\n")
            
            key = stdscr.getch()
            
            if key == curses.KEY_UP:
                current_row = max(0, current_row - 1)
            elif key == curses.KEY_DOWN:
                current_row = min(len(settings_options) - 1, current_row + 1)
            elif key == curses.KEY_ENTER or key in [10, 13]:
                if current_row == 0:
                    self.export_config()
                    stdscr.addstr("Config exported. Press any key to continue.\n")
                    stdscr.getch()
                elif current_row == 1:
                    self.import_config()
                    stdscr.addstr("Config imported. Press any key to continue.\n")
                    stdscr.getch()
                elif current_row == 2:
                    self.install_dependencies(stdscr)
                elif current_row == 3:
                    break

            stdscr.refresh()

if __name__ == "__main__":
    def main(stdscr):
        # Initialize color pairs for the online indicator
        curses.start_color()
        curses.init_pair(1, 12, curses.COLOR_BLACK)  # Light Blue
        curses.init_pair(2, 13, curses.COLOR_BLACK)  # Blue-Purple
        curses.init_pair(3, 5, curses.COLOR_BLACK)   # Purple
        curses.init_pair(4, 197, curses.COLOR_BLACK) # Red-Purple
        curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)    # Red
        # Status colors
        curses.init_pair(6, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Online: Green text
        curses.init_pair(7, curses.COLOR_RED, curses.COLOR_BLACK)    # Offline: Red text

        menu = MFMenu()
        menu.display(stdscr)

    curses.wrapper(main)
