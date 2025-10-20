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

    def __init__(self):
        self.games : Dict[str, dict] = {}
        
    
    def create_game(self, players):
        game_id = str(uuid4())
        self.games[game_id] = {
            'board': [
                ["", "", ""],
                ["", "", ""],
                ["", "", ""],
            ],
            'turn': 'X',
            'winner': None,
            'score': {
                'X': 0,
                'O': 0
            },
            'players': players
        }
        return game_id
        

    def reset_game(self, game_id):
        game = self.games[game_id]
        if game:
            game["board"] = [
                ["", "", ""],
                ["", "", ""],
                ["", "", ""],
            ]
            game['turn'] = 'X' 
            game['winner'] = None
    
    def get_game_by_nickname(self, player):
        for game_id, game_state in self.games.items():
            players = game_state['players']
            # print(players)
            if players:
                for nickname in players.values():
                    if nickname == player:
                        return game_id
        
        
    def _check_win(self, player, game):
        # Проверка по горизонтали
        board = game['board']
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
        game_id = self.get_game_by_nickname(player['nickname'])
        
        player = player['role']
        print(player, game_id)
        
        if not game_id:
            return False
        
        game = self.games.get(game_id)
        
        if not game:
            return False
        
        if game['winner']:
            return False
            
        if player != game['turn']:
            return False
        
        if game['board'][row][col] != '':
            return False
        
        game["board"][row][col] = player
        if self._check_win(player, game):
            game['winner']  = player
            game['score'][player] += 1

        elif all(game['board'][r][c] != "" for r in range(3) for c in range(3)):
            game['winner'] = "draw" # Ничья
        game['turn'] = 'O' if game['turn'] == 'X' else 'X'
        return True
    
    def game_state(self, game_id: str, type=None):
        if type:
            self.games[game_id]['type'] = type
        return self.games[game_id]


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

