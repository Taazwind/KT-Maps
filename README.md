# KT²Maps

Système de cartographie hors ligne sur Raspberry Pi.

## Installation

```bash
sudo apt update
sudo apt install -y i3-wm onboard unclutter python3 python3-pyqt5 flatpak
flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
flatpak install -y flathub io.github.rinigus.PureMaps io.github.rinigus.OSMScoutServer
```

## Démarrage

```bash
chmod +x setup.sh
./setup.sh
```

## Fonctionnalités

- Carte hors ligne avec PureMaps
- Géolocalisation par ombre solaire
- Interface kiosque

## Structure

- `kiosk_setup.sh` - Script de démarrage
- `install.sh` - Installation automatique  
- `overlay.py` - Module géolocalisation solaire

## Technologies

- PureMaps (interface carte)
- OSM Scout Server (données cartographiques)
- i3 Window Manager (mode kiosque)
- Python/Qt5 (géolocalisation)

## Utilisation

1. Lancer le système avec `./setup.sh`
2. Naviguer sur la carte avec souris/tactile
3. Utiliser le tutoriel pour la géolocalisation solaire
