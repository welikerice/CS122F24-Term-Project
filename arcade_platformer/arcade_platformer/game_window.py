import os.path
import pathlib

import arcade

# Game constants
# Window dimensions
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Deprecated King"
# KEYS = [arcade.key.A, arcade.key.W, arcade.key.S, arcade.key.D, arcade.key.F, arcade.key.G, arcade.key.SPACE, arcade.key.LSHIFT]
# # for now these are gonna be the keys for movement, we can change them if its hard for new users to
# # move + execute

# Assets path
ASSETS_PATH = pathlib.Path(__file__).resolve().parent.parent / "assets"

# Map scaling
MAP_SCALING = 2.0
PLAYER_SCALING = 2.0
COIN_SCALING = MAP_SCALING
SPRITE_PIXEL_SIZE = 128
GRID_PIXEL_SIZE = SPRITE_PIXEL_SIZE * MAP_SCALING

#movement speed in pixels per frame
PLAYER_MOVEMENT_SPEED = 7
GRAVITY = 1.5
PLAYER_JUMP_SPEED = 30

PLAYER_START_X = SPRITE_PIXEL_SIZE * MAP_SCALING * 2
PLAYER_START_Y = SPRITE_PIXEL_SIZE * MAP_SCALING * 1

#track facing direction of player
RIGHT_FACING = 0
LEFT_FACING = 1

LAYER_NAME_MOVING_PLATFORMS = "Moving Platforms"
LAYER_NAME_PLATFORMS = "Platforms Layer"
LAYER_NAME_COINS = "Coins"
LAYER_NAME_BACKGROUND = "Background"
LAYER_NAME_LADDERS = "Ladders"
LAYER_NAME_PLAYER = "Player"

def load_texture_pair(filename):
    """load a texture pair"""
    return[arcade.load_texture(filename), arcade.load_texture(filename, flipped_horizontally=True),]

