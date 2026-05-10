import flet as ft
import pyautogui as pag
import time
import keyboard as kb
import winsound
import threading

def main(page: ft.Page):
    page.title = "AllClickingMacro"
    page.window.width = 400
    page.window.height = 550
    page.window.resizable = False
    page.window.maximizable = False
    page.window.icon = "MacroIcon.ico"
    page.window.center()

    msg_success = ft.Text("Everything seems right", size=12, color=ft.Colors.GREEN, visible=True)
    msg_error = ft.Text("Delay input is wrong (use numbers like 0.01)", size=12, color=ft.Colors.RED, visible=False)
    
    def validate(e):
        try:
            float(delay_field.value)
            msg_success.visible = True
            msg_error.visible = False
            start_button.disabled = False
        except ValueError:
            msg_success.visible = False
            msg_error.visible = True
            start_button.disabled = True
        page.update()

    key_dropdown = ft.Dropdown(
        label="Key to be pressed",
        options=[ft.dropdown.Option("SHIFT"), ft.dropdown.Option("0"), ft.dropdown.Option("CTRL")],
        value="SHIFT"
    )
    
    delay_field = ft.TextField(
        label="Delay in seconds",
        value="0.01",
        on_change=validate
    )
    
    hotkey_dropdown = ft.Dropdown(
        label="Hotkey to stop",
        options=[ft.dropdown.Option("shift+q"), ft.dropdown.Option("shift+alt")],
        value="shift+alt"
    )

    def run_loop(e):
        t = threading.Thread(target=loop_logic, args=(key_dropdown.value, delay_field.value, hotkey_dropdown.value))
        t.start()

    def loop_logic(key, delay, hotkey):
        winsound.Beep(1000, 250)
        time.sleep(1)
        while True:
            pag.press(key.lower())
            time.sleep(float(delay))
            if kb.is_pressed(hotkey):
                winsound.Beep(2000, 250)
                break

    start_button = ft.ElevatedButton("Start", color=ft.Colors.GREEN, on_click=run_loop, icon=ft.Icons.PLAY_ARROW)

    page.add(
        key_dropdown,
        delay_field,
        msg_success,
        msg_error,
        hotkey_dropdown,
        ft.Text(f"Press the hotkey to stop", color=ft.Colors.GREY, size=12),
        start_button
    )

ft.app(target=main)
