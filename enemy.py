from raylibpy import *
from animation import Animation, REPEATING
from collisions import *

class Enemy:
    W = 32
    H = 32
    SCALE = 4

    def __init__(self, sheet, x, y, speed):
        self.sheet = load_texture(sheet)
        self.vel = Vector2(0.0, 0.0)
        self.speed = speed
        self.rect = Rectangle(x, y, self.W * self.SCALE, self.H * self.SCALE)
        self.animation = Animation(0, 3, 1, 0, 0.2, 0.2, REPEATING, 32, 32)
        self.hitbox = Rectangle(self.rect.x + (self.rect.width - 90) / 2, self.rect.y + self.rect.height - 60, 90, 60)
        self.health = 100  # Add health attribute
        self.maxHealth = 100
        self.is_alive = True  # Flag to track if the enemy is alive
        self.is_dying = False  # Flag to track if the enemy is in the process of dying
        self.death_animation = None  # Placeholder for death animation

    def update(self, player, rects):
        if self.health <= 0 and not self.is_dying:
            self.is_dying = True  # Start death process
            self.start_death_animation()  # Placeholder for death animation logic

        if self.is_dying:
            self.update_death_animation()  # Placeholder for death animation logic
            if self.death_animation_finished():  # Placeholder for checking if death animation is done
                self.is_alive = False  # Mark enemy as dead after animation finishes
        else:
            self.animation.animation_update()
            check_obstacle_collisions(self, rects)
            self.move(player.rect)
            self.update_position()

    def move(self, player):
        # Calculate dir
        enemy_center = Vector2(self.hitbox.x + self.hitbox.width/2, self.hitbox.y + self.hitbox.height/2)
        player_center = Vector2(player.x + player.width/2, player.y + player.height/2)
        dir = vector2_normalize(vector2_subtract(player_center, enemy_center))
        self.vel.x = dir.x * self.speed
        self.vel.y = dir.y * self.speed

    def update_position(self):
        self.rect.x += self.vel.x * get_frame_time()
        self.rect.y += self.vel.y * get_frame_time()
        self.hitbox.x = self.rect.x + (self.rect.width - self.hitbox.width) / 2
        self.hitbox.y = self.rect.y + self.rect.height - self.hitbox.height

    def draw(self):
        if not self.is_alive:
            return  # Don't draw if the enemy is dead

        if self.is_dying:
            # Draw death animation (placeholder)
            draw_rectangle_rec(self.rect, RED)  # Example: Draw a red rectangle as a placeholder
        else:
            # Draw normal animation
            self.draw_health_bar()
            source = self.animation.animation_frame_horizontal()
            origin = Vector2(0.0, 0.0)
            draw_texture_pro(self.sheet, source, self.rect, origin, 0.0, WHITE)
        
        #draw_rectangle_lines_ex(self.hitbox, 1, RED)

    def draw_health_bar(self):
        draw_rectangle(self.rect.x+25, self.rect.y+4, 80, 5, RED)
        ratio = self.health/self.maxHealth
        draw_rectangle(self.rect.x+25, self.rect.y+4, 80*ratio, 5, GREEN)

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.is_dying = True  # Start death process

    def start_death_animation(self):
        # Placeholder for starting death animation
        # Load a death animation here later
        pass

    def update_death_animation(self):
        # Placeholder for updating death animation
        # Update the death animation frames here later
        pass

    def death_animation_finished(self):
        # Placeholder for checking if death animation is finished
        # Add logic to check if the animation is done here later
        return True