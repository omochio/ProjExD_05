import sys
import pygame as pg

WIDTH = 1600
HEIGHT = 1024
CAMERA_POS = (WIDTH // 2, HEIGHT - 200)

class Player(pg.sprite.Sprite):
    move_dict = {
        pg.K_LEFT: (-1, 0),
        pg.K_a: (-1, 0),
        pg.K_RIGHT: (1, 0),
        pg.K_d: (1, 0),
        pg.K_UP: (0, -1),
        pg.K_SPACE: (0, -1)
    }

    def __init__(self, pos: tuple[int, int]):
        super().__init__()
        self.image = pg.Surface((64, 64))
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.gravity_vel = 5
        self.walk_vel = 20
        self.jump_power = 256
        self.is_ground = False
        self.valit_ipt = [0, 0]
        self.vel = [0, 0]

    def update(self, key_lst: dict):
        self.vel = [0, 0]
        self.valit_ipt = [0, 0]
        for d in __class__.move_dict:
            if key_lst[d]:
                self.valit_ipt[0] = self.move_dict[d][0]
                self.vel[0] = self.move_dict[d][0] * self.walk_vel
                if self.is_ground:
                    self.valit_ipt[1] = self.move_dict[d][1]
                    self.vel[1] = self.valit_ipt[1] * self.jump_power
                    if self.vel[1] < 0:
                        self.is_ground = False

        if not self.is_ground:
            self.vel[1] += self.gravity_vel

class Block(pg.sprite.Sprite):
    size = (32, 32)

    def __init__(self, pos: tuple[int, int]):
        super().__init__()
        self.image = pg.Surface((32, 32))
        self.image.fill((127, 127, 127))
        self.rect = self.image.get_rect()
        self.rect.center = pos

def main():
    pg.display.set_caption("proto")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.Surface((WIDTH, HEIGHT))
    bg_img.fill((0, 0, 0))

    obstacle_rect_lst = []

    player = Player(CAMERA_POS)
    blocks = pg.sprite.Group()
    for i in range(-WIDTH, WIDTH):
        # if 1 <= i % 32 <= 16:
        #     continue
        blocks.add(Block((i * Block.size[0], HEIGHT)))
    for i in range(1000):
        for j in range(10):
            blocks.add(Block((i * 1000, HEIGHT - j * Block.size[1])))
            blocks.add(Block((i * 1000 + Block.size[0], HEIGHT - j * Block.size[1])))
    for b in blocks:
        obstacle_rect_lst.append(b.rect)

    tmr = 0
    clock = pg.time.Clock()
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 0
        
        key_lst = pg.key.get_pressed()

        player.update(key_lst)

        # スクロール
        for r in obstacle_rect_lst:
            r.x -= player.vel[0]
            if not player.is_ground:
                r.y -= player.vel[1]

        collide_lst = pg.sprite.spritecollide(player, blocks, False)
        if len(collide_lst) == 0:
            player.is_ground = False
        for b in collide_lst:

            if player.vel[1] > 0:
                for r in obstacle_rect_lst:
                    r.y += player.vel[1]
                    player.is_ground = True
                    player.vel[1] = 0
            elif player.vel[1] < 0:
                for r in obstacle_rect_lst:
                    r.y += player.vel[1]
                    player.vel[1] = 0

            if player.rect.bottom > b.rect.centery:
                if player.vel[0] != 0:
                    if player.vel[0] < 0:
                        for r in obstacle_rect_lst:
                            r.x += player.vel[0]
                    elif player.vel[0] > 0:
                        for r in obstacle_rect_lst:
                            r.x += player.vel[0]
                    player.vel[0] = 0

        screen.blit(bg_img, (0, 0))
        blocks.draw(screen)
        screen.blit(player.image, player.rect)
        pg.display.update()

        tmr += 1
        clock.tick(60)

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
    