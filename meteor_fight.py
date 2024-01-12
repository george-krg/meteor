import sys
from time import sleep
import pygame.font
import pygame
from pygame.sprite import Sprite

class GameStats:
    """Track statistics for Alien Invasion."""
    
    def __init__(self, sp_game):
        """Initialize statistics."""
        self.settings = sp_game.settings
        self.reset_stats()

        # Start fight in an active state.
        self.game_active = True

        # keep track of the score
        self.score = 0
        
    def reset_stats(self):
        """Initialize statistics that can change during the game."""
        self.spaceships_left = self.settings.spaceship_limit
        self.score = 0

class Settings:
    """A class to store all settings for Space Fight."""

    def __init__(self):
        """Initialize the game's settings."""
        # Screen settings
        self.screen_width = 800
        self.screen_height = 600
        self.bg_color = (230, 230, 230)

        # SpaceShip settings
        self.spaceship_speed = 0.5
        self.spaceship_limit = 5

        # Bullet settings
        self.missile_speed = 1.0
        self.missile_width = 3
        self.missile_height = 15
        self.missile_color = (60, 60, 60)
        self.missiles_allowed = 3

        # Alien settings
        self.meteor_speed = 0.05
        self.meteorspacing = 3

        self.meteorpoints = 50


class Scoreboard:
    """A class to report scoring information."""

    def __init__(self, sp_game):
        """Initialize scorekeeping attributes."""
        self.sp_game = sp_game
        self.screen = sp_game.screen
        self.screen_rect = self.screen.get_rect()
        self.settings = sp_game.settings
        self.stats = sp_game.stats
        
        # Font settings for scoring information.
        self.text_color = (30, 30, 30)
        self.font = pygame.font.SysFont(None, 48)

        # Prepare the initial score images.
        self.prep_score()

    def prep_score(self):
        """Turn the score into a rendered image."""
        rounded_score = round(self.stats.score, -1)
        score_str = "{:,}".format(rounded_score)
        self.score_image = self.font.render(score_str, True,
                self.text_color, self.settings.bg_color)
        
        # Display the score at the top right of the screen.
        self.score_rect = self.score_image.get_rect()
        self.score_rect.right = self.screen_rect.right - 20
        self.score_rect.top = 20

    def show_score(self):
        """Draw score to the screen."""
        self.screen.blit(self.score_image, self.score_rect)


 
class SpaceShip:
    """A class to manage the ship."""
 
    def __init__(self, sp_game):
        """Initialize the ship and set its starting position."""
        self.screen = sp_game.screen
        self.settings = sp_game.settings
        self.screen_rect = sp_game.screen.get_rect()

        # Load the ship image and get its rect.
        self.image = pygame.image.load('images/spacecraft.bmp')
        self.rect = self.image.get_rect()

        # Start each new ship at the bottom center of the screen.
        self.rect.midbottom = self.screen_rect.midbottom

        # Store a decimal value for the spaceship's horizontal position.
        self.x = float(self.rect.x)

        # Movement flags
        self.moving_right = False
        self.moving_left = False

    def update(self):
        """Update the spaceship's position based on movement flags."""
        # Update the spaceship's x value, not the rect.
        if self.moving_right and self.rect.right < self.screen_rect.right:
            self.x += self.settings.spaceship_speed
        if self.moving_left and self.rect.left > 0:
            self.x -= self.settings.spaceship_speed

        # Update rect object from self.x.
        self.rect.x = self.x

    def blitme(self):
        """Draw the spaceship at its current location."""
        self.screen.blit(self.image, self.rect)
    
    def center_spaceship(self):
        """Center the spaceship on the screen."""
        self.rect.midbottom = self.screen_rect.midbottom
        self.x = float(self.rect.x)

class Meteor(Sprite):
    """A class to represent a single alien in the fleet."""

    def __init__(self, sp_game):
        """Initialize the alien and set its starting position."""
        super().__init__()
        self.screen = sp_game.screen
        self.settings = sp_game.settings

        # Load the alien image and set its rect attribute.
        self.image = pygame.image.load('images/meteor.bmp')
        self.rect = self.image.get_rect()

        # Start each new alien near the top left of the screen.
        self.rect.x = self.rect.width
        self.rect.y = 0

        # Store the alien's exact horizontal position.
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)

    def check_edges(self):
        """Return True if meteor is at edge of screen."""
        screen_rect = self.screen.get_rect()
        if self.rect.right >= screen_rect.right or self.rect.left <= 0:
            return True

    def update(self):
        """Move the alien right or left."""
        self.y += self.settings.meteor_speed 
        self.rect.y = self.y

 
class Missile(Sprite):
    """A class to manage missiles fired from the spaceship"""

    def __init__(self, sp_game):
        """Create a bullet object at the spaceship's current position."""
        super().__init__()
        self.screen = sp_game.screen
        self.settings = sp_game.settings
        self.color = self.settings.missile_color

        # Create a missile rect at (0, 0) and then set correct position.
        self.rect = pygame.Rect(0, 0, self.settings.missile_width,
            self.settings.missile_height)
        self.rect.midtop = sp_game.spaceship.rect.midtop
        
        # Store the bullet's position as a decimal value.
        self.y = float(self.rect.y)

    def update(self):
        """Move the bullet up the screen."""
        # Update the decimal position of the bullet.
        self.y -= self.settings.missile_speed
        # Update the rect position.
        self.rect.y = self.y

    def draw_missile(self):
        """Draw the bullet to the screen."""
        pygame.draw.rect(self.screen, self.color, self.rect)

