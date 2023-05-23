import sys
import pygame as pg

WIDTH = 1024
HEIGHT = 1024

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
        self.jump_power = 256
        self.isGround = False

    def update(self, key_lst: dict):
        for d in __class__.move_dict:
            if key_lst[d]:
                self.rect.x += self.move_dict[d][0] * 3
                if self.isGround:
                    self.rect.y += self.move_dict[d][1] * self.jump_power
                    if self.move_dict[d][1] < 0:
                        self.isGround = False

        if not self.isGround:
            self.rect.y += self.gravity_vel

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

    player = Player((500, HEIGHT - 50))
    blocks = pg.sprite.Group()
    for i in range(-1024, 1025):
        blocks.add(Block((i * Block.size[0], HEIGHT)))
    for i in range(100):
        for j in range(10):
            blocks.add(Block((i * 1000, WIDTH - j * Block.size[1])))
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

        player.isGround = False
        collide_lst = pg.sprite.spritecollide(player, blocks, False)
        if len(collide_lst) > 0:
            for b in collide_lst:
                if player.rect.top < b.rect.bottom:
                    player.rect.top = b.rect.bottom
                if player.rect.bottom > b.rect.top:
                    player.rect.bottom = b.rect.top
                    player.isGround = True

        # スクロール
        if player.rect.centerx > WIDTH // 2:
            player.rect.centerx = WIDTH // 2
            for r in obstacle_rect_lst:
                r.x -= WIDTH // 2 - player.rect.x
        elif player.rect.centerx < WIDTH // 2:
            player.rect.centerx = WIDTH // 2
            for r in obstacle_rect_lst:
                r.x += WIDTH // 2 - player.rect.x


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
    