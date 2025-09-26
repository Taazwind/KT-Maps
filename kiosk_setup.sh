#!/bin/bash


# Kill any existing processes
pkill -f onboard
pkill -f PureMaps

# Hide cursor after inactivity
unclutter -idle 1 -root &


# Configure i3 for kiosk mode
cat > ~/.config/i3/config << 'EOF'
# i3 config for kiosk mode
font pango:DejaVu Sans Mono 8

# Remove window decorations
for_window [class=".*"] border none

# Make Pure Maps fullscreen but allow overlays
for_window [class="io.github.rinigus.PureMaps"] fullscreen enable
for_window [class="io.github.rinigus.PureMaps"] focus

# Make onboard keyboard always on top and floating
for_window [class="Onboard"] floating enable
for_window [class="Onboard"] sticky enable
for_window [class="Onboard"] border none
for_window [class="Onboard"] above enable

# Disable window switching
bindsym Mod1+Tab exec true
bindsym Mod4+Tab exec true

# Emergency exit (Ctrl+Alt+Escape)
bindsym Control+Mod1+Escape exit

# Manual keyboard toggle (Ctrl+Alt+K)
bindsym Control+Mod1+k exec "python3 /home/user/kiosk/toggle_keyboard.py"
EOF

sleep 2

i3 &
sleep 2

# Start Pure Maps backend
flatpak run --command=osmscout-server io.github.rinigus.OSMScoutServer --listen &
sleep 2


# Start Pure Maps
flatpak run io.github.rinigus.PureMaps &

sleep 5

# Copy the overlay script and make it executable
cp /home/user/overlay.py /home/user/kiosk/native_overlay.py
chmod +x /home/user/kiosk/native_overlay.py

# Start the native transparent overlay
python3 /home/user/kiosk/native_overlay.py &

sleep 2

onboard


# Keep the session alive
wait