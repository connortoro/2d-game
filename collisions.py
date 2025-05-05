from raylibpy import *
from config import *
from raylibpy import Vector2, check_collision_lines

# enemy line-of-sight
def check_collision_line_rec(start, end, rect):
    dummy = Vector2(0, 0)
    top = check_collision_lines(start, end, (rect.x, rect.y), (rect.x + rect.width, rect.y), dummy)
    bottom = check_collision_lines(start, end, (rect.x, rect.y + rect.height), (rect.x + rect.width, rect.y + rect.height), dummy)
    left = check_collision_lines(start, end, (rect.x, rect.y), (rect.x, rect.y + rect.height), dummy)
    right = check_collision_lines(start, end, (rect.x + rect.width, rect.y), (rect.x + rect.width, rect.y + rect.height), dummy)
    return top or bottom or left or right

def check_enemy_collisions(player, room):
    for enemy in room.enemies:
        if not enemy.is_alive or enemy.is_dying:
            continue

        if check_collision_recs(player.hitbox, enemy.hitbox):
            player.take_damage(enemy.dmg, enemy.hitbox)

        if hasattr(enemy, "projectiles"):
            for projectile in enemy.projectiles:
                if check_collision_circle_rec(projectile.center, projectile.r, player.hitbox) and projectile.active:
                    player.take_damage(projectile.dmg, Rectangle(projectile.center.x, projectile.center.y, 1, 1))
                    projectile.active = False

    for spike in room.spikes:
        if check_collision_recs(spike, player.hitbox):
            player.take_damage(10, spike)

def check_obstacle_collisions(entity, obstacles):
    if entity.hitbox.x < SCALE:
        entity.rect.x = SCALE - (entity.hitbox.x - entity.rect.x)
    elif entity.hitbox.x + entity.hitbox.width > SCALE*(COLS-1):
        entity.rect.x = SCALE*(COLS-1) - ((entity.hitbox.x - entity.rect.x) + entity.hitbox.width)

    if entity.hitbox.y < SCALE:
        entity.rect.y = SCALE - (entity.hitbox.y - entity.rect.y)
    elif entity.hitbox.y + entity.hitbox.height > SCALE*(ROWS-1):
        entity.rect.y = SCALE*(ROWS-1) - ((entity.hitbox.y - entity.rect.y) + entity.hitbox.height)

    for obstacle in obstacles:
        if check_collision_recs(entity.hitbox, obstacle):
            entity_center = Vector2(entity.hitbox.x + entity.hitbox.width / 2, entity.hitbox.y + entity.hitbox.height / 2)
            obstacle_center = Vector2(obstacle.x + obstacle.width / 2, obstacle.y + obstacle.height / 2)

            direction = vector2_subtract(entity_center, obstacle_center)
            entity_half_size = Vector2(entity.hitbox.width / 2, entity.hitbox.height / 2)
            obstacle_half_size = Vector2(obstacle.width / 2, obstacle.height / 2)

            overlap_x = entity_half_size.x + obstacle_half_size.x - abs(direction.x)
            overlap_y = entity_half_size.y + obstacle_half_size.y - abs(direction.y)

            buffer = 1.0
            if overlap_x < overlap_y:
                if direction.x > 0:
                    entity.rect.x += overlap_x + buffer
                else:
                    entity.rect.x -= overlap_x + buffer
                entity.vel.x = 0
            else:
                if direction.y > 0:
                    entity.rect.y += overlap_y + buffer
                else:
                    entity.rect.y -= overlap_y + buffer
                entity.vel.y = 0

            # Ensure hitbox follows rect position
            entity.hitbox.x = entity.rect.x + (entity.rect.width - entity.hitbox.width) / 2
            entity.hitbox.y = entity.rect.y + entity.rect.height - entity.hitbox.height
            return
