from raylibpy import *

def check_enemy_collisions(player, enemies):
    for enemy in enemies:
        if not enemy.is_alive:
            continue  # Skip dead enemies

        if check_collision_recs(player.hitbox, enemy.hitbox):
            player.take_damage(10)  # Example: Player takes 10 damage


def check_obstacle_collisions(self, obstacles):
        for obstacle in obstacles:
            if check_collision_recs(self.hitbox, obstacle):
                # Calculate centers
                player_center = Vector2(self.hitbox.x + self.hitbox.width/2, self.hitbox.y + self.hitbox.height/2)
                obstacle_center = Vector2(obstacle.x + obstacle.width/2, obstacle.y + obstacle.height/2)
                
                # Vector from obstacle center to player center
                direction = vector2_subtract(player_center, obstacle_center)
                
                # Half sizes of each rectangle
                player_half_size = Vector2(self.hitbox.width/2, self.hitbox.height/2)
                obstacle_half_size = Vector2(obstacle.width/2, obstacle.height/2)
                
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
