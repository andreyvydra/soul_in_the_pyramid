from settings import *


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0
        self.true_dx = 0
        self.true_dy = 0

    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    def update(self, target):
        self.true_dx = -(target.rect.x + target.rect.w // 2 - SCREEN_WIDTH // 2)
        self.true_dy = -(target.rect.y + target.rect.h // 2 - SCREEN_HEIGHT // 2)

        if self.true_dx > 100:
            self.dx = self.true_dx - 100
        if self.true_dy > 100:
            self.dy = self.true_dy - 100
        if self.true_dx < 100:
            self.dx = self.true_dx + 100
        if self.true_dy < 100:
            self.dy = self.true_dy + 100

        if abs(self.true_dx) <= 100:
            self.dx = 0
        if abs(self.true_dy) <= 100:
            self.dy = 0

