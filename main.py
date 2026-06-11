import pygame
import sys
import random
import math

# Inicialización de Pygame
pygame.init()

# Configuración de la pantalla (Redimensionada para acomodar las Tarjetas)
ANCHO = 480
ALTO = 780
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Gato Llaves - Edición Premium")

# Colores (Tema Neón y Oscuro Premium)
COLOR_BG = (15, 18, 28)          # Fondo ultra oscuro
COLOR_LINEAS = (40, 48, 68)      # Rejillas
COLOR_X = (0, 229, 255)          # Celeste neón
COLOR_O = (255, 46, 99)          # Rosa neón
COLOR_TEXTO = (240, 243, 246)    # Blanco suave
COLOR_BOTON = (28, 35, 51)       # Botones comunes
COLOR_BOTON_HOVER = (42, 53, 77)
COLOR_TEXTO_MUTED = (120, 130, 150)
COLOR_CARTA_BG = (24, 30, 44)    # Fondo de las tarjetas de poder
COLOR_BORDE_CARTA = (53, 66, 97)
COLOR_GOLD = (255, 215, 0)       # Dorado para la Llave Felicidades

# Fuentes seguras con fallbacks
try:
    fuente_titulo = pygame.font.SysFont("sans-serif", 46, bold=True)
    fuente_normal = pygame.font.SysFont("sans-serif", 20, bold=True)
    fuente_sm = pygame.font.SysFont("sans-serif", 15)
    fuente_carta_titulo = pygame.font.SysFont("sans-serif", 14, bold=True)
    fuente_carta_cuerpo = pygame.font.SysFont("sans-serif", 11)
except:
    fuente_titulo = pygame.font.Font(None, 48)
    fuente_normal = pygame.font.Font(None, 22)
    fuente_sm = pygame.font.Font(None, 16)
    fuente_carta_titulo = pygame.font.Font(None, 14)
    fuente_carta_cuerpo = pygame.font.Font(None, 12)

# Estado del Juego
estado = "MENU"  # MENU, JUGANDO, TERMINADO
modo_juego = "AMIGO"  # AMIGO, IA_FACIL, IA_DIFICIL
tablero = [["" for _ in range(3)] for _ in range(3)]
turno = "X"  # 'X' empieza la ronda
ganador = None
cant_x = 0
cant_o = 0

# Puntuaciones acumuladas
puntos = {"X": 0, "O": 0, "EMPATE": 0}

# Dimensiones del tablero
TAM_CASILLA = 110
DESPLAZAMIENTO_Y = 135
DESPLAZAMIENTO_X = (ANCHO - (TAM_CASILLA * 3)) // 2

# Mecánicas de Llaves (Estado por ronda)
jugadas_realizadas = 0
turnos_desde_desbloqueo = 0
usada_alemana = False
usada_isla = False
usada_felicidades = False

# Definición de Rectángulos Interactivos (Botones y Tarjetas)
btn_amigo = pygame.Rect(40, 260, 400, 65)
btn_ia_facil = pygame.Rect(40, 350, 400, 65)
btn_ia_dificil = pygame.Rect(40, 440, 400, 65)

btn_reiniciar = pygame.Rect(30, 715, 195, 45)
btn_menu = pygame.Rect(255, 715, 195, 45)

# Posiciones de las Tarjetas de Llaves
CARD_W = 135
CARD_H = 175
CARD_Y = 515
btn_card_alemana = pygame.Rect(20, CARD_Y, CARD_W, CARD_H)
btn_card_isla = pygame.Rect(172, CARD_Y, CARD_W, CARD_H)
btn_card_felicidades = pygame.Rect(324, CARD_Y, CARD_W, CARD_H)

