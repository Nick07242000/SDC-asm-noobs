#!/usr/bin/env python3
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Button

# Disable the default Matplotlib toolbar
plt.rcParams['toolbar'] = 'None'

DEVICE_PATH = "/dev/asmn_driver"

# Arrays to store the graph data
x_data = []
y_data = []
current_channel = 0

# Initial setup of the Matplotlib figure
fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.25) # Bottom spacing for buttons

def set_channel(channel):
    """
    Writes to the Character Device Driver to change the signal
    and resets the graph data.
    """
    global current_channel, x_data, y_data
    try:
        with open(DEVICE_PATH, 'w') as f:
            f.write(str(channel))
        current_channel = channel
        
        # Reset the graph when changing measurement
        x_data.clear()
        y_data.clear()
        ax.clear()
        print(f"Internal channel changed to: {channel}")
    except Exception as e:
        print(f"Error writing to device: {e}")

def read_device():
    """
    Reads the character device and parses the format "counter: value".
    """
    try:
        with open(DEVICE_PATH, 'r') as f:
            data = f.read().strip()
            if data:
                parts = data.split(":")
                if len(parts) == 2:
                    return int(parts[0].strip()), int(parts[1].strip())
    except Exception as e:
        print(f"Error reading from device: {e}")
    return None, None

def animate(i):
    """
    Callback function to update the graph in real-time.
    """
    global x_data, y_data
    
    counter, value = read_device()
    
    if counter is not None and value is not None:
        # Avoid adding the same data twice if the Python timer 
        # reads faster than the kernel timer.
        if not x_data or x_data[-1] != counter:
            x_data.append(counter)
            y_data.append(value)
            
            # Keep a rolling window of the last 15 points
            x_data = x_data[-15:]
            y_data = y_data[-15:]

            ax.clear()
            
            # Assign a different color based on the signal for clarity
            color = 'b' if current_channel == 0 else 'r'
            ax.plot(x_data, y_data, marker='o', linestyle='-', color=color)
            
            # Dynamic labels updated to English
            title = "Signal 1 (Linear Wave)" if current_channel == 0 else "Signal 2 (Random)"
            ax.set_title(title)
            ax.set_xlabel("Time (Seconds / Counter)")
            ax.set_ylabel("Value (Units)")
            ax.grid(True)

# UI Button Configuration
ax_btn0 = plt.axes([0.2, 0.05, 0.2, 0.075])
# Button says 'Signal 1', but internally calls channel 0 of the driver
btn0 = Button(ax_btn0, 'Signal 1')
btn0.on_clicked(lambda event: set_channel(0))

ax_btn1 = plt.axes([0.6, 0.05, 0.2, 0.075])
# Button says 'Signal 2', but internally calls channel 1 of the driver
btn1 = Button(ax_btn1, 'Signal 2')
btn1.on_clicked(lambda event: set_channel(1))

# Initialize by forcing the reading of the first signal
set_channel(0)

# Animation at 500ms
ani = animation.FuncAnimation(fig, animate, interval=500, cache_frame_data=False)

plt.show()
