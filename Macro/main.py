import flet as ft
import pyautogui as pag
import time
import keyboard as kb
import winsound
import threading

def main(page: ft.Page):
    # UI Window Configuration
    page.title = "JapaLoop"
    page.window.width = 280
    page.window.height = 435
    page.window.resizable = False
    page.window.maximizable = False
    page.window.icon = "MacroIcon.ico"
    page.window.center()

    # Custom Font Registration
    page.fonts = {
        "Montserrat": "assets/Montserrat/static/Montserrat-Bold.ttf"
    }

    # State Variables
    isMacroRunning = False  # Tracks whether the clicking loop is active
    clickCount = 0          # Keeps score of how many clicks/presses have been made
    current_global_hotkey = None  # Stores the active keyboard shortcut so we can change it later
    recorded_key = ""       # Stores the raw string name of the physically pressed custom key
    
    # UI Text Elements
    txtMain = ft.Text(value="JapaLoop", size=22, weight="bold", font_family="Montserrat")
    txtErrorDelay = ft.Text(value="Invalid Delay", size=12, color=ft.Colors.RED, visible=False)
    txtCounter = ft.Text(value="", size=10, color=ft.Colors.GREY_400, italic=True)

    # UI Lock/Unlock Function
    # Disables or enables inputs so the user can't mess up settings while the macro is running
    def setControlsDisabled(state):
        lockIcon = ft.Icons.LOCK if state else None
        controlColor = ft.Colors.GREY_400 if state else ft.Colors.WHITE
        
        keyDropdown.disabled = state
        keyDropdown.prefix_icon = lockIcon
        keyDropdown.text_style = ft.TextStyle(color=controlColor)
        
        recordButton.disabled = state
        
        unitSelection.disabled = state
        
        delayField.disabled = state
        delayField.prefix_icon = lockIcon
        delayField.color = controlColor
        
        hotkeyDropdown.disabled = state
        hotkeyDropdown.prefix_icon = lockIcon
        hotkeyDropdown.text_style = ft.TextStyle(color=controlColor)
        
        page.update()

    # Input Validation Logic
    # Makes sure the user typed real numbers and selected a key before allowing the macro to start
    def validateInputs(e):
        if isMacroRunning: return  # Don't validate if it's already running
        
        isDelayValid = False
        fieldsNotEmpty = delayField.value.strip() != ""
        
        # If "CUSTOM" is picked, a key must have been physically recorded first
        if keyDropdown.value == "CUSTOM" and recorded_key == "":
            fieldsNotEmpty = False
            
        # Check if the delay input is actually a valid decimal/number
        try:
            float(delayField.value)
            isDelayValid = True
            txtErrorDelay.visible = False
        except ValueError:
            isDelayValid = False
            txtErrorDelay.visible = True
            
        # Update the Start button appearance based on validation results
        if not fieldsNotEmpty or not isDelayValid:
            startButton.text = "Error"
            startButton.color = ft.Colors.RED
            startButton.disabled = True
        else:
            startButton.text = "Start"
            startButton.color = ft.Colors.GREEN
            startButton.disabled = False
        page.update()

    # Dropdown Change Handler
    # Toggles the visibility of the Recording button instead of a text field
    def onKeyChange(e):
        if keyDropdown.value == "CUSTOM":
            recordButton.visible = True
            page.window.height = 520
        else:
            recordButton.visible = False
            page.window.height = 435
        validateInputs(e)
        page.update()

    # Dynamic Key Recording Logic
    # Freezes the UI temporarily while waiting for a single physical keyboard hit
    def start_recording(e):
        recordButton.text = "Listening... Press any key"
        # FIXED: Changed from KEYBOARD_ARMED_MENU to a valid Flet icon
        recordButton.icon = ft.Icons.RADIO_BUTTON_CHECKED
        recordButton.color = ft.Colors.ORANGE_400
        setControlsDisabled(True)
        page.update()
        
        # System blocks here until a hardware key event is caught
        event = kb.read_event()
        if event.event_type == kb.KEY_DOWN:
            nonlocal recorded_key
            recorded_key = event.name
            
        # Return UI controls back to active state
        setControlsDisabled(False)
        recordButton.text = f"Bound: {recorded_key.upper()}"
        recordButton.icon = ft.Icons.KEYBOARD
        recordButton.color = ft.Colors.BLUE_400
        
        validateInputs(None)
        page.update()

    # UI Inputs Components Definition
    keyDropdown = ft.Dropdown(
        label="Key to be pressed",
        options=[
            ft.dropdown.Option(text="MOUSE", disabled=True),
            ft.dropdown.Option("LEFT CLICK"),
            ft.dropdown.Option("RIGHT CLICK"),
            ft.dropdown.Option(text="NUMBERS", disabled=True),
            ft.dropdown.Option("1"), ft.dropdown.Option("2"), ft.dropdown.Option("3"),
            ft.dropdown.Option("4"), ft.dropdown.Option("5"), ft.dropdown.Option("0"),
            ft.dropdown.Option(text="SPECIAL", disabled=True),
            ft.dropdown.Option("SHIFT"), ft.dropdown.Option("CTRL"), ft.dropdown.Option("SPACE"),
            ft.dropdown.Option("ENTER"), ft.dropdown.Option("TAB"),
            ft.dropdown.Option(text="OTHERS", disabled=True),
            ft.dropdown.Option("CUSTOM"),
        ],
        value="LEFT CLICK",
        on_change=onKeyChange
    )

    # Interactive key binder button replacing the old basic TextField layout
    recordButton = ft.ElevatedButton(
        text="Click to record key", 
        icon=ft.Icons.KEYBOARD,
        visible=False, 
        on_click=start_recording,
        color=ft.Colors.BLUE_400
    )

    unitSelection = ft.SegmentedButton(
        segments=[
            ft.Segment(value="sec", label=ft.Text("Seconds")), 
            ft.Segment(value="min", label=ft.Text("Minutes"))
        ],
        selected={"sec"},
        on_change=validateInputs
    )
    
    delayField = ft.TextField(label="Delay value", value="0.01", on_change=validateInputs)
    
    # Whenever the user picks a new hotkey from the menu, bind it globally
    def onHotkeyChange(e):
        update_global_hotkey()

    hotkeyDropdown = ft.Dropdown(
        label="Hotkey Start/Stop",
        options=[
            ft.dropdown.Option(text="F KEYS", disabled=True),
            ft.dropdown.Option("F1"), ft.dropdown.Option("F5"), ft.dropdown.Option("F8"), ft.dropdown.Option("F12"),
            ft.dropdown.Option(text="SPECIAL", disabled=True),
            ft.dropdown.Option("ESC"), ft.dropdown.Option("END"), ft.dropdown.Option("HOME"), ft.dropdown.Option("INSERT"),
            ft.dropdown.Option(text="COMBOS", disabled=True),
            ft.dropdown.Option("SHIFT + ALT"), ft.dropdown.Option("CTRL + Q"), ft.dropdown.Option("CTRL + S"), ft.dropdown.Option("ALT + X"),
        ],
        value="F8",
        on_change=onHotkeyChange
    )

    # Macro Control Functions
    def stopMacro():
        nonlocal isMacroRunning
        isMacroRunning = False

    # The actual execution loop. Runs on a separate thread so the Flet window doesn't freeze.
    def loopLogic(key, customKey, delay, unit):
        nonlocal isMacroRunning, clickCount
        
        # Calculate delay based on time unit chosen (Seconds vs Minutes)
        val = float(delay)
        finalDelay = val * 60 if unit == "min" else val
        clickCount = 0
        
        # Play activation beep (low pitch) and pause 1 sec to let user position their cursor
        winsound.Beep(1000, 250)
        time.sleep(1)
        
        # Core automation loop
        while isMacroRunning:
            try:
                if key == "LEFT CLICK":
                    pag.click(button="left")
                elif key == "RIGHT CLICK":
                    pag.click(button="right")
                else:
                    finalKey = customKey if key == "CUSTOM" else key
                    pag.press(finalKey.lower())
                
                # Increment and update counter on the screen
                clickCount += 1
                txtCounter.value = f"Clicks: {clickCount}"
                page.update()
                
                time.sleep(finalDelay)
            except:
                # If something breaks (like Windows failsafe moving mouse to corner), stop cleanly
                isMacroRunning = False
        
        # UI Restoration after macro stops
        setControlsDisabled(False)
        startButton.text = "Start"
        startButton.color = ft.Colors.GREEN
        startButton.icon = ft.Icons.PLAY_ARROW
        
        # Play termination beep (high pitch)
        winsound.Beep(2000, 250)
        page.update()

    # Handles switching states between Start and Stop (triggered by button OR keyboard shortcut)
    def toggleMacro(e=None):
        nonlocal isMacroRunning
        
        # If inputs are wrong and macro isn't running, ignore both button click and hotkey press
        if startButton.disabled and not isMacroRunning:
            return

        if not isMacroRunning:
            # Turn ON macro
            isMacroRunning = True
            setControlsDisabled(True)
            startButton.text = "Stop"
            startButton.color = ft.Colors.RED
            startButton.icon = ft.Icons.STOP
            page.update()
            
            # Extract chosen unit from the set object
            currentUnit = list(unitSelection.selected)[0]
            
            # Start loopLogic on a daemon thread so it dies instantly if the main app closes
            t = threading.Thread(
                target=loopLogic, 
                args=(keyDropdown.value, recorded_key, delayField.value, currentUnit), 
                daemon=True
            )
            t.start()
        else:
            # Turn OFF macro
            stopMacro()

    startButton = ft.Button(text="Start", color=ft.Colors.GREEN, on_click=toggleMacro, icon=ft.Icons.PLAY_ARROW)

    # Global Hotkey System
    # Dynamically unbinds old keyboard keys and binds the new ones globally via background hooks
    def update_global_hotkey():
        nonlocal current_global_hotkey
        # If there's an older hotkey running, unhook it first to prevent overlapping hotkeys
        if current_global_hotkey:
            kb.remove_hotkey(current_global_hotkey)
        
        # Format input string (e.g., "CTRL + Q" becomes "ctrl+q")
        formatted_hotkey = hotkeyDropdown.value.lower().replace(" ", "")
        
        # Map hotkey directly to call toggleMacro without passing structural event arguments
        current_global_hotkey = kb.add_hotkey(formatted_hotkey, toggleMacro)

    # Render Elements to Layout
    page.add(
        ft.Container(content=txtMain, bgcolor=ft.Colors.BLUE_900, margin=ft.margin.only(bottom=10), border_radius=10, width=250, height=50, alignment=ft.alignment.center),
        keyDropdown, recordButton, ft.Text("Select unit:", size=12, weight="bold"), unitSelection, delayField, txtErrorDelay, hotkeyDropdown,
        ft.Row([ft.Text(value="Hotkey starts & stops", color=ft.Colors.GREY_500, size=11), txtCounter], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        startButton
    )

    # Run initial hook activation setup right when the application launches
    update_global_hotkey()

ft.app(target=main)