# --- SISTEMA DE LLUVIA DE PARTICULAS (X y O) ---
class ParticulaLluvia:
    def __init__(self):
        self.x = random.randint(0, ANCHO)
        self.y = random.randint(-100, ALTO)
        self.velocidad = random.uniform(1.5, 3.5)
        self.tipo = random.choice(["X", "O"])
        self.tamaño = random.randint(12, 22)
        # Opacidad simulada usando colores oscurecidos para que no estorbe la jugabilidad
        factor_brillo = random.uniform(0.15, 0.35)
        if self.tipo == "X":
            self.color = (int(COLOR_X[0]*factor_brillo), int(COLOR_X[1]*factor_brillo), int(COLOR_X[2]*factor_brillo))
        else:
            self.color = (int(COLOR_O[0]*factor_brillo), int(COLOR_O[1]*factor_brillo), int(COLOR_O[2]*factor_brillo))
        try:
            self.fuente = pygame.font.SysFont("sans-serif", self.tamaño, bold=True)
        except:
            self.fuente = pygame.font.Font(None, self.tamaño)

    def mover(self):
        self.y += self.velocidad
        if self.y > ALTO + 20:
            self.y = random.randint(-50, -10)
            self.x = random.randint(0, ANCHO)
            self.velocidad = random.uniform(1.5, 3.5)

    def dibujar(self, superficie):
        txt_surf = self.fuente.render(self.tipo, True, self.color)
        superficie.blit(txt_surf, (self.x, self.y))

# Crear un lote constante de 25 partículas para un fondo sutil pero vivo
lluvia_particulas = [ParticulaLluvia() for _ in range(25)]

# --- FUNCIONES ADICIONALES ---
def obtener_color_dinamico():
    """Calcula un color intermedio que varía suavemente de Rojo a Azul usando el tiempo transcurrido."""
    tiempo = pygame.time.get_ticks() / 1000.0  # Tiempo en segundos
    # Oscilador entre 0 y 1 usando seno
    factor = (math.sin(tiempo * 2.0) + 1.0) / 2.0  # Frecuencia suave de transicion
    
    # Interpolar de Rojo (255, 46, 99) a Celeste/Azul (0, 229, 255)
    r = int((1.0 - factor) * COLOR_O[0] + factor * COLOR_X[0])
    g = int((1.0 - factor) * COLOR_O[1] + factor * COLOR_X[1])
    b = int((1.0 - factor) * COLOR_O[2] + factor * COLOR_X[2])
    return (r, g, b)

def reiniciar_tablero():
    """Limpia todo el estado para iniciar una nueva ronda."""
    global tablero, turno, ganador, cant_x, cant_o
    global jugadas_realizadas, turnos_desde_desbloqueo
    global usada_alemana, usada_isla, usada_felicidades
    tablero = [["" for _ in range(3)] for _ in range(3)]
    turno = "X"
    ganador = None
    cant_x = 0
    cant_o = 0
    jugadas_realizadas = 0
    turnos_desde_desbloqueo = 0
    usada_alemana = False
    usada_isla = False
    usada_felicidades = False

def verificar_fin_partida():
    """
    Verifica si el tablero está lleno. Si lo está, calcula el ganador
    basado en la superioridad numérica (quien tiene más fichas).
    """
    global ganador, cant_x, cant_o

    temporal_x = 0
    temporal_o = 0
    celdas_vacias = 0

    for i in range(3):
        for j in range(3):
            if tablero[i][j] == "X":
                temporal_x += 1
            elif tablero[i][j] == "O":
                temporal_o += 1
            else:
                celdas_vacias += 1

    cant_x = temporal_x
    cant_o = temporal_o

    # Solo finaliza si el tablero está 100% lleno
    if celdas_vacias == 0:
        if cant_x > cant_o:
            ganador = "X"
        elif cant_o > cant_x:
            ganador = "O"
        else:
            ganador = "EMPATE"
        return ganador

    return None

def evaluar_puntuacion_tablero(tablero_temp):
    """Función de evaluación para la IA basada en conteo de fichas."""
    tx = sum(fila.count("X") for fila in tablero_temp)
    to = sum(fila.count("O") for fila in tablero_temp)
    return to - tx

def minimax(tablero_temp, profundidad, es_maximizador):
    """Algoritmo Minimax adaptado al llenado completo."""
    vacias = sum(fila.count("") for fila in tablero_temp)
    if vacias == 0:
        score = evaluar_puntuacion_tablero(tablero_temp)
        if score > 0:
            return 100 - profundidad
        elif score < 0:
            return profundidad - 100
        else:
            return 0

    if profundidad >= 5:
        return evaluar_puntuacion_tablero(tablero_temp)

    if es_maximizador:
        mejor_puntaje = -float('inf')
        for i in range(3):
            for j in range(3):
                if tablero_temp[i][j] == "":
                    tablero_temp[i][j] = "O"
                    puntaje = minimax(tablero_temp, profundidad + 1, False)
                    tablero_temp[i][j] = ""
                    mejor_puntaje = max(puntaje, mejor_puntaje)
        return mejor_puntaje
    else:
        mejor_puntaje = float('inf')
        for i in range(3):
            for j in range(3):
                if tablero_temp[i][j] == "":
                    tablero_temp[i][j] = "X"
                    puntaje = minimax(tablero_temp, profundidad + 1, True)
                    tablero_temp[i][j] = ""
                    mejor_puntaje = min(puntaje, mejor_puntaje)
        return mejor_puntaje

