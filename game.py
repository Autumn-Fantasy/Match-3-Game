import time

from config import *
from game_board import GameBoard
from renderer import GameRenderer


class Game:
    def __init__(self):
        self.initialize_game()

    def initialize_game(self):
        """初始化/重置游戏状态"""
        # 如果存在旧的游戏板，保存最高分数
        old_max_score = 0
        if hasattr(self, 'board'):
            old_max_score = self.board.max_score

        # 创建新的游戏板
        self.board = GameBoard()

        # 恢复最高分数
        self.board.max_score = old_max_score

        self.renderer = GameRenderer(self.board)
        self.running = True
        self.clock = pygame.time.Clock()

    def handle_events(self):
        """处理游戏事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键点击
                    if self.board.game_over:
                        # 游戏结束状态下，点击任意位置重新开始
                        self.initialize_game()
                    else:
                        # 游戏进行中，处理点击
                        self._handle_mouse_click(event.pos)

    def _handle_mouse_click(self, pos):
        """处理鼠标点击事件"""
        # 检查是否点击了打乱按钮
        if self.renderer.shuffle_button_rect.collidepoint(pos):
            # 点击了打乱按钮
            if self.board.shuffle_board():
                # 打乱成功，检查游戏是否结束
                self.board.check_game_over()
            return

        # 只有在没有动画时才响应游戏板点击
        if not self.board.falling_pieces and not self.board.shake_animation:
            cell_pos = self.board.get_cell_at_pos(pos)
            if cell_pos:
                if self.board.selected is None:
                    self.board.selected = cell_pos
                else:
                    if self.board.are_adjacent(self.board.selected, cell_pos):
                        # 先检查交换后是否会形成匹配
                        if self.board.would_form_match(self.board.selected, cell_pos):
                            # 开始交换动画
                            self.board.animation_start = time.time()
                            self.board.animation_pieces = (self.board.selected, cell_pos)
                            self.board.swap_pieces(self.board.selected, cell_pos)
                        else:
                            # 不会形成匹配，添加震动动画
                            self.board.shake_animation = (self.board.selected, time.time())
                        # 不管是否交换，都取消选择
                    self.board.selected = None

    def update(self):
        """更新游戏状态"""
        if not self.board.game_over:
            self.board.update()
            # 检查是否游戏结束
            if not self.board.has_possible_moves() and not self.board.animation_pieces and not self.board.falling_pieces:
                self.board.check_game_over()

    def render(self):
        """渲染游戏画面"""
        self.renderer.draw()

    def run(self):
        """运行游戏主循环"""
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(60)

        pygame.quit()
