import sys
import os
import requests
import random
import time
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                               QProgressBar, QTextEdit, QFrame, QSpacerItem, 
                               QSizePolicy, QGraphicsDropShadowEffect, QFileDialog)
from PySide6.QtCore import (Qt, QThread, QTimer, QPropertyAnimation, QEasingCurve, 
                            QRect, QParallelAnimationGroup, QSequentialAnimationGroup,
                            Signal, QSize, QSettings, QStandardPaths)
from PySide6.QtGui import QFont, QPalette, QColor, QPixmap, QIcon

class DownloadThread(QThread):
    """Hilo separado para manejar la descarga sin bloquear la UI"""
    progress_updated = Signal(int)
    status_updated = Signal(str, str)  # mensaje, tipo (success, error, info)
    download_finished = Signal(dict)
    
    def __init__(self, url, download_path):
        super().__init__()
        self.url = url
        self.download_path = download_path
        
    def run(self):
        """Ejecuta la descarga en un hilo separado"""
        try:
            self.status_updated.emit("Procesando URL...", "info")
            self.progress_updated.emit(20)
            
            # Extraer datos de la URL (lógica original)
            getdataclean1 = self.url.split('/')[-3]
            getdataclean2 = self.url.split('?')[0]
            getdataclean3 = getdataclean2.split('/')[-1]
            
            self.progress_updated.emit(40)
            self.status_updated.emit("Conectando al servidor...", "info")
            
            # User agents para evitar bloqueos
            userAgent = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.10240",
                "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
                "Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko",
                "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
                "Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko",
            ]
            
            headers = {"User-Agent": random.choice(userAgent)}
            
            self.progress_updated.emit(60)
            self.status_updated.emit("Descargando video...", "info")
            
            # Realizar la descarga
            response = requests.get(f"https://tikcdn.io/ssstik/{getdataclean3}", headers=headers)
            
            if response.status_code == 200:
                self.progress_updated.emit(80)
                
                # Usar la carpeta seleccionada por el usuario
                downloads_dir = Path(self.download_path)
                downloads_dir.mkdir(parents=True, exist_ok=True)
                
                # Guardar el video
                filename = f"video_{getdataclean1}_by_Stivion.mp4"
                filepath = downloads_dir / filename
                
                with open(filepath, "wb") as video:
                    video.write(response.content)
                
                self.progress_updated.emit(100)
                self.status_updated.emit("¡Descarga completada!", "success")
                
                result = {
                    "username": getdataclean1,
                    "idVideo": getdataclean3,
                    "filepath": str(filepath),
                    "filename": filename
                }
                
                self.download_finished.emit(result)
                
            else:
                self.status_updated.emit("Error: Servidor no disponible", "error")
                
        except Exception as e:
            self.status_updated.emit(f"Error: {str(e)}", "error")