def mejor_movimiento_ia():
    """Obtiene la casilla óptima calculada por la IA territorial."""
    mejor_puntaje = -float('inf')
    movimiento = None
    for i in range(3):
        for j in range(3):
            if tablero[i][j] == "":
                tablero[i][j] = "O"
                puntaje = minimax(tablero, 0, False)
                tablero[i][j] = ""
                if puntaje > mejor_puntaje:
                    mejor_puntaje = puntaje
                    movimiento = (i, j)
    if movimiento is None:
        vacias = [(r, c) for r in range(3) for c in range(3) if tablero[r][c] == ""]
        if vacias:
            movimiento = random.choice(vacias)
    return movimiento

def realizar_movimiento_ia():
    """Ejecuta el turno de la IA."""
    global turno, estado, jugadas_realizadas, turnos_desde_desbloqueo
    
    if ganador is not None:
        return

    celdas_vacias = []
    for i in range(3):
        for j in range(3):
            if tablero[i][j] == "":
                celdas_vacias.append((i, j))

    if not celdas_vacias:
        return

    if modo_juego == "IA_FACIL":
        fila, col = random.choice(celdas_vacias)
    else:
        fila, col = mejor_movimiento_ia()

    tablero[fila][col] = "O"
    
    # Conteo de turnos
    jugadas_realizadas += 1
    if jugadas_realizadas > 1:
        turnos_desde_desbloqueo += 1

    resultado = verificar_fin_partida()
    if resultado:
        estado = "TERMINADO"
        puntos[resultado] += 1
    else:
        turno = "X"

def dibujar_texto_ajustado(texto, color, rect, fuente, espaciado=2):
    """Renderiza textos ajustándose al ancho de una tarjeta."""
    palabras = texto.split(' ')
    lineas = []
    linea_actual = ""
    for palabra in palabras:
        test_linea = linea_actual + " " + palabra if linea_actual else palabra
        if fuente.size(test_linea)[0] < rect.width - 12:
            linea_actual = test_linea
        else:
            lineas.append(linea_actual)
            linea_actual = palabra
    if linea_actual:
        lineas.append(linea_actual)
    
    y = rect.top + 32
    for linea in lineas:
        surf = fuente.render(linea, True, color)
        pantalla.blit(surf, (rect.left + 8, y))
        y += fuente.get_height() + espaciado

def dibujar_boton(rect, texto, color_base, color_texto, hover=False):
    """Crea botones pulidos para móviles."""
    color = COLOR_BOTON_HOVER if hover else color_base
    pygame.draw.rect(pantalla, color, rect, border_radius=14)
    pygame.draw.rect(pantalla, COLOR_LINEAS, rect, width=2, border_radius=14)
    
    txt_surf = fuente_normal.render(texto, True, color_texto)
    txt_rect = txt_surf.get_rect(center=rect.center)
    pantalla.blit(txt_surf, txt_rect)

