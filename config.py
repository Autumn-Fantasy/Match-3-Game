import pygame

# 初始化Pygame
pygame.init()

# 常量定义
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 880  # 增加高度以容纳顶部区域
GRID_SIZE = 9
CELL_SIZE = WINDOW_WIDTH // GRID_SIZE
ANIMATION_DURATION = 1.0  # 动画持续时间（秒）
TOP_AREA_HEIGHT = 80  # 顶部区域高度
SHAKE_DURATION = 0.5  # 震动动画持续时间

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
HIGHLIGHT_COLOR = (255, 255, 0, 128)  # 半透明黄色
BACKGROUND_COLOR = (240, 248, 255)  # 淡蓝色背景
TOP_AREA_COLOR = (230, 230, 250)  # 顶部区域颜色

# 创建游戏窗口
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("三消游戏")

# 字体
DEFAULT_FONT = pygame.font.SysFont('幼圆', 32, bold=True)
