import os.path
import pathlib
import math
import arcade

# Global constants
# Window Resolution and Title
HORIZONTAL_SCREEN = 1024
VERTICAL_SCREEN = 600
SCREEN_TITLE = "Deprecated King"
##########################################
# FLASHING WARNING
# ENEMY SPRITES FLASH A LOT DUE TO REFRESH RATE/DELTA TIME?

##########################################

# KEYS = [arcade.key.A, arcade.key.W, arcade.key.S, arcade.key.D, arcade.key.J, arcade.key.K]
# # for now these are gonna be the keys for movement, we can change them if its hard for new users to
# # move + execute

# Assets path
ASSETS_PATH = pathlib.Path(__file__).resolve().parent.parent / "assets"

# Sprite Scaling
MAP_SIZE_MULTIPLIER = 2.0
PLAYER_SIZE_MULTIPLIER = 2.0
XENO_SIZE_MULTIPLIER = 0.5
BOW_SIZE_MULTIPLIER = 1.5
# Our pixels are 16x16 in Tiled
SPRITE_PIXEL_MULTIPLIER = 16
# This is our scaled size in the map
MAP_PIXEL_MULTIPLIER = SPRITE_PIXEL_MULTIPLIER * MAP_SIZE_MULTIPLIER

# Physics and Movement Constants
ENEMY_MOVEMENT_SPEED = 3
PLAYER_MOVEMENT_SPEED = 7
GRAVITY = 1.2
PLAYER_JUMP_SPEED = 25
SLASH_X_KNOCKBACK = 20

# Cant put multiple enemies into phys engine
ENEMY_FALL_SPEED = -5
ENEMY_LIFT_SPEED = 10

#Attack constants
ATTACK_INTERVAL = 30
ARROW_SPRITE_SCALING = 0.8
SLASH_DAMAGE = 8
ARROW_SPEED = 5
ARROW_DAMAGE = 25

# Player initial coordinates
PLAYER_INIT_X = 100
PLAYER_INIT_Y = 100

#for tracking and setting direction of character sprites
CHARACTER_FACE_RIGHT = 0
CHARACTER_FACE_LEFT = 1

LAYER_NAME_PLATFORMS = "Platforms Layer"
LAYER_NAME_PLAYER = "Player"
LAYER_NAME_ENEMIES = "Enemies"
LAYER_NAME_BOSS = "Boss"
LAYER_NAME_ARROWS = "Arrows"
LAYER_NAME_BOW = 'Bows'
LAYER_NAME_SLASH = 'Slash'
def load_texture_and_flipped(filename):
    """load a pair of textures, one original, one flipped"""
    # 0 for right (original, 1 for flipped to other direction)
    texture_and_flipped = []
    texture_and_flipped.append(arcade.load_texture(filename))
    texture_and_flipped.append(arcade.load_texture(filename, flipped_horizontally=True))
    return texture_and_flipped

class Arrow(arcade.Sprite):
    """Creates Arrow sprites without needing multiple sprites"""
    def __init__(self, name_folder, name_file):
        super().__init__()
        characters_path = ASSETS_PATH / f"{name_folder}/{name_file}"
        self.arrow_dir= load_texture_and_flipped(f"{characters_path}3.png")
        self.texture = self.arrow_dir[0]
        self.character_face_direction = CHARACTER_FACE_RIGHT

    def update_animation(self, delta_time: float = 1 / 60):
        if self.change_x < 0 and self.character_face_direction == CHARACTER_FACE_RIGHT:
            self.character_face_direction = CHARACTER_FACE_LEFT

        elif self.change_x > 0 and self.character_face_direction == CHARACTER_FACE_LEFT:
            self.character_face_direction = CHARACTER_FACE_RIGHT
        self.texture = self.arrow_dir[self.character_face_direction]

