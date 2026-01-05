import os
import sys

# --- БЛОК СОВМЕСТИМОСТИ С PYINSTALLER ---
if hasattr(sys, '_MEIPASS'):
    os.chdir(sys._MEIPASS)
# ---------------------------------------

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import math
import random
import time

app = Ursina()

# ---------------- НАСТРОЙКИ ----------------
window.fps_counter.enabled = True
window.exit_button.visible = False
window.title = "MINESHAFT"
camera.fov = 120
mouse.visible = True

# ---------------- БЛОКИ ----------------
blocks = [
    {'name': 'Трава', 'color': color.green, 'texture': 'grass'},
    {'name': 'Камень', 'color': color.light_gray, 'texture': 'white_cube'},
    {'name': 'Кирпич', 'color': color.red, 'texture': 'brick'},
    {'name': 'Дерево', 'color': color.brown, 'texture': 'white_cube'},
    {'name': 'Ступенька', 'color': color.orange, 'texture': 'white_cube'},
    {'name': 'Полублок', 'color': color.azure, 'texture': 'white_cube'},
]
selected_block = 0

# ---------------- МИР ----------------
ground = Entity(
    model='cube',
    scale=(100,1,100),
    texture='grass',
    collider='box',
    position=(0,-0.5,0),
    enabled=False
)

preview_block = Entity(
    model='cube',
    color=color.rgba(255,255,255,120),
    scale=1.01,
    enabled=False
)

# ---------------- ИГРОК ----------------
player = FirstPersonController(enabled=False)
player.speed = 14  
player.cursor.visible = False

crosshair = Entity(
    parent=camera.ui,
    model='quad',
    scale=0.005,
    color=color.white
)

# ---------------- ИНВЕНТАРЬ ----------------
inventory_ui = Entity(parent=camera.ui, y=-0.4, enabled=False)
slots = []

for i, b in enumerate(blocks):
    slot = Entity(
        parent=inventory_ui,
        model='quad',
        texture=b['texture'],
        color=b['color'],
        scale=0.1,
        x=(i-2.5)*0.12
    )
    slots.append(slot)

selector = Entity(
    parent=inventory_ui,
    model='quad',
    color=color.yellow,
    scale=0.12,
    z=-0.01
)
selector.position = slots[0].position

# ---------------- ГЛАВНОЕ МЕНЮ ----------------
main_menu = Entity(parent=camera.ui, enabled=True)
Panel(parent=main_menu, scale=(0.8,0.8), color=color.rgba(0,0,0,200))

Text("MINESHAFT", parent=main_menu, y=0.35, scale=3, origin=(0,0), color=color.yellow)

world_name = InputField(
    parent=main_menu,
    y=0.15,
    default_value="Новый мир",
    scale=(0.4,0.05)
)

def start_loading():
    main_menu.enabled = False
    loading_screen.enabled = True
    world_text.text = f"Мир: {world_name.text}"
    invoke(start_game, delay=2)

def start_game():
    loading_screen.enabled = False
    ground.enabled = True
    inventory_ui.enabled = True
    player.enabled = True
    mouse.locked = True
    mouse.visible = False
    player.position = (0,2,0)
    
    for drop in rain_drops:
        drop.enabled = True
    for cloud in clouds:
        cloud.enabled = True

# Исправлено: используем application.quit
Button(text="Играть", parent=main_menu, y=0.05, scale=(0.3,0.06), on_click=start_loading)
Button(text="Выйти", parent=main_menu, y=-0.05, scale=(0.3,0.06), color=color.red, on_click=application.quit)

# ---------------- ЭКРАН ЗАГРУЗКИ ----------------
loading_screen = Entity(parent=camera.ui, enabled=False)
Panel(parent=loading_screen, scale=(2,2), color=color.black)

loading_text = Text("Создание мира", parent=loading_screen, scale=2, origin=(0,0))
world_text = Text("", parent=loading_screen, y=-0.1, color=color.gray, origin=(0,0))

# ---------------- ПАУЗА ----------------
pause_menu = Entity(parent=camera.ui, enabled=False)
Panel(parent=pause_menu, scale=(0.4,0.5), color=color.rgba(0,0,0,180))

