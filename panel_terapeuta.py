"""
PANEL DE TERAPEUTA - Interfaz de administración
Permite visualizar progreso y modificar niveles de usuarios
VERSIÓN COMPLETA CON TODOS LOS MÉTODOS
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
    """Panel de administración para el terapeuta"""
    
    def __init__(self, db: Database, audio_system=None):
        self.db = db
        self.audio = audio_system
        self.ventana = None
        self.persona_seleccionada = None
        self.modo_admin_activo = True
        
        # Colores profesionales
        self.color_fondo = '#F5F5F5'
        self.color_primario = '#2C3E50'
        self.color_secundario = '#3498DB'
        self.color_exito = '#2ECC71'
        self.color_advertencia = '#F39C12'
        self.color_error = '#E74C3C'
        
        # Widgets principales
        self.tree_usuarios = None
        self.frame_detalles = None
        self.label_nombre = None
        self.label_dni = None
        self.label_edad = None
        self.label_sexo = None
        self.label_fecha = None
        self.label_nivel = None
        self.combo_nivel = None
        self.text_observaciones = None
        self.canvas_grafico = None
        self.tree_historial = None
        self.frame_stats = None
        self.frame_grafico = None
    
    def crear(self):
        """Crear ventana del panel"""
        self.ventana = tk.Toplevel()
        self.ventana.title("Panel de Terapeuta - Robot DODO")
        self.ventana.geometry("1400x900")
        self.ventana.configure(bg=self.color_fondo)
        
        # Centrar en pantalla
        self.ventana.update_idletasks()
        width = self.ventana.winfo_width()
        height = self.ventana.winfo_height()
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
            print("🎤 Escucha por voz activada en panel de administrador")
            print("   Di 'salir' o 'cerrar' para salir del panel")
        
        # Header
        self._crear_header()
        
        # Contenedor principal
        frame_principal = tk.Frame(self.ventana, bg=self.color_fondo)
        frame_principal.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Panel izquierdo: Lista de usuarios
        self._crear_panel_usuarios(frame_principal)
        
        # Panel derecho: Detalles y edición
        self._crear_panel_detalles(frame_principal)
        
        # Cargar datos iniciales
        self.cargar_usuarios()
    
    def _escuchar_comandos_voz(self):
        """Escuchar comandos de voz para salir del panel"""
        from chatopenai import detectar_salir_panel
        import time
        
        while self.modo_admin_activo:
            try:
                texto = self.audio.escuchar(timeout=5, phrase_time_limit=5)
                
                if texto:
                    print(f"🎤 [Panel Admin] Escuché: '{texto}'")
                    
                    if detectar_salir_panel(texto):
                        print("🚪 Detectada intención de salir del panel")
                        self.audio.hablar("Cerrando panel de administrador.")
                        self.ventana.after(100, self.cerrar)
                        break
                
                time.sleep(0.5)
                
            except Exception as e:
                print(f"⚠️ Error en escucha de panel admin: {e}")
                time.sleep(1)
    
    def _crear_header(self):
        """Crear header del panel"""
        frame_header = tk.Frame(self.ventana, bg=self.color_primario, height=80)
        frame_header.pack(fill='x')
        frame_header.pack_propagate(False)
        
        # Título
        label_titulo = tk.Label(
            frame_header,
            text="🩺 Panel de Terapeuta",
            font=('Arial', 28, 'bold'),
            bg=self.color_primario,
            fg='white'
        )
        label_titulo.pack(side='left', padx=30, pady=20)
        
        # Información del sistema
        info_db = self.db.verificar_integridad()
        texto_info = f"👥 {info_db.get('personas', 0)} pacientes  |  📊 {info_db.get('sesiones', 0)} sesiones  |  📝 {info_db.get('ejercicios', 0)} ejercicios"
        
        label_info = tk.Label(
            frame_header,
            text=texto_info,
            font=('Arial', 12),
            bg=self.color_primario,
            fg='white'
        )
        label_info.pack(side='right', padx=30)
    
    def _crear_panel_usuarios(self, parent):
        """Crear panel de lista de usuarios"""
        frame_izquierdo = tk.Frame(parent, bg=self.color_fondo)
        frame_izquierdo.pack(side='left', fill='both', expand=False, padx=(0, 10))
        frame_izquierdo.configure(width=500)
        
        # Título
        label_titulo = tk.Label(
            frame_izquierdo,
            text="📋 Lista de Pacientes",
            font=('Arial', 16, 'bold'),
            bg=self.color_fondo,
            fg=self.color_primario
        )
        label_titulo.pack(pady=(0, 10))
        
        # Frame para el Treeview
        frame_tree = tk.Frame(frame_izquierdo, bg='white', relief='ridge', bd=2)
        frame_tree.pack(fill='both', expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_tree)
        scrollbar.pack(side='right', fill='y')
        
        # Treeview
        columnas = ('ID', 'Nombre', 'Edad', 'Nivel', 'Sesiones')
        self.tree_usuarios = ttk.Treeview(
            frame_tree,
            columns=columnas,
            show='headings',
            yscrollcommand=scrollbar.set,
            selectmode='browse'
        )
        
        # Configurar columnas
        self.tree_usuarios.heading('ID', text='ID')
        self.tree_usuarios.heading('Nombre', text='Nombre')
        self.tree_usuarios.heading('Edad', text='Edad')
        self.tree_usuarios.heading('Nivel', text='Nivel Actual')
        self.tree_usuarios.heading('Sesiones', text='Sesiones')
        
        self.tree_usuarios.column('ID', width=50, anchor='center')
        self.tree_usuarios.column('Nombre', width=180)
        self.tree_usuarios.column('Edad', width=60, anchor='center')
        self.tree_usuarios.column('Nivel', width=120)
        self.tree_usuarios.column('Sesiones', width=80, anchor='center')
        
        self.tree_usuarios.pack(fill='both', expand=True)
        scrollbar.config(command=self.tree_usuarios.yview)
        
        # Evento de selección
        self.tree_usuarios.bind('<<TreeviewSelect>>', self.on_seleccionar_usuario)
        
        # Botones de acción
        frame_botones = tk.Frame(frame_izquierdo, bg=self.color_fondo)
        frame_botones.pack(pady=10)
        
        btn_actualizar = tk.Button(
            frame_botones,
            text="🔄 Actualizar",
            font=('Arial', 11),
            bg=self.color_secundario,
            fg='white',
            relief='flat',
            padx=20,
            pady=8,
            cursor='hand2',
            command=self.cargar_usuarios
        )
        btn_actualizar.pack(side='left', padx=5)
    
    def _crear_panel_detalles(self, parent):
        """Crear panel de detalles del usuario"""
        frame_derecho = tk.Frame(parent, bg=self.color_fondo)
        frame_derecho.pack(side='right', fill='both', expand=True)
        
        # Título
        label_titulo = tk.Label(
            frame_derecho,
            text="📊 Detalles del Paciente",
            font=('Arial', 16, 'bold'),
            bg=self.color_fondo,
            fg=self.color_primario
        )
        label_titulo.pack(pady=(0, 10))
        
        # Frame contenedor con scroll
        canvas = tk.Canvas(frame_derecho, bg=self.color_fondo, highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame_derecho, orient='vertical', command=canvas.yview)
        self.frame_detalles = tk.Frame(canvas, bg=self.color_fondo)
        
        self.frame_detalles.bind(
            '<Configure>',
            lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
        )
        
        canvas.create_window((0, 0), window=self.frame_detalles, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Secciones del panel de detalles
        self._crear_seccion_informacion()
        self._crear_seccion_nivel()
        self._crear_seccion_progreso()
        self._crear_seccion_historial()
        
        # Mostrar mensaje inicial
        self._mostrar_mensaje_inicial()
    
    def _crear_seccion_informacion(self):
        """Crear sección de información básica"""
        frame = tk.LabelFrame(
            self.frame_detalles,
            text="ℹ️ Información Básica",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg=self.color_primario,
            relief='ridge',
            bd=2
        )
        frame.pack(fill='x', pady=(0, 10), padx=5)
        
        # Nombre
        frame_nombre = tk.Frame(frame, bg='white')
        frame_nombre.pack(fill='x', padx=15, pady=8)
        
        tk.Label(
            frame_nombre,
            text="Nombre:",
            font=('Arial', 11, 'bold'),
            bg='white',
            fg=self.color_primario
        ).pack(side='left')
        
        self.label_nombre = tk.Label(
            frame_nombre,
            text="",
            font=('Arial', 11),
            bg='white',
            fg='#333'
        )
        self.label_nombre.pack(side='left', padx=10)
        
        # DNI
        frame_dni = tk.Frame(frame, bg='white')
        frame_dni.pack(fill='x', padx=15, pady=8)
        
        tk.Label(
            frame_dni,
            text="DNI:",
            font=('Arial', 11, 'bold'),
            bg='white',
            fg=self.color_primario
        ).pack(side='left')
        
        self.label_dni = tk.Label(
            frame_dni,
            text="",
            font=('Arial', 11),
            bg='white',
            fg='#333'
        )
        self.label_dni.pack(side='left', padx=10)
        
        # Edad y Sexo
        frame_edad_sexo = tk.Frame(frame, bg='white')
        frame_edad_sexo.pack(fill='x', padx=15, pady=8)
        
        tk.Label(
            frame_edad_sexo,
            text="Edad:",
            font=('Arial', 11, 'bold'),
            bg='white',
            fg=self.color_primario
        ).pack(side='left')
        
        self.label_edad = tk.Label(
            frame_edad_sexo,
            text="",
            font=('Arial', 11),
            bg='white',
            fg='#333'
        )
        self.label_edad.pack(side='left', padx=10)
        
        tk.Label(
            frame_edad_sexo,
            text="  |  Sexo:",
            font=('Arial', 11, 'bold'),
            bg='white',
            fg=self.color_primario
        ).pack(side='left', padx=(20, 0))
        
        self.label_sexo = tk.Label(
            frame_edad_sexo,
            text="",
            font=('Arial', 11),
            bg='white',
            fg='#333'
        )
        self.label_sexo.pack(side='left', padx=10)
        
        # Fecha registro
        frame_fecha = tk.Frame(frame, bg='white')
        frame_fecha.pack(fill='x', padx=15, pady=8)
        
        tk.Label(
            frame_fecha,
            text="Registro:",
            font=('Arial', 11, 'bold'),
            bg='white',
            fg=self.color_primario
        ).pack(side='left')
        
        self.label_fecha = tk.Label(
            frame_fecha,
            text="",
            font=('Arial', 11),
            bg='white',
            fg='#333'
        )
        self.label_fecha.pack(side='left', padx=10)
    
    def _crear_seccion_nivel(self):
        """Crear sección de modificación de nivel"""
        frame = tk.LabelFrame(
            self.frame_detalles,
            text="🎯 Gestión de Nivel Terapéutico",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg=self.color_primario,
            relief='ridge',
            bd=2
        )
        frame.pack(fill='x', pady=(0, 10), padx=5)
        
        # Nivel actual
        frame_actual = tk.Frame(frame, bg='white')
        frame_actual.pack(fill='x', padx=15, pady=10)
        
        tk.Label(
            frame_actual,
            text="Nivel Actual:",
            font=('Arial', 11, 'bold'),
            bg='white',
            fg=self.color_primario
        ).pack(side='left')
        
        self.label_nivel = tk.Label(
            frame_actual,
            text="",
            font=('Arial', 14, 'bold'),
            bg='white',
            fg=self.color_secundario
        )
        self.label_nivel.pack(side='left', padx=10)
        
        # Selector de nuevo nivel
        frame_selector = tk.Frame(frame, bg='white')
        frame_selector.pack(fill='x', padx=15, pady=10)
        
        tk.Label(
            frame_selector,
            text="Cambiar a:",
            font=('Arial', 11, 'bold'),
            bg='white',
            fg=self.color_primario
        ).pack(side='left')
        
        niveles = [nivel.name for nivel in NivelTerapia]
        self.combo_nivel = ttk.Combobox(
            frame_selector,
            values=niveles,
            state='readonly',
            font=('Arial', 11),
            width=20
        )
        self.combo_nivel.pack(side='left', padx=10)
        
        # Botones de acción
        frame_botones = tk.Frame(frame, bg='white')
        frame_botones.pack(fill='x', padx=15, pady=10)
        
        btn_aplicar = tk.Button(
            frame_botones,
            text="✓ Aplicar Cambio",
            font=('Arial', 11, 'bold'),
            bg=self.color_exito,
            fg='white',
            relief='flat',
            padx=15,
            pady=8,
            cursor='hand2',
            command=self.cambiar_nivel
        )
        btn_aplicar.pack(side='left', padx=5)
        
        btn_subir = tk.Button(
            frame_botones,
            text="⬆️ Subir Nivel",
            font=('Arial', 11),
            bg=self.color_secundario,
            fg='white',
            relief='flat',
            padx=15,
            pady=8,
            cursor='hand2',
            command=self.subir_nivel
        )
        btn_subir.pack(side='left', padx=5)
        
        btn_bajar = tk.Button(
            frame_botones,
            text="⬇️ Bajar Nivel",
            font=('Arial', 11),
            bg=self.color_advertencia,
            fg='white',
            relief='flat',
            padx=15,
            pady=8,
            cursor='hand2',
            command=self.bajar_nivel
        )
        btn_bajar.pack(side='left', padx=5)
        
        btn_reiniciar = tk.Button(
            frame_botones,
            text="🔄 Reiniciar a INICIAL",
            font=('Arial', 11),
            bg=self.color_error,
            fg='white',
            relief='flat',
            padx=15,
            pady=8,
            cursor='hand2',
            command=self.reiniciar_nivel
        )
        btn_reiniciar.pack(side='left', padx=5)
        
        # Observaciones
        frame_obs = tk.Frame(frame, bg='white')
        frame_obs.pack(fill='both', expand=True, padx=15, pady=10)
        
        tk.Label(
            frame_obs,
            text="📝 Observaciones del terapeuta:",
            font=('Arial', 11, 'bold'),
            bg='white',
            fg=self.color_primario
        ).pack(anchor='w', pady=(0, 5))
        
        self.text_observaciones = scrolledtext.ScrolledText(
            frame_obs,
            height=4,
            font=('Arial', 10),
            wrap='word',
            relief='solid',
            bd=1
        )
        self.text_observaciones.pack(fill='both', expand=True)
        
        btn_guardar_obs = tk.Button(
            frame,
            text="💾 Guardar Observaciones",
            font=('Arial', 10),
            bg=self.color_secundario,
            fg='white',
            relief='flat',
            padx=15,
            pady=5,
            cursor='hand2',
            command=self.guardar_observaciones
        )
        btn_guardar_obs.pack(pady=10)
    
    def _crear_seccion_progreso(self):
        """Crear sección de progreso con gráfico"""
        frame = tk.LabelFrame(
            self.frame_detalles,
            text="📈 Progreso de Sesiones",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg=self.color_primario,
            relief='ridge',
            bd=2
        )
        frame.pack(fill='both', expand=True, pady=(0, 10), padx=5)
        
        # Estadísticas rápidas
        self.frame_stats = tk.Frame(frame, bg='white')
        self.frame_stats.pack(fill='x', padx=15, pady=10)
        
        # Frame para el gráfico
        self.frame_grafico = tk.Frame(frame, bg='white')
        self.frame_grafico.pack(fill='both', expand=True, padx=15, pady=10)
    
    def _crear_seccion_historial(self):
        """Crear sección de historial de sesiones"""
        frame = tk.LabelFrame(
            self.frame_detalles,
            text="📅 Historial de Sesiones",
            font=('Arial', 12, 'bold'),
            bg='white',
            fg=self.color_primario,
            relief='ridge',
            bd=2
        )
        frame.pack(fill='both', expand=True, padx=5)
        
        # Treeview para historial
        columnas = ('Fecha', 'Nivel', 'Correctos', 'Fallidos', 'Tasa')
        self.tree_historial = ttk.Treeview(
            frame,
            columns=columnas,
            show='headings',
            height=8
        )
        
        self.tree_historial.heading('Fecha', text='Fecha')
        self.tree_historial.heading('Nivel', text='Nivel')
        self.tree_historial.heading('Correctos', text='✓ Correctos')
        self.tree_historial.heading('Fallidos', text='✗ Fallidos')
        self.tree_historial.heading('Tasa', text='% Éxito')
        
        self.tree_historial.column('Fecha', width=150)
        self.tree_historial.column('Nivel', width=120)
        self.tree_historial.column('Correctos', width=100, anchor='center')
        self.tree_historial.column('Fallidos', width=100, anchor='center')
        self.tree_historial.column('Tasa', width=100, anchor='center')
        
        self.tree_historial.pack(fill='both', expand=True, padx=10, pady=10)
    
    def _mostrar_mensaje_inicial(self):
        """Mostrar mensaje cuando no hay usuario seleccionado"""
        for widget in self.frame_detalles.winfo_children():
            widget.pack_forget()
        
        label = tk.Label(
            self.frame_detalles,
            text="👈 Selecciona un paciente de la lista",
            font=('Arial', 16),
            bg=self.color_fondo,
            fg='#999'
        )
        label.pack(expand=True)
    
    def cargar_usuarios(self):
        """Cargar lista de usuarios"""
        # Limpiar tree
        for item in self.tree_usuarios.get_children():
            self.tree_usuarios.delete(item)
        
        # Obtener personas de la BD
        try:
            conn = self.db.conn
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    p.personId,
                    p.name,
                    p.age,
                    p.sex,
                    p.dni,
                    l.name as nivel,
                    COUNT(DISTINCT s.sesionId) as num_sesiones
                FROM person p
                LEFT JOIN level l ON p.actual_level = l.levelId
                LEFT JOIN sesion s ON p.personId = s.personId
                GROUP BY p.personId
                ORDER BY p.personId DESC
            """)
            
            personas = cursor.fetchall()
            
            for persona in personas:
                sexo_icono = "👦" if persona['sex'] == 'M' else "👧" if persona['sex'] == 'F' else "👤"
                
                self.tree_usuarios.insert(
                    '',
                    'end',
                    values=(
                        persona['personId'],
                        f"{sexo_icono} {persona['name']}",
                        f"{persona['age']} años",
                        persona['nivel'] or 'N/A',
                        persona['num_sesiones']
                    )
                )
            
            print(f"✅ Cargados {len(personas)} pacientes")
            
        except Exception as e:
            print(f"❌ Error al cargar usuarios: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"No se pudieron cargar los usuarios:\n{e}")
    
    def on_seleccionar_usuario(self, event):
        """Evento cuando se selecciona un usuario"""
        seleccion = self.tree_usuarios.selection()
        if not seleccion:
            return
        
        item = self.tree_usuarios.item(seleccion[0])
        person_id = item['values'][0]
        
        self.cargar_detalles_usuario(person_id)
    
    def cargar_detalles_usuario(self, person_id: int):
        """Cargar detalles completos de un usuario"""
        try:
            # Obtener persona
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
                'age': persona_row['age'],
                'dni': persona_row['dni'] if 'dni' in persona_row.keys() else None,
                'sex': persona_row['sex'] if 'sex' in persona_row.keys() else None,
                'nivel_id': persona_row['actual_level'],
                'nivel_nombre': persona_row['nivel_nombre'],
                'fecha_registro': persona_row['register_date']
            }
            
            # Mostrar secciones
            for widget in self.frame_detalles.winfo_children():
                widget.pack(fill='x', pady=(0, 10), padx=5)
            
            # Actualizar información básica
            self.label_nombre.config(text=persona_row['name'])
            
            dni_text = persona_row['dni'] if persona_row['dni'] else "No registrado"
            self.label_dni.config(text=dni_text)
            
            self.label_edad.config(text=f"{persona_row['age']} años")
            
            sexo_text = "Masculino" if persona_row['sex'] == 'M' else "Femenino" if persona_row['sex'] == 'F' else "No registrado"
            self.label_sexo.config(text=sexo_text)
            
            fecha_registro = persona_row['register_date']
            if fecha_registro:
                try:
                    fecha_obj = datetime.fromisoformat(fecha_registro)
                    fecha_formateada = fecha_obj.strftime('%d/%m/%Y')
                except:
                    fecha_formateada = fecha_registro
            else:
                fecha_formateada = "N/A"
            
            self.label_fecha.config(text=fecha_formateada)
            
            # Actualizar nivel
            self.label_nivel.config(text=persona_row['nivel_nombre'] or 'N/A')
            self.combo_nivel.set(persona_row['nivel_nombre'] or '')
            
            # Cargar historial
            self._cargar_historial_sesiones(person_id)
            
            # Cargar gráfico de progreso
            self._cargar_grafico_progreso(person_id)
            
            # Cargar observaciones
            self._cargar_observaciones(person_id)
            
            print(f"✅ Detalles cargados para: {persona_row['name']}")
            
        except Exception as e:
            print(f"❌ Error al cargar detalles: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"No se pudieron cargar los detalles:\n{e}")
    
    def _cargar_historial_sesiones(self, person_id: int):
        """Cargar historial de sesiones del usuario"""
        # Limpiar tree
        for item in self.tree_historial.get_children():
            self.tree_historial.delete(item)
        
        try:
            sesiones = self.db.obtener_sesiones_por_persona(person_id)
            
            for sesion in sesiones:
                fecha = sesion.fecha.strftime('%d/%m/%Y %H:%M')
                tasa = f"{sesion.tasa_exito * 100:.0f}%"
                
                # Color según tasa de éxito
                tag = ''
                if sesion.tasa_exito >= 0.8:
                    tag = 'exito'
                elif sesion.tasa_exito >= 0.5:
                    tag = 'medio'
                else:
                    tag = 'bajo'
                
                self.tree_historial.insert(
                    '',
                    'end',
                    values=(
                        fecha,
                        sesion.nivel.name,
                        sesion.ejercicios_correctos,
                        sesion.ejercicios_fallidos,
                        tasa
                    ),
                    tags=(tag,)
                )
            
            # Configurar colores
            self.tree_historial.tag_configure('exito', background='#d4edda')
            self.tree_historial.tag_configure('medio', background='#fff3cd')
            self.tree_historial.tag_configure('bajo', background='#f8d7da')
            
        except Exception as e:
            print(f"❌ Error al cargar historial: {e}")
    
    def _cargar_grafico_progreso(self, person_id: int):
        """Cargar gráfico de progreso del usuario"""
        # Limpiar frame
        for widget in self.frame_grafico.winfo_children():
            widget.destroy()
        
        try:
            sesiones = self.db.obtener_sesiones_por_persona(person_id)
            
            if not sesiones:
                label = tk.Label(
                    self.frame_grafico,
                    text="Sin sesiones registradas",
                    font=('Arial', 12),
                    bg='white',
                    fg='#999'
                )
                label.pack(expand=True)
                return
            
            # Preparar datos
            fechas = [s.fecha.strftime('%d/%m') for s in sesiones[-10:]]
            tasas = [s.tasa_exito * 100 for s in sesiones[-10:]]
            
            # Crear figura
            fig = Figure(figsize=(8, 4), dpi=80)
            ax = fig.add_subplot(111)
            
            # Gráfico de línea
            ax.plot(fechas, tasas, marker='o', linewidth=2, markersize=8, color=self.color_secundario)
            ax.axhline(y=80, color=self.color_exito, linestyle='--', label='Umbral subida nivel (80%)')
            ax.axhline(y=70, color=self.color_advertencia, linestyle='--', label='Umbral éxito (70%)')
            
            ax.set_xlabel('Fecha', fontsize=11)
            ax.set_ylabel('Tasa de Éxito (%)', fontsize=11)
            ax.set_title('Evolución del Desempeño', fontsize=12, fontweight='bold')
            ax.grid(True, alpha=0.3)
            ax.legend(fontsize=9)
            ax.set_ylim(0, 105)
            
            # Rotar etiquetas del eje x
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
            
            fig.tight_layout()
            
            # Agregar a tkinter
            canvas = FigureCanvasTkAgg(fig, self.frame_grafico)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)
            
            # Actualizar estadísticas
            self._actualizar_estadisticas(sesiones)
            
        except Exception as e:
            print(f"❌ Error al crear gráfico: {e}")
            import traceback
            traceback.print_exc()
    
    def _actualizar_estadisticas(self, sesiones: List):
        """Actualizar estadísticas rápidas"""
        # Limpiar frame
        for widget in self.frame_stats.winfo_children():
            widget.destroy()
        
        if not sesiones:
            return
        
        # Calcular estadísticas
        total_sesiones = len(sesiones)
        ultima_sesion = sesiones[-1]
        promedio_exito = sum(s.tasa_exito for s in sesiones) / total_sesiones * 100
        
        # Crear cards de estadísticas
        stats = [
            ("Total Sesiones", str(total_sesiones), self.color_secundario),
            ("Última Tasa", f"{ultima_sesion.tasa_exito * 100:.0f}%", self.color_exito),
            ("Promedio", f"{promedio_exito:.1f}%", self.color_advertencia)
        ]
        
        for titulo, valor, color in stats:
            card = tk.Frame(self.frame_stats, bg=color, relief='raised', bd=2)
            card.pack(side='left', fill='both', expand=True, padx=5)
            
            tk.Label(
                card,
                text=titulo,
                font=('Arial', 10),
                bg=color,
                fg='white'
            ).pack(pady=(5, 0))
            
            tk.Label(
                card,
                text=valor,
                font=('Arial', 16, 'bold'),
                bg=color,
                fg='white'
            ).pack(pady=(0, 5))
    
    def _cargar_observaciones(self, person_id: int):
        """Cargar observaciones del terapeuta"""
        try:
            observaciones = self.db.obtener_observaciones_persona(person_id)
            
            if observaciones:
                obs_reciente = observaciones[0]
                self.text_observaciones.delete("1.0", "end")
                self.text_observaciones.insert("1.0", obs_reciente['observacion'])
        except Exception as e:
            print(f"⚠️ Error al cargar observaciones: {e}")
    
    # ===== FUNCIONES DE MODIFICACIÓN =====
    
    def cambiar_nivel(self):
        """Aplicar cambio de nivel seleccionado"""
        if not self.persona_seleccionada:
            messagebox.showwarning("Advertencia", "No hay paciente seleccionado")
            return
        
        nuevo_nivel_nombre = self.combo_nivel.get()
        
        if not nuevo_nivel_nombre:
            messagebox.showwarning("Advertencia", "Selecciona un nivel")
            return
        
        # Confirmar
        respuesta = messagebox.askyesno(
            "Confirmar cambio",
            f"¿Cambiar el nivel de {self.persona_seleccionada['name']}\n"
            f"de {self.persona_seleccionada['nivel_nombre']} a {nuevo_nivel_nombre}?"
        )
        
        if not respuesta:
            return
        
        try:
            # Obtener NivelTerapia
            nuevo_nivel = None
            for nivel in NivelTerapia:
                if nivel.name == nuevo_nivel_nombre:
                    nuevo_nivel = nivel
                    break
            
            if not nuevo_nivel:
                raise ValueError("Nivel no válido")
            
            # Actualizar en BD
            self.db.actualizar_nivel_persona(
                self.persona_seleccionada['person_id'],
                nuevo_nivel
            )
            
            # Actualizar interfaz
            self.label_nivel.config(text=nuevo_nivel_nombre)
            self.persona_seleccionada['nivel_nombre'] = nuevo_nivel_nombre
            
            # Recargar lista
            self.cargar_usuarios()
            
            messagebox.showinfo(
                "Éxito",
                f"Nivel actualizado a {nuevo_nivel_nombre}"
            )
            
            print(f"✅ Nivel cambiado a {nuevo_nivel_nombre} para {self.persona_seleccionada['name']}")
            
        except Exception as e:
            print(f"❌ Error al cambiar nivel: {e}")
            messagebox.showerror("Error", f"No se pudo cambiar el nivel:\n{e}")
    
    def subir_nivel(self):
        """Subir un nivel al usuario"""
        if not self.persona_seleccionada:
            messagebox.showwarning("Advertencia", "No hay paciente seleccionado")
            return
        
        try:
            nivel_actual = None
            for nivel in NivelTerapia:
                if nivel.name == self.persona_seleccionada['nivel_nombre']:
                    nivel_actual = nivel
                    break
            
            if not nivel_actual:
                raise ValueError("Nivel actual no válido")
            
            niveles = list(NivelTerapia)
            indice_actual = niveles.index(nivel_actual)
            
            if indice_actual >= len(niveles) - 1:
                messagebox.showinfo("Info", "El paciente ya está en el nivel máximo")
                return
            
            nuevo_nivel = niveles[indice_actual + 1]
            
            # Actualizar
            self.db.actualizar_nivel_persona(
                self.persona_seleccionada['person_id'],
                nuevo_nivel
            )
            
            # Actualizar interfaz
            self.label_nivel.config(text=nuevo_nivel.name)
            self.combo_nivel.set(nuevo_nivel.name)
            self.persona_seleccionada['nivel_nombre'] = nuevo_nivel.name
            
            # Recargar lista
            self.cargar_usuarios()
            
            messagebox.showinfo(
                "Éxito",
                f"¡Nivel subido a {nuevo_nivel.name}!"
            )
            
            print(f"✅ Nivel subido a {nuevo_nivel.name}")
            
        except Exception as e:
            print(f"❌ Error al subir nivel: {e}")
            messagebox.showerror("Error", f"No se pudo subir el nivel:\n{e}")
    
    def bajar_nivel(self):
        """Bajar un nivel al usuario"""
        if not self.persona_seleccionada:
            messagebox.showwarning("Advertencia", "No hay paciente seleccionado")
            return
        
        try:
            nivel_actual = None
            for nivel in NivelTerapia:
                if nivel.name == self.persona_seleccionada['nivel_nombre']:
                    nivel_actual = nivel
                    break
            
            if not nivel_actual:
                raise ValueError("Nivel actual no válido")
            
            niveles = list(NivelTerapia)
            indice_actual = niveles.index(nivel_actual)
            
            if indice_actual <= 0:
                messagebox.showinfo("Info", "El paciente ya está en el nivel mínimo")
                return
            
            nuevo_nivel = niveles[indice_actual - 1]
            
            # Confirmar
            respuesta = messagebox.askyesno(
                "Confirmar",
                f"¿Bajar el nivel a {nuevo_nivel.name}?"
            )
            
            if not respuesta:
                return
            
            # Actualizar
            self.db.actualizar_nivel_persona(
                self.persona_seleccionada['person_id'],
                nuevo_nivel
            )
            
            # Actualizar interfaz
            self.label_nivel.config(text=nuevo_nivel.name)
            self.combo_nivel.set(nuevo_nivel.name)
            self.persona_seleccionada['nivel_nombre'] = nuevo_nivel.name
            
            # Recargar lista
            self.cargar_usuarios()
            
            messagebox.showinfo(
                "Éxito",
                f"Nivel bajado a {nuevo_nivel.name}"
            )
            
            print(f"✅ Nivel bajado a {nuevo_nivel.name}")
            
        except Exception as e:
            print(f"❌ Error al bajar nivel: {e}")
            messagebox.showerror("Error", f"No se pudo bajar el nivel:\n{e}")
    
    def reiniciar_nivel(self):
        """Reiniciar al nivel INICIAL"""
        if not self.persona_seleccionada:
            messagebox.showwarning("Advertencia", "No hay paciente seleccionado")
            return
        
        # Confirmar
        respuesta = messagebox.askyesno(
            "⚠️ Confirmar Reinicio",
            f"¿REINICIAR el nivel de {self.persona_seleccionada['name']} a INICIAL?\n\n"
            "Esta acción moverá al paciente al nivel más básico.",
            icon='warning'
        )
        
        if not respuesta:
            return
        
        try:
            # Actualizar a INICIAL
            self.db.actualizar_nivel_persona(
                self.persona_seleccionada['person_id'],
                NivelTerapia.INICIAL
            )
            
            # Actualizar interfaz
            self.label_nivel.config(text='INICIAL')
            self.combo_nivel.set('INICIAL')
            self.persona_seleccionada['nivel_nombre'] = 'INICIAL'
            
            # Recargar lista
            self.cargar_usuarios()
            
            messagebox.showinfo(
                "Éxito",
                "Nivel reiniciado a INICIAL"
            )
            
            print(f"✅ Nivel reiniciado a INICIAL")
            
        except Exception as e:
            print(f"❌ Error al reiniciar nivel: {e}")
            messagebox.showerror("Error", f"No se pudo reiniciar el nivel:\n{e}")
    
    def guardar_observaciones(self):
        """Guardar observaciones del terapeuta"""
        if not self.persona_seleccionada:
            messagebox.showwarning("Advertencia", "No hay paciente seleccionado")
            return
        
        observaciones = self.text_observaciones.get("1.0", "end-1c").strip()
        
        if not observaciones:
            messagebox.showwarning("Advertencia", "No hay observaciones para guardar")
            return
        
        try:
            # Guardar en tabla de observaciones
            obs_id = self.db.crear_observacion(
                person_id=self.persona_seleccionada['person_id'],
                observacion=observaciones,
                terapeuta="Sistema"
            )
            
            if obs_id:
                messagebox.showinfo(
                    "Éxito",
                    "Observaciones guardadas correctamente"
                )
                
                print(f"✅ Observaciones guardadas para {self.persona_seleccionada['name']}")
                print(f"📝 {observaciones}")
            else:
                raise Exception("No se pudo guardar")
            
        except Exception as e:
            print(f"❌ Error al guardar observaciones: {e}")
            messagebox.showerror("Error", f"No se pudieron guardar las observaciones:\n{e}")
    
    def cerrar(self):
        """Cerrar el panel"""
        print("\n🚪 Cerrando panel de administrador...")
        self.modo_admin_activo = False
        
        if self.ventana:
            try:
                self.ventana.destroy()
            except:
                pass
        
        print("✅ Panel cerrado. Robot vuelve a modo normal.\n")
    
    def mostrar(self):
        """Mostrar la ventana del panel"""
        if self.ventana:
            self.ventana.deiconify()
            self.ventana.lift()
            self.ventana.mainloop()