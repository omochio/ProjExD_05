import sys
import pygame as pg

WIDTH = 1600
HEIGHT = 1000
# ビューの座標
VIEW_POS = (WIDTH // 2, HEIGHT - 200)

# スクロールのために動的に変更されるrectのリスト
dynamic_rect_lst = []

class Player(pg.sprite.Sprite):

    # 入力と移動方向の対応
    __move_dict = {
        pg.K_LEFT: (-1, 0),
        pg.K_a: (-1, 0),
        pg.K_RIGHT: (1, 0),
        pg.K_d: (1, 0),
        pg.K_UP: (0, -1),
        pg.K_SPACE: (0, -1)
    }

    def __init__(self, pos: tuple[int, int]):
        """
        Playerクラスの初期化
        pos: 初期座標
        """
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
        self.__acc = [.0, .0]
        self.__vel = [.0, .0]

    @property
    def is_grounded(self) -> bool:
        """
        接地判定変数のgetter
        返り値: 接地判定変数の値
        """
        return self.__is_grounded
    
    @is_grounded.setter
    def is_grounded(self, value: bool):
        """
        接地判定変数のsetter
        value: 接地判定変数の値
        """
        self.__is_grounded = value

    @property
    def vel(self) -> list[float, float]:
        """
        速度のgetter
        返り値: 速度のリスト
        """
        return self.__vel.copy()

    def set_vel(self, vx: float = None, vy: float = None):
        """
        速度のsetter
        Noneを入れた方向は変更しない
        vx: x方向の速度
        vy: y方向の速度
        """
        if vx is not None:
            self.__vel[0] = vx
        if vy is not None:
            self.__vel[1] = vy

    def add_vel(self, vx: float = .0, vy: float = .0):
        """
        速度の加算
        vx: x方向の加算速度
        vy: y方向の加算速度
        """
        self.__vel[0] += vx
        self.__vel[1] += vy

    def update(self, key_lst: dict):
        """
        Playerの更新を行う
        key_lst: 押されているキーのリスト
        """
        self.__acc = [.0, .0]
        # 入力と移動方向dictに応じて加速度を設定
        for d in __class__.__move_dict:
            if key_lst[d]:
                self.__acc[0] += self.__walk_acc * __class__.__move_dict[d][0]
                # 接地時のみジャンプ可能
                if self.is_grounded:
                    self.set_vel(vy=self.__jump_init_vel * __class__.__move_dict[d][1])
                    # self.__vel[1] = self.__jump_init_vel * __class__.__move_dict[d][1]
                    if self.vel[1] < 0:
                        self.is_grounded = False

        # 重力加速度を加算
        if not self.is_grounded:
            self.__acc[1] += self.__gravity_acc

        # 加速度と速度上限から速度を計算
        self.add_vel(self.__acc[0])
        if self.vel[0] < -self.__walk_vel_max:
            self.set_vel(-self.__walk_vel_max)
        elif self.vel[0] > self.__walk_vel_max:
            self.set_vel(self.__walk_vel_max)
        self.add_vel(vy=self.__acc[1])

class Block(pg.sprite.Sprite):
    """
    初期生成されるブロックに関するクラス
    """
    # ブロックのサイズ
    __size = (50, 50)

    def __init__(self, pos: tuple[int, int]):
        super().__init__()
        self.image = pg.Surface(__class__.__size)
        self.image.fill((127, 127, 127))
        self.rect = self.image.get_rect()
        self.rect.center = pos

    @classmethod
    @property
    def size(cls) -> tuple[int, int]:
        """
        サイズのgetter
        返り値: サイズのタプル
        """
        return cls.__size

def main():
    """
    ゲームループ
    """
    pg.display.set_caption("proto")
    screen = pg.display.set_mode((WIDTH, HEIGHT))

    bg_img = pg.Surface((WIDTH, HEIGHT))
    dynamic_rect_lst.append(bg_img.get_rect())

    player = Player(VIEW_POS)
    blocks = pg.sprite.Group()
    floor_blocks = pg.sprite.Group()

    # 床の生成
    for i in range(WIDTH // Block.size[0] + 1):
        floor_blocks.add(Block((i * Block.size[0], HEIGHT)))
    # 壁の生成
    for i in range(1000):
        for j in range(10):
            blocks.add(Block((i * 2000, HEIGHT - j * Block.size[1])))
            if j > 3:
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

        # 各スプライトの更新
        player.update(key_lst)

        # スクロール処理
        # player以外のrectをplayerの速度に応じて移動
        # 床はy方向のみ移動
        for r in dynamic_rect_lst:
            r.x -= int(player.vel[0])
            if not player.is_grounded:
                r.y -= int(player.vel[1])
        for sb in floor_blocks:
            sb.rect.y -= int(player.vel[1])

        # ブロックとの衝突判定
        collide_lst = pg.sprite.spritecollide(player, blocks, False) + pg.sprite.spritecollide(player, floor_blocks, False)
        if len(collide_lst) == 0:
            player.is_grounded = False
        else:
            for b in collide_lst:
                # x方向
                if b.rect.top - player.rect.bottom < -player.rect.height // 4 and b.rect.bottom - player.rect.top > player.rect.height // 4:
                    if player.vel[0] < 0:
                        gap = b.rect.right - player.rect.left
                        for r in dynamic_rect_lst:
                            r.x -= gap
                        player.set_vel(0)
                    elif player.vel[0] > 0:
                        gap = player.rect.right - b.rect.left
                        for r in dynamic_rect_lst:
                            r.x += gap
                        player.set_vel(0)

                # y方向
                if b.rect.left - player.rect.right < -player.rect.width // 4 and b.rect.right - player.rect.left > player.rect.width // 4:
                    if player.vel[1] > 0:
                        gap = player.rect.bottom - b.rect.top - 1
                        for r in dynamic_rect_lst:
                            r.y += gap
                        for sb in floor_blocks:
                            sb.rect.y += gap
                        player.is_grounded = True
                    elif player.vel[1] < 0:
                        gap = b.rect.bottom - player.rect.top
                        for r in dynamic_rect_lst:
                            r.y -= gap
                        for sb in floor_blocks:
                            sb.rect.y -= gap
                    player.set_vel(vy=0)

        # Playerの摩擦処理
        if (player.is_grounded):
            player.set_vel(0.9 * player.vel[0])

        print(player.vel)
        
        # 各種描画処理
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
    