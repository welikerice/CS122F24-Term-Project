import os.path
import pathlib
import math
import arcade

# Global constants
# Window Resolution and Title
HORIZONTAL_SCREEN = 1024
VERTICAL_SCREEN = 600
SCREEN_TITLE = "Deprecated King"

# KEYS = [arcade.key.A, arcade.key.W, arcade.key.S, arcade.key.D, arcade.key.F, arcade.key.G, arcade.key.SPACE, arcade.key.LSHIFT]
# # for now these are gonna be the keys for movement, we can change them if its hard for new users to
# # move + execute

# Assets path
ASSETS_PATH = pathlib.Path(__file__).resolve().parent.parent / "assets"

# Sprite Scaling
MAP_SIZE_MULTIPLIER = 2.0
PLAYER_SIZE_MULTIPLIER = MAP_SIZE_MULTIPLIER
XENO_SIZE_MULTIPLIER = 0.5
#COIN_SCALING = MAP_SCALING
SPRITE_PIXEL_SIZE = 128
GRID_PIXEL_SIZE = SPRITE_PIXEL_SIZE * MAP_SIZE_MULTIPLIER

#movement speed in pixels per frame
PLAYER_MOVEMENT_SPEED = 7
GRAVITY = 1.2
PLAYER_JUMP_SPEED = 25

#Bow Constants
ARROW_SPRITE_SCALING = 0.8
SHOOT_SPEED = 15
ARROW_SPEED = 5
ARROW_DAMAGE = 25

#margins of view point
# LEFT_VIEW = 500
# RIGHT_VIEW = 600
# TOP_VIEW = 600
# BOTTOM_VIEW = 650


PLAYER_INIT_X = 100
PLAYER_INIT_Y = 100

#for tracking and setting direction of character sprites
CHARACTER_FACE_RIGHT = 0
CHARACTER_FACE_LEFT = 1

# LAYER_NAME_MOVING_PLATFORMS = "Moving Platforms"
LAYER_NAME_PLATFORMS = "Platforms Layer"
# LAYER_NAME_COINS = "Coins"
LAYER_NAME_BACKGROUND = "Background"
LAYER_NAME_LADDERS = "Ladders"
LAYER_NAME_PLAYER = "Player"
LAYER_NAME_ENEMIES = "Enemies"
LAYER_NAME_BOSS = "Boss"
LAYER_NAME_ARROWS = "Arrows"
LAYER_NAME_BOW = 'Bows'
def load_texture_and_flipped(filename):
    """load a pair of textures, one original, one flipped"""
    # 0 for right (original, 1 for flipped to other direction)
    texture_and_flipped = []
    texture_and_flipped.append(arcade.load_texture(filename))
    texture_and_flipped.append(arcade.load_texture(filename, flipped_horizontally=True))
    return texture_and_flipped

class Arrow(arcade.Sprite):
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
        if self.visible:
            if self.change_x < 0 and self.character_face_direction == CHARACTER_FACE_RIGHT:
                self.character_face_direction = CHARACTER_FACE_LEFT
            elif self.change_x > 0 and self.character_face_direction == CHARACTER_FACE_LEFT:
                self.character_face_direction = CHARACTER_FACE_RIGHT


            self.cur_texture += 1
            if self.cur_texture >= 6:
                self.cur_texture = 0
            self.texture = self.bow_cycle[self.cur_texture][self.character_face_direction]
        # 41-46

class Character(arcade.Sprite):
    """Creates a character based on the arcade Sprite class,
    and implements its direction facing, and animations
    used mainly for subclasses"""
    def __init__(self, name_folder, name_file):
        # make the sprite obj
        super().__init__()

        #Setting file path of sprite
        characters_path = ASSETS_PATH / f"{name_folder}/{name_file}"

        # set the initial texture
        self.idle_textures = load_texture_and_flipped(f"{characters_path}1.png")
        self.texture = self.idle_textures[0]
        self.character_face_direction = CHARACTER_FACE_RIGHT

        self.walk_cycle = []
        for i in range(4):
            textures = load_texture_and_flipped(f"{characters_path}{i + 1}.png")
            self.walk_cycle.append(textures)

        self.cur_texture = 0
        self.scale = PLAYER_SIZE_MULTIPLIER

        self.jump_textures = load_texture_and_flipped(f"{characters_path}2.png")
        self.fall_textures = load_texture_and_flipped(f"{characters_path}3.png")

        # hit box texture
        # self.set_hit_box(self.texture.hit_box_points)
        #
        # self.health = 100
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
        self.texture = self.walk_cycle[self.cur_texture][self.character_face_direction]

class Enemy(Character):
    def __init__(self, name_folder, name_file):

        super().__init__(name_folder, name_file)

