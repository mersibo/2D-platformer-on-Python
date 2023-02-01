import pygame
import pygame.freetype
from pygame import *
from player import *
from blocks import *
from tkinter import *
import os

import tmxreader # Может загружать tmx файлы
import helperspygame # Преобразует tmx карты в формат  спрайтов pygame

#Объявляем переменные
WIN_WIDTH = 800 #Ширина создаваемого окна
WIN_HEIGHT = 640 # Высота
DISPLAY = (WIN_WIDTH, WIN_HEIGHT) # Группируем ширину и высоту в одну переменную
BACKGROUND_COLOR = "#000000"
CENTER_OF_SCREEN = WIN_WIDTH / 2, WIN_HEIGHT / 2

FILE_DIR = os.path.dirname(__file__)


class Camera(object):
    '''Класс для работы с камерой'''
    def __init__(self, camera_func, width, height):
        '''Конструктор класса'''
        self.camera_func = camera_func
        self.state = Rect(0, 0, width, height)

    def apply(self, target):
        '''Применение камеры к объекту'''
        
        return target.rect.move(self.state.topleft)
        

    def update(self, target):
        '''Обновление положения камеры'''
        self.state = self.camera_func(self.state, target.rect)

    def reverse(self, pos):# получение внутренних координат из глобальных
        '''Преобразование координат из глобальных во внутренние'''
        
        return pos[0] - self.state.left, pos[1] - self.state.top
        
def camera_config(camera, target_rect):
    '''Конфигурация камеры'''
    l, t, _, _ = target_rect
    _, _, w, h = camera
    l, t = -l+WIN_WIDTH / 2, -t+WIN_HEIGHT / 2

    l = min(0, l)                           # Не движемся дальше левой границы
    l = max(-(camera.width-WIN_WIDTH), l)   # Не движемся дальше правой границы
    t = max(-(camera.height-WIN_HEIGHT), t) # Не движемся дальше нижней границы
    t = min(0, t)                           # Не движемся дальше верхней границы


    return Rect(l, t, w, h) 



def loadLevel(name):
    '''Загрузка уровня'''
    global playerX, playerY # объявляем глобальные переменные, это координаты героя
    global total_level_height, total_level_width
    global sprite_layers # все слои карты
    world_map = tmxreader.TileMapParser().parse_decode('%s/%s.tmx' % (FILE_DIR, name)) # загружаем карту
    resources = helperspygame.ResourceLoaderPygame() # инициируем преобразователь карты
    resources.load(world_map) # и преобразуем карту в понятный pygame формат

    sprite_layers = helperspygame.get_layers_from_map(resources) # получаем все слои карты

    
    platforms_layer = sprite_layers[1]
    dieBlocks_layer = sprite_layers[2]

    for row in range(0, platforms_layer.num_tiles_x): # перебираем все координаты тайлов
        for col in range(0, platforms_layer.num_tiles_y):
            if platforms_layer.content2D[col][row] is not None:
                pf = Platform(row * PLATFORM_WIDTH, col * PLATFORM_WIDTH)# опять создаем объкты класса Platform
                platforms.append(pf)
            if dieBlocks_layer.content2D[col][row] is not None:
                bd = BlockDie(row * PLATFORM_WIDTH, col * PLATFORM_WIDTH)
                platforms.append(bd)

    monsters_layer = sprite_layers[3]
    for monster in monsters_layer.objects:
        try:
            x = monster.x
            y = monster.y
            if monster.name == "Player":
                playerX = x
                playerY = y - PLATFORM_HEIGHT
            elif monster.name == "Comp":
                pr = Comp(x, y - PLATFORM_HEIGHT)
                platforms.append(pr)
                entities.add(pr)
                animatedEntities.add(pr)
        except:
            print("Ошибка на монстрах")

    total_level_width = platforms_layer.num_tiles_x * PLATFORM_WIDTH # Считаем ширину уровня
    total_level_height = platforms_layer.num_tiles_y * PLATFORM_HEIGHT   # высоту





