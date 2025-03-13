from raylibpy import Vector2, Rectangle
import math

def check_collision_recs(rect1: Rectangle, rect2: Rectangle) -> bool:
    """
    Check if two rectangles are colliding.
    rect1 and rect2 are Rectangle objects with x, y, width, and height attributes.
    """
    return (rect1.x < rect2.x + rect2.width and
            rect1.x + rect1.width > rect2.x and
            rect1.y < rect2.y + rect2.height and
            rect1.y + rect1.height > rect2.y)

def Vector2Normalize(v: Vector2) -> Vector2:
    """Normalize a Vector2 to have a length of 1."""
    length = math.sqrt(v.x * v.x + v.y * v.y)
    if length == 0:
        return Vector2(0, 0)
    return Vector2(v.x / length, v.y / length)

def check_enemy_collisions(player, enemies):
    """Check for collisions between the player and enemies."""
    for enemy in enemies:
        if not enemy.is_alive:
            continue  # Skip dead enemies

        if check_collision_recs(player.hitbox, enemy.hitbox):
            # Calculate damage direction (from enemy to player)
            damage_direction = Vector2(player.rect.x - enemy.rect.x, player.rect.y - enemy.rect.y)
            damage_direction = Vector2Normalize(damage_direction)  # Normalize the direction vector

            # Apply damage to the player
            player.take_damage(10, damage_direction)  # Pass both damage_amount and damage_direction

def check_obstacle_collisions(self, obstacles):
    """Check for collisions between the player and obstacles."""
    for obstacle in obstacles:
        if check_collision_recs(self.hitbox, obstacle):
            # Calculate centers
            player_center = Vector2(self.hitbox.x + self.hitbox.width / 2, self.hitbox.y + self.hitbox.height / 2)
            obstacle_center = Vector2(obstacle.x + obstacle.width / 2, obstacle.y + obstacle.height / 2)

            # Vector from obstacle center to player center
            direction = Vector2(player_center.x - obstacle_center.x, player_center.y - obstacle_center.y)

            # Half sizes of each rectangle
            player_half_size = Vector2(self.hitbox.width / 2, self.hitbox.height / 2)
            obstacle_half_size = Vector2(obstacle.width / 2, obstacle.height / 2)

            # Calculate overlap on each axis
            overlap_x = player_half_size.x + obstacle_half_size.x - abs(direction.x)
            overlap_y = player_half_size.y + obstacle_half_size.y - abs(direction.y)

            # Add a small buffer to prevent getting stuck
            buffer = 1.0

            # Resolve collision based on smallest overlap
            if overlap_x < overlap_y:
                if direction.x > 0:  # player to right of obstacle
                    self.rect.x += overlap_x + buffer
                else:  # player to left of obstacle
                    self.rect.x -= overlap_x + buffer
                self.vel.x = 0
            else:
                if direction.y > 0:  # player above obstacle
                    self.rect.y += overlap_y + buffer
                else:  # player below obstacle
                    self.rect.y -= overlap_y + buffer
                self.vel.y = 0

            # Update hitbox position immediately
            self.hitbox.x = self.rect.x + (self.rect.width - self.hitbox.width) / 2
            self.hitbox.y = self.rect.y + self.rect.height - self.hitbox.height

            # Check if still colliding after adjustment (could happen at corners)
            if check_collision_recs(self.hitbox, obstacle):
                # If still colliding, apply correction on the other axis too
                if overlap_x < overlap_y:
                    if direction.y > 0:  # player above obstacle
                        self.rect.y += overlap_y + buffer
                    else:  # player below obstacle
                        self.rect.y -= overlap_y + buffer
                    self.vel.y = 0
                else:
                    if direction.x > 0:  # player to right of obstacle
                        self.rect.x += overlap_x + buffer
                    else:  # player to left of obstacle
                        self.rect.x -= overlap_x + buffer
                    self.vel.x = 0

                # Update hitbox position again
                self.hitbox.x = self.rect.x + (self.rect.width - self.hitbox.width) / 2
                self.hitbox.y = self.rect.y + self.rect.height - self.hitbox.height