class MiniEnemy(Enemy):
    def __init__(self):

        #update the file path when set up
        super().__init__("images/enemies/Xeno/Walk", "Xeno")
        self.character_face_direction = CHARACTER_FACE_RIGHT
        self.health = 50
        self.scale = XENO_SIZE_MULTIPLIER



class Boss(Enemy):
    def __init__(self):

        #update the file pather when set up
        super().__init__("darkemperor", 'darkemperor_run')
        self.character_face_direction = CHARACTER_FACE_RIGHT
        self.health = 50


class PlayerCharacter(Character):
    """Player Sprite"""
    def __init__(self):
        super().__init__("player_sprites", 'king')

        #track the state we are in
        self.jumping = False
        self.health = 3

        self.character_face_direction = CHARACTER_FACE_RIGHT




class Platformer(arcade.Window):
    def __init__(self) -> None:
        super().__init__(HORIZONTAL_SCREEN, VERTICAL_SCREEN, SCREEN_TITLE)
        arcade.set_background_color(arcade.csscolor.SKY_BLUE)
        # file_path = os.path.dirname(os.path.abspath(__file__))
        # os.chdir(file_path)

        #track the current state of what key is pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.shoot_pressed = False
        self.jump_needs_reset = False

        self.tile_map = None

        # These lists will hold different sets of sprites
        self.coins = None
        self.background = None
        self.collisions = None
        self.ladders = None
        self.goals = None
        self.enemies = None
        self.boss = None
        # mainly for displaying the platform i guess
        self.scene = None


        # One sprite for the player, no more is needed
        self.player = None

        # We need a physics engine as well
        self.physics_engine = None

        #Camera that is used to scroll the screen
        self.camera = None

        self.gui_camera = None

        self.end_of_map = 0

        # Someplace to keep score
        self.score = 0

        #shooting mechs
        self.can_shoot = False
        self.shoot_timer = 0

        # Which level are we on?
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

        #setup the cam
        self.camera = arcade.Camera(self.width, self.height)

        self.gui_camera = arcade.Camera(self.width, self.height)

        self.score = 0
        self.can_shoot = True
        self.shoot_timer = 0
        map = ASSETS_PATH / "maps" / "platformer_map1.json"
        layer_options = {
            "Platforms Layer": {"use_spatial_hash": True,},
        }

        self.tile_map = arcade.load_tilemap(map, MAP_SIZE_MULTIPLIER, layer_options)
        #self.collisions = arcade.load_tilemap(map, MAP_SCALING, layer_options)
        self.scene = arcade.Scene.from_tilemap(self.tile_map)
        # scene is needed, cannot directly use tile map as scene anymore

        self.player = PlayerCharacter()
        self.player.center_x = PLAYER_INIT_X
        self.player.center_y = PLAYER_INIT_Y
        self.scene.add_sprite(LAYER_NAME_PLAYER, self.player)

        self.bow = Bow("recurve bow", "recurvebow")
        self.bow.visible = False
        self.bow.center_x = PLAYER_INIT_X
        self.bow.center_x = PLAYER_INIT_Y

        self.scene.add_sprite(LAYER_NAME_BOW, self.bow)

        self.enemies = []
        for i in range(5):
            enemy = MiniEnemy()
            enemy.center_x = 200 + i *20
            enemy.center_y = 100
            enemy.change_y = -20
            enemy.change_x = 2
            self.scene.add_sprite(LAYER_NAME_ENEMIES, enemy)
            self.enemies.append(enemy)

        self.boss = Boss()
        self.boss.center_x = 400
        self.boss.center_y = 400
        self.boss.change_y = -20

        self.scene.add_sprite(LAYER_NAME_ENEMIES, self.boss)
        self.enemies.append(self.boss)

        self.end_of_map = self.tile_map.tiled_map.map_size.width * GRID_PIXEL_SIZE
        self.scene.add_sprite_list(LAYER_NAME_ARROWS)


        #enemies
        # enemies_layer = self.tile_map.object_lists[LAYER_NAME_ENEMIES]
        # for my_object in enemies_layer:
        #     cartesian = self.tile_map.get_cartesian(my_object.shape[0], my_object.shape[1])
        #     enemy_type = my_object.properties['type']
        #     if enemy_type == 'Xeno':
        #         enemy = MiniEnemy()
        #     elif enemy_type =='darkemperor':
        #         enemy = Boss()
        #     enemy.center_x = math.floor(cartesian[0] * MAP_SCALING * self.tile_map.tile_width)
        #     enemy.center_y = math.floor((cartesian[1] + 1) * (self.tile_map.tile_height * MAP_SCALING))
        #
        #     if "boundary_left" in my_object.properties:
        #         enemy.boundary_left = my_object.properties["boundary_left"]
        #
        #     if "boundary_right" in my_object.properties:
        #         enemy.boundary_left = my_object.properties["boundary_right"]
        #
        #     if "change_x" in my_object.properties:
        #         enemy.change_x = my_object.properties["change_x"]
        #     self.scene.add_sprite(LAYER_NAME_ENEMIES, enemy)

        if self.tile_map.tiled_map.background_color:
            arcade.set_background_color(arcade.csscolor.SKY_BLUE)


        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player,[self.scene.get_sprite_list(LAYER_NAME_PLATFORMS)], gravity_constant = GRAVITY,)

        # pass
        #old player properties
    #def create_player_sprite(self):
        #characters_path = ASSETS_PATH / "player_sprites"
        #player_standing = arcade.load_texture(characters_path / "king1.png")
        #walk_cycle = []
        #for i in range((4)):
            #walk_cycle.append(arcade.load_texture(characters_path / ("king" + str(i+1) + ".png")))
        # player_walk_right =


        # Set the player defaults
        #player = arcade.AnimatedWalkingSprite()
        #player.stand_left_textures = [player_standing]
        #player.stand_right_textures = [player_standing]
        #player.walk_left_textures = walk_cycle
        #player.walk_right_textures = walk_cycle
        #player.center_x = 200
        #player.center_y = 200
        #player.state = arcade.FACE_RIGHT
        #player.texture = walk_cycle[0]
        #return player

    def process_keychange(self):
        """called when we change up/down or ladder"""
        if self.up_pressed and not self.down_pressed:
            if(self.physics_engine.can_jump(y_distance=10) and not self.jump_needs_reset):
                self.player.change_y = PLAYER_JUMP_SPEED
                self.jump_needs_reset = True

        if self.right_pressed and not self.left_pressed:
            self.player.change_x = PLAYER_MOVEMENT_SPEED
        elif self.left_pressed and not self.right_pressed:
            self.player.change_x = -PLAYER_MOVEMENT_SPEED
        else:
            self.player.change_x = 0

    def on_key_press(self, key: int, modifiers: int):
        """Arguments:
        key {int} -- Which key was pressed
        modifiers {int} -- Which modifiers were down at the time
        """
        # player moving to the left
        if key == arcade.key.A:
            self.left_pressed = True
        #player moving to the right
        elif key == arcade.key.D :
            self.right_pressed = True
        # player moving up
        elif key == arcade.key.W:
            self.up_pressed = True

        if key == arcade.key.J:
            self.shoot_pressed = True

        self.process_keychange()

    def on_key_release(self, key: int, modifiers: int):
        """Arguments:
        key {int} -- Which key was released
        modifiers {int} -- Which modifiers were down at the time
        """
        if key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.D:
            self.right_pressed = False
        elif key == arcade.key.W:
            self.up_pressed = False
            self.jump_needs_reset = False
        # elif key == arcade.key.S or key == arcade.key.DOWN:
        #     self.down_pressed = False

        if key == arcade.key.J:
            self.shoot_pressed = False

        self.process_keychange()

    def on_update(self, delta_time: float):
        """Updates the position of all game objects

        Arguments:
            delta_time {float} -- How much time since the last call
        """

        #self.player.update_animation(delta_time)
        self.physics_engine.update()

        if  self.physics_engine.can_jump():
            self.player.can_jump = False
        else:
            self.player.can_jump = True

        #if self.player.is_on_ladder() and not self.physics_engine.can_jump():
            #self.player.is_on_ladder = True
            #self.process_keychange()
        #else:
            #self.player.is_on_ladder = False
            #self.process_keychange()

        self.bow.center_x = self.player.center_x
        self.bow.center_y = self.player.center_y
        self.bow.change_x = self.player.change_x
        self.bow.character_face_direction = self.player.character_face_direction

        if self.can_shoot:
            if self.shoot_pressed:
                self.bow.visible = True
                self.bow.scale = 1.5
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

                self.can_shoot = False
        else:

            self.shoot_timer += 1
            if self.shoot_timer == SHOOT_SPEED:
                self.bow.visible = False
                self.can_shoot = True
                self.shoot_timer = 0

        for arrow in self.scene.get_sprite_list(LAYER_NAME_ARROWS):
            arrow.center_x += arrow.change_x

        # implements collision with enemies
        # if(arcade.check_for_collision_with_list(self.player, self.scene.get_sprite_list(LAYER_NAME_ENEMIES))):
        #     self.player.center_y = 250
        #
        # if(arcade.check_for_collision_with_list(self.player, self.scene.get_sprite_list(LAYER_NAME_BOSS))):
        #     self.player.center_y = 250




        # enemy missing collision for walls?


        # if arcade.check_for_collision_with_list( self.boss, self.scene.get_sprite_list(LAYER_NAME_PLATFORMS)):
        #     self.boss.change_y = 0
        # else:
        #     self.boss.center_y += self.boss.change_y

        # if(arcade.check_for_collision_with_list(self.player, self.scene.get_sprite_list(LAYER_NAME_BOSS))):
            # self.player.center_y += 650

        # Enemies chase you within 300 units
        for enemy in self.enemies:

            if abs(self.player.center_y - enemy.center_y < 300) and abs(self.player.center_x - enemy.center_x) < 500 and not arcade.check_for_collision_with_list(enemy, self.scene.get_sprite_list(LAYER_NAME_PLATFORMS)):

                if self.player.center_x >= enemy.center_x:
                    enemy.change_x = 7
                    enemy.center_x += enemy.change_x
                elif self.player.center_x < enemy.center_x:
                    enemy.change_x = -7
                    enemy.center_x += enemy.change_x
            else:
                enemy.change_x = 0
        # some way of stutter stepping to move, i kinda like how stupid it is
        # i am only allowed ot put one sprite for physics engine, so this is the next best thing
        for enemy in self.enemies:
            if abs(self.player.center_y - enemy.center_y > 300) and abs(self.player.center_x - enemy.center_x) > 500:
                enemy.change_y = 0
                enemy.change_x = 0
            elif arcade.check_for_collision_with_list(enemy, self.scene.get_sprite_list(LAYER_NAME_PLATFORMS)):
                enemy.change_y = 0
                enemy.center_y += 10
            elif not arcade.check_for_collision_with_list(enemy, self.scene.get_sprite_list(LAYER_NAME_PLATFORMS)):
                enemy.center_y += -5

        #FOR WHEN ENEMIES IS IMPLEMENTED
        self.scene.update_animation(delta_time, [LAYER_NAME_PLAYER, LAYER_NAME_ENEMIES,
                                                 LAYER_NAME_ARROWS, LAYER_NAME_BOW])

        #for enemy in self.scene.get_sprite_list(LAYER_NAME_ENEMIES):
            #if(enemy.boundary_right and enemy.right > enemy.boundary_left and enemy.change_x > 0):
                #enemy.change_x *= -1

            #if(enemy.boundary_left and enemy.left < enemy.boundary_left and enemy.change_x < 0):
                #enemy.change_x *= -1

        #ENEMY COLLISION
        #player_collision_list = arcade.check_for_collision_with_lists(self.player, [self.scene.get_sprite_list(LAYER_NAME_ENEMIES)],)

        # for arrow in self.scene.get_sprite_list(LAYER_NAME_ARROWS):
        #     hit_list = arcade.check_for_collision_with_list(arrow,[self.scene.get_sprite_list(LAYER_NAME_ENEMIES), self.scene.get_sprite_list(LAYER_NAME_PLATFORMS),])
        #
        #     if hit_list:
        #         arrow.remove_from_sprite_list()
        #
        #         for collision in hit_list:
        #             if(self.scene.get_sprite_list(LAYER_NAME_ENEMIES) in collision.sprite_lists):
        #                 collision.health -= ARROW_DAMAGE
        #
        #                 if collision.health <= 0:
        #                     collision.remove_from_sprite_lists()
        #                     self.score += 100
        #         return
        #     if (arrow.right < 0) or (arrow.left > (self.tile_map.width * self.tile_map.tile_width) * MAP_SCALING):
        #         arrow.remove_from_sprite_list()
        #for collision in player_collision_list:
            #if self.player.health == 0:
                #self.setup()
                #return
            #elif self.scene.get_sprite_list(LAYER_NAME_ENEMIES) in collision.sprite_lists:
                #self.player.health -= 1
                #return

        self.center_camera_to_player()

    def on_draw(self):
        arcade.start_render()

        self.camera.use()
        self.scene.draw(pixelated=True)
        self.gui_camera.use()

        # score_text = f"Score: {self.score}"
        # arcade.draw_text(score_text, 10, 10, arcade.csscolor.BLACK, 18)

        # pass
    def center_camera_to_player(self):
        screen_center_x = self.player.center_x - (self.camera.viewport_width / 2)
        screen_center_y = self.player.center_y - (self.camera.viewport_height / 2)

        if screen_center_x < 0:
            screen_center_x = 0
        if screen_center_y < 0:
            screen_center_y = 0
        player_centered = screen_center_x, screen_center_y

        self.camera.move_to(player_centered)

def main():
    window = Platformer()
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()
