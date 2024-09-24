import pygame
import serial

import threading
import time
import random

# Configura la connessione seriale
ser = serial.Serial('COM9', 9600, timeout=1)  # Sostituisci 'COMX' con la tua porta seriale

# Variabili globali per i dati
x_value = 512
y_value = 512
distance = 100  # Valore iniziale della distanza
button_state = 1  # 1 = non premuto, 0 = premuto

def read_from_arduino():
    global x_value, y_value, distance, button_state
    while True:
        try:
            data = ser.readline().decode('utf-8').rstrip()
            if data:
                values = data.split(',')
                if len(values) == 4:
                    x_value = int(values[0])
                    y_value = int(values[1])
                    distance = float(values[2])
                    button_state = int(values[3])
        except Exception as e:
            print(f"Errore nella lettura seriale: {e}")

# Avvia un thread per leggere i dati dall'Arduino
thread = threading.Thread(target=read_from_arduino)
thread.daemon = True
thread.start()

# Inizializza Pygame
pygame.init()
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Gioco Interattivo con Sensore a Ultrasuoni")

# Colori
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
PLAYER_COLOR = (0, 255, 0)
ITEM_COLOR = (255, 255, 0)
ENEMY_COLOR = (255, 0, 0)
SHIELD_COLOR = (0, 0, 255)  # Colore dello scudo (blu)

# Posizione iniziale del giocatore
player_pos = [screen_width // 2, screen_height // 2]
player_radius = 20

# Variabile per il punteggio
score = 0

# Lista per gli oggetti da raccogliere
items = []

# Lista per i proiettili
bullets = []

# Font per il punteggio e il messaggio di game over
font = pygame.font.Font(None, 36)
game_over_font = pygame.font.Font(None, 72)

# Variabile per lo stato del gioco
game_over = False

# Posizione iniziale del nemico
enemy_pos = [random.randint(0, screen_width - 30), random.randint(0, screen_height - 30)]
enemy_size = 30
enemy_speed = 2  # Velocità del nemico

# Stato precedente del pulsante
previous_button_state = 1  # 1 = non premuto, 0 = premuto

# Variabile per lo scudo
shield_active = False
shield_duration = 0  # Durata dello scudo in frame

# Soglia per attivare lo scudo (in centimetri)
SHIELD_DISTANCE_THRESHOLD = 10  # Se la mano è entro 30 cm dal sensore, lo scudo si attiva

# Funzione per generare un nuovo oggetto
def spawn_item():
    item_x = random.randint(20, screen_width - 20)
    item_y = random.randint(20, screen_height - 20)
    items.append([item_x, item_y])

# Timer per la generazione degli oggetti
SPAWN_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_EVENT, 2000)  # Genera un nuovo oggetto ogni 2 secondi

# Loop principale del gioco
running = True
clock = pygame.time.Clock()