def dibujar_tarjeta_llave(rect, titulo, descripcion, color_borde, usada=False, bloqueada=False, countdown=0):
    """Dibuja las tarjetas de habilidades."""
    pygame.draw.rect(pantalla, COLOR_CARTA_BG, rect, border_radius=10)
    
    borde = COLOR_LINEAS if usada or bloqueada else color_borde
    pygame.draw.rect(pantalla, borde, rect, width=2, border_radius=10)
    
    color_titulo = COLOR_TEXTO_MUTED if (usada or bloqueada) else COLOR_TEXTO
    lbl_titulo = fuente_carta_titulo.render(titulo, True, color_titulo)
    pantalla.blit(lbl_titulo, (rect.left + 8, rect.top + 10))
    
    pygame.draw.line(pantalla, borde, (rect.left + 5, rect.top + 28), (rect.right - 5, rect.top + 28), 1)

    if bloqueada:
        dibujar_texto_ajustado(f"Desbloqueo en {countdown} turnos.", COLOR_TEXTO_MUTED, rect, fuente_carta_cuerpo)
        candado_surf = fuente_normal.render("🔒", True, COLOR_TEXTO_MUTED)
        candado_rect = candado_surf.get_rect(center=(rect.centerx, rect.bottom - 40))
        pantalla.blit(candado_surf, candado_rect)
    elif usada:
        dibujar_texto_ajustado("Ya has consumido este poder.", COLOR_TEXTO_MUTED, rect, fuente_carta_cuerpo)
        txt_usada = fuente_normal.render("USADA", True, COLOR_O)
        txt_rect = txt_usada.get_rect(center=(rect.centerx, rect.bottom - 30))
        pantalla.blit(txt_usada, txt_rect)
    else:
        dibujar_texto_ajustado(descripcion, COLOR_TEXTO, rect, fuente_carta_cuerpo)
        spark_surf = fuente_sm.render("✨ ACTIVAR ✨", True, color_borde)
        spark_rect = spark_surf.get_rect(center=(rect.centerx, rect.bottom - 20))
        pantalla.blit(spark_surf, spark_rect)

def dibujar_lluvia():
    """Actualiza y dibuja las partículas de fondo."""
    for p in lluvia_particulas:
        p.mover()
        p.draw.dibujar(pantalla) if hasattr(p, 'draw') else p.dibujar(pantalla)

