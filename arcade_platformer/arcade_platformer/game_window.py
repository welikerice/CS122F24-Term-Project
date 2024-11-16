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
GRAVITY = 0.2

class Platformer(arcade.Window):
    def __init__(self) -> None:
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.csscolor.SKY_BLUE)

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

        map = ASSETS_PATH / "maps" / "platformer_map1.json"
        layer_options = {
            "Platforms Layer": {"use_spatial_hash": True,},
        }

        # tile_map = arcade.tilemap.TileMap(map, layer_options)
        self.collisions = arcade.load_tilemap(map, MAP_SCALING, layer_options)
        self.scene = arcade.Scene.from_tilemap(self.collisions)
        # scene is needed, cannot directly use tilemap as scene

        self.player = self.create_player_sprite()
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player, gravity_constant = 0, platforms=None)



        # pass
    def create_player_sprite(self):
        characters_path = ASSETS_PATH / "player_sprites"
        player_standing = arcade.load_texture(characters_path / "king1.png")
        walk_cycle = []
        for i in range((4)):
            walk_cycle.append(arcade.load_texture(characters_path / ("king" + str(i+1) + ".png")))
        # player_walk_right =


        # Set the player defaults
        player = arcade.AnimatedWalkingSprite()
        player.stand_left_textures = [player_standing]
        player.stand_right_textures = [player_standing]
        player.walk_left_textures = walk_cycle
        player.walk_right_textures = walk_cycle
        player.center_x = 250
        player.center_y = 250
        player.state = arcade.FACE_RIGHT
        player.texture = walk_cycle[0]
        return player
    def on_key_press(self, key: int, modifiers: int):
        """Arguments:
        key {int} -- Which key was pressed
        modifiers {int} -- Which modifiers were down at the time
        """
        if key == arcade.key.A:
            self.player.change_x = -10
        elif key == arcade.key.D:
            self.player.change_x = 10

    def on_key_release(self, key: int, modifiers: int):
        """Arguments:
        key {int} -- Which key was released
        modifiers {int} -- Which modifiers were down at the time
        """
        if key == arcade.key.A:
            self.player.change_x = 0
        elif key == arcade.key.D:
            self.player.change_x = 0

    def on_update(self, delta_time: float):
        """Updates the position of all game objects

        Arguments:
            delta_time {float} -- How much time since the last call
        """
        self.player.update_animation(delta_time)
        self.physics_engine.update()
        pass

    def on_draw(self):
        arcade.start_render()


        self.scene.draw()
        self.player.draw()
        # pass


if __name__ == "__main__":
    window = Platformer()
    window.setup()
    arcade.run()