class Bow(arcade.Sprite):
    """Creates bow sprite with animation for visibility when firing arrows"""
    def __init__(self, name_folder, name_file):
        super().__init__()
        characters_path = ASSETS_PATH / f"{name_folder}/{name_file}"

        self.texture = load_texture_and_flipped(f"{characters_path}45.png")[0]
        self.bow_cycle = []
        for i in range(6):
            texture = load_texture_and_flipped(f"{characters_path}{i+46}.png")
            self.bow_cycle.append(texture)
        self.cur_texture = 0
        self.character_face_direction = CHARACTER_FACE_RIGHT

    def update_animation(self, delta_time: float = 1 / 60):
        # Only update when its visible
        if self.visible:
            if self.change_x < 0 and self.character_face_direction == CHARACTER_FACE_RIGHT:
                self.character_face_direction = CHARACTER_FACE_LEFT
            elif self.change_x > 0 and self.character_face_direction == CHARACTER_FACE_LEFT:
                self.character_face_direction = CHARACTER_FACE_RIGHT

            # Bow has a few more sprites in its animation, so it updates with more stages of texture
            self.cur_texture += 1
            if self.cur_texture >= 6:
                self.cur_texture = 0
            self.texture = self.bow_cycle[self.cur_texture][self.character_face_direction]

        # 41-46
class Slash(arcade.Sprite):
    """Creates slash animation sprite obj for collision with enemies when slashing"""
    def __init__(self, name_folder, name_file):
        super().__init__()
        characters_path = ASSETS_PATH / f"{name_folder}/{name_file}"
        self.texture = load_texture_and_flipped(f"{characters_path}1.png")[0]
        self.slash_cycle = []

        for i in range(4): # 1,2,3,4
            texture = load_texture_and_flipped(f"{characters_path}{i + 1}.png")
            self.slash_cycle.append(texture)
        self.cur_texture = 0
        self.character_face_direction = CHARACTER_FACE_RIGHT



    def update_animation(self, delta_time: float = 1 / 60):

        if self.change_x < 0 and self.character_face_direction == CHARACTER_FACE_RIGHT:
            self.character_face_direction = CHARACTER_FACE_LEFT
        elif self.change_x > 0 and self.character_face_direction == CHARACTER_FACE_LEFT:
            self.character_face_direction = CHARACTER_FACE_RIGHT

        self.cur_texture += 1
        if self.cur_texture >= 3:
            self.cur_texture = 0
        self.texture = self.slash_cycle[self.cur_texture][self.character_face_direction]
        return



class Character(arcade.Sprite):
    """Creates a character based on the arcade Sprite class,
    and implements its direction facing, and animations
    used mainly for subclasses"""
    def __init__(self, name_folder, name_file):
        # make the sprite obj
        super().__init__()

        #Setting file path of sprite
        characters_path = ASSETS_PATH / f"{name_folder}/{name_file}"

        # set the initial textures
        self.idle_textures = load_texture_and_flipped(f"{characters_path}1.png")
        self.texture = self.idle_textures[0]
        self.character_face_direction = CHARACTER_FACE_RIGHT

        self.walk_textures = []
        for i in range(4):
            textures = load_texture_and_flipped(f"{characters_path}{i + 1}.png")
            self.walk_textures.append(textures)

        self.cur_texture = 0
        self.scale = PLAYER_SIZE_MULTIPLIER

        self.jump_textures = load_texture_and_flipped(f"{characters_path}2.png")
        self.fall_textures = load_texture_and_flipped(f"{characters_path}3.png")

    def update_animation(self, delta_time: float = 1 / 60):

        #check if we need to flip the character around
        if self.change_x < 0 and self.character_face_direction == CHARACTER_FACE_RIGHT:
            self.character_face_direction = CHARACTER_FACE_LEFT
        elif self.change_x > 0 and self.character_face_direction == CHARACTER_FACE_LEFT:
            self.character_face_direction = CHARACTER_FACE_RIGHT
        if self.change_x == 0:
            self.texture = self.idle_textures[self.character_face_direction]
            return

        if self.change_y > 0 :
            self.texture = self.jump_textures[self.character_face_direction]
            return
        elif self.change_y < 0 :
            self.texture = self.fall_textures[self.character_face_direction]
            return

        #walking animation
        self.cur_texture += 1
        if self.cur_texture >= 4:
            self.cur_texture = 0
        self.texture = self.walk_textures[self.cur_texture][self.character_face_direction]

