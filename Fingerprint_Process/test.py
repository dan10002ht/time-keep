from guizero import App, Box, PushButton, Text

# Function to update the display
def update_display(text):
    display.value += text

# Function to calculate the result
def calculate_result():
    try:
        result = eval(display.value)
        display.value = str(result)
    except:
        display.value = "Error"

# Function to clear the display
def clear_display():
    display.value = ""

# Create the app
app = App("Calculator", width=600, height=800)

# Create the display box
display_box = Box(app, width="fill", height=100, align="top")
display = Text(display_box, text="", size=40)

# Define the button layout
button_layout = [
    ["7", "8", "9", "/"],
    ["4", "5", "6", "*"],
    ["1", "2", "3", "-"],
    ["0", ".", "=", "+"],
    ["C"]
]

# Create the button grid
button_box = Box(app, width="fill", height="fill", layout="grid")

# Create the buttons
buttons = []
for row, row_buttons in enumerate(button_layout):
    for col, label in enumerate(row_buttons):
        button = PushButton(
            button_box, text=label, grid=[col, row],
            width=7, height=5, padx=10, pady=10
        )
        button.bg = "white"
        button.text_color = "black"

        if label == "C":
            button.update_command(clear_display)
        elif label == "=":
            button.update_command(calculate_result)
        else:
            button.update_command(update_display, [label])

        buttons.append(button)

# Display the app
app.display()
