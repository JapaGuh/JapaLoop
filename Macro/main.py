import flet as ft
import pyautogui as pag
import time
import keyboard as kb
import winsound
import threading

def main(page: ft.Page):
    page.title = "AllClickingMacro"
    page.window.width = 280
    page.window.height = 435
    page.window.resizable = False
    page.window.maximizable = False
    page.window.icon = "MacroIcon.ico"
    page.window.center()
    page.horizontal_alignment = ft.CrossAxisAlignment.START

    page.fonts = {
        "Montserrat": "Python/Minecraft/Macro/assets/Montserrat/static/Montserrat-Bold.ttf"
    }

    isMacroRunning = False
    clickCount = 0
    
    txtMain = ft.Text(value = "All Clicking Macro", size = 22, weight = "bold", font_family = "Montserrat")
    txtErrorDelay = ft.Text(value = "Invalid Delay", size = 12, color = ft.Colors.RED, visible = False)
    txtErrorKey = ft.Text(value = "Invalid Key Name", size = 12, color = ft.Colors.RED, visible = False)
    txtCounter = ft.Text(value = "", size = 10, color = ft.Colors.GREY_400, italic = True)

    def setControlsDisabled(state):
        lockIcon = ft.Icons.LOCK if state else None
        controlColor = ft.Colors.GREY_400 if state else ft.Colors.WHITE
        keyDropdown.disabled = state
        keyDropdown.prefix_icon = lockIcon
        keyDropdown.text_style = ft.TextStyle(color = controlColor)
        customKeyField.disabled = state
        customKeyField.prefix_icon = lockIcon
        customKeyField.color = controlColor
        unitSelection.disabled = state
        delayField.disabled = state
        delayField.prefix_icon = lockIcon
        delayField.color = controlColor
        hotkeyDropdown.disabled = state
        hotkeyDropdown.prefix_icon = lockIcon
        hotkeyDropdown.text_style = ft.TextStyle(color = controlColor)
        page.update()

    def validateInputs(e):
        if isMacroRunning: return
        isDelayValid = False
        isKeyValid = True
        fieldsNotEmpty = delayField.value.strip() != ""
        if keyDropdown.value == "CUSTOM" and customKeyField.value.strip() == "":
            fieldsNotEmpty = False
        try:
            float(delayField.value)
            isDelayValid = True
            txtErrorDelay.visible = False
        except ValueError:
            isDelayValid = False
            txtErrorDelay.visible = True
        if keyDropdown.value == "CUSTOM":
            typedKey = customKeyField.value.lower()
            isKeyValid = typedKey in pag.KEYBOARD_KEYS
            txtErrorKey.visible = not isKeyValid
        else:
            txtErrorKey.visible = False
        if not fieldsNotEmpty or not isDelayValid or not isKeyValid:
            startButton.text = "Error"
            startButton.color = ft.Colors.RED
            startButton.disabled = True
        else:
            startButton.text = "Start"
            startButton.color = ft.Colors.GREEN
            startButton.disabled = False
        page.update()

    def onKeyChange(e):
        if keyDropdown.value == "CUSTOM":
            customKeyField.visible = True
            page.window.height = 520
        else:
            customKeyField.visible = False
            page.window.height = 435
        validateInputs(e)
        page.update()

    keyDropdown = ft.Dropdown(
        label = "Key to be pressed",
        options = [
            ft.dropdown.Option(text = "MOUSE", disabled = True),
            ft.dropdown.Option("LEFT CLICK"),
            ft.dropdown.Option("RIGHT CLICK"),
            ft.dropdown.Option(text = "NUMBERS", disabled = True),
            ft.dropdown.Option("1"), ft.dropdown.Option("2"), ft.dropdown.Option("3"),
            ft.dropdown.Option("4"), ft.dropdown.Option("5"), ft.dropdown.Option("0"),
            ft.dropdown.Option(text = "SPECIAL", disabled = True),
            ft.dropdown.Option("SHIFT"), ft.dropdown.Option("CTRL"), ft.dropdown.Option("SPACE"),
            ft.dropdown.Option("ENTER"), ft.dropdown.Option("TAB"),
            ft.dropdown.Option(text = "OTHERS", disabled = True),
            ft.dropdown.Option("CUSTOM"),
        ],
        value = "LEFT CLICK",
        on_change = onKeyChange
    )

    customKeyField = ft.TextField(label = "Type custom key", visible = False, on_change = validateInputs)

    unitSelection = ft.SegmentedButton(
        segments = [ft.Segment(value = "sec", label = ft.Text("Seconds")), ft.Segment(value = "min", label = ft.Text("Minutes"))],
        selected = {"sec"},
        on_change = validateInputs
    )
    
    delayField = ft.TextField(label = "Delay value", value = "0.01", on_change = validateInputs)
    
    hotkeyDropdown = ft.Dropdown(
        label = "Hotkey to stop",
        options = [
            ft.dropdown.Option(text = "F KEYS", disabled = True),
            ft.dropdown.Option("F1"), ft.dropdown.Option("F5"), ft.dropdown.Option("F8"), ft.dropdown.Option("F12"),
            ft.dropdown.Option(text = "SPECIAL", disabled = True),
            ft.dropdown.Option("ESC"), ft.dropdown.Option("END"), ft.dropdown.Option("HOME"), ft.dropdown.Option("INSERT"),
            ft.dropdown.Option(text = "COMBOS", disabled = True),
            ft.dropdown.Option("SHIFT + ALT"), ft.dropdown.Option("CTRL + Q"), ft.dropdown.Option("CTRL + S"), ft.dropdown.Option("ALT + X"),
        ],
        value = "F8"
    )

    def stopMacro():
        nonlocal isMacroRunning
        isMacroRunning = False
        kb.unhook_all_hotkeys()

    def loopLogic(key, customKey, delay, hotkey, unit):
        nonlocal isMacroRunning, clickCount
        val = float(delay)
        finalDelay = val * 60 if unit == "min" else val
        clickCount = 0
        
        winsound.Beep(1000, 250)
        time.sleep(1)
        
        kb_hotkey = hotkey.lower().replace(" ", "")
        kb.add_hotkey(kb_hotkey, stopMacro)
        
        while isMacroRunning:
            try:
                if key == "LEFT CLICK":
                    pag.click(button = "left")
                elif key == "RIGHT CLICK":
                    pag.click(button = "right")
                else:
                    finalKey = customKey if key == "CUSTOM" else key
                    pag.press(finalKey.lower())
                
                clickCount += 1
                txtCounter.value = f"Clicks: {clickCount}"
                page.update()
                time.sleep(finalDelay)
            except:
                isMacroRunning = False
        
        setControlsDisabled(False)
        startButton.text = "Start"
        startButton.color = ft.Colors.GREEN
        startButton.icon = ft.Icons.PLAY_ARROW
        winsound.Beep(2000, 250)
        page.update()

    def toggleMacro(e):
        nonlocal isMacroRunning
        if not isMacroRunning:
            isMacroRunning = True
            setControlsDisabled(True)
            startButton.text = "Stop"
            startButton.color = ft.Colors.RED
            startButton.icon = ft.Icons.STOP
            page.update()
            currentUnit = list(unitSelection.selected)
            t = threading.Thread(target = loopLogic, args = (keyDropdown.value, customKeyField.value, delayField.value, hotkeyDropdown.value, currentUnit), daemon = True)
            t.start()
        else:
            stopMacro()

    startButton = ft.Button(text = "Start", color = ft.Colors.GREEN, on_click = toggleMacro, icon = ft.Icons.PLAY_ARROW)

    page.add(
        ft.Container(content = txtMain, bgcolor = ft.Colors.BLUE_900, margin = ft.margin.only(bottom = 10), border_radius = 10, width = 250, height = 50, alignment = ft.alignment.center),
        keyDropdown, customKeyField, txtErrorKey, ft.Text("Select unit:", size = 12, weight = "bold"), unitSelection, delayField, txtErrorDelay, hotkeyDropdown,
        ft.Row([ft.Text(value = "Press the hotkey to stop", color = ft.Colors.GREY_500, size = 11), txtCounter], alignment = ft.MainAxisAlignment.SPACE_BETWEEN),
        startButton
    )

ft.app(target = main)