while running:
    # Gestione degli eventi
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == SPAWN_EVENT and not game_over:
            spawn_item()

    # Se il gioco è terminato
    if game_over:
        # Legge l'input del joystick per il riavvio
        if y_value < 500:  # Se il joystick è spinto verso l'alto (valore minore di 500)
            # Reset delle variabili di gioco
            game_over = False
            score = 0
            player_pos = [screen_width // 2, screen_height // 2]
            items.clear()
            bullets.clear()
            enemy_pos = [random.randint(0, screen_width - enemy_size), random.randint(0, screen_height - enemy_size)]
            shield_active = False
            shield_duration = 0
        else:
            # Mostra la schermata di game over
            screen.fill(BLACK)
            game_over_text = game_over_font.render("GAME OVER", True, WHITE)
            instruction_text = font.render("Move the joystick up to start again", True, WHITE)
            screen.blit(game_over_text, ((screen_width - game_over_text.get_width()) // 2, screen_height // 2 - 50))
            screen.blit(instruction_text, ((screen_width - instruction_text.get_width()) // 2, screen_height // 2 + 20))
            pygame.display.flip()
            clock.tick(60)
            continue  # Salta il resto del loop e aspetta l'input per il riavvio

    # Mappa i valori del joystick (da 0-1023 a -1 a 1)
    x_mapped = (x_value - 512) / 512  # Valori da -1 a 1
    y_mapped = (y_value - 512) / 512  # Valori da -1 a 1

    # Velocità costante del giocatore
    speed = 5  # Velocità fissa

    # Aggiorna la posizione del giocatore
    player_pos[0] += x_mapped * speed
    player_pos[1] += y_mapped * speed

    # Limita ai bordi dello schermo
    player_pos[0] = max(0, min(player_pos[0], screen_width))
    player_pos[1] = max(0, min(player_pos[1], screen_height))

    # Movimento del nemico verso il giocatore
    if enemy_pos[0] < player_pos[0]:
        enemy_pos[0] += enemy_speed
    elif enemy_pos[0] > player_pos[0]:
        enemy_pos[0] -= enemy_speed

    if enemy_pos[1] < player_pos[1]:
        enemy_pos[1] += enemy_speed
    elif enemy_pos[1] > player_pos[1]:
        enemy_pos[1] -= enemy_speed

    # Gestione del Pulsante del Joystick per Sparare
    # Controlla se il pulsante è appena stato premuto
    if button_state == 0 and previous_button_state == 1:
        # Crea un nuovo proiettile
        bullet_pos = [player_pos[0], player_pos[1]]
        bullet_speed = -10  # Velocità del proiettile (verso l'alto)
        bullets.append({'pos': bullet_pos, 'speed': bullet_speed})

    # Aggiorna lo stato precedente del pulsante
    previous_button_state = button_state

    # Aggiorna la posizione dei proiettili
    for bullet in bullets[:]:
        bullet['pos'][1] += bullet['speed']
        # Rimuovi il proiettile se esce dallo schermo
        if bullet['pos'][1] < 0:
            bullets.remove(bullet)
        else:
            # Verifica la collisione con il nemico
            bullet_rect = pygame.Rect(bullet['pos'][0] - 5, bullet['pos'][1] - 10, 10, 10)
            enemy_rect = pygame.Rect(int(enemy_pos[0]), int(enemy_pos[1]), enemy_size, enemy_size)
            if bullet_rect.colliderect(enemy_rect):
                bullets.remove(bullet)
                # Il nemico è stato colpito
                # Riposiziona il nemico in una nuova posizione casuale
                enemy_pos = [random.randint(0, screen_width - enemy_size), random.randint(0, screen_height - enemy_size)]
                # Aumenta il punteggio o la difficoltà
                score += 5  # Incrementa il punteggio

    # Gestione dello Scudo Protettivo
    if distance <= SHIELD_DISTANCE_THRESHOLD:
        shield_active = True
        shield_duration = 120  # Lo scudo rimane attivo per 2 secondi (60 FPS * 2)
    else:
        if shield_duration > 0:
            shield_duration -= 1
        else:
            shield_active = False

    # Disegna sullo schermo
    screen.fill(BLACK)

    # Disegna gli oggetti
    for item in items[:]:
        pygame.draw.circle(screen, ITEM_COLOR, (int(item[0]), int(item[1])), 10)

        # Verifica la collisione con il giocatore
        distance_to_player = ((player_pos[0] - item[0]) ** 2 + (player_pos[1] - item[1]) ** 2) ** 0.5
        if distance_to_player < player_radius + 10:
            items.remove(item)
            score += 1  # Incrementa il punteggio

    # Disegna il giocatore
    pygame.draw.circle(screen, PLAYER_COLOR, (int(player_pos[0]), int(player_pos[1])), player_radius)

    # Disegna lo scudo se attivo
    if shield_active:
        pygame.draw.circle(screen, SHIELD_COLOR, (int(player_pos[0]), int(player_pos[1])), player_radius + 10, 2)

    # Disegna i proiettili
    for bullet in bullets:
        pygame.draw.polygon(screen, WHITE, [
            (bullet['pos'][0], bullet['pos'][1]),
            (bullet['pos'][0] - 5, bullet['pos'][1] + 10),
            (bullet['pos'][0] + 5, bullet['pos'][1] + 10)
        ])

    # Disegna il nemico
    pygame.draw.rect(screen, ENEMY_COLOR, (int(enemy_pos[0]), int(enemy_pos[1]), enemy_size, enemy_size))

    # Verifica la collisione tra il giocatore e il nemico
    enemy_rect = pygame.Rect(int(enemy_pos[0]), int(enemy_pos[1]), enemy_size, enemy_size)
    player_rect = pygame.Rect(int(player_pos[0] - player_radius), int(player_pos[1] - player_radius), player_radius * 2, player_radius * 2)
    if enemy_rect.colliderect(player_rect):
        if not shield_active:
            game_over = True
        else:
            # Il nemico viene respinto o riposizionato
            enemy_pos = [random.randint(0, screen_width - enemy_size), random.randint(0, screen_height - enemy_size)]

    # Visualizza il punteggio
    score_text = font.render(f"Punteggio: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

    pygame.display.flip()

    # Controlla il frame rate
    clock.tick(60)

# Chiudi tutto
pygame.quit()
ser.close()
