import pathlib

import arcade

# Game constants
# Window dimensions
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Deprecated King"


# Assets path
ASSETS_PATH = pathlib.Path(__file__).resolve().parent.parent / "assets"

# Map scaling
MAP_SCALING = 1.0


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
        self.collisions = arcade.load_tilemap(map, 1, layer_options)
        self.scene = arcade.Scene.from_tilemap(self.collisions)
        # scene is needed, cannot directly use tilemap as scene


        # self.physics_engine = arcade.PhysicsEnginePlatformer(None, platforms=self.collision_list)


        # pass

    def on_key_press(self, key: int, modifiers: int):
        """Arguments:
        key {int} -- Which key was pressed
        modifiers {int} -- Which modifiers were down at the time
        """

    def on_key_release(self, key: int, modifiers: int):
        """Arguments:
        key {int} -- Which key was released
        modifiers {int} -- Which modifiers were down at the time
        """

    def on_update(self, delta_time: float):
        """Updates the position of all game objects

        Arguments:
            delta_time {float} -- How much time since the last call
        """
        pass

    def on_draw(self):
        arcade.start_render()


        self.scene.draw()

        # pass


if __name__ == "__main__":
    window = Platformer()
    window.setup()
    arcade.run()
