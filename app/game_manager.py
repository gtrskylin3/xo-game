from typing import Dict
from uuid import uuid4


# Структура игр
# games = {
#     game_id: {
#         game_state: {
#             'board': self.board,
#             'turn': self.turn,
#             'winner': self.winner,
#             'score': self.score,
#         }
#     },
#     game_id2: {
#         game_state: {
#             'board': self.board,
#             'turn': self.turn,
#             'winner': self.winner,
#             'score': self.score,
#         }
#     },
# }


class Game:
    def __init__(self, players: dict):
        self.turn = "X"
        self.board = [
            ["", "", ""],
            ["", "", ""],
            ["", "", ""],
        ]
        self.winner = None
        self.score = {"X": 0, "O": 0}
        self.players = players

    def check_win(self, player):
        # Проверка по горизонтали
        board = self.board
        for r in range(3):
            if board[r][0] == board[r][1] == board[r][2] == player:
                return True

        # Проверка по вертикали
        for c in range(3):
            if board[0][c] == board[1][c] == board[2][c] == player:
                return True

        # Проверка диагоналей
        if board[0][0] == board[1][1] == board[2][2] == player:
            return True

        if board[0][2] == board[1][1] == board[2][0] == player:
            return True

        return False

    def make_move(self, row, col, player):
        player = player["role"]
        if self.winner:
            return False

        if player != self.turn:
            return False

        if self.board[row][col] != "":
            return False

        self.board[row][col] = player
        if self.check_win(player):
            self.winner = player
            self.score[player] += 1

        elif all(self.board[r][c] != "" for r in range(3) for c in range(3)):
            self.winner = "draw"  # Ничья
        self.turn = "O" if self.turn == "X" else "X"
        return True

    def game_state(self, type=None):
        game_state = {
            "board": self.board,
            "winner": self.winner,
            "score": self.score,
            "turn": self.turn,
            "players": self.players,
        }
        if type:
            game_state["type"] = type
        return game_state

    def reset_game(self):
        self.board = [
            ["", "", ""],
            ["", "", ""],
            ["", "", ""],
        ]
        self.turn = "X"
        self.winner = None


class GameManager:
    def __init__(self):
        self.games: Dict[str, Game] = {}

    def create_game(self, players):
        game_id = str(uuid4())
        self.games[game_id] = Game(players)
        return game_id

    def reset_game(self, game_id):
        game = self.games[game_id]
        if game:
            game.reset_game()

    def get_game_by_nickname(self, nickname_to_find: str) -> str | None:
        for game_id, game in self.games.items():
            if nickname_to_find in game.players.values():
                return game_id
        
    def make_move(self, row, col, player):
        game_id = self.get_game_by_nickname(player["nickname"])

        if not game_id:
            return False

        game = self.games.get(game_id)

        if not game:
            return False

        return game.make_move(row, col, player)

    def game_state(self, game_id: str, type=None):
        return self.games[game_id].game_state(type)


# game = Game()
# cur = 'X'
# i = 1
# while True:
#     if game.winner:
#         game.__init__()
#     cur = 'X' if i % 2 != 0 else 'O'
#     game.make_move(int(input('row: ')), int(input('col: ')), cur)
#     for row in game.board:
#         print(row)
#     i += 1
#     continue
