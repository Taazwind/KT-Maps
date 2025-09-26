import sys
import math
from datetime import datetime, timezone
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QLineEdit, 
                            QFormLayout, QTextEdit, QScrollArea, QDialog,
                            QDoubleSpinBox, QSpinBox, QTimeEdit, QDateEdit,
                            QMessageBox, QFrame, QGroupBox, QGridLayout,
                            QTabWidget)
from PyQt5.QtCore import Qt, QTime, QDate, pyqtSlot, QTimer
from PyQt5.QtGui import QFont, QPalette, QColor, QPixmap, QPainter, QBrush, QLinearGradient

class SolarGeolocationCalculator:
    @staticmethod
    def to_radians(degrees):
        return degrees * math.pi / 180
    
    @staticmethod
    def to_degrees(radians):
        return radians * 180 / math.pi
    
    @staticmethod
    def calculate_position(stick_height, shadow_length, shadow_azimuth, 
                          utc_time, date, magnetic_declination):
        
        # Convert UTC time to decimal hours
        utc_decimal = utc_time.hour() + utc_time.minute() / 60.0
        
        # Calculate day of year
        day_of_year = date.dayOfYear()
        
        # Solar declination
        declination = 23.45 * math.sin(SolarGeolocationCalculator.to_radians(360 * (284 + day_of_year) / 365))
        
        # Sun elevation angle
        elevation = math.atan(stick_height / shadow_length)
        elevation_deg = SolarGeolocationCalculator.to_degrees(elevation)
        
        # Correct azimuth for magnetic declination
        true_azimuth = shadow_azimuth + magnetic_declination
        # Shadow azimuth is opposite to sun azimuth
        sun_azimuth = (true_azimuth + 180) % 360
        
        # Initial estimates
        longitude = 0
        latitude = 0
        
        # Iterative method to solve for latitude and longitude
        for i in range(5):
            # Hour angle
            hour_angle = 15 * (utc_decimal - 12 + longitude / 15)
            
            # Calculate latitude
            sin_elevation = math.sin(elevation)
            sin_declination = math.sin(SolarGeolocationCalculator.to_radians(declination))
            cos_declination = math.cos(SolarGeolocationCalculator.to_radians(declination))
            cos_hour_angle = math.cos(SolarGeolocationCalculator.to_radians(hour_angle))
            
            sin_latitude = (sin_elevation - cos_declination * cos_hour_angle) / sin_declination
            sin_latitude = max(-1, min(1, sin_latitude))  # Clamp to [-1, 1]
            latitude = SolarGeolocationCalculator.to_degrees(math.asin(sin_latitude))
            
            # Calculate theoretical sun azimuth
            cos_elevation = math.cos(elevation)
            cos_latitude = math.cos(SolarGeolocationCalculator.to_radians(latitude))
            sin_latitude2 = math.sin(SolarGeolocationCalculator.to_radians(latitude))
            
            cos_azimuth = (sin_declination - sin_elevation * sin_latitude2) / (cos_elevation * cos_latitude)
            cos_azimuth = max(-1, min(1, cos_azimuth))  # Clamp to [-1, 1]
            theoretical_azimuth = SolarGeolocationCalculator.to_degrees(math.acos(cos_azimuth))
            
            # Adjust for correct quadrant
            if hour_angle > 0:
                theoretical_azimuth = 360 - theoretical_azimuth
            
            # Longitude correction based on azimuth error
            azimuth_error = sun_azimuth - theoretical_azimuth
            longitude += azimuth_error / 4  # Convergence factor
        
        return {
            'latitude': latitude,
            'longitude': longitude,
            'elevation': elevation_deg,
            'declination': declination,
            'sun_azimuth': sun_azimuth,
            'day_of_year': day_of_year
        }

class TutorialDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setFixedSize(650, 350)
        
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowCloseButtonHint)

        self.setWindowFlags(
            Qt.WindowType.Window | 
            Qt.WindowType.WindowCloseButtonHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.X11BypassWindowManagerHint
        )
        
        self.center_on_screen()
        
        self.setup_ui()
    
    def center_on_screen(self):
        """Centre la fenêtre sur l'écran principal"""
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        x = (screen_geometry.width() - 650) // 2
        y = (screen_geometry.height() - 350) // 2
        self.move(x, y)
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(15)
        
        # Title
        title_label = QLabel("Géolocalisation par Ombre Solaire")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                padding: 15px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                                          stop:0 #667eea, stop:1 #764ba2);
                color: white;
                border-radius: 10px;
                margin-bottom: 10px;
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)
        scroll_layout.addWidget(title_label)
        
        # Material section
        material_group = QGroupBox("Matériel nécessaire")
        material_layout = QVBoxLayout(material_group)
        
        materials = [
            "Bâton droit d'environ 1 mètre",
            "Mètre ou règle", 
            "Boussole (ou smartphone avec boussole)",
            "Montre avec heure UTC/GMT précise",
            "Cette application ou calculatrice"
        ]
        
        for material in materials:
            label = QLabel(material)
            label.setStyleSheet("QLabel { padding: 5px; font-size: 14px; }")
            material_layout.addWidget(label)
        
        scroll_layout.addWidget(material_group)
        
        # Steps section
        steps = [
            ("Installation du bâton", 
             "Plantez le bâton parfaitement vertical dans un sol ferme. "
             "Utilisez un fil à plomb pour vérifier la verticalité. "
             "Mesurez précisément sa hauteur avec votre règle.\n\n"
             "Astuce : Un bâton de randonnée télescopique est parfait."),
            
            ("Mesure de l'ombre",
             "Mesurez la longueur de l'ombre du bout du bâton jusqu'au pied du bâton. "
             "Soyez précis au centimètre près.\n\n"
             "Important : Attendez que l'ombre soit bien nette."),
            
            ("Relevé de l'azimut",
             "Utilisez votre boussole pour mesurer la direction de l'ombre "
             "(du pied du bâton vers la pointe de l'ombre).\n\n"
             "Astuce smartphone : Utilisez une app boussole."),
            
            ("Heure et date précises",
             "Notez l'heure UTC exacte au moment de la mesure.\n\n"
             "Date : Notez la date exacte car la position du soleil varie."),
            
            ("Déclinaison magnétique (optionnel)",
             "Recherchez la déclinaison magnétique de votre région.\n\n"
             "En France métropolitaine : généralement entre 0° et 2° Est."),
            
            ("Calcul",
             "Saisissez toutes vos mesures dans le formulaire ci-dessous et cliquez sur "
             "'Calculer ma position'.\n\n"
             "Précision attendue : ±5-15 km selon la qualité des mesures.")
        ]
        
        for i, (title, desc) in enumerate(steps, 1):
            step_group = QGroupBox(f"Étape {i}: {title}")
            step_layout = QVBoxLayout(step_group)
            
            desc_label = QLabel(desc)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("QLabel { padding: 10px; font-size: 14px; line-height: 1.4; }")
            step_layout.addWidget(desc_label)
            
            scroll_layout.addWidget(step_group)
        
        # Tips section
        tips_group = QGroupBox("Conseils pour une meilleure précision")
        tips_layout = QVBoxLayout(tips_group)
        
        tips = [
            "• Effectuez les mesures quand le soleil est bien visible",
            "• Évitez les surfaces réfléchissantes autour du bâton",
            "• Prenez plusieurs mesures à quelques minutes d'intervalle",
            "• Utilisez un terrain le plus plat possible",
            "• Vérifiez que votre boussole n'est pas influencée par du métal"
        ]
        
        for tip in tips:
            label = QLabel(tip)
            label.setStyleSheet("QLabel { padding: 3px; font-size: 14px; }")
            tips_layout.addWidget(label)
        
        scroll_layout.addWidget(tips_group)
        
        form_group = QGroupBox("Saisie des mesures")
        form_layout = QFormLayout(form_group)
        form_layout.setSpacing(10)
        
        # Stick height
        self.stick_height = QDoubleSpinBox()
        self.stick_height.setDecimals(2)
        self.stick_height.setRange(0.01, 10.0)
        self.stick_height.setValue(1.0)
        self.stick_height.setSuffix(" m")
        form_layout.addRow("Hauteur du bâton:", self.stick_height)
        
        # Shadow length
        self.shadow_length = QDoubleSpinBox()
        self.shadow_length.setDecimals(2)
        self.shadow_length.setRange(0.01, 100.0)
        self.shadow_length.setSuffix(" m")
        form_layout.addRow("Longueur de l'ombre:", self.shadow_length)
        
        # Shadow azimuth
        self.shadow_azimuth = QDoubleSpinBox()
        self.shadow_azimuth.setDecimals(1)
        self.shadow_azimuth.setRange(0, 360)
        self.shadow_azimuth.setSuffix("°")
        form_layout.addRow("Azimut de l'ombre:", self.shadow_azimuth)
        
        # UTC time
        self.utc_time = QTimeEdit()
        self.utc_time.setDisplayFormat("HH:mm")
        current_time = datetime.now(timezone.utc).time()
        self.utc_time.setTime(QTime(current_time.hour, current_time.minute))
        form_layout.addRow("Heure UTC:", self.utc_time)
        
        # Date
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setDisplayFormat("dd/MM/yyyy")
        form_layout.addRow("Date:", self.date_edit)
        
        # Magnetic declination
        self.magnetic_declination = QDoubleSpinBox()
        self.magnetic_declination.setDecimals(1)
        self.magnetic_declination.setRange(-180, 180)
        self.magnetic_declination.setValue(0)
        self.magnetic_declination.setSuffix("°")
        form_layout.addRow("Déclinaison magnétique:", self.magnetic_declination)
        
        scroll_layout.addWidget(form_group)
        
        # Calculate button
        calc_btn = QPushButton("Calculer ma position")
        calc_btn.clicked.connect(self.calculate_position)
        calc_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                                          stop:0 #667eea, stop:1 #764ba2);
                color: white;
                border: none;
                padding: 15px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                min-height: 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                                          stop:0 #5a6fd8, stop:1 #6a4190);
            }
        """)
        scroll_layout.addWidget(calc_btn)
        
        # Results area
        self.results_group = QGroupBox("Résultats")
        results_layout = QVBoxLayout(self.results_group)
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setMaximumHeight(150)
        results_layout.addWidget(self.results_text)
        
        # Copy button
        self.copy_btn = QPushButton("Copier les coordonnées")
        self.copy_btn.clicked.connect(self.copy_coordinates)
        self.copy_btn.setEnabled(False)
        self.copy_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
                min-height: 15px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        results_layout.addWidget(self.copy_btn)
        
        scroll_layout.addWidget(self.results_group)
        self.results_group.hide()
        
        # Set scroll widget
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        # Close button
        close_btn = QPushButton("Fermer")
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 12px 30px;
                border-radius: 5px;
                font-weight: bold;
                min-height: 15px;
            }
            QPushButton:hover {
                background-color: #545b62;
            }
        """)
        layout.addWidget(close_btn, alignment=Qt.AlignCenter)
        
        # Apply styles
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #dee2e6;
                border-radius: 10px;
                margin-top: 1ex;
                padding-top: 15px;
                background-color: white;
                font-size: 14px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                color: #495057;
                font-size: 15px;
            }
            QFormLayout QLabel {
                font-weight: 600;
                color: #444;
                font-size: 14px;
            }
            QDoubleSpinBox, QTimeEdit, QDateEdit {
                padding: 8px;
                border: 2px solid #ddd;
                border-radius: 5px;
                font-size: 14px;
                background-color: white;
                min-height: 20px;
            }
            QDoubleSpinBox:focus, QTimeEdit:focus, QDateEdit:focus {
                border-color: #667eea;
            }
            QTextEdit {
                border: 2px solid #ddd;
                border-radius: 5px;
                background-color: #f8f9fa;
                font-family: 'Courier New', monospace;
                font-size: 13px;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
    
    @pyqtSlot()
    def calculate_position(self):
        # Validate inputs
        if self.shadow_length.value() == 0:
            QMessageBox.warning(self, "Erreur", 
                              "Veuillez remplir tous les champs obligatoires.")
            return
        
        try:
            # Get values
            stick_height = self.stick_height.value()
            shadow_length = self.shadow_length.value()
            shadow_azimuth = self.shadow_azimuth.value()
            utc_time = self.utc_time.time()
            date = self.date_edit.date()
            magnetic_declination = self.magnetic_declination.value()
            
            # Calculate position
            results = SolarGeolocationCalculator.calculate_position(
                stick_height, shadow_length, shadow_azimuth,
                utc_time, date, magnetic_declination
            )
            
            self.display_results(results)
            
        except Exception as e:
            QMessageBox.critical(self, "Erreur de calcul", 
                               f"Une erreur s'est produite lors du calcul:\n{str(e)}")
    
    def display_results(self, results):
        results_text = f"""Position estimée:
Latitude: {results['latitude']:.4f}°
Longitude: {results['longitude']:.4f}°

Coordonnées pour copie: {results['latitude']:.4f}, {results['longitude']:.4f}
"""
        
        self.results_text.setPlainText(results_text)
        self.results_group.show()
        self.copy_btn.setEnabled(True)
        
        # Store coordinates for copying
        self.current_coordinates = f"{results['latitude']:.4f}, {results['longitude']:.4f}"
    
    @pyqtSlot()
    def copy_coordinates(self):
        if hasattr(self, 'current_coordinates'):
            clipboard = QApplication.clipboard()
            clipboard.setText(self.current_coordinates)
            
            # Show confirmation
            self.copy_btn.setText("Copié !")
            
            # Reset button after 2 seconds
            QTimer.singleShot(2000, self.reset_copy_button)
    
    def reset_copy_button(self):
        self.copy_btn.setText("Copier les coordonnées")


class SolarShadowApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setFixedSize(120, 40)
        
        # Position sur la carte
        self.move(35, 10)
        
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.X11BypassWindowManagerHint
        )
        
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        central_widget.setAttribute(Qt.WA_TranslucentBackground, True)
        central_widget.setStyleSheet("background: transparent;")
        
        # Layout sans marges ni espacement
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Bouton principal
        tutorial_btn = QPushButton("Tutoriel")
        tutorial_btn.clicked.connect(self.show_tutorial)
        tutorial_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                                          stop:0 #667eea, stop:1 #764ba2);
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
                min-height: 25px;
                /* Supprimer toute marge ou border */
                margin: 0px;
                border: 0px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                                          stop:0 #5a6fd8, stop:1 #6a4190);
                transform: translateY(-1px);
            }
            QPushButton:pressed {
                transform: translateY(1px);
            }
        """)
        main_layout.addWidget(tutorial_btn)
        
        self.setStyleSheet("""
            QMainWindow {
                background: transparent;
                border: none;
            }
        """)
    
    @pyqtSlot()
    def show_tutorial(self):
        dialog = TutorialDialog(self)
        dialog.exec_()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = SolarShadowApp()
    window.show()
    
    sys.exit(app.exec_())