def dibujar_menu():
    """Pantalla de inicio principal con animaciones."""
    pantalla.fill(COLOR_BG)
    
    # Dibujar la lluvia de fondo
    dibujar_lluvia()
    
    # Título animado dinámicamente Rojo -> Azul
    color_dinamico = obtener_color_dinamico()
    titulo_sombra = fuente_titulo.render("GATO LLAVES", True, (8, 10, 16))
    titulo_texto = fuente_titulo.render("GATO LLAVES", True, color_dinamico)
    pantalla.blit(titulo_sombra, (ANCHO // 2 - titulo_sombra.get_width() // 2 + 3, 103))
    pantalla.blit(titulo_texto, (ANCHO // 2 - titulo_texto.get_width() // 2, 100))
    
    sub_txt = "¡Rellena el tablero y domina al rival!"
    subtitulo = fuente_sm.render(sub_txt, True, COLOR_TEXTO_MUTED)
    pantalla.blit(subtitulo, (ANCHO // 2 - subtitulo.get_width() // 2, 160))

    mouse_pos = pygame.mouse.get_pos()
    dibujar_boton(btn_amigo, "Contra un amigo (Local)", COLOR_BOTON, COLOR_TEXTO, btn_amigo.collidepoint(mouse_pos))
    dibujar_boton(btn_ia_facil, "Contra IA (Fácil)", COLOR_BOTON, COLOR_TEXTO, btn_ia_facil.collidepoint(mouse_pos))
    dibujar_boton(btn_ia_dificil, "Contra IA (Imposible)", COLOR_BOTON, COLOR_TEXTO, btn_ia_dificil.collidepoint(mouse_pos))

    firma = fuente_sm.render("Optimizado para Pydroid 3", True, COLOR_LINEAS)
    pantalla.blit(firma, (ANCHO // 2 - firma.get_width() // 2, 680))

def dibujar_tablero():
    """Cuadrícula del juego."""
    # Líneas verticales
    pygame.draw.line(pantalla, COLOR_LINEAS, (DESPLAZAMIENTO_X + TAM_CASILLA, DESPLAZAMIENTO_Y), 
                     (DESPLAZAMIENTO_X + TAM_CASILLA, DESPLAZAMIENTO_Y + TAM_CASILLA * 3), 6)
    pygame.draw.line(pantalla, COLOR_LINEAS, (DESPLAZAMIENTO_X + TAM_CASILLA * 2, DESPLAZAMIENTO_Y), 
                     (DESPLAZAMIENTO_X + TAM_CASILLA * 2, DESPLAZAMIENTO_Y + TAM_CASILLA * 3), 6)
    
    # Líneas horizontales
    pygame.draw.line(pantalla, COLOR_LINEAS, (DESPLAZAMIENTO_X, DESPLAZAMIENTO_Y + TAM_CASILLA), 
                     (DESPLAZAMIENTO_X + TAM_CASILLA * 3, DESPLAZAMIENTO_Y + TAM_CASILLA), 6)
    pygame.draw.line(pantalla, COLOR_LINEAS, (DESPLAZAMIENTO_X, DESPLAZAMIENTO_Y + TAM_CASILLA * 2), 
                     (DESPLAZAMIENTO_X + TAM_CASILLA * 3, DESPLAZAMIENTO_Y + TAM_CASILLA * 2), 6)

    # Figuras (X / O) con sombreado luminoso simple
    for i in range(3):
        for j in range(3):
            figura = tablero[i][j]
            x_centro = DESPLAZAMIENTO_X + j * TAM_CASILLA + TAM_CASILLA // 2
            y_centro = DESPLAZAMIENTO_Y + i * TAM_CASILLA + TAM_CASILLA // 2
            radio = TAM_CASILLA // 3

            if figura == "X":
                pygame.draw.line(pantalla, COLOR_X, (x_centro - radio, y_centro - radio), (x_centro + radio, y_centro + radio), 8)
                pygame.draw.line(pantalla, COLOR_X, (x_centro + radio, y_centro - radio), (x_centro - radio, y_centro + radio), 8)
            elif figura == "O":
                pygame.draw.circle(pantalla, COLOR_O, (x_centro, y_centro), radio, 8)

def dibujar_interfaz_juego():
    """Dibuja todo el entorno del partido (marcador, tablero, llaves y botones)."""
    pantalla.fill(COLOR_BG)

    # Dibujar la lluvia de fondo sutil detrás de los elementos de juego
    dibujar_lluvia()

    # 1. Marcador Global (Victorias acumuladas)
    marcador_rect = pygame.Rect(30, 15, ANCHO - 60, 55)
    pygame.draw.rect(pantalla, COLOR_BOTON, marcador_rect, border_radius=12)
    pygame.draw.rect(pantalla, COLOR_LINEAS, marcador_rect, width=2, border_radius=12)

    txt_x = fuente_normal.render(f"Rondas X: {puntos['X']}", True, COLOR_X)
    txt_empate = fuente_normal.render(f"Empate: {puntos['EMPATE']}", True, COLOR_TEXTO_MUTED)
    txt_o = fuente_normal.render(f"Rondas O: {puntos['O']}", True, COLOR_O)

    pantalla.blit(txt_x, (45, 30))
    pantalla.blit(txt_empate, (ANCHO // 2 - txt_empate.get_width() // 2, 30))
    pantalla.blit(txt_o, (ANCHO - 45 - txt_o.get_width(), 30))

    # Actualizar recuento de fichas actuales del tablero
    temp_x = sum(fila.count("X") for fila in tablero)
    temp_o = sum(fila.count("O") for fila in tablero)

    # Barra de dominación territorial visual
    barra_y = 80
    barra_ancho = ANCHO - 60
    barra_alto = 14
    pygame.draw.rect(pantalla, COLOR_LINEAS, (30, barra_y, barra_ancho, barra_alto), border_radius=7)
    
    total_fichas = temp_x + temp_o
    if total_fichas > 0:
        ancho_x = int(barra_ancho * (temp_x / 9))
        ancho_o = int(barra_ancho * (temp_o / 9))
        
        # Barra X (Celeste, izquierda)
        if temp_x > 0:
            pygame.draw.rect(pantalla, COLOR_X, (30, barra_y, ancho_x, barra_alto), border_radius=7)
        # Barra O (Rosa, derecha)
        if temp_o > 0:
            pygame.draw.rect(pantalla, COLOR_O, (30 + barra_ancho - ancho_o, barra_y, ancho_o, barra_alto), border_radius=7)

    # Textos de dominación territorial actual
    lbl_dom_x = fuente_sm.render(f"{temp_x} casillas", True, COLOR_X)
    lbl_dom_o = fuente_sm.render(f"{temp_o} casillas", True, COLOR_O)
    pantalla.blit(lbl_dom_x, (30, barra_y + 18))
    pantalla.blit(lbl_dom_o, (ANCHO - 30 - lbl_dom_o.get_width(), barra_y + 18))

    # 2. Línea de Estado (Turno / Ganador)
    if estado == "JUGANDO":
        if turno == "X":
            txt_status = "Tu Turno (X)" if modo_juego != "AMIGO" else "Turno de X"
            color_status = COLOR_X
        else:
            txt_status = "Turno de la IA (O)" if modo_juego != "AMIGO" else "Turno de O"
            color_status = COLOR_O
    else:
        if ganador == "EMPATE":
            txt_status = f"¡Empate Territorial! ({temp_x} - {temp_o})"
            color_status = COLOR_TEXTO_MUTED
        elif ganador == "X":
            txt_status = f"¡Ganó X por dominación! ({temp_x} a {temp_o})" if modo_juego == "AMIGO" else f"¡Ganaste por dominación! ({temp_x} a {temp_o})"
            color_status = COLOR_X
        else:
            txt_status = f"¡Ganó O por dominación! ({temp_o} a {temp_x})" if modo_juego == "AMIGO" else f"¡IA gana por dominación! ({temp_o} a {temp_x})"
            color_status = COLOR_O

    lbl_status = fuente_normal.render(txt_status, True, color_status)
    pantalla.blit(lbl_status, (ANCHO // 2 - lbl_status.get_width() // 2, barra_y + 35))

    # 3. Tablero
    dibujar_tablero()

    # 4. Sección de Tarjetas (Llaves Especiales)
    lbl_habilidad = fuente_sm.render("HABILIDADES ESPECIALES (LLAVES)", True, COLOR_TEXTO_MUTED)
    pantalla.blit(lbl_habilidad, (ANCHO // 2 - lbl_habilidad.get_width() // 2, 485))

    # Las llaves se desbloquean en el segundo turno (jugadas_realizadas >= 1)
    if jugadas_realizadas >= 1:
        # Llave Alemana
        dibujar_tarjeta_llave(
            btn_card_alemana, 
            "Llave Alemana", 
            f"Rellena todos los casilleros del tablero con tu ficha, excepto el centro.", 
            COLOR_X if turno == "X" else COLOR_O, 
            usada=usada_alemana
        )
        
        # Llave Isla
        dibujar_tarjeta_llave(
            btn_card_isla, 
            "Llave Isla", 
            f"Limpia todas las fichas del tablero por completo.", 
            COLOR_X if turno == "X" else COLOR_O, 
            usada=usada_isla
        )
        
        # Llave Felicidades
        felicidades_desbloqueada = (turnos_desde_desbloqueo > 2)
        countdown_restante = max(0, 3 - turnos_desde_desbloqueo)
        
        dibujar_tarjeta_llave(
            btn_card_felicidades, 
            "Llave Felicidades", 
            "Asimila todo el tablero borrando al rival y gana la ronda automáticamente.", 
            COLOR_GOLD, 
            usada=usada_felicidades, 
            bloqueada=not felicidades_desbloqueada,
            countdown=countdown_restante
        )
    else:
        # Bloqueo temporal inicial
        bloqueo_rect = pygame.Rect(20, CARD_Y, ANCHO - 40, CARD_H)
        pygame.draw.rect(pantalla, COLOR_CARTA_BG, bloqueo_rect, border_radius=12)
        pygame.draw.rect(pantalla, COLOR_LINEAS, bloqueo_rect, width=2, border_radius=12)
        
        txt_bloq_1 = fuente_normal.render("LLAVES BLOQUEADAS", True, COLOR_TEXTO_MUTED)
        txt_bloq_2 = fuente_sm.render("Estarán disponibles a partir del segundo turno.", True, COLOR_TEXTO_MUTED)
        
        pantalla.blit(txt_bloq_1, (bloqueo_rect.centerx - txt_bloq_1.get_width() // 2, bloqueo_rect.centery - 20))
        pantalla.blit(txt_bloq_2, (bloqueo_rect.centerx - txt_bloq_2.get_width() // 2, bloqueo_rect.centery + 15))

    # 5. Botones inferiores
    mouse_pos = pygame.mouse.get_pos()
    dibujar_boton(btn_reiniciar, "Reiniciar Ronda", COLOR_BOTON, COLOR_TEXTO, btn_reiniciar.collidepoint(mouse_pos))
    dibujar_boton(btn_menu, "Menú Principal", COLOR_BOTON, COLOR_TEXTO, btn_menu.collidepoint(mouse_pos))

# Bucle principal de ejecución
reloj = pygame.time.Clock()

while True:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if evento.type == pygame.MOUSEBUTTONDOWN:
            pos_clic = pygame.mouse.get_pos()

            if estado == "MENU":
                if btn_amigo.collidepoint(pos_clic):
                    modo_juego = "AMIGO"
                    reiniciar_tablero()
                    estado = "JUGANDO"
                elif btn_ia_facil.collidepoint(pos_clic):
                    modo_juego = "IA_FACIL"
                    reiniciar_tablero()
                    estado = "JUGANDO"
                elif btn_ia_dificil.collidepoint(pos_clic):
                    modo_juego = "IA_DIFICIL"
                    reiniciar_tablero()
                    estado = "JUGANDO"

            elif estado in ["JUGANDO", "TERMINADO"]:
                # Botones globales
                if btn_reiniciar.collidepoint(pos_clic):
                    reiniciar_tablero()
                    estado = "JUGANDO"
                elif btn_menu.collidepoint(pos_clic):
                    puntos = {"X": 0, "O": 0, "EMPATE": 0}
                    estado = "MENU"

                # Interacciones durante el juego activo
                elif estado == "JUGANDO":
                    es_turno_humano = (modo_juego == "AMIGO") or (modo_juego != "AMIGO" and turno == "X")

                    if es_turno_humano:
                        # 1. Tarjetas de Habilidad (Llaves)
                        if jugadas_realizadas >= 1:
                            # CLICK EN LLAVE ALEMANA
                            if btn_card_alemana.collidepoint(pos_clic) and not usada_alemana:
                                for r in range(3):
                                    for c in range(3):
                                        if r == 1 and c == 1:
                                            tablero[r][c] = ""
                                        else:
                                            tablero[r][c] = turno
                                usada_alemana = True
                                jugadas_realizadas += 1
                                turnos_desde_desbloqueo += 1
                                
                                resultado = verificar_fin_partida()
                                if resultado:
                                    estado = "TERMINADO"
                                    puntos[resultado] += 1
                                else:
                                    turno = "O" if turno == "X" else "X"
                                continue

                            # CLICK EN LLAVE ISLA
                            elif btn_card_isla.collidepoint(pos_clic) and not usada_isla:
                                tablero = [["" for _ in range(3)] for _ in range(3)]
                                usada_isla = True
                                jugadas_realizadas += 1
                                turnos_desde_desbloqueo += 1
                                turno = "O" if turno == "X" else "X"
                                continue

                            # CLICK EN LLAVE FELICIDADES
                            elif btn_card_felicidades.collidepoint(pos_clic) and not usada_felicidades:
                                if turnos_desde_desbloqueo > 2:
                                    for r in range(3):
                                        for c in range(3):
                                            tablero[r][c] = turno
                                    
                                    usada_felicidades = True
                                    resultado = verificar_fin_partida()
                                    estado = "TERMINADO"
                                    if resultado:
                                        puntos[resultado] += 1
                                    continue

                        # 2. Clic en cuadrícula normal
                        x, y = pos_clic
                        dentro_tablero_x = DESPLAZAMIENTO_X <= x <= DESPLAZAMIENTO_X + TAM_CASILLA * 3
                        dentro_tablero_y = DESPLAZAMIENTO_Y <= y <= DESPLAZAMIENTO_Y + TAM_CASILLA * 3

                        if dentro_tablero_x and dentro_tablero_y:
                            col = (x - DESPLAZAMIENTO_X) // TAM_CASILLA
                            fila = (y - DESPLAZAMIENTO_Y) // TAM_CASILLA

                            if tablero[fila][col] == "":
                                tablero[fila][col] = turno
                                jugadas_realizadas += 1
                                
                                if jugadas_realizadas > 1:
                                    turnos_desde_desbloqueo += 1

                                resultado = verificar_fin_partida()
                                if resultado:
                                    estado = "TERMINADO"
                                    puntos[resultado] += 1
                                else:
                                    turno = "O" if turno == "X" else "X"

    # Turno lógico de la Inteligencia Artificial
    if estado == "JUGANDO" and modo_juego != "AMIGO" and turno == "O":
        pygame.time.delay(400)
        realizar_movimiento_ia()

    # Renderizar pantalla según el estado
    if estado == "MENU":
        dibujar_menu()
    else:
        dibujar_interfaz_juego()

    pygame.display.flip()
    reloj.tick(60)