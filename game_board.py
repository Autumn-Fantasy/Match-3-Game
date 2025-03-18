import os
import random
import time

from config import *


class GameBoard:
    def __init__(self):
        self.grid = []
        self.selected = None
        self.animation_start = None
        self.animation_pieces = None
        self.falling_pieces = []  # 用于保存正在下落的元素
        self.score = 0  # 添加分数变量
        self.max_score = 0  # 添加最高分数变量
        self.font = DEFAULT_FONT
        self.shake_animation = None  # 震动动画状态
        self.game_over = False  # 游戏是否结束
        self.load_images()
        self.initialize_grid()

    def load_images(self):
        """加载游戏元素图片"""
        self.images = []
        for i in range(1, 9):
            img_path = os.path.join('pics', 'elements', f'element{i}.png')
            img = pygame.image.load(img_path)
            img = pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE))
            self.images.append(img)

    def initialize_grid(self):
        """初始化游戏网格"""
        self.grid = []
        for _ in range(GRID_SIZE):
            row = []
            for _ in range(GRID_SIZE):
                row.append(random.randint(0, 7))  # 0-7对应8种图片
            self.grid.append(row)

    def get_cell_at_pos(self, pos):
        """根据屏幕坐标获取网格位置"""
        x, y = pos
        # 考虑顶部区域的偏移
        y = y - TOP_AREA_HEIGHT
        if 0 <= x < WINDOW_WIDTH and 0 <= y < WINDOW_WIDTH:
            return (y // CELL_SIZE, x // CELL_SIZE)
        return None

    def are_adjacent(self, pos1, pos2):
        """判断两个位置是否相邻"""
        row1, col1 = pos1
        row2, col2 = pos2
        return (abs(row1 - row2) == 1 and col1 == col2) or \
            (abs(col1 - col2) == 1 and row1 == row2)

    def swap_pieces(self, pos1, pos2):
        """交换两个位置的元素"""
        row1, col1 = pos1
        row2, col2 = pos2
        self.grid[row1][col1], self.grid[row2][col2] = \
            self.grid[row2][col2], self.grid[row1][col1]

    def find_matches(self):
        """查找所有匹配的元素"""
        matches = set()

        # 检查水平匹配
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE - 2):
                if (self.grid[row][col] == self.grid[row][col + 1] ==
                        self.grid[row][col + 2]):
                    matches.add((row, col))
                    matches.add((row, col + 1))
                    matches.add((row, col + 2))

        # 检查垂直匹配
        for row in range(GRID_SIZE - 2):
            for col in range(GRID_SIZE):
                if (self.grid[row][col] == self.grid[row + 1][col] ==
                        self.grid[row + 2][col]):
                    matches.add((row, col))
                    matches.add((row + 1, col))
                    matches.add((row + 2, col))

        return matches

    def remove_matches(self):
        """移除匹配的元素并增加分数"""
        matches = self.find_matches()
        if matches:
            # 将匹配的位置设为None
            for row, col in matches:
                self.grid[row][col] = None
            # 每消除一个元素得10分
            self.score += len(matches) * 10
            # 更新最高分数
            if self.score > self.max_score:
                self.max_score = self.score
            return True
        return False

    def drop_pieces(self):
        """处理元素下落和生成新元素"""
        # 从底部开始识别需要下落的元素
        self.falling_pieces = []
        for col in range(GRID_SIZE):
            empty_spaces = []  # 记录空位置
            for row in range(GRID_SIZE - 1, -1, -1):
                if self.grid[row][col] is None:
                    empty_spaces.append(row)
                elif empty_spaces:  # 如果下方有空位
                    # 记录需要下落的元素信息
                    target_row = empty_spaces.pop(0)
                    self.falling_pieces.append({
                        'type': self.grid[row][col],
                        'start_row': row,
                        'target_row': target_row,
                        'col': col,
                        'progress': 0,
                        'start_time': time.time()
                    })
                    # 更新网格
                    self.grid[target_row][col] = self.grid[row][col]
                    self.grid[row][col] = None
                    empty_spaces.append(row)  # 当前位置变为空位

            # 只在顶部填充新元素
            fall_delay = 0.1  # 每个新元素的延迟时间
            for i, row in enumerate(empty_spaces):
                element_type = random.randint(0, 7)
                self.grid[row][col] = element_type
                # 添加新生成元素的下落动画
                self.falling_pieces.append({
                    'type': element_type,
                    'start_row': -1,  # 从屏幕顶部之外开始
                    'target_row': row,
                    'col': col,
                    'progress': 0,
                    'start_time': time.time() + i * fall_delay  # 添加一些延迟
                })

    def would_form_match(self, pos1, pos2):
        """预判断交换两个位置的元素后是否会形成匹配"""
        # 保存原始值
        row1, col1 = pos1
        row2, col2 = pos2
        original_value1 = self.grid[row1][col1]
        original_value2 = self.grid[row2][col2]

        # 临时交换
        self.grid[row1][col1] = original_value2
        self.grid[row2][col2] = original_value1

        # 检查是否有匹配
        has_match = len(self.find_matches()) > 0

        # 恢复原状
        self.grid[row1][col1] = original_value1
        self.grid[row2][col2] = original_value2

        return has_match

    def update(self):
        """更新游戏状态"""
        # 检查是否有动画正在进行
        current_time = time.time()

        # 更新震动动画
        if self.shake_animation:
            shake_pos, shake_start = self.shake_animation
            if current_time - shake_start > SHAKE_DURATION:  # 震动持续时间
                self.shake_animation = None

        # 更新下落动画
        for piece in self.falling_pieces[:]:
            if current_time >= piece['start_time']:
                progress = (current_time - piece['start_time']) / (ANIMATION_DURATION * 0.8)
                if progress >= 1:
                    self.falling_pieces.remove(piece)
                else:
                    piece['progress'] = progress

        # 只有在没有动画时才检查消除
        if not self.falling_pieces and self.animation_pieces is None:
            if self.remove_matches():
                self.drop_pieces()
                return True
        return False

    def is_piece_animating(self, row, col):
        """检查某个位置的元素是否正在动画中"""
        # 检查元素是否正在下落动画中
        for piece in self.falling_pieces:
            if piece['target_row'] == row and piece['col'] == col:
                return True

        # 检查元素是否正在交换动画中
        if self.animation_pieces:
            pos1, pos2 = self.animation_pieces
            if (row, col) == pos1 or (row, col) == pos2:
                return True

        return False

    def shuffle_board(self):
        """打乱棋盘所有元素并减50分"""
        if self.score >= 50:  # 只有分数足够时才能使用
            self.score -= 50
            # 保存当前所有元素类型
            elements = []
            for row in range(GRID_SIZE):
                for col in range(GRID_SIZE):
                    if self.grid[row][col] is not None:
                        elements.append(self.grid[row][col])

            # 随机打乱
            random.shuffle(elements)

            # 重新分配到网格
            index = 0
            for row in range(GRID_SIZE):
                for col in range(GRID_SIZE):
                    if self.grid[row][col] is not None and index < len(elements):
                        self.grid[row][col] = elements[index]
                        index += 1

            return True
        return False

    def has_possible_moves(self):
        """检查是否还有可能的移动"""
        # 尝试所有可能的交换，看是否有能形成匹配的
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                # 检查右侧交换
                if col < GRID_SIZE - 1:
                    if self.would_form_match((row, col), (row, col + 1)):
                        return True
                # 检查下方交换
                if row < GRID_SIZE - 1:
                    if self.would_form_match((row, col), (row + 1, col)):
                        return True
        return False

    def check_game_over(self):
        """检查游戏是否结束"""
        # 分数为零或不存在可消除元素且分数低于50时判定为游戏失败
        if self.score == 0 or (not self.has_possible_moves() and self.score < 50):
            self.game_over = True
            return True
        return False
