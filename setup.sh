#!/bin/bash


sudo apt update

# Install required packages
sudo apt install -y \
    i3-wm \
    onboard \
    unclutter \
    xdotool \
    python3 \
    python3-pip \
    python3-psutil \
    python3-pyqt5



# Create necessary directories
mkdir -p ~/.config/i3
mkdir -p /home/user/kiosk

# Install the new .xinitrc
cp kiosk_setup.sh ~/.xinitrc
chmod +x ~/.xinitrc

# Create systemd service for auto-start (optional)
sudo tee /etc/systemd/system/kiosk.service > /dev/null << 'EOF'
[Unit]
Description=Kiosk Mode
After=multi-user.target

[Service]
Type=simple
User=user
Group=user
ExecStart=/usr/bin/startx /home/user/.xinitrc
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF


# Add auto-startx to profile
if ! grep -q "startx" ~/.bash_profile 2>/dev/null; then
    echo "if [[ -z $DISPLAY ]] && [[ $(tty) == /dev/tty1 ]]; then exec startx fi" >> ~/.bash_profile
fi

# Create backup of original xinitrc if it exists
if [ -f ~/.xinitrc.original ]; then
    echo "Backup of original .xinitrc already exists"
else
    if [ -f ~/.xinitrc ]; then
        cp ~/.xinitrc ~/.xinitrc.original
        echo "Original .xinitrc backed up to ~/.xinitrc.original"
    fi
fi

echo "Installation complete!"
