import sys
import pygame as pg

WIDTH = 1600
HEIGHT = 1024
CAMERA_POS = (WIDTH // 2, HEIGHT - 200)

dynamic_rect_lst = []

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
        self.__size = (64, 64)
        self.image = pg.Surface(self.__size)
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.__gravity_acc = 1
        self.__walk_acc = 2
        self.__walk_vel_max = 20
        self.__jump_init_vel = 20
        self.__is_grounded = False
        self.__acc = [0, 0]
        self.__vel = [0, 0]

    @property
    def is_grounded(self):
        return self.__is_grounded
    
    @is_grounded.setter
    def is_grounded(self, value: bool):
        self.__is_grounded = value

    @property
    def vel(self):
        return self.__vel

    @vel.setter
    def vel(self, vx: int = None, vy: int = None):
        if vx is None:
            vx = self.__vel[0]
        else:
            self.__vel[0] = int(vx)
        if vy is None:
            vy = self.__vel[1]
        else:
            self.__vel[1] = int(vy)

    def update(self, key_lst: dict):
        self.__acc = [0, 0]
        for d in __class__.move_dict:
            if key_lst[d]:
                self.__acc[0] += self.__walk_acc * self.move_dict[d][0]
                if self.is_grounded:
                    self.vel[1] = self.__jump_init_vel * self.move_dict[d][1]
                    if self.vel[1] < 0:
                        self.is_grounded = False

        if not self.is_grounded:
            self.__acc[1] += self.__gravity_acc

        self.vel[0] += self.__acc[0]
        if self.vel[0] < -self.__walk_vel_max:
            self.vel[0] = -self.__walk_vel_max
        elif self.vel[0] > self.__walk_vel_max:
            self.vel[0] = self.__walk_vel_max
        self.vel[1] += self.__acc[1]

class Block(pg.sprite.Sprite):
    size = (50, 50)

    def __init__(self, pos: tuple[int, int]):
        super().__init__()
        self.image = pg.Surface(__class__.size)
        self.image.fill((127, 127, 127))
        self.rect = self.image.get_rect()
        self.rect.center = pos

def main():
    pg.display.set_caption("proto")
    screen = pg.display.set_mode((WIDTH, HEIGHT))

    bg_img = pg.Surface((WIDTH, HEIGHT))
    dynamic_rect_lst.append(bg_img.get_rect())

    player = Player(CAMERA_POS)
    blocks = pg.sprite.Group()
    floor_blocks = pg.sprite.Group()
    for i in range(WIDTH // Block.size[0] + 1):
        floor_blocks.add(Block((i * Block.size[0], HEIGHT)))
    for i in range(1000):
        for j in range(10):
            blocks.add(Block((i * 2000, HEIGHT - j * Block.size[1])))
            blocks.add(Block((i * 2000 + Block.size[0], HEIGHT - j * Block.size[1])))
    for b in blocks:
        dynamic_rect_lst.append(b.rect)

    tmr = 0
    clock = pg.time.Clock()
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 0
        
        key_lst = pg.key.get_pressed()

        player.update(key_lst)

        # スクロール
        for r in dynamic_rect_lst:
            r.x -= player.vel[0]
            if not player.is_grounded:
                r.y -= player.vel[1]
        for sb in floor_blocks:
            sb.rect.y -= player.vel[1]

        # ブロックとの衝突判定
        collide_lst = pg.sprite.spritecollide(player, blocks, False) + pg.sprite.spritecollide(player, floor_blocks, False)
        if len(collide_lst) == 0:
            player.is_grounded = False
        else:
            for b in collide_lst:
                # x方向
                if player.rect.bottom > b.rect.centery:
                    if player.vel[0] < 0:
                        for r in dynamic_rect_lst:
                            r.x += player.vel[0]
                        player.vel[0] = 0
                        # break
                    elif player.vel[0] > 0:
                        for r in dynamic_rect_lst:
                            r.x += player.vel[0]
                        player.vel[0] = 0
                        # break
                # y方向
                if b.rect.left <= player.rect.centerx <= b.rect.right:
                    for r in dynamic_rect_lst:
                        r.y += player.vel[1]
                    for sb in floor_blocks:
                        sb.rect.y += player.vel[1]
                    if player.vel[1] > 0:
                        player.is_grounded = True
                    player.vel[1] = 0
                    # 摩擦
                    player.vel[0] = int(0.8 * player.vel[0])

        print(player.vel, player.is_grounded)

        screen.blit(bg_img, (0, 0))
        blocks.draw(screen)
        floor_blocks.draw(screen)
        screen.blit(player.image, player.rect)
        pg.display.update()

        tmr += 1
        clock.tick(60)

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
    