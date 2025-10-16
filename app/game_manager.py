
# Создать класс Game для хранения доски (3x3 матрица), текущего хода, проверки победы/ничьей.
# Функции: инициализация доски, валидация хода, обновление доски, проверка на конец игры.
# Цель: Улучшить навыки Python (работа с списками, алгоритмами проверки).

class Game:

    def __init__(self):
        self.board = [
            ["", "", ""],
            ["", "", ""],
            ["", "", ""],
        ]
        self.turn = 'X'
        self.winner = None
    
    def _check_win(self, player):
        win_combo = ((0,1,2), (0,0,0), (1,1,1), (2,2,2), (2,1,0))
        for combo in win_combo:
            if self.board[0][combo[0]] == self.board[1][combo[1]] == self.board[2][combo[2]] == player:
            # if self.board[0][combo[0]] == player and self.board[1][combo[1]] == player and self.board[2][combo[2]] == player:
                return True
            
        for row in self.board:
            if all(i == player for i in row):
                return True
        return False

    def make_move(self, row, col, player):
        if self.winner:
            return False
        if player != self.turn:
            return False
        if self.board[row][col] != '':
            return False
        
        self.board[row][col] = player
        if self._check_win(player):
            self.winner = player
        elif all(self.board[r][c] != "" for r in range(3) for c in range(3)):
            self.winner = "draw" # Ничья
        self.turn = 'O' if self.turn == 'X' else 'X'
        return True
    
game = Game()
cur = 'X'
i = 1
while not game.winner:
    cur = 'X' if i % 2 != 0 else 'O'
    game.make_move(int(input('row: ')), int(input('col: ')), cur)
    for row in game.board:
        print(row)
    i += 1
    continue