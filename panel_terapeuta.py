"""
PANEL DE TERAPEUTA MODERNO
Interfaz de administración con diseño moderno usando pestañas
Optimizado para resolución 1024x600
Diseño profesional, amigable y con colores modernos
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
from typing import List, Optional
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from database import Database
from models import NivelTerapia, Persona


class PanelTerapeuta:
    """Panel de administración moderno con diseño de pestañas"""
    
    def __init__(self, db: Database, audio_system=None):
        self.db = db
        self.audio = audio_system
        self.ventana = None
        self.persona_seleccionada = None
        self.modo_admin_activo = True
        
        # 🎨 PALETA DE COLORES MODERNA Y PROFESIONAL
        self.colores = {
            # Colores principales
            'primary': '#4A90E2',      # Azul profesional
            'primary_dark': '#357ABD', # Azul oscuro
            'secondary': '#7B68EE',    # Púrpura moderno
            'accent': '#50C878',       # Verde esmeralda
            
            # Fondos
            'bg_main': '#F8F9FA',      # Gris muy claro
            'bg_card': '#FFFFFF',      # Blanco puro
            'bg_header': '#2C3E50',    # Azul oscuro elegante
            
            # Estados
            'success': '#10B981',      # Verde éxito
            'warning': '#F59E0B',      # Naranja advertencia
            'error': '#EF4444',        # Rojo error
            'info': '#3B82F6',         # Azul info
            
            # Tabs
            'tab_info': '#4A90E2',     # Azul
            'tab_terapia': '#7B68EE',  # Púrpura
            'tab_progreso': '#10B981', # Verde
            'tab_historial': '#F59E0B',# Naranja
            
            # Texto
            'text_dark': '#1F2937',    # Gris oscuro
            'text_medium': '#6B7280',  # Gris medio
            'text_light': '#9CA3AF',   # Gris claro
            'text_white': '#FFFFFF',   # Blanco
            
            # Bordes
            'border_light': '#E5E7EB', # Borde claro
            'border_medium': '#D1D5DB',# Borde medio
        }
        
        # Widgets principales
        self.tree_usuarios = None
        self.notebook = None  # Pestañas principales
        
        # Widgets por pestaña
        self.tabs = {}
        self.widgets = {}
    
    def crear(self):
        """Crear ventana del panel moderno"""
        self.ventana = tk.Toplevel()
        self.ventana.title("Panel de Terapeuta - Robot DODO")
        
        # 📐 OPTIMIZADO PARA 1024x600
        self.ventana.geometry("1024x600")
        self.ventana.configure(bg=self.colores['bg_main'])
        
        # Centrar en pantalla
        self.ventana.update_idletasks()
        width = 1024
        height = 600
        x = (self.ventana.winfo_screenwidth() // 2) - (width // 2)
        y = (self.ventana.winfo_screenheight() // 2) - (height // 2)
        self.ventana.geometry(f'{width}x{height}+{x}+{y}')
        
        # Evento de cierre
        self.ventana.protocol("WM_DELETE_WINDOW", self.cerrar)
        
        # Iniciar escucha por voz si hay audio
        if self.audio:
            import threading
            self.hilo_escucha_admin = threading.Thread(
                target=self._escuchar_comandos_voz,
                daemon=True
            )
            self.hilo_escucha_admin.start()
        
        # 🎨 Crear interfaz
        self._crear_header_moderno()
        self._crear_layout_principal()
        
        # Cargar datos iniciales
        self.cargar_usuarios()
    
    def _escuchar_comandos_voz(self):
        """Escuchar comandos de voz para salir del panel"""
        import time
        
        # ✅ Import FUERA del loop para detectar errores
        try:
            from chatopenai import detectar_salir_panel
        except Exception as e:
            print(f"❌ [Panel Admin] Error importando detectar_salir_panel: {e}")
            return
        
        print("🎤 [Panel Admin] Escucha de voz iniciada")
        print("   Di 'salir' o 'cerrar' para salir del panel")
        
        while self.modo_admin_activo:
            try:
                print("🎤 [Panel Admin] Escuchando...")
                
                texto = self.audio.escuchar(timeout=2, phrase_time_limit=5)
                
                if not self.modo_admin_activo:
                    break
                
                if texto:
                    print(f"🎤 [Panel Admin] Escuché: '{texto}'")
                    
                    if detectar_salir_panel(texto):
                        print("🚪 [Panel Admin] Detectado comando de salida")
                        self.audio.hablar("Cerrando panel de administrador.")
                        self.ventana.after(100, self.cerrar)
                        break
                else:
                    print("🎤 [Panel Admin] Silencio o timeout")
            
            except Exception as e:
                # ✅ Ahora SÍ muestra el error en lugar de ocultarlo
                print(f"⚠️ [Panel Admin] Error en escucha: {e}")
                time.sleep(1)
            
            time.sleep(0.3)
        
        print("🔇 [Panel Admin] Escucha finalizada")
    
    def _crear_header_moderno(self):
        """Crear header moderno y compacto"""
        frame_header = tk.Frame(
            self.ventana, 
            bg=self.colores['bg_header'], 
            height=60
        )
        frame_header.pack(fill='x')
        frame_header.pack_propagate(False)
        
        # Contenedor interno para centrar
        container = tk.Frame(frame_header, bg=self.colores['bg_header'])
        container.pack(fill='both', expand=True, padx=20)
        
        # Título con icono
        label_titulo = tk.Label(
            container,
            text="🩺 Panel de Terapeuta",
            font=('Segoe UI', 18, 'bold'),
            bg=self.colores['bg_header'],
            fg=self.colores['text_white']
        )
        label_titulo.pack(side='left', pady=15)
        
        # Información compacta del sistema
        info_db = self.db.verificar_integridad()
        texto_info = f"👥 {info_db.get('personas', 0)} Pacientes  •  📊 {info_db.get('sesiones', 0)} Sesiones"
        
        label_info = tk.Label(
            container,
            text=texto_info,
            font=('Segoe UI', 10),
            bg=self.colores['bg_header'],
            fg=self.colores['text_light']
        )
        label_info.pack(side='right', pady=15)
    
    def _crear_layout_principal(self):
        """Crear layout principal con lista y pestañas"""
        # Frame principal
        frame_main = tk.Frame(self.ventana, bg=self.colores['bg_main'])
        frame_main.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 📋 PANEL IZQUIERDO: Lista de pacientes (30% del ancho)
        self._crear_panel_lista(frame_main)
        
        # 📑 PANEL DERECHO: Pestañas con detalles (70% del ancho)
        self._crear_panel_pestanas(frame_main)
    
    def _crear_panel_lista(self, parent):
        """Crear panel de lista de pacientes"""
        frame_lista = tk.Frame(parent, bg=self.colores['bg_main'])
        frame_lista.pack(side='left', fill='both', padx=(0, 10))
        frame_lista.configure(width=300)
        
        # Card contenedor
        card = tk.Frame(
            frame_lista,
            bg=self.colores['bg_card'],
            relief='flat',
            bd=0
        )
        card.pack(fill='both', expand=True)
        
        # Agregar borde sutil
        card.configure(highlightbackground=self.colores['border_light'], highlightthickness=1)
        
        # Título
        frame_titulo = tk.Frame(card, bg=self.colores['bg_card'])
        frame_titulo.pack(fill='x', padx=15, pady=(15, 10))
        
        tk.Label(
            frame_titulo,
            text="📋 Pacientes",
            font=('Segoe UI', 13, 'bold'),
            bg=self.colores['bg_card'],
            fg=self.colores['text_dark']
        ).pack(side='left')
        
        # Botón actualizar
        btn_refresh = tk.Button(
            frame_titulo,
            text="🔄",
            font=('Segoe UI', 11),
            bg=self.colores['bg_card'],
            fg=self.colores['primary'],
            relief='flat',
            bd=0,
            cursor='hand2',
            command=self.cargar_usuarios
        )
        btn_refresh.pack(side='right')
        
        # Frame para Treeview
        frame_tree = tk.Frame(card, bg=self.colores['bg_card'])
        frame_tree.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_tree)
        scrollbar.pack(side='right', fill='y')
        
        # Treeview con estilo moderno
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(
            "Treeview",
            background=self.colores['bg_card'],
            foreground=self.colores['text_dark'],
            fieldbackground=self.colores['bg_card'],
            borderwidth=0,
            font=('Segoe UI', 9)
        )
        style.configure("Treeview.Heading", font=('Segoe UI', 9, 'bold'))
        style.map('Treeview', background=[('selected', self.colores['primary'])])
        
        columnas = ('Nombre', 'Nivel')
        self.tree_usuarios = ttk.Treeview(
            frame_tree,
            columns=columnas,
            show='headings',
            yscrollcommand=scrollbar.set,
            selectmode='browse',
            height=16
        )
        
        self.tree_usuarios.heading('Nombre', text='Nombre')
        self.tree_usuarios.heading('Nivel', text='Nivel')
        
        self.tree_usuarios.column('Nombre', width=180)
        self.tree_usuarios.column('Nivel', width=80)
        
        self.tree_usuarios.pack(fill='both', expand=True)
        scrollbar.config(command=self.tree_usuarios.yview)
        
        # Evento de selección
        self.tree_usuarios.bind('<<TreeviewSelect>>', self.on_seleccionar_usuario)
    
    def _crear_panel_pestanas(self, parent):
        """Crear panel de pestañas moderno"""
        frame_pestanas = tk.Frame(parent, bg=self.colores['bg_main'])
        frame_pestanas.pack(side='right', fill='both', expand=True)
        
        # Configurar estilo de pestañas
        style = ttk.Style()
        style.configure(
            'Modern.TNotebook',
            background=self.colores['bg_main'],
            borderwidth=0
        )
        style.configure(
            'Modern.TNotebook.Tab',
            padding=[20, 10],
            font=('Segoe UI', 10, 'bold'),
            background=self.colores['bg_card'],
            foreground=self.colores['text_medium']
        )
        style.map(
            'Modern.TNotebook.Tab',
            background=[('selected', self.colores['bg_card'])],
            foreground=[('selected', self.colores['primary'])],
            expand=[('selected', [1, 1, 1, 0])]
        )
        
        # Crear Notebook
        self.notebook = ttk.Notebook(frame_pestanas, style='Modern.TNotebook')
        self.notebook.pack(fill='both', expand=True)
        
        # 🎨 Crear 4 pestañas
        self._crear_tab_informacion()
        self._crear_tab_terapia()
        self._crear_tab_progreso()
        self._crear_tab_historial()
        
        # Mostrar mensaje inicial
        self._mostrar_mensaje_inicial()
    
    def _crear_tab_informacion(self):
        """Tab 1: Información del Paciente"""
        tab = tk.Frame(self.notebook, bg=self.colores['bg_main'])
        self.notebook.add(tab, text='👤 Información')
        self.tabs['info'] = tab
        
        # Canvas con scroll
        canvas = tk.Canvas(tab, bg=self.colores['bg_main'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(tab, orient='vertical', command=canvas.yview)
        frame_contenido = tk.Frame(canvas, bg=self.colores['bg_main'])
        
        frame_contenido.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
        )
        
        canvas.create_window((0, 0), window=frame_contenido, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y')
        
        self.widgets['frame_info'] = frame_contenido
        
        # Card de información
        self._crear_card_informacion(frame_contenido)
    
    def _crear_card_informacion(self, parent):
        """Crear card de información del paciente"""
        card = self._crear_card(parent, "Datos del Paciente")
        
        # Contenedor de datos
        frame_datos = tk.Frame(card, bg=self.colores['bg_card'])
        frame_datos.pack(fill='x', padx=20, pady=10)
        
        # Función helper para crear fila de dato
        def crear_fila_dato(texto_label, row):
            frame = tk.Frame(frame_datos, bg=self.colores['bg_card'])
            frame.grid(row=row, column=0, columnspan=2, sticky='ew', pady=8)
            
            tk.Label(
                frame,
                text=texto_label,
                font=('Segoe UI', 10, 'bold'),
                bg=self.colores['bg_card'],
                fg=self.colores['text_medium'],
                width=12,
                anchor='w'
            ).pack(side='left')
            
            label_valor = tk.Label(
                frame,
                text="",
                font=('Segoe UI', 11),
                bg=self.colores['bg_card'],
                fg=self.colores['text_dark'],
                anchor='w'
            )
            label_valor.pack(side='left', fill='x', expand=True)
            
            return label_valor
        
        # Crear campos
        self.widgets['label_nombre'] = crear_fila_dato("Nombre:", 0)
        self.widgets['label_apellido'] = crear_fila_dato("Apellido:", 1)
        self.widgets['label_dni'] = crear_fila_dato("DNI:", 2)
        self.widgets['label_edad'] = crear_fila_dato("Edad:", 3)
        self.widgets['label_sexo'] = crear_fila_dato("Sexo:", 4)
        self.widgets['label_fecha'] = crear_fila_dato("Registro:", 5)
        
        frame_datos.columnconfigure(0, weight=1)
        
        # Botón de edición
        frame_btn = tk.Frame(card, bg=self.colores['bg_card'])
        frame_btn.pack(fill='x', padx=20, pady=(10, 20))
        
        btn_editar = tk.Button(
            frame_btn,
            text="✏️ Editar Información",
            font=('Segoe UI', 11, 'bold'),
            bg=self.colores['primary'],
            fg=self.colores['text_white'],
            relief='flat',
            bd=0,
            padx=25,
            pady=12,
            cursor='hand2',
            command=self.abrir_ventana_edicion
        )
        btn_editar.pack()
        
        # Efecto hover
        btn_editar.bind('<Enter>', lambda e: btn_editar.config(bg=self.colores['primary_dark']))
        btn_editar.bind('<Leave>', lambda e: btn_editar.config(bg=self.colores['primary']))
    
    def _crear_tab_terapia(self):
        """Tab 2: Gestión de Terapia"""
        tab = tk.Frame(self.notebook, bg=self.colores['bg_main'])
        self.notebook.add(tab, text='🎯 Terapia')
        self.tabs['terapia'] = tab
        
        # Canvas con scroll
        canvas = tk.Canvas(tab, bg=self.colores['bg_main'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(tab, orient='vertical', command=canvas.yview)
        frame_contenido = tk.Frame(canvas, bg=self.colores['bg_main'])
        
        frame_contenido.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
        )
        
        canvas.create_window((0, 0), window=frame_contenido, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y')
        
        self.widgets['frame_terapia'] = frame_contenido
        
        # Cards
        self._crear_card_nivel(frame_contenido)
        self._crear_card_observaciones(frame_contenido)
    
    def _crear_card_nivel(self, parent):
        """Crear card de gestión de nivel"""
        card = self._crear_card(parent, "Nivel Terapéutico Actual")
        
        # Nivel actual (grande y destacado)
        frame_nivel = tk.Frame(card, bg=self.colores['bg_card'])
        frame_nivel.pack(fill='x', padx=20, pady=15)
        
        tk.Label(
            frame_nivel,
            text="Nivel:",
            font=('Segoe UI', 11),
            bg=self.colores['bg_card'],
            fg=self.colores['text_medium']
        ).pack()
        
        self.widgets['label_nivel'] = tk.Label(
            frame_nivel,
            text="",
            font=('Segoe UI', 24, 'bold'),
            bg=self.colores['bg_card'],
            fg=self.colores['primary']
        )
        self.widgets['label_nivel'].pack(pady=5)
        
        # Separador
        tk.Frame(card, bg=self.colores['border_light'], height=1).pack(fill='x', padx=20, pady=10)
        
        # Selector de nuevo nivel
        frame_cambio = tk.Frame(card, bg=self.colores['bg_card'])
        frame_cambio.pack(fill='x', padx=20, pady=10)
        
        tk.Label(
            frame_cambio,
            text="Cambiar a:",
            font=('Segoe UI', 10, 'bold'),
            bg=self.colores['bg_card'],
            fg=self.colores['text_dark']
        ).pack(anchor='w', pady=(0, 5))
        
        niveles = [nivel.name for nivel in NivelTerapia]
        self.widgets['combo_nivel'] = ttk.Combobox(
            frame_cambio,
            values=niveles,
            state='readonly',
            font=('Segoe UI', 10),
            width=25
        )
        self.widgets['combo_nivel'].pack(fill='x', pady=(0, 10))
        
        # Botón aplicar
        btn_aplicar = tk.Button(
            frame_cambio,
            text="✓ Aplicar Cambio",
            font=('Segoe UI', 11, 'bold'),
            bg=self.colores['success'],
            fg=self.colores['text_white'],
            relief='flat',
            bd=0,
            padx=20,
            pady=10,
            cursor='hand2',
            command=self.cambiar_nivel
        )
        btn_aplicar.pack(fill='x')
        
        # Efecto hover
        btn_aplicar.bind('<Enter>', lambda e: btn_aplicar.config(bg='#0ea872'))
        btn_aplicar.bind('<Leave>', lambda e: btn_aplicar.config(bg=self.colores['success']))
    
    def _crear_card_observaciones(self, parent):
        """Crear card de observaciones"""
        card = self._crear_card(parent, "Observaciones del Terapeuta")
        
        frame_obs = tk.Frame(card, bg=self.colores['bg_card'])
        frame_obs.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.widgets['text_observaciones'] = scrolledtext.ScrolledText(
            frame_obs,
            height=6,
            font=('Segoe UI', 10),
            wrap='word',
            relief='solid',
            bd=1,
            borderwidth=1
        )
        self.widgets['text_observaciones'].pack(fill='both', expand=True, pady=(0, 10))
        
        # Botón guardar
        btn_guardar = tk.Button(
            frame_obs,
            text="💾 Guardar Observaciones",
            font=('Segoe UI', 10, 'bold'),
            bg=self.colores['primary'],
            fg=self.colores['text_white'],
            relief='flat',
            bd=0,
            padx=20,
            pady=10,
            cursor='hand2',
            command=self.guardar_observaciones
        )
        btn_guardar.pack()
        
        # Efecto hover
        btn_guardar.bind('<Enter>', lambda e: btn_guardar.config(bg=self.colores['primary_dark']))
        btn_guardar.bind('<Leave>', lambda e: btn_guardar.config(bg=self.colores['primary']))
    
    def _crear_tab_progreso(self):
        """Tab 3: Progreso y Estadísticas"""
        tab = tk.Frame(self.notebook, bg=self.colores['bg_main'])
        self.notebook.add(tab, text='📈 Progreso')
        self.tabs['progreso'] = tab
        
        # Canvas con scroll
        canvas = tk.Canvas(tab, bg=self.colores['bg_main'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(tab, orient='vertical', command=canvas.yview)
        frame_contenido = tk.Frame(canvas, bg=self.colores['bg_main'])
        
        frame_contenido.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
        )
        
        canvas.create_window((0, 0), window=frame_contenido, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y')
        
        self.widgets['frame_progreso'] = frame_contenido
        
        # Estadísticas
        self._crear_estadisticas_rapidas(frame_contenido)
        
        # Gráfico
        self._crear_card_grafico(frame_contenido)
    
    def _crear_estadisticas_rapidas(self, parent):
        """Crear cards de estadísticas rápidas"""
        frame_stats = tk.Frame(parent, bg=self.colores['bg_main'])
        frame_stats.pack(fill='x', pady=(0, 10))
        
        self.widgets['frame_stats'] = frame_stats
        
        # Se llenará dinámicamente al seleccionar usuario
    
    def _crear_card_grafico(self, parent):
        """Crear card para gráfico de progreso"""
        card = self._crear_card(parent, "Evolución del Desempeño")
        
        self.widgets['frame_grafico'] = tk.Frame(card, bg=self.colores['bg_card'])
        self.widgets['frame_grafico'].pack(fill='both', expand=True, padx=20, pady=20)
    
    def _crear_tab_historial(self):
        """Tab 4: Historial de Sesiones"""
        tab = tk.Frame(self.notebook, bg=self.colores['bg_main'])
        self.notebook.add(tab, text='📅 Historial')
        self.tabs['historial'] = tab
        
        frame_contenido = tk.Frame(tab, bg=self.colores['bg_main'])
        frame_contenido.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Card con tabla
        card = self._crear_card(frame_contenido, "Historial de Sesiones")
        
        # Treeview
        columnas = ('Fecha', 'Nivel', 'Correctos', 'Fallidos', 'Éxito %')
        self.widgets['tree_historial'] = ttk.Treeview(
            card,
            columns=columnas,
            show='headings',
            height=12
        )
        
        self.widgets['tree_historial'].heading('Fecha', text='Fecha')
        self.widgets['tree_historial'].heading('Nivel', text='Nivel')
        self.widgets['tree_historial'].heading('Correctos', text='✓ Correctos')
        self.widgets['tree_historial'].heading('Fallidos', text='✗ Fallidos')
        self.widgets['tree_historial'].heading('Éxito %', text='% Éxito')
        
        self.widgets['tree_historial'].column('Fecha', width=140)
        self.widgets['tree_historial'].column('Nivel', width=100)
        self.widgets['tree_historial'].column('Correctos', width=80, anchor='center')
        self.widgets['tree_historial'].column('Fallidos', width=80, anchor='center')
        self.widgets['tree_historial'].column('Éxito %', width=80, anchor='center')
        
        self.widgets['tree_historial'].pack(fill='both', expand=True, padx=20, pady=20)
    
    def _crear_card(self, parent, titulo):
        """Helper: Crear card moderno con sombra sutil"""
        # Frame externo para sombra
        frame_shadow = tk.Frame(parent, bg='#D1D5DB')
        frame_shadow.pack(fill='both', expand=True, pady=(0, 15))
        
        # Card principal
        card = tk.Frame(
            frame_shadow,
            bg=self.colores['bg_card'],
            relief='flat',
            bd=0
        )
        card.pack(fill='both', expand=True, padx=1, pady=1)
        
        # Borde
        card.configure(highlightbackground=self.colores['border_light'], highlightthickness=1)
        
        # Header del card
        if titulo:
            header = tk.Frame(card, bg=self.colores['bg_card'])
            header.pack(fill='x', padx=20, pady=(15, 10))
            
            tk.Label(
                header,
                text=titulo,
                font=('Segoe UI', 12, 'bold'),
                bg=self.colores['bg_card'],
                fg=self.colores['text_dark']
            ).pack(side='left')
        
        return card
    
    def _crear_stat_card(self, parent, titulo, valor, color):
        """Helper: Crear mini-card de estadística"""
        card = tk.Frame(
            parent,
            bg=color,
            relief='flat',
            bd=0
        )
        card.pack(side='left', fill='both', expand=True, padx=5)
        
        # Borde sutil
        card.configure(highlightbackground=self.colores['border_medium'], highlightthickness=1)
        
        tk.Label(
            card,
            text=titulo,
            font=('Segoe UI', 9),
            bg=color,
            fg=self.colores['text_white']
        ).pack(pady=(12, 2))
        
        tk.Label(
            card,
            text=valor,
            font=('Segoe UI', 20, 'bold'),
            bg=color,
            fg=self.colores['text_white']
        ).pack(pady=(2, 12))
        
        return card
    
    def _mostrar_mensaje_inicial(self):
        """Mostrar mensaje cuando no hay usuario seleccionado"""
        for tab_name, tab_frame in self.tabs.items():
            # Limpiar contenido
            for widget in tab_frame.winfo_children():
                widget.destroy()
            
            # Mensaje
            label = tk.Label(
                tab_frame,
                text="👈 Selecciona un paciente\nde la lista",
                font=('Segoe UI', 14),
                bg=self.colores['bg_main'],
                fg=self.colores['text_light'],
                justify='center'
            )
            label.place(relx=0.5, rely=0.5, anchor='center')
    
    # ========== CARGA DE DATOS ==========
    
    def cargar_usuarios(self):
        """Cargar lista de usuarios"""
        for item in self.tree_usuarios.get_children():
            self.tree_usuarios.delete(item)
        
        try:
            conn = self.db.conn
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    p.personId,
                    p.name,
                    p.apellido,
                    p.sex,
                    l.name as nivel
                FROM person p
                LEFT JOIN level l ON p.actual_level = l.levelId
                ORDER BY p.personId DESC
            """)
            
            personas = cursor.fetchall()
            
            for persona in personas:
                sexo_icono = "👦" if persona['sex'] == 'M' else "👧" if persona['sex'] == 'F' else "👤"
                
                nombre_completo = persona['name']
                if persona['apellido']:
                    nombre_completo += f" {persona['apellido']}"
                
                # Agregar con ID oculto
                item_id = self.tree_usuarios.insert(
                    '',
                    'end',
                    values=(
                        f"{sexo_icono} {nombre_completo}",
                        persona['nivel'] or 'N/A'
                    )
                )
                # Guardar ID en tags para recuperarlo después
                self.tree_usuarios.item(item_id, tags=(str(persona['personId']),))
            
            print(f"✅ Cargados {len(personas)} pacientes")
            
        except Exception as e:
            print(f"❌ Error al cargar usuarios: {e}")
            messagebox.showerror("Error", f"No se pudieron cargar los usuarios:\n{e}")
    
    def on_seleccionar_usuario(self, event):
        """Evento cuando se selecciona un usuario"""
        seleccion = self.tree_usuarios.selection()
        if not seleccion:
            return
        
        # Obtener ID desde tags
        item = self.tree_usuarios.item(seleccion[0])
        tags = item['tags']
        if tags:
            person_id = int(tags[0])
            self.cargar_detalles_usuario(person_id)
    
    def cargar_detalles_usuario(self, person_id: int):
        """Cargar detalles completos de un usuario"""
        try:
            conn = self.db.conn
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT p.*, l.name as nivel_nombre
                FROM person p
                LEFT JOIN level l ON p.actual_level = l.levelId
                WHERE p.personId = ?
            """, (person_id,))
            
            persona_row = cursor.fetchone()
            
            if not persona_row:
                return
            
            # Guardar persona seleccionada
            self.persona_seleccionada = {
                'person_id': persona_row['personId'],
                'name': persona_row['name'],
                'apellido': persona_row['apellido'] if 'apellido' in persona_row.keys() else None,
                'age': persona_row['age'],
                'dni': persona_row['dni'] if 'dni' in persona_row.keys() else None,
                'sex': persona_row['sex'] if 'sex' in persona_row.keys() else None,
                'nivel_id': persona_row['actual_level'],
                'nivel_nombre': persona_row['nivel_nombre'],
                'fecha_registro': persona_row['register_date']
            }
            
            # Recrear pestañas con contenido
            self._recrear_tabs_con_contenido()
            
            # Cargar datos en cada tab
            self._cargar_tab_informacion()
            self._cargar_tab_terapia()
            self._cargar_tab_progreso()
            self._cargar_tab_historial()
            
            print(f"✅ Detalles cargados para: {persona_row['name']}")
            
        except Exception as e:
            print(f"❌ Error al cargar detalles: {e}")
            import traceback
            traceback.print_exc()
    
    def _recrear_tabs_con_contenido(self):
        """Recrear pestañas con contenido real"""
        # Limpiar mensaje inicial de todos los tabs
        for tab_frame in self.tabs.values():
            for widget in tab_frame.winfo_children():
                widget.destroy()
        
        # Recrear estructura de cada tab
        # Tab Info
        tab_info = self.tabs['info']
        canvas = tk.Canvas(tab_info, bg=self.colores['bg_main'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(tab_info, orient='vertical', command=canvas.yview)
        frame_contenido = tk.Frame(canvas, bg=self.colores['bg_main'])
        
        frame_contenido.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=frame_contenido, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y')
        
        self.widgets['frame_info'] = frame_contenido
        self._crear_card_informacion(frame_contenido)
        
        # Tab Terapia
        tab_terapia = self.tabs['terapia']
        canvas = tk.Canvas(tab_terapia, bg=self.colores['bg_main'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(tab_terapia, orient='vertical', command=canvas.yview)
        frame_contenido = tk.Frame(canvas, bg=self.colores['bg_main'])
        
        frame_contenido.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=frame_contenido, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y')
        
        self.widgets['frame_terapia'] = frame_contenido
        self._crear_card_nivel(frame_contenido)
        self._crear_card_observaciones(frame_contenido)
        
        # Tab Progreso
        tab_progreso = self.tabs['progreso']
        canvas = tk.Canvas(tab_progreso, bg=self.colores['bg_main'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(tab_progreso, orient='vertical', command=canvas.yview)
        frame_contenido = tk.Frame(canvas, bg=self.colores['bg_main'])
        
        frame_contenido.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=frame_contenido, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y')
        
        self.widgets['frame_progreso'] = frame_contenido
        self._crear_estadisticas_rapidas(frame_contenido)
        self._crear_card_grafico(frame_contenido)
        
        # Tab Historial
        tab_historial = self.tabs['historial']
        frame_contenido = tk.Frame(tab_historial, bg=self.colores['bg_main'])
        frame_contenido.pack(fill='both', expand=True, padx=10, pady=10)
        
        card = self._crear_card(frame_contenido, "Historial de Sesiones")
        
        columnas = ('Fecha', 'Nivel', 'Correctos', 'Fallidos', 'Éxito %')
        self.widgets['tree_historial'] = ttk.Treeview(card, columns=columnas, show='headings', height=12)
        
        self.widgets['tree_historial'].heading('Fecha', text='Fecha')
        self.widgets['tree_historial'].heading('Nivel', text='Nivel')
        self.widgets['tree_historial'].heading('Correctos', text='✓ Correctos')
        self.widgets['tree_historial'].heading('Fallidos', text='✗ Fallidos')
        self.widgets['tree_historial'].heading('Éxito %', text='% Éxito')
        
        self.widgets['tree_historial'].column('Fecha', width=140)
        self.widgets['tree_historial'].column('Nivel', width=100)
        self.widgets['tree_historial'].column('Correctos', width=80, anchor='center')
        self.widgets['tree_historial'].column('Fallidos', width=80, anchor='center')
        self.widgets['tree_historial'].column('Éxito %', width=80, anchor='center')
        
        self.widgets['tree_historial'].pack(fill='both', expand=True, padx=20, pady=20)
    
    def _cargar_tab_informacion(self):
        """Cargar datos en tab de información"""
        if not self.persona_seleccionada:
            return
        
        p = self.persona_seleccionada
        
        self.widgets['label_nombre'].config(text=p['name'])
        self.widgets['label_apellido'].config(text=p['apellido'] if p['apellido'] else "No registrado")
        self.widgets['label_dni'].config(text=p['dni'] if p['dni'] else "No registrado")
        self.widgets['label_edad'].config(text=f"{p['age']} años")
        
        sexo_text = "Masculino" if p['sex'] == 'M' else "Femenino" if p['sex'] == 'F' else "No registrado"
        self.widgets['label_sexo'].config(text=sexo_text)
        
        if p['fecha_registro']:
            try:
                fecha_obj = datetime.fromisoformat(p['fecha_registro'])
                fecha_formateada = fecha_obj.strftime('%d/%m/%Y')
            except:
                fecha_formateada = p['fecha_registro']
        else:
            fecha_formateada = "N/A"
        
        self.widgets['label_fecha'].config(text=fecha_formateada)
    
    def _cargar_tab_terapia(self):
        """Cargar datos en tab de terapia"""
        if not self.persona_seleccionada:
            return
        
        self.widgets['label_nivel'].config(text=self.persona_seleccionada['nivel_nombre'] or 'N/A')
        self.widgets['combo_nivel'].set(self.persona_seleccionada['nivel_nombre'] or '')
        
        # Cargar observaciones
        self.widgets['text_observaciones'].delete("1.0", "end")
        
        try:
            observaciones = self.db.obtener_observaciones_persona(self.persona_seleccionada['person_id'])
            if observaciones:
                self.widgets['text_observaciones'].insert("1.0", observaciones[0]['observacion'])
        except:
            pass
    
    def _cargar_tab_progreso(self):
        """Cargar datos en tab de progreso"""
        if not self.persona_seleccionada:
            return
        
        try:
            sesiones = self.db.obtener_sesiones_por_persona(self.persona_seleccionada['person_id'])
            
            # Limpiar frame de stats
            for widget in self.widgets['frame_stats'].winfo_children():
                widget.destroy()
            
            if not sesiones:
                label = tk.Label(
                    self.widgets['frame_stats'],
                    text="Sin sesiones registradas",
                    font=('Segoe UI', 12),
                    bg=self.colores['bg_main'],
                    fg=self.colores['text_light']
                )
                label.pack(expand=True)
                return
            
            # Estadísticas
            total = len(sesiones)
            ultima = sesiones[-1]
            promedio = sum(s.tasa_exito for s in sesiones) / total * 100
            
            self._crear_stat_card(
                self.widgets['frame_stats'],
                "Total Sesiones",
                str(total),
                self.colores['info']
            )
            self._crear_stat_card(
                self.widgets['frame_stats'],
                "Última Tasa",
                f"{ultima.tasa_exito * 100:.0f}%",
                self.colores['success']
            )
            self._crear_stat_card(
                self.widgets['frame_stats'],
                "Promedio",
                f"{promedio:.1f}%",
                self.colores['warning']
            )
            
            # Gráfico
            self._crear_grafico_progreso(sesiones)
            
        except Exception as e:
            print(f"❌ Error al cargar progreso: {e}")
    
    def _crear_grafico_progreso(self, sesiones):
        """Crear gráfico de progreso"""
        # Limpiar frame
        for widget in self.widgets['frame_grafico'].winfo_children():
            widget.destroy()
        
        try:
            # Preparar datos (últimas 10 sesiones)
            fechas = [s.fecha.strftime('%d/%m') for s in sesiones[-10:]]
            tasas = [s.tasa_exito * 100 for s in sesiones[-10:]]
            
            # Crear figura
            fig = Figure(figsize=(5, 3), dpi=90)
            ax = fig.add_subplot(111)
            
            # Gráfico
            ax.plot(fechas, tasas, marker='o', linewidth=2, markersize=6, color=self.colores['primary'])
            ax.axhline(y=80, color=self.colores['success'], linestyle='--', alpha=0.7, label='Meta 80%')
            ax.axhline(y=70, color=self.colores['warning'], linestyle='--', alpha=0.7, label='Mínimo 70%')
            
            ax.set_xlabel('Fecha', fontsize=9)
            ax.set_ylabel('Tasa de Éxito (%)', fontsize=9)
            ax.set_title('Evolución (últimas 10 sesiones)', fontsize=10, fontweight='bold')
            ax.grid(True, alpha=0.2)
            ax.legend(fontsize=8)
            ax.set_ylim(0, 105)
            
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right', fontsize=8)
            ax.tick_params(axis='y', labelsize=8)
            
            fig.tight_layout()
            
            # Agregar a tkinter
            canvas = FigureCanvasTkAgg(fig, self.widgets['frame_grafico'])
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)
            
        except Exception as e:
            print(f"❌ Error al crear gráfico: {e}")
    
    def _cargar_tab_historial(self):
        """Cargar datos en tab de historial"""
        if not self.persona_seleccionada:
            return
        
        # Limpiar tree
        for item in self.widgets['tree_historial'].get_children():
            self.widgets['tree_historial'].delete(item)
        
        try:
            sesiones = self.db.obtener_sesiones_por_persona(self.persona_seleccionada['person_id'])
            
            for sesion in sesiones:
                fecha = sesion.fecha.strftime('%d/%m/%Y %H:%M')
                tasa = f"{sesion.tasa_exito * 100:.0f}%"
                
                tag = 'exito' if sesion.tasa_exito >= 0.8 else 'medio' if sesion.tasa_exito >= 0.5 else 'bajo'
                
                self.widgets['tree_historial'].insert(
                    '',
                    'end',
                    values=(fecha, sesion.nivel.name, sesion.ejercicios_correctos, sesion.ejercicios_fallidos, tasa),
                    tags=(tag,)
                )
            
            # Colores
            self.widgets['tree_historial'].tag_configure('exito', background='#d4edda')
            self.widgets['tree_historial'].tag_configure('medio', background='#fff3cd')
            self.widgets['tree_historial'].tag_configure('bajo', background='#f8d7da')
            
        except Exception as e:
            print(f"❌ Error al cargar historial: {e}")
    
    # ========== FUNCIONES DE MODIFICACIÓN ==========
    
    def cambiar_nivel(self):
        """Aplicar cambio de nivel"""
        if not self.persona_seleccionada:
            messagebox.showwarning("Advertencia", "No hay paciente seleccionado")
            return
        
        nuevo_nivel_nombre = self.widgets['combo_nivel'].get()
        
        if not nuevo_nivel_nombre:
            messagebox.showwarning("Advertencia", "Selecciona un nivel")
            return
        
        respuesta = messagebox.askyesno(
            "Confirmar cambio",
            f"¿Cambiar el nivel de {self.persona_seleccionada['name']}\n"
            f"de {self.persona_seleccionada['nivel_nombre']} a {nuevo_nivel_nombre}?"
        )
        
        if not respuesta:
            return
        
        try:
            nuevo_nivel = None
            for nivel in NivelTerapia:
                if nivel.name == nuevo_nivel_nombre:
                    nuevo_nivel = nivel
                    break
            
            if not nuevo_nivel:
                raise ValueError("Nivel no válido")
            
            self.db.actualizar_nivel_persona(self.persona_seleccionada['person_id'], nuevo_nivel)
            
            self.widgets['label_nivel'].config(text=nuevo_nivel_nombre)
            self.persona_seleccionada['nivel_nombre'] = nuevo_nivel_nombre
            
            self.cargar_usuarios()
            
            messagebox.showinfo("Éxito", f"Nivel actualizado a {nuevo_nivel_nombre}")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cambiar el nivel:\n{e}")
    
    def guardar_observaciones(self):
        """Guardar observaciones del terapeuta"""
        if not self.persona_seleccionada:
            messagebox.showwarning("Advertencia", "No hay paciente seleccionado")
            return
        
        observaciones = self.widgets['text_observaciones'].get("1.0", "end-1c").strip()
        
        if not observaciones:
            messagebox.showwarning("Advertencia", "No hay observaciones para guardar")
            return
        
        try:
            obs_id = self.db.crear_observacion(
                person_id=self.persona_seleccionada['person_id'],
                observacion=observaciones,
                terapeuta="Sistema"
            )
            
            if obs_id:
                messagebox.showinfo("Éxito", "Observaciones guardadas correctamente")
            else:
                raise Exception("No se pudo guardar")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron guardar las observaciones:\n{e}")
    
    def abrir_ventana_edicion(self):
        """Abrir ventana modal para editar información"""
        if not self.persona_seleccionada:
            messagebox.showwarning("Advertencia", "No hay paciente seleccionado")
            return
        
        # Crear ventana modal
        ventana_modal = tk.Toplevel(self.ventana)
        ventana_modal.title(f"Editar Información - {self.persona_seleccionada['name']}")
        ventana_modal.geometry("500x450")
        ventana_modal.configure(bg=self.colores['bg_card'])
        
        # Centrar
        ventana_modal.update_idletasks()
        width = 500
        height = 450
        x = (ventana_modal.winfo_screenwidth() // 2) - (width // 2)
        y = (ventana_modal.winfo_screenheight() // 2) - (height // 2)
        ventana_modal.geometry(f'{width}x{height}+{x}+{y}')
        
        ventana_modal.transient(self.ventana)
        ventana_modal.grab_set()
        
        # Header
        frame_header = tk.Frame(ventana_modal, bg=self.colores['primary'], height=60)
        frame_header.pack(fill='x')
        frame_header.pack_propagate(False)
        
        tk.Label(
            frame_header,
            text="✏️ Editar Información",
            font=('Segoe UI', 16, 'bold'),
            bg=self.colores['primary'],
            fg=self.colores['text_white']
        ).pack(pady=15)
        
        # Contenido
        frame_contenido = tk.Frame(ventana_modal, bg=self.colores['bg_card'])
        frame_contenido.pack(fill='both', expand=True, padx=30, pady=20)
        
        # Variables
        var_nombre = tk.StringVar(value=self.persona_seleccionada['name'])
        var_apellido = tk.StringVar(value=self.persona_seleccionada.get('apellido', '') or '')
        var_dni = tk.StringVar(value=self.persona_seleccionada.get('dni', '') or '')
        var_edad = tk.IntVar(value=self.persona_seleccionada['age'])
        var_sexo = tk.StringVar()
        
        sexo_actual = self.persona_seleccionada.get('sex', '')
        if sexo_actual == 'M':
            var_sexo.set('Masculino')
        elif sexo_actual == 'F':
            var_sexo.set('Femenino')
        else:
            var_sexo.set('No especificado')
        
        # Función helper para crear campo
        def crear_campo(label_text, variable, row, tipo='entry'):
            tk.Label(
                frame_contenido,
                text=label_text,
                font=('Segoe UI', 10, 'bold'),
                bg=self.colores['bg_card'],
                fg=self.colores['text_dark']
            ).grid(row=row, column=0, sticky='w', pady=8)
            
            if tipo == 'entry':
                widget = tk.Entry(
                    frame_contenido,
                    textvariable=variable,
                    font=('Segoe UI', 10),
                    width=30,
                    relief='solid',
                    bd=1
                )
            elif tipo == 'spinbox':
                widget = tk.Spinbox(
                    frame_contenido,
                    from_=1,
                    to=100,
                    textvariable=variable,
                    font=('Segoe UI', 10),
                    width=10,
                    relief='solid',
                    bd=1
                )
            elif tipo == 'combobox':
                widget = ttk.Combobox(
                    frame_contenido,
                    textvariable=variable,
                    values=['Masculino', 'Femenino', 'No especificado'],
                    state='readonly',
                    font=('Segoe UI', 10),
                    width=27
                )
            
            widget.grid(row=row, column=1, pady=8, sticky='ew')
            return widget
        
        crear_campo("Nombre:", var_nombre, 0)
        crear_campo("Apellido:", var_apellido, 1)
        crear_campo("DNI:", var_dni, 2)
        crear_campo("Edad:", var_edad, 3, tipo='spinbox')
        crear_campo("Sexo:", var_sexo, 4, tipo='combobox')
        
        frame_contenido.columnconfigure(1, weight=1)
        
        # Botones
        frame_botones = tk.Frame(ventana_modal, bg=self.colores['bg_card'])
        frame_botones.pack(fill='x', padx=30, pady=20)
        
        def guardar_cambios():
            nombre = var_nombre.get().strip()
            apellido = var_apellido.get().strip()
            dni = var_dni.get().strip()
            edad = var_edad.get()
            sexo_texto = var_sexo.get()
            
            sexo = 'M' if sexo_texto == 'Masculino' else 'F' if sexo_texto == 'Femenino' else None
            
            exito = self.db.actualizar_datos_persona(
                person_id=self.persona_seleccionada['person_id'],
                name=nombre,
                apellido=apellido if apellido else None,
                dni=dni if dni else None,
                age=edad,
                sex=sexo
            )
            
            if exito:
                messagebox.showinfo("Éxito", "Información actualizada")
                ventana_modal.destroy()
                self.cargar_detalles_usuario(self.persona_seleccionada['person_id'])
                self.cargar_usuarios()
            else:
                messagebox.showerror("Error", "No se pudo actualizar")
        
        btn_guardar = tk.Button(
            frame_botones,
            text="✅ Guardar",
            font=('Segoe UI', 11, 'bold'),
            bg=self.colores['success'],
            fg=self.colores['text_white'],
            relief='flat',
            bd=0,
            padx=25,
            pady=10,
            cursor='hand2',
            command=guardar_cambios
        )
        btn_guardar.pack(side='left', padx=5)
        
        btn_cancelar = tk.Button(
            frame_botones,
            text="❌ Cancelar",
            font=('Segoe UI', 11),
            bg=self.colores['text_medium'],
            fg=self.colores['text_white'],
            relief='flat',
            bd=0,
            padx=25,
            pady=10,
            cursor='hand2',
            command=ventana_modal.destroy
        )
        btn_cancelar.pack(side='left', padx=5)
    
    def cerrar(self):
        """Cerrar el panel"""
        print("\n🚪 Cerrando panel de administrador...")
        self.modo_admin_activo = False
        
        # ✅ Esperar que el hilo termine limpiamente
        if hasattr(self, 'hilo_escucha_admin') and self.hilo_escucha_admin.is_alive():
            print("⏳ Esperando que el hilo de audio se libere...")
            self.hilo_escucha_admin.join(timeout=6)
            
            if self.hilo_escucha_admin.is_alive():
                print("⚠️ El hilo tardó más de lo esperado")
            else:
                print("✅ Hilo de audio liberado correctamente")
                
        if self.ventana:
            try:
                self.ventana.destroy()
            except:
                pass
        
        print("✅ Panel cerrado.\n")
    
    def mostrar(self):
        """Mostrar la ventana del panel"""
        if self.ventana:
            self.ventana.deiconify()
            self.ventana.lift()
            self.ventana.mainloop()
