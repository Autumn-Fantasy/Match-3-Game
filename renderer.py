import os
import time

from animations import *
from config import *


class GameRenderer:
    def __init__(self, game_board):
        self.game_board = game_board
        self.shuffle_button_img = self._load_button_image()
        self.shuffle_button_rect = self._create_button_rect()

    def _load_button_image(self):
        """加载按钮图片"""
        button_path = os.path.join('pics', 'button', 'exchange.png')
        img = pygame.image.load(button_path)
        # 调整按钮尺寸
        button_size = min(TOP_AREA_HEIGHT - 20, 60)
        return pygame.transform.scale(img, (button_size, button_size))

    def _create_button_rect(self):
        """创建按钮的矩形区域"""
        button_size = self.shuffle_button_img.get_rect().width
        # 放在右侧
        return pygame.Rect(WINDOW_WIDTH - button_size - 20,
                           (TOP_AREA_HEIGHT - button_size) // 2,
                           button_size, button_size)

    def draw(self):
        """绘制游戏界面"""
        # 填充背景色
        screen.fill(BACKGROUND_COLOR)

        # 绘制顶部区域
        pygame.draw.rect(screen, TOP_AREA_COLOR, (0, 0, WINDOW_WIDTH, TOP_AREA_HEIGHT))

        # 绘制分数 - 移至顶部区域
        score_text = self.game_board.font.render(f'分数: {self.game_board.score}', True, BLACK)
        score_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2, TOP_AREA_HEIGHT // 2))
        screen.blit(score_text, score_rect)

        # 绘制打乱按钮
        screen.blit(self.shuffle_button_img, self.shuffle_button_rect)

        if not self.game_board.game_over:
            # 正常游戏界面
            self._draw_static_elements()
            self._draw_falling_pieces()
            self._draw_selection_highlight()
            self._draw_swap_animation()
        else:
            # 游戏结束画面
            self._draw_game_over()

        pygame.display.flip()

    def _draw_game_over(self):
        """绘制游戏结束画面"""
        # 半透明背景
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))

        # 游戏结束文字
        game_over_font = pygame.font.SysFont('幼圆', 64, bold=True)
        game_over_text = game_over_font.render('游戏结束', True, (255, 0, 0))
        game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 80))

        # 最终分数
        score_font = pygame.font.SysFont('幼圆', 48, bold=True)
        max_score_text = score_font.render(f'最高分数: {self.game_board.max_score}', True, (255, 215, 0))  # 金色
        max_score_rect = max_score_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))

        # 提示文字
        hint_font = pygame.font.SysFont('幼圆', 28)
        hint_text = hint_font.render('点击屏幕重新开始', True, WHITE)
        hint_rect = hint_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 140))

        # 绘制文字
        screen.blit(game_over_text, game_over_rect)
        screen.blit(max_score_text, max_score_rect)
        screen.blit(hint_text, hint_rect)

    def _draw_static_elements(self):
        """绘制静态网格元素"""
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                x = col * CELL_SIZE
                y = row * CELL_SIZE + TOP_AREA_HEIGHT  # 添加顶部区域偏移
                img_index = self.game_board.grid[row][col]
                # 只绘制不在动画中的静态元素
                if img_index is not None and not self.game_board.is_piece_animating(row, col):
                    # 检查是否需要应用震动效果
                    if self.game_board.shake_animation and (row, col) == self.game_board.shake_animation[0]:
                        # 计算震动偏移
                        shake_time = time.time() - self.game_board.shake_animation[1]
                        shake_offset = int(math.sin(shake_time * 40) * 5 * (1 - shake_time * 2))
                        x += shake_offset
                    screen.blit(self.game_board.images[img_index], (x, y))

    def _draw_falling_pieces(self):
        """绘制下落动画"""
        for piece in self.game_board.falling_pieces:
            col = piece['col']
            start_row = piece['start_row']
            target_row = piece['target_row']
            progress = piece['progress']

            # 应用弹跳缓动效果
            eased_progress = ease_out_bounce(progress)

            # 计算当前位置
            current_row = start_row + (target_row - start_row) * eased_progress
            x = col * CELL_SIZE
            y = current_row * CELL_SIZE + TOP_AREA_HEIGHT  # 添加顶部区域偏移

            # 绘制元素
            screen.blit(self.game_board.images[piece['type']], (x, y))

    def _draw_selection_highlight(self):
        """绘制选中高亮"""
        if self.game_board.selected:
            row, col = self.game_board.selected
            x = col * CELL_SIZE
            y = row * CELL_SIZE + TOP_AREA_HEIGHT  # 添加顶部区域偏移
            highlight_surface = pygame.Surface((CELL_SIZE, CELL_SIZE))
            highlight_surface.fill(HIGHLIGHT_COLOR)
            screen.blit(highlight_surface, (x, y), special_flags=pygame.BLEND_RGBA_MULT)

    def _draw_swap_animation(self):
        """绘制交换动画"""
        if self.game_board.animation_pieces:
            current_time = time.time()
            if current_time - self.game_board.animation_start < ANIMATION_DURATION:
                progress = (current_time - self.game_board.animation_start) / ANIMATION_DURATION

                # 应用缓动效果
                eased_progress = ease_in_out_quad(progress)

                pos1, pos2 = self.game_board.animation_pieces
                row1, col1 = pos1
                row2, col2 = pos2

                # 计算元素1的起始位置和目标位置
                start_x1 = col2 * CELL_SIZE
                start_y1 = row2 * CELL_SIZE + TOP_AREA_HEIGHT
                target_x1 = col1 * CELL_SIZE
                target_y1 = row1 * CELL_SIZE + TOP_AREA_HEIGHT

                # 计算元素2的起始位置和目标位置
                start_x2 = col1 * CELL_SIZE
                start_y2 = row1 * CELL_SIZE + TOP_AREA_HEIGHT
                target_x2 = col2 * CELL_SIZE
                target_y2 = row2 * CELL_SIZE + TOP_AREA_HEIGHT

                # 计算当前位置
                current_x1 = start_x1 + (target_x1 - start_x1) * eased_progress
                current_y1 = start_y1 + (target_y1 - start_y1) * eased_progress
                current_x2 = start_x2 + (target_x2 - start_x2) * eased_progress
                current_y2 = start_y2 + (target_y2 - start_y2) * eased_progress

                # 添加轻微的缩放效果
                scale = 1.0 + 0.1 * math.sin(progress * math.pi)
                scaled_size = int(CELL_SIZE * scale)
                offset = (scaled_size - CELL_SIZE) // 2

                # 缩放图像
                img1 = pygame.transform.scale(self.game_board.images[self.game_board.grid[row1][col1]],
                                              (scaled_size, scaled_size))
                img2 = pygame.transform.scale(self.game_board.images[self.game_board.grid[row2][col2]],
                                              (scaled_size, scaled_size))

                # 绘制动画中的图片
                screen.blit(img1, (current_x1 - offset, current_y1 - offset))
                screen.blit(img2, (current_x2 - offset, current_y2 - offset))
            else:
                self.game_board.animation_pieces = None