class SpaceFight:
    """Overall class to manage game assets and behavior."""

    def __init__(self):
        """Initialize the game, and create game resources."""
        pygame.init()
        self.settings = Settings()

        #self.screen = pygame.display.set_mode((0, 0), pygame.w.FULLSCREEN)
        self.screen = pygame.display.set_mode([self.settings.screen_width,self.settings.screen_height])
        
        # if fullscreen store the size
        # self.settings.screen_width = self.screen.get_rect().width
        # self.settings.screen_height = self.screen.get_rect().height
        pygame.display.set_caption("Space Fight")

        # Create an instance to store game statistics.
        self.stats = GameStats(self)

        self.sb = Scoreboard(self)

        
        self.spaceship = SpaceShip(self)
        self.missiles = pygame.sprite.Group()

        self.meteors = pygame.sprite.Group()
        self._create_meteors()

    def run_game(self):
        """Start the main loop for the game."""
        while True:
            self._check_events()

            if self.stats.game_active:
                self.spaceship.update()
                self._update_missiles()
                self._update_meteors()

            self._update_screen()

    def _check_events(self):
        """Respond to keypresses and mouse events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)

    def _check_keydown_events(self, event):
        """Respond to keypresses."""
        if event.key == pygame.K_RIGHT:
            self.spaceship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.spaceship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_missile()

    def _check_keyup_events(self, event):
        """Respond to key releases."""
        if event.key == pygame.K_RIGHT:
            self.spaceship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.spaceship.moving_left = False

    def _fire_missile(self):
        """Create a new missile and add it to the missiles group."""
        if len(self.missiles) < self.settings.missiles_allowed:
            new_missile = Missile(self)
            self.missiles.add(new_missile)

    def _update_missiles(self):
        """Update position of bullets and get rid of old bullets."""
        # Update missile positions.
        self.missiles.update()

        # Get rid of bullets that have disappeared.
        for missile in self.missiles.copy():
            if missile.rect.bottom <= 0:
                 self.missiles.remove(missile)
        
        self._check_missile_meteor_collisions()
    

    def _check_missile_meteor_collisions(self):
        
        """Respond to missile-meteor collisions."""
        # Remove any missiles and meteors that have collided.
        collisions = pygame.sprite.groupcollide(
                self.missiles, self.meteors, True, True)
        
        if collisions:
            self.stats.score += self.settings.meteorpoints
            self.sb.prep_score() 

        if not self.meteors:
            # Destroy existing bullets and create new fleet.
            self.missiles.empty()
            self._create_meteors()
    
    def _update_meteors(self):
        """
        Check if the set of meteors is at an edge,
          then update the positions of all meteors in the set.
        """
        self._check_set_edges()
        self.meteors.update()

        # Look for meteor-spaceship collisions.
        if pygame.sprite.spritecollideany(self.spaceship, self.meteors):
            self._spaceship_hit()

        # Look for aliens hitting the bottom of the screen.
        self._check_meteors_bottom()
    
    def _check_meteors_bottom(self):
        """Check if any aliens have reached the bottom of the screen."""
        screen_rect = self.screen.get_rect()
        for meteor in self.meteors.sprites():
            if meteor.rect.bottom >= screen_rect.bottom:
                # Treat this the same as if the spaceship got hit.
                self.meteors.remove(meteor)
    
    def _spaceship_hit(self):
        """Respond to the spaceship being hit by a meteor."""
        if self.stats.spaceships_left > 0:
            # Decrement spaceships_left.
            self.stats.spaceships_left -= 1
            
            # Get rid of any remaining aliens and bullets.
            self.meteors.empty()
            self.missiles.empty()
            
            # Create a new set of meteors and center the spaceship.
            self._create_meteors()
            self.spaceship.center_spaceship()
            
            # Pause.
            sleep(0.5)
        else:
            self.stats.game_active = False
    
    def _create_meteors(self):
        """Create the fleet of meteors."""
        # Create a meteor and find the number of meteors in a row.
        # Spacing between each meteor is equal to one meteor width multiplied by a spacing.
        
        meteor = Meteor(self)
        meteor_width, meteor_height = meteor.rect.size
        available_space_x = self.settings.screen_width - meteor_width
        number_meteors_x = available_space_x // (self.settings.meteorspacing * meteor_width)
        
                
        # Create the full fleet of aliens.
        for meteor_number in range(number_meteors_x):
            self._create_meteor(meteor_number)

    def _create_meteor(self, meteor_number):
        """Create a meteor and place it in the row."""
        meteor = Meteor(self)
        meteor_width, meteor_height = meteor.rect.size
        meteor.x = meteor_width + self.settings.meteorspacing * meteor_width * meteor_number
        meteor.rect.x = meteor.x
        meteor.rect.y = 0
        self.meteors.add(meteor)

    def _check_set_edges(self):
        """Respond appropriately if any meteors have reached an edge."""
        for meteor in self.meteors.sprites():
            if meteor.check_edges():
                self._change_set_direction()
                break
            
    def _change_set_direction(self):
        pass


    def _update_screen(self):
        """Update images on the screen, and flip to the new screen."""
        self.screen.fill(self.settings.bg_color)
        self.spaceship.blitme()
        for missile in self.missiles.sprites():
            missile.draw_missile()
        self.meteors.draw(self.screen)

        self.sb.show_score()

        pygame.display.flip()


if __name__ == '__main__':
    # Make a game instance, and run the game.
    sp_game = SpaceFight()
    sp_game.run_game()
