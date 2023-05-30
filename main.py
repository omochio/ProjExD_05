import sys
import random
import pygame as pg
import time

WIDTH = 1600
HEIGHT = 1000
# ビューの座標
VIEW_POS = (WIDTH // 2, HEIGHT - 200)

# スクロールのために動的に変更されるrectのリスト
dynamic_rect_lst = []

class Player(pg.sprite.Sprite):
    """
    Playerに関するクラス
    """
    # 入力と移動方向の対応
    __move_dict = {
        pg.K_LEFT: (-1, 0),
        pg.K_a: (-1, 0),
        pg.K_RIGHT: (1, 0),
        pg.K_d: (1, 0),
        pg.K_UP: (0, -1),
        pg.K_SPACE: (0, -1)
    }

    def __init__(self, center: tuple[int, int]):
        """
        Playerクラスの初期化
        center: 初期座標
        """
        super().__init__()
        self.__size = (64, 64)
        self.image = pg.Surface(self.__size)
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.__acc = [.0, .0]
        self.__vel = [.0, .0]
        self.__gravity_acc = 1
        self.__walk_acc = 2
        self.__walk_vel_max = 10
        self.__jump_init_vel = 20
        self.__is_grounded = False
        self.state = "normal" # プレイヤーの状態
        self.hyper_life = 0 # 残りの無敵状態時間

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

    def change_state(self, state: str, hyper_life: int):
        """
        右シフトキーが押された時に, プレイヤーを無敵状態にする関数
        引数1 state : プレイヤーの状態
        引数2 hyper_life : 無敵状態になっている時間
        戻り値 : なし
        """
        self.state = state
        self.hyper_life = hyper_life

    def check_hyper(self):
        """
        プレイヤーが無敵状態かどうかを判定し, プレイヤーの色を変える
        戻り値 : なし
        """
        if self.state == "hyper":
            # プレイヤーが無敵状態だったら
            self.image.fill((168, 88, 168)) # プレイヤーの色を紫にする
            self.hyper_life += -1 # 残りの無敵状態時間を1秒減らす

        if self.hyper_life < 0: # 残りの無敵状態時間が0秒だったら
            self.state == "normal" # プレイヤーを通常状態にする
            self.image.fill((255, 255, 255)) # プレイヤーの色を元に戻す


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
        self.check_hyper()

class Block(pg.sprite.Sprite):
    """
    初期生成されるブロックに関するクラス
    """
    def __init__(self, center: tuple[int, int], size: tuple[int, int]):
        super().__init__()
        self.__size = size
        self.image = pg.Surface(size)
        self.image.fill((127, 127, 127))
        self.rect = self.image.get_rect()
        self.rect.center = center

    @property
    def size(self) -> tuple[int, int]:
        """
        サイズのgetter
        返り値: サイズのタプル
        """
        return self.__size

class Level():
    """
    レベル生成と保持を担うクラス
    """
    def __init__(self):
        global dynamic_rect_lst
        self.blocks = pg.sprite.Group()
        self.__flcl_height = 100    # 床と天井の高さ
        self.__ceil_y = -HEIGHT // 2    # 天井の中心y座標
        # 天井の生成
        self.create_ceil((WIDTH // 2, self.__ceil_y))
        # 床の生成
        self.blocks.add(Block((WIDTH // 2, HEIGHT), (WIDTH, self.__flcl_height)))
        dynamic_rect_lst.append(self.blocks.sprites()[-1].rect)
        self.__left_floor_rct = self.blocks.sprites()[-1].rect
        self.__right_floor_rct = self.blocks.sprites()[-1].rect
        
        self.min_obstacle_count = 50
        self.max_obstacle_count = 100
        self.min_obstacle_width = 50
        self.min_obstacle_height = 50
        self.max_obstacle_width = 100
        self.max_obstacle_height = 100
        self.min_floor_width = 100
        self.max_floor_width = WIDTH // 2
        self.min_hole_width = 0
        self.max_hole_width = WIDTH // 2

    def update(self):
        """
        レベルの更新を行う
        """
        global WIDTH
        # 左端の床のx座標が-WIDHT//2より大きくなったら床、天井、障害物を生成
        if self.__left_floor_rct.left >= -WIDTH // 2:
            self.create_ceil((self.__left_floor_rct.left - WIDTH // 2, self.__ceil_rct.centery))
            prev_floor_rct = self.__left_floor_rct
            total = 0
            # 生成した床の長さが穴を含めてWIDTHを超えるまで生成
            while total < WIDTH:
                offset = random.randint(self.min_hole_width, self.max_hole_width)
                sizex = random.randint(self.min_floor_width, self.max_floor_width)
                if total + offset + sizex >= WIDTH:
                    sizex = WIDTH - total
                    offset = 0
                    total += sizex
                else:
                    total += offset + sizex
                self.create_floor((self.__left_floor_rct.left - (offset + sizex // 2), self.__left_floor_rct.centery), (sizex, self.__flcl_height))
                self.__left_floor_rct = self.blocks.sprites()[-1].rect
            self.create_obstacles((self.__left_floor_rct.left, prev_floor_rct.left), (self.__ceil_rct.bottom, self.__left_floor_rct.top))
        # 右端の床のx座標がWIDHT * 3//2より小さくなったら床、天井、障害物を生成
        elif self.__right_floor_rct.right <= WIDTH * 3 // 2:
            self.create_ceil((self.__right_floor_rct.right + WIDTH // 2, self.__ceil_rct.centery))
            prev_floor_rct = self.__right_floor_rct
            total = 0
            # 生成した床の長さが穴を含めてWIDTHを超えるまで生成
            while total < WIDTH:
                offset = random.randint(self.min_hole_width, self.max_hole_width)
                sizex = random.randint(self.min_floor_width, self.max_floor_width)
                if total + offset + sizex >= WIDTH:
                    sizex = WIDTH - total
                    offset = 0
                    total += sizex
                else:
                    total += offset + sizex
                self.create_floor((self.__right_floor_rct.right + (offset + sizex // 2), self.__right_floor_rct.centery), (sizex, self.__flcl_height))
                self.__right_floor_rct = self.blocks.sprites()[-1].rect
            self.create_obstacles((prev_floor_rct.right, self.__right_floor_rct.right), (self.__ceil_rct.bottom, self.__right_floor_rct.top))

    def create_ceil(self, ceil_center: tuple[int, int]):
        """
        天井を生成する関数
        ceil_center: 天井の中心座標
        """
        global WIDTH, dynamic_rect_lst
        self.blocks.add(Block(ceil_center, (WIDTH, self.__flcl_height)))
        self.__ceil_rct = self.blocks.sprites()[-1].rect
        dynamic_rect_lst.append(self.__ceil_rct)
        print("create")
        print(self.__ceil_rct.left)


    def create_floor(self, floor_center: tuple[int, int], floor_size: tuple[int, int]):
        """
        床を生成する関数
        floor_center: 床の中心座標
        floor_size: 床のサイズ
        """
        global WIDTH, dynamic_rect_lst
        self.blocks.add(Block(floor_center, floor_size))
        dynamic_rect_lst.append(self.blocks.sprites()[-1].rect)

    def create_obstacles(self, rangex: tuple[int, int], rangey: tuple[int, int]):
        """
        障害物を生成する関数
        rangex: x方向の生成範囲
        rangey: y方向の範囲
        """
        for i in range(random.randint(self.min_obstacle_count, self.max_obstacle_count)):
            self.blocks.add(Block((random.randint(*rangex), random.randint(*rangey)), (random.randint(self.min_obstacle_width, self.max_obstacle_width), random.randint(self.min_obstacle_height, self.max_obstacle_height))))
            dynamic_rect_lst.append(self.blocks.sprites()[-1].rect)            

class Enemy(pg.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pg.Surface((64, 64))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = pos

def main():
    """
    ゲームループ
    """
    global dynamic_rect_lst
    pg.display.set_caption("ハコツミツミ(仮称)")
    screen = pg.display.set_mode((WIDTH, HEIGHT))

    bg_img = pg.Surface((WIDTH, HEIGHT))
    dynamic_rect_lst.append(bg_img.get_rect())

    player = Player(VIEW_POS)
    level = Level()
    enemys = pg.sprite.Group()
    enemys.add(Enemy((0, HEIGHT - 120)))
    dynamic_rect_lst.append(enemys.sprites()[-1].rect)

    tmr = 0
    clock = pg.time.Clock()
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 0
            if event.type == pg.KEYDOWN and event.key == pg.K_RSHIFT:
                # 右シフトキーが押されたら
                player.change_state("hyper", 400)
        
        key_lst = pg.key.get_pressed()

        # 各スプライトの更新
        player.update(key_lst)
        level.update()

        # スクロール処理
        # player以外のrectをplayerの速度に応じて移動
        # 床はy方向のみ移動
        for r in dynamic_rect_lst:
            r.x -= int(player.vel[0])
            if not player.is_grounded:
                r.y -= int(player.vel[1])

        # ブロックとの衝突判定
        collide_lst = pg.sprite.spritecollide(player, level.blocks, False)
        if len(collide_lst) == 0:
            player.is_grounded = False
        else:
            for b in collide_lst:
                # x方向
                if player.rect.right <= b.rect.left + player.vel[0] or player.rect.left >= b.rect.right + player.vel[0]:
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
                else:
                    if player.vel[1] > 0:
                        gap = player.rect.bottom - b.rect.top
                        for r in dynamic_rect_lst:
                            r.y += gap
                        player.is_grounded = True
                    elif player.vel[1] < 0:
                        gap = b.rect.bottom - player.rect.top
                        for r in dynamic_rect_lst:
                            r.y -= gap
                    player.set_vel(vy=0)

        # Playerの摩擦処理
        if (player.is_grounded):
            if player.vel[0] == 0:
                pass
            elif abs(player.vel[0]) < 0.001:
                player.set_vel(0)
            else:
                player.set_vel(0.7 * player.vel[0])
                
        for enemy in pg.sprite.spritecollide(player, enemys, True):
            if player.state == "hyper":
                x = 1
            else:
                return

        # 各種描画処理
        screen.blit(bg_img, (0, 0))
        level.blocks.draw(screen)
        screen.blit(player.image, player.rect)
        enemys.draw(screen)
        pg.display.update()

        tmr += 1
        clock.tick(60)

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
    