class AnimatedButton(QPushButton):
    """Botón personalizado con animaciones"""
    
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setupUI()
        self.setupAnimations()
        
    def setupUI(self):
        """Configurar el estilo del botón"""
        self.setMinimumHeight(40)  # Reducido de 50 a 40
        self.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))  # Reducido de 12 a 11
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Estilo CSS moderno
        self.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4A90E2, stop:1 #357ABD);
                border: none;
                border-radius: 20px;
                color: white;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5BA0F2, stop:1 #4A90E2);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #357ABD, stop:1 #2E6BA8);
            }
            QPushButton:disabled {
                background: #CCCCCC;
                color: #666666;
            }
        """)
        
        # Sombra
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)  # Reducido de 15 a 10
        shadow.setColor(QColor(0, 0, 0, 60))  # Reducido de 80 a 60
        shadow.setOffset(0, 2)  # Reducido de 3 a 2
        self.setGraphicsEffect(shadow)
        
    def setupAnimations(self):
        """Configurar animaciones del botón"""
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(150)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
    def enterEvent(self, event):
        """Animación al pasar el mouse por encima"""
        current_rect = self.geometry()
        new_rect = QRect(current_rect.x(), current_rect.y() - 1, 
                        current_rect.width(), current_rect.height())
        
        self.animation.setStartValue(current_rect)
        self.animation.setEndValue(new_rect)
        self.animation.start()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        """Animación al quitar el mouse"""
        current_rect = self.geometry()
        new_rect = QRect(current_rect.x(), current_rect.y() + 1, 
                        current_rect.width(), current_rect.height())
        
        self.animation.setStartValue(current_rect)
        self.animation.setEndValue(new_rect)
        self.animation.start()
        super().leaveEvent(event)

class TikTokDownloaderGUI(QMainWindow):
    """Ventana principal de la aplicación"""
    
    def __init__(self):
        super().__init__()
        self.download_thread = None
        self.settings = QSettings("Stivionllc", "Stivion")
        self.setupUI()
        self.setupAnimations()
        self.load_settings()
        
    def setupUI(self):
        """Configurar la interfaz de usuario"""
        self.setWindowTitle("Stivion - TikTok Video Downloader")
        # Configurar tamaño de ventana más compacto
        self.setMinimumSize(550, 600)  # Reducido
        self.setMaximumSize(1000, 800)  # Reducido
        self.resize(650, 650)  # Tamaño inicial más pequeño
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1e3c72, stop:1 #2a5298);
            }
        """)
        # Permitir redimensionar
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowMaximizeButtonHint)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal con menos espaciado
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(12)  # Reducido de 20 a 12
        main_layout.setContentsMargins(25, 25, 25, 25)  # Reducido de 40 a 25
        
        # Header con logo y título
        self.create_header(main_layout)
        
        # Espaciador pequeño
        main_layout.addItem(QSpacerItem(10, 10, QSizePolicy.Policy.Minimum, 
                                       QSizePolicy.Policy.Expanding))
        
        # Área de entrada de URL
        self.create_url_input(main_layout)

        # Selector de carpeta de descarga
        self.create_download_path_selector(main_layout)
        
        # Botón de descarga
        self.create_download_button(main_layout)
        
        # Barra de progreso
        self.create_progress_bar(main_layout)
        
        # Área de estado/mensajes
        self.create_status_area(main_layout)
        
        # Espaciador final pequeño
        main_layout.addItem(QSpacerItem(10, 20, QSizePolicy.Policy.Minimum, 
                                       QSizePolicy.Policy.Expanding))
        
    def create_header(self, layout):
        """Crear el header con título y logo"""
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 15px;
            }
        """)
        
        header_layout = QVBoxLayout(header_frame)
        header_layout.setSpacing(8)  # Reducido
        
        # Botones de control de tamaño (más pequeños)
        size_controls_layout = QHBoxLayout()
        size_controls_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        size_controls_layout.setSpacing(8)

        self.compact_btn = QPushButton("📱 Compacto")
        self.compact_btn.setMinimumSize(80, 28)  # Más pequeño
        self.compact_btn.setFont(QFont("Segoe UI", 8))  # Fuente más pequeña
        self.compact_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 14px;
                color: white;
                padding: 4px 8px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.3);
            }
        """)
        self.compact_btn.clicked.connect(self.set_compact_mode)

        self.large_btn = QPushButton("🖥️ Grande")
        self.large_btn.setMinimumSize(80, 28)
        self.large_btn.setFont(QFont("Segoe UI", 8))
        self.large_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 14px;
                color: white;
                padding: 4px 8px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.3);
            }
        """)
        self.large_btn.clicked.connect(self.set_large_mode)

        self.fullscreen_btn = QPushButton("⛶ Pantalla")
        self.fullscreen_btn.setMinimumSize(90, 28)
        self.fullscreen_btn.setFont(QFont("Segoe UI", 8))
        self.fullscreen_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 14px;
                color: white;
                padding: 4px 8px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.3);
            }
        """)
        self.fullscreen_btn.clicked.connect(self.toggle_fullscreen)

        size_controls_layout.addWidget(self.compact_btn)
        size_controls_layout.addWidget(self.large_btn)
        size_controls_layout.addWidget(self.fullscreen_btn)

        # Título principal (más pequeño)
        title_label = QLabel("Stivion")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))  # Reducido de 28 a 22
        title_label.setStyleSheet("color: #00FFFF; margin: 5px;")
        
        # Subtítulo (más pequeño)
        subtitle_label = QLabel("TikTok Video Downloader")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setFont(QFont("Segoe UI", 12))  # Reducido de 14 a 12
        subtitle_label.setStyleSheet("color: white; margin-bottom: 5px;")
        
        # Créditos (más pequeños)
        credits_label = QLabel("Develop by K1LLU")
        credits_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        credits_label.setFont(QFont("Segoe UI", 9))  # Reducido de 10 a 9
        credits_label.setStyleSheet("color: #CCCCCC;")
        
        # Agregar todo al layout
        header_layout.addLayout(size_controls_layout)
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        header_layout.addWidget(credits_label)
        
        layout.addWidget(header_frame)
        
    def create_url_input(self, layout):
        """Crear el área de entrada de URL"""
        url_frame = QFrame()
        url_frame.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 15px;
            }
        """)
        
        url_layout = QVBoxLayout(url_frame)
        url_layout.setSpacing(8)  # Reducido
        
        # Etiqueta
        url_label = QLabel("Ingresa el enlace de TikTok:")
        url_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))  # Reducido de 12 a 10
        url_label.setStyleSheet("color: white; margin-bottom: 5px;")
        
        # Campo de entrada
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://www.tiktok.com/@usuario/video/...")
        self.url_input.setMinimumHeight(38)  # Reducido de 45 a 38
        self.url_input.setFont(QFont("Segoe UI", 10))  # Reducido de 11 a 10
        self.url_input.setStyleSheet("""
            QLineEdit {
                background: white;
                border: 2px solid #4A90E2;
                border-radius: 19px;
                padding: 8px 12px;
                color: #333333;
            }
            QLineEdit:focus {
                border: 2px solid #00FFFF;
                background: #F8F9FA;
            }
        """)
        
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        
        layout.addWidget(url_frame)
        
    def create_download_path_selector(self, layout):
        """Crear el selector de carpeta de descarga"""
        path_frame = QFrame()
        path_frame.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 15px;
            }
        """)
        
        path_layout = QVBoxLayout(path_frame)
        path_layout.setSpacing(8)  # Reducido
        
        # Etiqueta
        path_label = QLabel("Carpeta de descarga:")
        path_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))  # Reducido
        path_label.setStyleSheet("color: white; margin-bottom: 5px;")
        
        # Campo de ruta
        self.path_input = QLineEdit()
        self.path_input.setReadOnly(True)
        self.path_input.setMinimumHeight(38)  # Reducido
        self.path_input.setFont(QFont("Segoe UI", 9))  # Reducido
        self.path_input.setStyleSheet("""
            QLineEdit {
                background: rgba(255, 255, 255, 0.9);
                border: 2px solid #4A90E2;
                border-radius: 19px;
                padding: 8px 12px;
                color: #333333;
                margin-bottom: 8px;
            }
        """)
        
        # Layout horizontal para los botones
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)  # Reducido
        
        # Botón para seleccionar carpeta
        self.browse_btn = QPushButton("📁 Explorar")
        self.browse_btn.setMinimumHeight(38)  # Reducido
        self.browse_btn.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))  # Reducido
        self.browse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.browse_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.browse_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #28a745, stop:1 #1e7e34);
                border: none;
                border-radius: 19px;
                color: white;
                padding: 8px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #34ce57, stop:1 #28a745);
                }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1e7e34, stop:1 #155724);
            }
        """)
        self.browse_btn.clicked.connect(self.select_download_folder)
        
        # Botón para abrir carpeta
        self.open_folder_btn = QPushButton("🗂️ Abrir")
        self.open_folder_btn.setMinimumHeight(38)  # Reducido
        self.open_folder_btn.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))  # Reducido
        self.open_folder_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.open_folder_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.open_folder_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffc107, stop:1 #e0a800);
                border: none;
                border-radius: 19px;
                color: white;
                padding: 8px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffcd39, stop:1 #ffc107);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e0a800, stop:1 #d39e00);
            }
        """)
        self.open_folder_btn.clicked.connect(self.open_download_folder)
        
        # Agregar botones al layout horizontal
        buttons_layout.addWidget(self.browse_btn)
        buttons_layout.addWidget(self.open_folder_btn)
        
        # Agregar todo al layout principal
        path_layout.addWidget(path_label)
        path_layout.addWidget(self.path_input)
        path_layout.addLayout(buttons_layout)
        
        layout.addWidget(path_frame)
        
    def create_download_button(self, layout):
        """Crear el botón de descarga"""
        self.download_btn = AnimatedButton("🚀 Descargar Video")
        self.download_btn.clicked.connect(self.start_download)
        layout.addWidget(self.download_btn)
        
    def create_progress_bar(self, layout):
        """Crear la barra de progreso"""
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimumHeight(20)  # Reducido de 25 a 20
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background: rgba(255, 255, 255, 0.2);
                border: none;
                border-radius: 10px;
                text-align: center;
                color: white;
                font-weight: bold;
                font-size: 10px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00FFFF, stop:1 #4A90E2);
                border-radius: 10px;
            }
        """)
        
        layout.addWidget(self.progress_bar)
        
    def create_status_area(self, layout):
        """Crear el área de estado y mensajes"""
        status_frame = QFrame()
        status_frame.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 15px;
            }
        """)
        
        status_layout = QVBoxLayout(status_frame)
        
        # Área de mensajes (más pequeña)
        self.status_text = QTextEdit()
        self.status_text.setMinimumHeight(80)  # Reducido de 120
        self.status_text.setMaximumHeight(200)  # Reducido de 300
        self.status_text.setReadOnly(True)
        self.status_text.setFont(QFont("Consolas", 9))  # Reducido de 10 a 9
        self.status_text.setStyleSheet("""
            QTextEdit {
                background: rgba(0, 0, 0, 0.3);
                border: 1px solid #4A90E2;
                border-radius: 8px;
                color: white;
                padding: 8px;
            }
        """)
        
        status_layout.addWidget(self.status_text)
        layout.addWidget(status_frame)
        
    def setupAnimations(self):
        """Configurar animaciones de la ventana"""
        # Animación de entrada
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(500)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
    def showEvent(self, event):
        """Ejecutar animación al mostrar la ventana"""
        super().showEvent(event)
        self.fade_animation.start()
        
    def select_download_folder(self):
        """Abrir diálogo para seleccionar carpeta de descarga"""
        current_path = self.path_input.text() or str(Path.home() / "Downloads")
        
        folder = QFileDialog.getExistingDirectory(
            self,
            "Seleccionar carpeta de descarga",
            current_path,
            QFileDialog.Option.ShowDirsOnly
        )
        
        if folder:
            self.path_input.setText(folder)
            self.settings.setValue("download_path", folder)
            self.show_status(f"📁 Carpeta seleccionada: {folder}", "info")

    def open_download_folder(self):
        """Abrir la carpeta de descarga en el explorador"""
        path = self.path_input.text()
        if path and Path(path).exists():
            import subprocess
            import platform
            
            try:
                if platform.system() == "Windows":
                    subprocess.run(["explorer", path])
                elif platform.system() == "Darwin":  # macOS
                    subprocess.run(["open", path])
                else:  # Linux
                    subprocess.run(["xdg-open", path])
                
                self.show_status("🗂️ Carpeta abierta en el explorador", "info")
            except Exception as e:
                self.show_status(f"❌ Error al abrir carpeta: {str(e)}", "error")
        else:
            self.show_status("❌ La carpeta no existe", "error")

    def load_settings(self):
        """Cargar configuraciones guardadas"""
        # Cargar carpeta de descarga guardada o usar por defecto
        default_path = str(Path.home() / "Downloads" / "TikTok_Videos")
        saved_path = self.settings.value("download_path", default_path)
        self.path_input.setText(saved_path)
        
        # Crear la carpeta si no existe
        Path(saved_path).mkdir(parents=True, exist_ok=True)
        
        # Cargar tamaño y posición de ventana
        if self.settings.value("window_size"):
            self.resize(self.settings.value("window_size"))
        if self.settings.value("window_position"):
            self.move(self.settings.value("window_position"))
        
    def start_download(self):
        """Iniciar el proceso de descarga"""
        url = self.url_input.text().strip()
        download_path = self.path_input.text().strip()
        
        if not url:
            self.show_status("❌ Por favor ingresa una URL válida", "error")
            return
            
        if "tiktok.com" not in url:
            self.show_status("❌ La URL debe ser de TikTok", "error")
            return
        
        if not download_path:
            self.show_status("❌ Por favor selecciona una carpeta de descarga", "error")
            return
        
        # Deshabilitar botón y mostrar progreso
        self.download_btn.setEnabled(False)
        self.download_btn.setText("⏳ Descargando...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Limpiar mensajes anteriores
        self.status_text.clear()
        
        # Iniciar descarga en hilo separado con la ruta personalizada
        self.download_thread = DownloadThread(url, download_path)
        self.download_thread.progress_updated.connect(self.update_progress)
        self.download_thread.status_updated.connect(self.show_status)
        self.download_thread.download_finished.connect(self.download_completed)
        self.download_thread.start()
        
    def update_progress(self, value):
        """Actualizar la barra de progreso"""
        self.progress_bar.setValue(value)
        
    def show_status(self, message, status_type):
        """Mostrar mensaje de estado con colores"""
        colors = {
            "info": "#00FFFF",
            "success": "#00FF00", 
            "error": "#FF4444"
        }
        
        color = colors.get(status_type, "#FFFFFF")
        timestamp = time.strftime("%H:%M:%S")
        
        formatted_message = f'<span style="color: {color};">[{timestamp}] {message}</span>'
        self.status_text.append(formatted_message)
        
        # Auto-scroll al final
        cursor = self.status_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.status_text.setTextCursor(cursor)
        
    def download_completed(self, result):
        """Manejar la finalización de la descarga"""
        # Restaurar botón
        self.download_btn.setEnabled(True)
        self.download_btn.setText("🚀 Descargar Video")
        
        # Mostrar información del video descargado
        info_message = f"""
✅ <b>Descarga Completada</b><br>
👤 <b>Usuario:</b> {result['username']}<br>
🆔 <b>ID Video:</b> {result['idVideo']}<br>
📁 <b>Guardado en:</b> {result['filepath']}<br>
📄 <b>Archivo:</b> {result['filename']}
        """
        
        self.show_status("🎉 ¡Video descargado exitosamente!", "success")
        self.status_text.append(f'<div style="background: rgba(0, 255, 0, 0.1); padding: 8px; border-radius: 4px; margin: 4px 0;">{info_message}</div>')
        
        # Ocultar barra de progreso después de un momento
        QTimer.singleShot(2000, lambda: self.progress_bar.setVisible(False))
        
        # Limpiar campo de URL
        self.url_input.clear()

    def set_compact_mode(self):
        """Cambiar a modo compacto"""
        self.showNormal()
        self.resize(550, 600)  # Más pequeño
        self.show_status("📱 Modo compacto activado", "info")
        
    def set_large_mode(self):
        """Cambiar a modo grande"""
        self.showNormal()
        self.resize(800, 750)  # Más pequeño que antes
        self.show_status("🖥️ Modo grande activado", "info")
        
    def toggle_fullscreen(self):
        """Alternar pantalla completa"""
        if self.isFullScreen():
            self.showNormal()
            self.show_status("🪟 Modo ventana activado", "info")
            self.fullscreen_btn.setText("⛶ Pantalla")
        else:
            self.showFullScreen()
            self.show_status("⛶ Pantalla completa activada", "info")
            self.fullscreen_btn.setText("🪟 Ventana")

    def keyPressEvent(self, event):
        """Manejar teclas de acceso rápido"""
        if event.key() == Qt.Key.Key_F11:
            self.toggle_fullscreen()
        elif event.key() == Qt.Key.Key_Escape and self.isFullScreen():
            self.showNormal()
            self.fullscreen_btn.setText("⛶ Pantalla")
        super().keyPressEvent(event)

    def resizeEvent(self, event):
        """Manejar redimensionamiento de ventana"""
        super().resizeEvent(event)
        # Guardar el tamaño de ventana
        self.settings.setValue("window_size", self.size())
        self.settings.setValue("window_position", self.pos())

def main():
    """Función principal"""
    app = QApplication(sys.argv)
    
    # Configurar la aplicación
    app.setApplicationName("Stivio - TikTok Downloader")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("Stivionllc")
    
    # Crear y mostrar la ventana principal
    window = TikTokDownloaderGUI()
    window.show()
    
    # Ejecutar la aplicación
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