def main():
    '''Основная функция'''
    pygame.init() # Инициация PyGame, обязательная строчка
    screen = pygame.display.set_mode(DISPLAY) # Создаем окошко
    pygame.display.set_caption("Побег из МИЭМа") # Пишем в шапку
    bg = Surface((WIN_WIDTH, WIN_HEIGHT)) # Создание видимой поверхности
    # будем использовать как фон

    renderer = helperspygame.RendererPygame() # визуализатор
    for lvl in range(1,2):
        loadLevel("levels/map_%s" % lvl)
        bg.fill(Color(BACKGROUND_COLOR))     # Заливаем поверхность сплошным цветом

        left = right = False # по умолчанию - стоим
        up = False
        running = False
        try:
            hero = Player(playerX, playerY) # создаем героя по (x,y) координатам
            entities.add(hero)
        except:
            print (u"Не удалось на карте найти героя, взяты координаты по-умолчанию")
            hero = Player(38, 768)
        entities.add(hero)

        timer = pygame.time.Clock()

        camera = Camera(camera_config, total_level_width, total_level_height)

        start_time = pygame.time.get_ticks()
        font = pygame.freetype.SysFont('Times New Roman', 30)
        while not hero.winner: # Основной цикл программы
            timer.tick(60)
            
            current_time = pygame.time.get_ticks()
            delta_time_s = (current_time - start_time) // 100 / 10

            text_surf, text_rect = font.render(str(delta_time_s), (255, 255, 255), size=30)  
            text_pos = (700, 50)
            screen.blit(text_surf, text_pos)

            for e in pygame.event.get(): # Обрабатываем события
                if e.type == QUIT:
                    raise SystemExit
                if e.type == KEYDOWN and e.key == K_w:
                    up = True
                if e.type == KEYDOWN and e.key == K_a:
                    left = True
                if e.type == KEYDOWN and e.key == K_d:
                    right = True

                if e.type == KEYUP and e.key == K_w:
                    up = False
                if e.type == KEYUP and e.key == K_d:
                    right = False
                if e.type == KEYUP and e.key == K_a:
                    left = False
            for sprite_layer in sprite_layers: # перебираем все слои
                if not sprite_layer.is_object_group: # и если это не слой объектов
                   renderer.render_layer(screen, sprite_layer) # отображаем его

            for e in entities:
                screen.blit(e.image, camera.apply(e))
            animatedEntities.update() # показываеaм анимацию
            camera.update(hero) # центризируем камеру относительно персонажа
            center_offset = camera.reverse(CENTER_OF_SCREEN) # получаем координаты внутри длинного уровня
            renderer.set_camera_position_and_size(center_offset[0], center_offset[1], \
                                                  WIN_WIDTH, WIN_HEIGHT, "center")
            hero.update(left, right, up, running, platforms) # передвижение
            pygame.display.update()     # обновление и вывод всех изменений на экран
            screen.blit(bg, (0, 0))      # Каждую итерацию необходимо всё перерисовывать
        for sprite_layer in sprite_layers:
            if not sprite_layer.is_object_group:
                renderer.render_layer(screen, sprite_layer)
        # когда заканчиваем уровень
        color = (0, 0, 0)
        for e in entities:
            screen.blit(e.image, camera.apply(e)) # еще раз все перерисовываем
        font=pygame.font.Font("scaring.otf",32)
        screen.fill(color)
        smile_image = pygame.image.load("blocks/smile.png")
        screen.blit(smile_image, (230, 220))
        text=font.render(("Ты первый...кому удалось отсюда сбежать... поздравляю!"), True, (139, 0, 0))# выводим надпись
        screen.blit(text, (25, 70))
        text=font.render(("Тебе понадобилось" + ' ' + str(delta_time_s) + ' ' + "сек"), True, (139, 0, 0))# выводим надпись
        screen.blit(text, (230, 130))
        pygame.display.update()
        time.wait(3000) # ждем 3 секунд и после - переходим на следующий уровень
        

level = []
entities = pygame.sprite.Group() # Все объекты
animatedEntities = pygame.sprite.Group() # все анимированные объекты, за исключением героя
monsters = pygame.sprite.Group() # Все передвигающиеся объекты
platforms = [] # то, во что мы будем врезаться или опираться

def register():
    '''Функция регистрации'''
    global register_screen
    register_screen = Toplevel(main_screen, background=('#2F4F4F'))
    register_screen.title("Регистрация")
    register_screen.geometry("800x640")
 
    global username
    global password
    global username_entry
    global password_entry
    username = StringVar()
    password = StringVar()
    
    Label(register_screen, text="\n\n\n\n\n\n\n\n\n\n", bg=('#2F4F4F')).pack()
    Label(register_screen, text="Заполните поля", font=("Calibri", 18), bg=('#2F4F4F'), fg=('#FFFAFA')).pack()
    Label(register_screen, text="", bg=('#2F4F4F')).pack()
    username_lable = Label(register_screen, text="Имя пользователя", bg=('#2F4F4F'), fg=('#FFFAFA'))
    username_lable.pack()
    username_entry = Entry(register_screen, textvariable=username)
    username_entry.pack()
    password_lable = Label(register_screen, text="Пароль", bg=('#2F4F4F'), fg=('#FFFAFA'))
    password_lable.pack()
    password_entry = Entry(register_screen, textvariable=password, show='*')
    password_entry.pack()
    Label(register_screen, text="\n\n", bg=('#2F4F4F')).pack()
    Button(register_screen, text="Зарегестрироваться", width=25, height=2, command = register_user).pack()
 

 
