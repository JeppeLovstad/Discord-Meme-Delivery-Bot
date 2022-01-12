from discord.ext import commands
import random
import traceback

class TicTacToe(commands.Cog):
    def __init__(self, config, bot: commands.Bot):
        self.config = config
        self.bot = bot
        self.games = {}
    
    @commands.command()
    async def tictactoe(self, ctx, arg1=None, arg2=None):
        try:
            if arg1 is None and arg2 is None:
                possible_players = [player.nick for player in ctx.guild.members if not player.bot]
                await ctx.send('possible players:')
                for player in possible_players:
                    await ctx.send(player)
            # check for existing game
            if arg1 in self.games:
                if self.games[arg1] != None:
                    await self.turn(ctx, arg1, arg2)
            # new game
            if arg1 is not None:
                await self._new_game(ctx, arg1, arg2)
        except Exception:
            await ctx.send(traceback.format_exc())
    
    async def _new_game(self, ctx, other_player, id):
        possible_players = [player.nick for player in ctx.guild.members if not player.bot]
        if other_player not in possible_players:
            await ctx.send(f'who {other_player}?')
            return False
        if other_player == ctx.author.nick:
            await ctx.send(f'i will not waste cpu cycles for you to play tictactoe with yourself')
            return False
        
        turn = True if random.randint(0, 1) == 1 else False
        game = {
            'player_one'            : ctx.author.nick,
            'player_two'            : other_player,
            'board'                 : [[0 for _ in range(3)] for _ in range(3)],
            'turn'                  : turn # true for player_one, false for player_two
        }
        if id is None:
            await ctx.send('y u no give id')
            return False
        
        if id in self.games:
            if self.games[id] != None:
                await ctx.send('get your own id man')
                return False

        self.games[id] = game
        await ctx.send(f'come, come! {game["player_one"]} and {game["player_two"]} are gonna battle it out with sticks and stones!')
        await ctx.send(self.empty_board())
        await ctx.send(f'use command !tictactoe {id} x,y to place a piece')
        if game['turn']:
            await ctx.send(f'your turn, {game["player_one"]}')
        else:
            await ctx.send(f'your turn, {game["player_two"]}')
        self.games[id] = game
        return True

    async def turn(self, ctx, id, move):
        # find game
        if id not in self.games:
            await ctx.send('you got the wrong id kiddo')
            return
        else:
            if self.games[id] is None:
                await ctx.send('you got the wrong id kiddo')
                return
        
        game = self.games[id]

        # check turn
        if game['turn']: # player_one's turn
            if ctx.author.nick != game["player_one"]:
                await ctx.send(f'you\'re an impatient little shit, aren\'t you?')
                return
        else: # player_two's turn
            if ctx.author.nick != game["player_two"]:
                await ctx.send(f'you\'re an impatient little shit, aren\'t you?')
        
        # parse move
        move = [x for x in move.split(',')]
        try:
            x, y = int(move[0]), int(move[1])
            if x not in [0, 1, 2] or y not in [0, 1, 2]:
                await ctx.send('what the hell kind of move is this')
                return

        except:
            await ctx.send('what the hell kind of move is this')
            return

        # check if valid move
        if game['board'][y][x] != 0:
            await ctx.send(f'someone here dawg, find another place to put your weird signs')
            return
        
        # make move and print board
        game["board"][y][x] = 1 if game["turn"] else 2
        player = game['player_one'] if game['turn'] else game['player_two']
        await ctx.send(f'{player} has managed to write something i understand!')
        await ctx.send(self.print_board(game['board']))
        game['turn'] = not game['turn']
        if game['turn']:
            await ctx.send(f'your turn, {game["player_one"]}')
        else:
            await ctx.send(f'your turn, {game["player_two"]}')
        self.games[id] = game
        return


    async def check_if_won(self, ctx, id):
        game = self.games[id]
        board = game['board']
        # check horizontal
        for x in range(3):
            one_won = True
            two_won = True
            for y in range(3):
                if board[x][y] in [0, 2]:
                    one_won = False
                if board[x][y] in [0, 1]:
                    two_won = False
            if one_won:
                await ctx.send(f'{game["player_one"]} has won the game!')
                self.games[id] = None
                return
            if two_won:
                await ctx.send(f'{game["player_two"]} has won the game!')
                self.games[id] = None
                return
        # check vertical
        for x in range(3):
            one_won = True
            two_won = True
            for y in range(3):
                if board[y][x] in [0, 2]:
                    one_won = False
                if board[y][x] in [0, 1]:
                    two_won = False
            if one_won:
                await ctx.send(f'{game["player_one"]} has won the game!')
                self.games[id] = None
                return
            if two_won:
                await ctx.send(f'{game["player_two"]} has won the game!')
                self.games[id] = None
                return
        # check diagonal
        one_won = True
        two_won = True
        for x in range(3):
            if board[x][x] in [0, 2]:
                one_won = False
            if board[x][x] in [0, 1]:
                two_won = False
        if one_won:
            await ctx.send(f'{game["player_one"]} has won the game!')
            self.games[id] = None
            return
        if two_won:
            await ctx.send(f'{game["player_two"]} has won the game!')
            self.games[id] = None
            return

        im_smart = {
            0 : 2,
            1 : 1,
            2 : 0
        }
        one_won = True
        two_won = True
        for x in range(3):
            if board[im_smart[x]][x] in [0, 2]:
                one_won = False
            if board[im_smart[x]][x] in [0, 1]:
                two_won = False
        if one_won:
            await ctx.send(f'{game["player_one"]} has won the game!')
            self.games[id] = None
            return
        if two_won:
            await ctx.send(f'{game["player_two"]} has won the game!')
            self.games[id] = None
            return

        # check stalemate
        stale_mate = True
        for x in range(3):
            for y in range(3):
                if board[x][y] == 0:
                    stale_mate = False

        if stale_mate:
            await ctx.send(f'none of you won, you should be ashamed of yourselves')
            self.games[id] = None
            return

    def print_board(self, board):
        print_board = [
            '-------------',
            '|   |   |   |',
            '-------------',
            '|   |   |   |',
            '-------------',
            '|   |   |   |',
            '-------------',

        ]
        for x in range(3):
            for y in range(3):
                if board[x][y] == 0:
                    continue
                # best code i have ever written
                piece = 'x' if board[x][y] == 1 else 'o'
                line = print_board[(x * 2) + 1]
                line = str(line[0:(y*4)+1]) + ' ' + piece + ' ' + str(line[(y*4)+4:])
                print_board[(x * 2) + 1] = line

        return "```\n" + '\n'.join(print_board) + '\n```'

    def empty_board(self):
        return """```
-------------
|   |   |   |
-------------
|   |   |   |
-------------
|   |   |   |
-------------
```""" # who needs formatering

