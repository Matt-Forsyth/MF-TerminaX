import curses
import subprocess
import json
import os
import sys

# Utility to run tasks from dynamically configured programs
def run_task(stdscr, task_name, script_path, config_file):
    stdscr.clear()
    stdscr.addstr(f"Running {task_name} in a new terminal...\n")
    stdscr.refresh()
    try:
        # Check if the config file exists
        config_data = {}
        if os.path.exists(config_file):
            with open(config_file, "r") as f:
                config_data = json.load(f)
                stdscr.addstr(f"Loaded config: {config_data}\n")
                stdscr.refresh()

        # Determine if config_file should be passed
        command = [sys.executable, script_path]
        if "config" in script_path.lower():  # Pass config only if required
            command.append(config_file)

        # Launch the program in a new terminal
        subprocess.Popen([
            "gnome-terminal", "--", "bash", "-c",
            f"{' '.join(command)}; echo 'Press Enter to close...'; read"
        ])
    except Exception as e:
        stdscr.addstr(f"Error running {task_name}: {e}\nPress any key to return to the menu.\n")
    stdscr.getch()

# Main menu
class MFProgram:
    def __init__(self, name, script_path):
        self.name = name
        self.script_path = script_path

class MFMenu:
    def __init__(self):
        self.menus = {"Main": [MFProgram("Settings", None)]}
        self.current_menu = "Main"
        self.config_file = "config.json"
        self.banner = self.load_banner()
        self.load_programs()

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

    def add_program(self, menu, name, script_path):
        if menu not in self.menus:
            self.menus[menu] = []
        self.menus[menu].append(MFProgram(name, script_path))

    def export_config(self):
        config_data = {
            "menus": {menu: [{"name": p.name, "script_path": p.script_path} for p in programs] for menu, programs in self.menus.items()},
            "banner": self.banner
        }
        with open(self.config_file, "w") as f:
            json.dump(config_data, f, indent=4)

    def import_config(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r") as f:
                    config_data = json.load(f)
                    self.banner = config_data.get("banner", self.banner)
                    self.menus = {
                        menu: [MFProgram(p["name"], p["script_path"]) for p in programs]
                        for menu, programs in config_data.get("menus", {}).items()
                    }
        except Exception as e:
            print(f"Error loading configuration: {e}")

    def display(self, stdscr):
        curses.curs_set(0)
        current_row = 0

        while True:
            stdscr.clear()
            stdscr.addstr(self.banner, curses.A_BOLD)
            stdscr.addstr("\n\n")
            stdscr.addstr(f"Current Menu: {self.current_menu}\n", curses.A_BOLD)
            options = self.menus.get(self.current_menu, []) + ([MFProgram("Back", None)] if self.current_menu != "Main" else []) +([MFProgram("Settings", None)] if self.current_menu == "Main" else [])

            for idx, program in enumerate(options):
                if idx == current_row:
                    stdscr.addstr(f"> {program.name}\n", curses.A_REVERSE)
                else:
                    stdscr.addstr(f"  {program.name}\n")

            key = stdscr.getch()

            if key == curses.KEY_UP and current_row > 0:
                current_row -= 1
            elif key == curses.KEY_DOWN and current_row < len(options) - 1:
                current_row += 1
            elif key == curses.KEY_ENTER or key in [10, 13]:
                selected_program = options[current_row]

                if selected_program.name == "Settings":
                    self.settings_menu(stdscr)
                elif selected_program.script_path:  # Only run if there's a script path
                    run_task(stdscr, selected_program.name, selected_program.script_path, self.config_file)
                elif selected_program.name in self.menus:  # Navigate to submenu
                    self.current_menu = selected_program.name
                    current_row = 0
                elif selected_program.name == "Back":
                    self.current_menu = "Main"
                    current_row = 0

            stdscr.refresh()

    def settings_menu(self, stdscr):
        options = ["Export Config", "Import Config", "Back"]
        current_row = 0

        while True:
            stdscr.clear()
            stdscr.addstr(self.banner, curses.A_BOLD)
            stdscr.addstr("\n\n")
            stdscr.addstr(f"Current Menu: Settings\n", curses.A_BOLD)

            for idx, option in enumerate(options):
                if idx == current_row:
                    stdscr.addstr(f"> {option}\n", curses.A_REVERSE)
                else:
                    stdscr.addstr(f"  {option}\n")

            key = stdscr.getch()

            if key == curses.KEY_UP and current_row > 0:
                current_row -= 1
            elif key == curses.KEY_DOWN and current_row < len(options) - 1:
                current_row += 1
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
                    break

            stdscr.refresh()

if __name__ == "__main__":
    menu = MFMenu()
    curses.wrapper(menu.display)
