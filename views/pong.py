from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QKeyEvent, QFont
from PySide6.QtCore import Qt, QTimer, QRect


class PongGame(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pong Game")
        self.setFixedSize(600, 400)

        # Ball
        self.ball = QRect(290, 190, 20, 20)
        self.ball_dx = 4
        self.ball_dy = 4

        # Paddles
        self.paddle = QRect(20, 150, 10, 80)
        self.opponent = QRect(570, 150, 10, 80)

        # Scores
        self.player_score = 0
        self.opponent_score = 0

        # Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_game)
        self.timer.start(16)  # ~60 FPS

        self.setFocusPolicy(Qt.StrongFocus)

    def update_game(self):
        # Move ball
        self.ball.moveLeft(self.ball.x() + self.ball_dx)
        self.ball.moveTop(self.ball.y() + self.ball_dy)

        # Wall bounce
        if self.ball.top() <= 0 or self.ball.bottom() >= self.height():
            self.ball_dy = -self.ball_dy

        # Paddle collision
        if self.ball.intersects(self.paddle) or self.ball.intersects(self.opponent):
            self.ball_dx = -self.ball_dx

        # Score update: Left or right wall
        if self.ball.left() <= 0:
            self.opponent_score += 1
            self.reset_ball(direction=1)
        elif self.ball.right() >= self.width():
            self.player_score += 1
            self.reset_ball(direction=-1)

        # Simple opponent AI
        if self.ball.center().y() < self.opponent.center().y():
            self.opponent.moveTop(self.opponent.y() - 3)
        elif self.ball.center().y() > self.opponent.center().y():
            self.opponent.moveTop(self.opponent.y() + 3)

        # Clamp opponent paddle
        self.opponent.moveTop(max(0, min(self.opponent.y(), self.height() - self.opponent.height())))

        self.update()

    def reset_ball(self, direction=1):
        self.ball.moveTo(self.width() // 2 - 10, self.height() // 2 - 10)
        self.ball_dx = 4 * direction
        self.ball_dy = 4

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key_Up:
            self.paddle.moveTop(self.paddle.y() - 20)
        elif event.key() == Qt.Key_Down:
            self.paddle.moveTop(self.paddle.y() + 20)

        # Clamp paddle
        self.paddle.moveTop(max(0, min(self.paddle.y(), self.height() - self.paddle.height())))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)

        # Background
        painter.fillRect(self.rect(), QColor(0, 0, 0))

        # Draw paddles and ball
        painter.setBrush(QColor(255, 255, 255))
        painter.drawRect(self.paddle)
        painter.drawRect(self.opponent)
        painter.drawEllipse(self.ball)

        # Draw scores
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Arial", 20, QFont.Bold))
        painter.drawText(200, 40, f"Player: {self.player_score}")
        painter.drawText(370, 40, f"CPU: {self.opponent_score}")