class PlayerCharacter(arcade.Sprite):
    """Player Sprite"""
    def __init__(self):
        super().__init__()

        #by defult player is facing right
        self.character_face_direction = RIGHT_FACING

        # filp between images
        self.cur_texture = 0
        self.scale = PLAYER_SCALING

        #track the state we are in
        self.jumping = False
        self.climbing = False
        self.is_on_ladder = False

        #--- load textures ---

        #Images from https://opengameart.org/content/a-platformer-in-the-forest
        characters_path = ASSETS_PATH / "player_sprites"

        #load textures for idle
        self.idle_texture_pair = load_texture_pair(characters_path / "king1.png")
        self.jump_texture_pair = load_texture_pair(characters_path / "king2.png")
        self.fall_texture_pair = load_texture_pair(characters_path / "king3.png")

        #load the walking textures
        self.walk_cycle = []
        for i in range((4)):
            texture = load_texture_pair(characters_path / ("king" + str(i + 1) + ".png"))
            self.walk_cycle.append(texture)

        #load the climbing textures
        self.climbing_textures = []
        texture = arcade.load_texture(characters_path / "king20.png")
        self.climbing_textures.append(texture)
        texture = arcade.load_texture(characters_path / "king22.png")
        self.climbing_textures.append(texture)

        #set the initial texture
        self.texture = self.idle_texture_pair[0]

        #hit box texture
        self.hit_box = self.texture.hit_box_points

    def update_animation(self, delta_time: float = 1 / 60):

        #check if we need to flip the character around
        if self.change_x < 0 and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
        elif self.change_x > 0 and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING

        #climbing animation
        if self.is_on_ladder:
            self.climbing = True
        if not self.is_on_ladder and self.climbing:
            self.climbing = False
        if self.climbing and abs(self.change_y) > 1:
            self.cur_texture += 1
            if self.cur_texture > 3:
                self.cur_texture = 0
        if self.climbing:
            self.texture = self.climbing_textures[self.cur_texture // 4]
            return

        #jumping animation
        if self.change_y > 0 and not self.is_on_ladder:
            self.texture = self.jump_texture_pair[self.character_face_direction]
            return
        elif self.change_y < 0 and not self.is_on_ladder:
            self.texture = self.fall_texture_pair[self.character_face_direction]
            return

        #idle animation
        if self.change_x == 0:
            self.texture = self.idle_texture_pair[self.character_face_direction]
            return

        #walking animation
        self.cur_texture += 1
        if self.cur_texture > 3:
            self.cur_texture = 0
        self.texture = self.walk_cycle[self.cur_texture][self.character_face_direction]


class Platformer(arcade.Window):
    def __init__(self) -> None:
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.csscolor.SKY_BLUE)
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        #track the current state of what key is pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.jump_needs_reset = False

        self.tile_map = None

        # These lists will hold different sets of sprites
        self.coins = None
        self.background = None
        self.collisions = None
        self.ladders = None
        self.goals = None
        self.enemies = None

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

    def setup(self):
        """Sets up the game for the current level"""

        #setup the cam
        self.camera = arcade.Camera(self.width, self.height)

        self.gui_camera = arcade.Camera(self.width, self.height)

        self.score = 0

        map = ASSETS_PATH / "maps" / "platformer_map1.json"
        layer_options = {
            "Platforms Layer": {"use_spatial_hash": True,},
        }

        self.tile_map = arcade.load_tilemap(map, MAP_SCALING, layer_options)
        #self.collisions = arcade.load_tilemap(map, MAP_SCALING, layer_options)
        self.scene = arcade.Scene.from_tilemap(self.tile_map)
        # scene is needed, cannot directly use tilemap as scene

        self.player = PlayerCharacter()
        self.player.center_x = PLAYER_START_X
        self.player.center_y = PLAYER_START_Y
        self.scene.add_sprite(LAYER_NAME_PLAYER, self.player)

        self.end_of_map = self.tile_map.tiled_map.map_size.width * GRID_PIXEL_SIZE

        if self.tile_map.tiled_map.background_color:
            arcade.set_background_color(arcade.csscolor.SKY_BLUE)


        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player,[self.scene.get_sprite_list(LAYER_NAME_PLATFORMS),], gravity_constant = GRAVITY,)

        # pass
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
            if self.physics_engine.is_on_ladder():
                self.player.change_y = PLAYER_MOVEMENT_SPEED
            elif(self.physics_engine.can_jump(y_distance=10) and not self.jump_needs_reset):
                self.player.change_y = PLAYER_JUMP_SPEED
                self.jump_needs_reset = True
        elif self.down_pressed and not self.up_pressed:
            if self.physics_engine.is_on_ladder():
                self.player.change_y = -PLAYER_MOVEMENT_SPEED

        if self.physics_engine.is_on_ladder():
            if not self.up_pressed and not self.down_pressed:
                self.player.change_y = 0
            elif self.up_pressed and self.down_pressed:
                self.player.change_y = 0

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
        if key == arcade.key.A or key == arcade.key.LEFT:
            self.left_pressed = True
        #player moving to the right
        elif key == arcade.key.D or key == arcade.key.RIGHT:
            self.right_pressed = True
        # player moving up
        elif key == arcade.key.W or key == arcade.key.UP:
            self.up_pressed = True
        #player moving down
        elif key == arcade.key.S or key == arcade.key.DOWN:
            self.down_pressed = True

        self.process_keychange()

    def on_key_release(self, key: int, modifiers: int):
        """Arguments:
        key {int} -- Which key was released
        modifiers {int} -- Which modifiers were down at the time
        """
        if key == arcade.key.A or key == arcade.key.LEFT:
            self.left_pressed = False
        elif key == arcade.key.D or key == arcade.key.RIGHT:
            self.right_pressed = False
        elif key == arcade.key.W or key == arcade.key.UP:
            self.up_pressed = False
            self.jump_needs_reset = False
        elif key == arcade.key.S or key == arcade.key.DOWN:
            self.down_pressed = False

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

        self.scene.update_animation(delta_time, [LAYER_NAME_PLAYER])

        #self.scene.update([LAYER_NAME_MOVING_PLATFORMS])

        #for wall in self.scene.get_sprite_list(LAYER_NAME_MOVING_PLATFORMS):

            #if(wall.boundary_right and wall.right > wall.boundary_right and wall.change_x > 0):
                #wall.change_x *= -1
            #if (wall.boundary_left and wall.left < wall.boundary_left and wall.change_x < 0):
                #wall.change_x *= -1
            #if wall.boundary_top and wall.top > wall.boundary_top and wall.change_y > 0:
                #wall.change_y *= -1
            #if (wall.boundary_bottom and wall.bottom < wall.boundary_bottom and wall.change_y < 0):
                #wall.change_y *= -1
        self.center_camera_to_player()

    def on_draw(self):
        arcade.start_render()

        self.camera.use()

        self.scene.draw(pixelated=True)

        self.gui_camera.use()

        score_text = f"Score: {self.score}"
        arcade.draw_text(score_text, 10, 10, arcade.csscolor.WHITE, 18)


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


if __name__ == "__main__":
    window = Platformer()
    window.setup()
    arcade.run()