Text("ПАУЗА", parent=pause_menu, y=0.18, scale=2, origin=(0,0))

def resume():
    pause_menu.enabled = False
    application.paused = False
    mouse.locked = True
    mouse.visible = False

def return_to_menu():
    pause_menu.enabled = False
    application.paused = False
    player.enabled = False
    ground.enabled = False
    inventory_ui.enabled = False
    main_menu.enabled = True
    mouse.locked = False
    mouse.visible = True

Button(text="Продолжить", parent=pause_menu, y=0.05, scale=(0.3,0.06), on_click=resume)
Button(text="В меню", parent=pause_menu, y=-0.05, scale=(0.3,0.06), color=color.orange, on_click=return_to_menu)
Button(text="Выйти", parent=pause_menu, y=-0.15, scale=(0.3,0.06), color=color.red, on_click=application.quit)

# ---------------- ДОЖДЬ И ОБЛАКА ----------------
rain_drops = []
for _ in range(200):
    drop = Entity(
        model='cube', scale=(0.02, 0.3, 0.02), color=color.azure,
        position=(random.uniform(-50, 50), random.uniform(20, 40), random.uniform(-50, 50)),
        enabled=False
    )
    rain_drops.append(drop)

clouds = []
for _ in range(10):
    cloud = Entity(
        model='cube', scale=(random.uniform(5, 15), random.uniform(2, 5), random.uniform(5, 15)),
        color=color.rgba(255, 255, 255, 150),
        position=(random.uniform(-50, 50), random.uniform(20, 30), random.uniform(-50, 50)),
        enabled=False
    )
    clouds.append(cloud)

# ---------------- ОБНОВЛЕНИЕ ----------------
def update():
    if loading_screen.enabled:
        loading_text.text = "Создание мира" + "." * (int(time.time()*3)%4)
        return

    if not player.enabled or application.paused:
        return

    # Дождь
    wind_strength = 0.3
    for drop in rain_drops:
        drop.y -= time.dt * 20
        drop.x += math.sin(time.time() * 0.5) * wind_strength * time.dt * 2
        if drop.y < -2:
            drop.y = random.uniform(20, 40)
            drop.x = random.uniform(-50, 50)
            drop.z = random.uniform(-50, 50)

    # Облака
    for cloud in clouds:
        cloud.x += time.dt * 0.2
        if cloud.x > 60: cloud.x = -60

    # Предпросмотр блока
    hit = raycast(camera.world_position, camera.forward, distance=10, ignore=[player, preview_block, crosshair])
    if hit.hit:
        if hit.entity == ground:
            pos = Vec3(round(hit.world_point.x), 0, round(hit.world_point.z))
        else:
            pos = hit.entity.position + hit.normal
        
        preview_block.enabled = True
        preview_block.position = Vec3(round(pos.x), round(pos.y), round(pos.z))
    else:
        preview_block.enabled = False

# ---------------- ВВОД ----------------
def input(key):
    global selected_block

    if key == 'escape' and player.enabled:
        pause_menu.enabled = not pause_menu.enabled
        application.paused = pause_menu.enabled
        mouse.locked = not pause_menu.enabled
        mouse.visible = pause_menu.enabled

    if not player.enabled or application.paused:
        return

    if key in ('1','2','3','4','5','6'):
        selected_block = int(key)-1
        selector.position = slots[selected_block].position
        c = blocks[selected_block]['color']
        preview_block.color = color.rgba(c.r,c.g,c.b,120)

    if key == 'left mouse down' and preview_block.enabled:
        b = blocks[selected_block]
        e = Entity(
            model='cube', texture=b['texture'], color=b['color'],
            position=preview_block.position, collider='box'
        )
        if b['name'] == 'Ступенька': e.scale = (1, 0.5, 1)
        if b['name'] == 'Полублок': e.scale = (0.5, 1, 0.5)

    if key == 'right mouse down':
        hit = raycast(camera.world_position, camera.forward, 10, ignore=[player, preview_block, crosshair])
        if hit.hit and hit.entity != ground:
            destroy(hit.entity)

Sky()
app.run()