class Enemy(Character):
    """Parent class of enemies"""
    def __init__(self, name_folder, name_file):

        super().__init__(name_folder, name_file)

class MiniEnemy(Enemy):
    def __init__(self):
        super().__init__("images/enemies/Xeno/Walk", "Xeno")
        self.character_face_direction = CHARACTER_FACE_RIGHT
        self.health = 50
        self.scale = XENO_SIZE_MULTIPLIER



class Boss(Enemy):
    def __init__(self):

        """Creates a Boss (Knight)"""
        super().__init__("darkemperor", 'darkemperor_run')
        self.character_face_direction = CHARACTER_FACE_RIGHT
        self.health = 500


class PlayerCharacter(Character):
    """Creates the player sprite: A king"""
    def __init__(self):
        super().__init__("player_sprites", 'king')
        self.health = 3
        self.character_face_direction = CHARACTER_FACE_RIGHT

class Platformer(arcade.Window):
    """Creates the window which the user interacts with """
    def __init__(self) -> None:
        super().__init__(HORIZONTAL_SCREEN, VERTICAL_SCREEN, SCREEN_TITLE)
        arcade.set_background_color(arcade.csscolor.SKY_BLUE)

        # Track key presses (Movement and Combat)
        # "W, A, D "
        self.move_left = False
        self.move_right = False
        self.up_pressed = False
        self.can_jump = True

        # "J, K"
        self.shoot_pressed = False
        self.slash_pressed = False

        # The map to be loaded into the scene
        self.tile_map = None

        # For enemy and boss sprites
        self.enemies = None
        self.boss = None

        # mainly for displaying the platform i guess
        self.scene = None

        # One sprite for the player, no more is needed
        self.player = None

        # We need a physics engine as well for physics
        self.physics_engine = None

        #Camera for screen and UI
        self.camera = None
        self.ui_camera = None

        # Init Attack Variables
        self.attack = False
        self.attack_timer = 0

        # Init Placeholders for bow and slash sprites
        self.bow = None
        self.slash = None

        # Collision Variables, for temporary invulnerability after collision
        self.enemy_collision_timer = 60
        self.can_collision_damage = False

        # Track level for changing levels/maps
        self.level = 1

        # Load up our sounds here
        # self.coin_sound = arcade.load_sound(
        #     str(ASSETS_PATH / "sounds" / "coin.wav")
        # )
        # self.jump_sound = arcade.load_sound(
        #     str(ASSETS_PATH / "sounds" / "jump.wav")
        # )
        # self.victory_sound = arcade.load_sound(
        #     str(ASSETS_PATH / "sounds" / "victory.wav")
        # )
        # self.shoot_sound = arcade.load_sound(str(ASSETS_PATH / "sound" / "shoot.wav")

        #self.hit_sound = arcade.load_sound(str(ASSETS_PATH / "sound" / "hit.wav")

    def setup(self):
        """Sets up the game for the current level"""

        # Camera setup
        # For some reason, needs 2 cameras, otherwise ui wont follow
        self.camera = arcade.Camera(self.width, self.height)
        self.ui_camera = arcade.Camera(self.width, self.height)


        # Tracks attack interval time
        self.attack = True
        self.attack_timer = 0

        # Map Path
        map = ASSETS_PATH / "maps" / f"platformer_map{self.level}.json"
        layer_options = {
            "Platforms Layer": {"use_spatial_hash": True},
        }

        self.tile_map = arcade.load_tilemap(map, MAP_SIZE_MULTIPLIER, layer_options)
        # scene is needed, cannot directly use tile map as scene anymore
        self.scene = arcade.Scene.from_tilemap(self.tile_map)


        # Create our player character and set position on map
        self.player = PlayerCharacter()
        self.player.center_x = PLAYER_INIT_X
        self.player.center_y = PLAYER_INIT_Y
        self.scene.add_sprite(LAYER_NAME_PLAYER, self.player)

        # Creates player's bow sprite
        self.bow = Bow("recurve bow", "recurvebow")
        self.bow.visible = False
        self.bow.center_x = PLAYER_INIT_X
        self.bow.center_y = PLAYER_INIT_Y
        self.bow.scale = BOW_SIZE_MULTIPLIER
        self.scene.add_sprite(LAYER_NAME_BOW, self.bow)

        # creates player's slash sprite
        self.slash = Slash("slash", "swoosh")
        self.slash.visible = False
        self.slash.center_x = PLAYER_INIT_X
        self.slash.center_Y = PLAYER_INIT_Y
        self.slash.scale = 4
        self.scene.add_sprite(LAYER_NAME_SLASH, self.slash)

        # Init layers for enemies (before adding any enemies)
        self.enemies = []
        self.scene.add_sprite_list(LAYER_NAME_ENEMIES)
        self.scene.add_sprite_list(LAYER_NAME_BOSS)

        # Sets up the map's specific enemy requirements
        self.load_enemies_and_map()

        # Init arrow layer for scene
        self.scene.add_sprite_list(LAYER_NAME_ARROWS)

        # Set background
        arcade.set_background_color(arcade.csscolor.SKY_BLUE)

        # Setup Physics engine
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player,[self.scene.get_sprite_list(LAYER_NAME_PLATFORMS)], gravity_constant = GRAVITY,)





    def on_key_press(self, key: int, modifiers: int):
        """Arguments:
        key {int} -- Which key was pressed
        modifiers {int} -- Which modifiers were down at the time
        """
        # player moving to the left
        if key == arcade.key.A:
            self.move_left = True
        #player moving to the right
        elif key == arcade.key.D :
            self.move_right = True
        # player moving up
        elif key == arcade.key.W:
            self.up_pressed = True

        if key == arcade.key.J:
            self.shoot_pressed = True
        if key == arcade.key.K:
            self.slash_pressed = True

        if self.up_pressed:
            if (self.physics_engine.can_jump(y_distance=10) and self.can_jump):
                self.player.change_y = PLAYER_JUMP_SPEED
                self.jump_needs_reset = False

        if self.move_right and not self.move_left:
            self.player.change_x = PLAYER_MOVEMENT_SPEED
        elif self.move_left and not self.move_right:
            self.player.change_x = -PLAYER_MOVEMENT_SPEED
        else:
            self.player.change_x = 0

    def on_key_release(self, key: int, modifiers: int):
        """Arguments:
        key {int} -- Which key was released
        modifiers {int} -- Which modifiers were down at the time
        """
        if key == arcade.key.A:
            self.move_left = False
        elif key == arcade.key.D:
            self.move_right = False
        elif key == arcade.key.W:
            self.up_pressed = False
            self.can_jump = True


        if key == arcade.key.J:
            self.shoot_pressed = False
        if key == arcade.key.K:
            self.slash_pressed = False

        # Jump only if
        if self.up_pressed:
            if self.physics_engine.can_jump(y_distance=10) and not self.can_jump:
                self.player.change_y = PLAYER_JUMP_SPEED
                self.can_jump = False

        # will cancel out movement if both keys are pressed, or neither
        if self.move_right and not self.move_left:
            self.player.change_x = PLAYER_MOVEMENT_SPEED
        elif self.move_left and not self.move_right:
            self.player.change_x = -PLAYER_MOVEMENT_SPEED
        else:
            self.player.change_x = 0

    def on_update(self, delta_time: float):
        """Updates the position of all game objects

        Arguments:
            delta_time {float} -- How much time since the last call
        """
        self.enemy_collision_timer += 0.5
        #self.player.update_animation(delta_time)
        self.physics_engine.update()

        self.slash.center_y = self.player.center_y

        self.slash.character_face_direction = self.player.character_face_direction
        if self.slash.character_face_direction == CHARACTER_FACE_RIGHT:
            self.slash.center_x = self.player.center_x +16
        else:
            self.slash.center_x = self.player.center_x -16

        if  self.physics_engine.can_jump():
            self.player.can_jump = False
        else:
            self.player.can_jump = True

        self.bow.center_x = self.player.center_x
        self.bow.center_y = self.player.center_y
        self.bow.change_x = self.player.change_x
        self.bow.character_face_direction = self.player.character_face_direction

        if self.attack:
            if self.shoot_pressed:
                self.bow.visible = True
                self.slash.visible = False

                arrow = Arrow("images/Arrows", "arrow")
                arrow.scale = 2

                if self.player.character_face_direction == CHARACTER_FACE_RIGHT:

                    arrow.change_x = ARROW_SPEED
                    arrow.center_x = self.player.center_x+10
                    arrow.center_y = self.player.center_y
                else:
                    arrow.change_x = -ARROW_SPEED
                    arrow.character_face_direction = self.player.character_face_direction
                    arrow.center_x = self.player.center_x-10
                    arrow.center_y = self.player.center_y

                self.scene.add_sprite(LAYER_NAME_ARROWS, arrow)

                self.attack = False
            elif self.slash_pressed:

                self.slash.visible = True
                self.slash.character_face_direction = self.player.character_face_direction

                if self.slash.character_face_direction == CHARACTER_FACE_RIGHT:
                    self.slash.center_x = self.player.center_x + 16
                else:
                    self.slash.center_x = self.player.center_x - 16
                self.bow.visible = False
                self.attack = False

        else:
            # only show the sprite (bow or slash) temporarily
            self.attack_timer += 0.5
            if self.attack_timer > ATTACK_INTERVAL / 4:
                self.slash.visible = False

            if self.attack_timer >= ATTACK_INTERVAL:
                self.attack = True
                self.attack_timer = 0
            elif self.attack_timer > ATTACK_INTERVAL / 2:
                self.bow.visible = False

        # delete arrows that leave the map
        for arrow in self.scene.get_sprite_list(LAYER_NAME_ARROWS):
            if arrow.center_x < -20 or arrow.center_x > self.tile_map.width* MAP_PIXEL_MULTIPLIER:
                self.scene.get_sprite_list(LAYER_NAME_ARROWS).remove(arrow)
            arrow.center_x += arrow.change_x

        # implements collision with enemies
        if(arcade.check_for_collision_with_list(self.player, self.scene.get_sprite_list(LAYER_NAME_ENEMIES))):
            if self.enemy_collision_timer >= 60:
                self.player.health -= 1
                self.enemy_collision_timer = 0

        # delete arrows that touch the platforms
        for arrow in self.scene.get_sprite_list(LAYER_NAME_ARROWS):
            if arcade.check_for_collision_with_list(arrow, self.scene.get_sprite_list(LAYER_NAME_PLATFORMS)):
                self.scene.get_sprite_list(LAYER_NAME_ARROWS).remove(arrow)

        # check if player can move to next level
        if arcade.check_for_collision_with_list(self.player, self.tile_map.sprite_lists["Victory"]):
            self.level+= 1
            print("Winner")
            self.setup()


        # if(arcade.check_for_collision_with_list(self.player, self.scene.get_sprite_list(LAYER_NAME_BOSS))):
        #     if self.enemy_collision_timer >= 60:
        #         self.player.health -= 1
        #         self.enemy_collision_timer = 0
        #

        # Enemies chase you within 300 units of height, 500 units of width
        for enemy in self.enemies:

            if (abs(self.player.center_y - enemy.center_y < 300) and
                    abs(self.player.center_x - enemy.center_x) < 500 and not arcade.check_for_collision_with_list(enemy, self.scene.get_sprite_list(LAYER_NAME_PLATFORMS))):
                if self.player.center_x >= enemy.center_x:
                    enemy.change_x = ENEMY_MOVEMENT_SPEED
                    enemy.center_x += enemy.change_x
                elif self.player.center_x < enemy.center_x:
                    enemy.change_x = -ENEMY_MOVEMENT_SPEED
                    enemy.center_x += enemy.change_x
            else:
                enemy.change_x = 0

        # Updates sprites too quickly
        # Clunky way of "simulating gravity" on enemy
        # Idea: Enemies move up if touching ground -> In air -> Touch ground again -> Repeat
        for enemy in self.enemies:
            if abs(self.player.center_y - enemy.center_y > 300) and abs(self.player.center_x - enemy.center_x) > 500:
                enemy.change_x = 0
            elif arcade.check_for_collision_with_list(enemy, self.scene.get_sprite_list(LAYER_NAME_PLATFORMS)):
                enemy.change_y = 0
                enemy.center_y += ENEMY_LIFT_SPEED
            elif not arcade.check_for_collision_with_list(enemy, self.scene.get_sprite_list(LAYER_NAME_PLATFORMS)):
                enemy.center_y += ENEMY_FALL_SPEED

        # arrow collision
        for arrow in self.scene.get_sprite_list(LAYER_NAME_ARROWS):
            for enemy in self.enemies:

                if arcade.check_for_collision(arrow, enemy):
                    print(enemy.center_x)

                    enemy.health -= ARROW_DAMAGE
                    self.scene.get_sprite_list(LAYER_NAME_ARROWS).remove(arrow)
                    print(enemy.health)
                    if(enemy.health <= 0):
                        if enemy in self.scene.get_sprite_list(LAYER_NAME_ENEMIES):

                            self.enemies.remove(enemy)
                            self.scene.get_sprite_list(LAYER_NAME_ENEMIES).remove(enemy)
                            print("Enemy Dead")
                    # break

        if self.slash.visible:

            for enemy in self.enemies:
                if arcade.check_for_collision(self.slash, enemy):
                    # print("Slash Hit")
                    enemy.health -= SLASH_DAMAGE
                    if self.player.center_x > enemy.center_x:
                        enemy.center_x -= SLASH_X_KNOCKBACK
                        # print("left hit")
                    else:

                        enemy.center_x += SLASH_X_KNOCKBACK
                        # print("right hit")
                    if (enemy.health <= 0):
                        if enemy in self.scene.get_sprite_list(LAYER_NAME_ENEMIES):
                            self.enemies.remove(enemy)
                            self.scene.get_sprite_list(LAYER_NAME_ENEMIES).remove(enemy)
                            print("Enemy Dead")

        # Updates each sprite in layers
        self.scene.update_animation(delta_time, [LAYER_NAME_PLAYER, LAYER_NAME_SLASH, LAYER_NAME_ENEMIES,
                                                 LAYER_NAME_BOSS, LAYER_NAME_ARROWS, LAYER_NAME_BOW])
        # restart the game level
        if self.player.health == 0:
            self.setup()


        self.player_camera()

    def on_draw(self):
        arcade.start_render()
        self.camera.use()
        self.scene.draw(pixelated=True)

        self.ui_camera.use()
        health_number = f"Health: {self.player.health}"
        arcade.draw_text(health_number, 10, 550, arcade.csscolor.BLACK, 18)

        # pass
    def player_camera(self):
        screen_center_x = self.player.center_x - (self.camera.viewport_width / 2)
        screen_center_y = self.player.center_y - (self.camera.viewport_height / 2)

        if screen_center_x < 0:
            screen_center_x = 0
        if screen_center_y < 0:
            screen_center_y = 0
        player_centered = screen_center_x, screen_center_y

        self.camera.move_to(player_centered)

    def load_enemies_and_map(self):
        if self.level == 1:
            pass
        elif self.level == 2:
            for i in range(5):
                enemy = MiniEnemy()
                enemy.center_x = 600 + ((i*10) * 60)
                enemy.center_y = 100
                enemy.change_y = ENEMY_FALL_SPEED
                enemy.change_x = ENEMY_MOVEMENT_SPEED
                self.scene.add_sprite(LAYER_NAME_ENEMIES, enemy)
                self.enemies.append(enemy)

            self.boss = Boss()
            self.boss.center_x = 400
            self.boss.center_y = 400
            self.boss.change_y = ENEMY_FALL_SPEED

            self.scene.add_sprite(LAYER_NAME_BOSS, self.boss)
            self.enemies.append(self.boss)



def main():
    window = Platformer()
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()