def login():
    '''Функция входа'''
    global login_screen
    login_screen = Toplevel(main_screen, background=('#2F4F4F'))
    login_screen.title("Вход")
    login_screen.geometry("800x640")
    
 
    global username_verify
    global password_verify
 
    username_verify = StringVar()
    password_verify = StringVar()
 
    global username_login_entry
    global password_login_entry
    
    Label(login_screen, text="\n\n\n\n\n\n\n\n\n\n", bg=('#2F4F4F')).pack()
    Label(login_screen, text="Введите данные для входа", font=("calibri", 18), bg=('#2F4F4F'), fg=('#FFFAFA')).pack()
    Label(login_screen, text="", bg=('#2F4F4F')).pack()
    Label(login_screen, text="Имя пользователя", width=30, height=2, bg=('#2F4F4F'), fg=('#FFFAFA')).pack()
    username_login_entry = Entry(login_screen, textvariable=username_verify)
    username_login_entry.pack()
    Label(login_screen, text="Пароль", width=30, height=2, bg=('#2F4F4F'), fg=('#FFFAFA')).pack()
    password_login_entry = Entry(login_screen, textvariable=password_verify, show= '*')
    password_login_entry.pack()
    Label(login_screen, text="", bg=('#2F4F4F')).pack()
    Button(login_screen, text="Вход", width=10, height=1, command = login_verify).pack()

 
def register_user():
    '''Функция регистрации пользователя'''
    username_info = username.get()
    password_info = password.get()
 
    file = open(username_info, "w")
    file.write(username_info + "\n")
    file.write(password_info)
    file.close()
 
    username_entry.delete(0, END)
    password_entry.delete(0, END)
 
    Label(register_screen, text="Регистрация прошла успешно", fg=('#FFD700'), font=("calibri", 15), bg=('#2F4F4F')).pack()

 
def login_verify():
    '''Функция проверки входа'''
    username1 = username_verify.get()
    password1 = password_verify.get()
    username_login_entry.delete(0, END)
    password_login_entry.delete(0, END)
 
    list_of_files = os.listdir()
    if username1 in list_of_files:
        file1 = open(username1, "r")
        verify = file1.read().splitlines()
        if password1 in verify:
            login_sucess()
 
        else:
            password_not_recognised()
 
    else:
        user_not_found()

 
def login_sucess():
    '''Функция проверки успешного входа'''
    if __name__ == "__main__":
        main()

 
def password_not_recognised():
    '''Функция проверки неверного пароля'''
    global password_not_recog_screen
    password_not_recog_screen = Toplevel(login_screen)
    password_not_recog_screen.title("Успешно")
    password_not_recog_screen.geometry("150x100")
    Label(password_not_recog_screen, text="Неверный пароль или имя пользователя").pack()
    Button(password_not_recog_screen, text="OK", command=delete_password_not_recognised).pack()
 
 
def user_not_found():
    '''Функция проверки неверного имени пользователя'''
    global user_not_found_screen
    user_not_found_screen = Toplevel(login_screen)
    user_not_found_screen.title("Успешно")
    user_not_found_screen.geometry("150x100")
    Label(user_not_found_screen, text="Неверное имя пользователя").pack()
    Button(user_not_found_screen, text="OK", command=delete_user_not_found_screen).pack()

 
def delete_password_not_recognised():
    '''Функция удаления окна неверного пароля'''
    password_not_recog_screen.destroy()
 
 
def delete_user_not_found_screen():
    '''Функция удаления окна неверного имени пользователя'''
    user_not_found_screen.destroy()

 
def main_account_screen():
    '''Функция главного окна'''
    global main_screen
    main_screen = Tk()
    main_screen.geometry("800x600")
    main_screen.title("Game Launcher")
    image = PhotoImage(file="blocks/background.png")
    background_label = Label(main_screen, image=image)
    background_label.place(x=0, y=-50, width=800, height=700)
    Label(text="\n\n\n\n\n\n\n\n\n\n\n\n\n", bg=BACKGROUND_COLOR).pack()
    Label(text="Войдите или зарегестрируйтесь", width="300", bg = BACKGROUND_COLOR, fg='#fffafa', height="2", font=("calibri", 18)).pack()
    Button(text="Войти", height="2", width="30", font=("calibri", 11), command = login).pack()
    Label(text="", bg=BACKGROUND_COLOR).pack()
    Button(text="Зарегестрироваться", height="2", width="30", font=("calibri", 11), command=register).pack()

    main_screen.mainloop()
 
main_account_screen()

