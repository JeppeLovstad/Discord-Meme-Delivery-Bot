from os import truncate
from typing import Optional, Tuple
from discord.ext import commands
from discord import Guild
import random
import traceback


#####################
#       UTILS       #
#####################
def try_parse_int(x):
    try:
        x = int(x)
        return x, True
    except:
        return None, False

class TicTacToe(commands.Cog):
    def __init__(self, config, bot: commands.Bot):
        self.config = config
        self.bot = bot
        self.games = {}


    @commands.command(name='ttt-list')
    async def list_members_short(self, ctx):
        await self.list_members(ctx)

    @commands.command(name='tictactoe-list')
    async def list_members(self, ctx):
        id = 0
        await ctx.send(f'Members (Use id or nickname to start a new game with a player):')
        members = [member.nick for member in ctx.guild.members if not member.bot]
        for member in members:
            await ctx.send(f'{id}: {member}')
            id += 1

    @commands.command(name='ttt-new')
    async def new_game_short(self, ctx, id, opponent):
        await self.new_game(ctx, id, opponent)

    @commands.command(name='tictactoe-new')
    async def new_game(self, ctx, id, opponent):
        # check if id is in use
        if self.games.get(id) != None:
            await ctx.send(f'ID {id} is already in use.')
            return
        
        # validate opponent
        opponent, valid = await self._validate_opponent(ctx, opponent)
        if not valid:
            return
        
        # create new game
        game = await self._create_game(ctx, id, opponent)
        self.games[id] = game
        
        # print new game message
        await self._new_game_message(ctx, game)

    @commands.command(name='ttt-move')
    async def move_short(self, ctx, id, move):
        await self.move(ctx, id, move)

    @commands.command(name='tictactoe-move')
    async def move(self, ctx, id, move):
        try:
            # check if id is valid
            game = self.games.get(id)
            if game == None:
                await ctx.send(f'No game found with ID {id}')
                return

            # check if move is valid
            x, y, valid = await self._validate_move(ctx, move, game['board'])
            if not valid:
                return

            # update board
            val = 1 if game['turn'] else 2
            game['board'][x][y] = val

            # print move message
            await self._move_message(ctx, game)

            # update turn
            game['turn'] = not game['turn']

            # check if game is over
            winner, done = await self._is_game_over(game)
            if done:
                if winner is not None:
                    await ctx.send(f'{winner} won the game!')
                else:
                    await ctx.send(f'No one won the game.')
                self.games[id] = None
            self.games[id] = game
        except Exception as e:
            await ctx.send(traceback.format_exc())

    async def _is_game_over(self, game):
        board = game['board']
        # check lines
        for x in range(3):
            player_one_won_horizontal = True
            player_one_won_vertical = True
            player_two_won_horizontal = True
            player_two_won_vertical = True
            for y in range(3):
                if board[x][y] in [0, 2]:
                    player_one_won_horizontal = False
                if board[x][y] in [0, 1]:
                    player_two_won_horizontal = False
                if board[y][x] in [0, 2]:
                    player_one_won_vertical = False
                if board[y][x] in [0, 1]:
                    player_two_won_vertical = False
            if player_one_won_horizontal or player_one_won_vertical:
                return game['player_two'], True
            if player_two_won_horizontal or player_two_won_vertical:
                return game['player_two'], True
        
        # check diagonal
        map = {
            0 : 2,
            1 : 1,
            2 : 0
        }
        player_one_won_diagonal_one = True
        player_one_won_diagonal_two = True
        player_two_won_diagonal_one = True
        player_two_won_diagonal_two = True
        for x in range(3):
            if board[x][x] in [0, 2]:
                player_one_won_diagonal_one = False
            if board[map[x]][x] in [0, 2]:
                player_one_won_diagonal_two = False
            if board[x][x] in [0, 1]:
                player_two_won_diagonal_one = False
            if board[map[x]][x] in [0, 1]:
                player_two_won_diagonal_two = False
        if player_one_won_diagonal_one or player_one_won_diagonal_two:
            return game['player_one'], True
        if player_two_won_diagonal_one or player_two_won_diagonal_two:
            return game['player_two'], True

        # check if no one won
        over = True
        for x in range(3):
            for y in range(3):
                if board[x][y] != 0:
                    over = False
        if over:
            return None, True
        else:
            return None, False
    async def _print_board(self, board):
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


    async def _move_message(self, ctx, game):
        cur_player = game['player_one'] if game['turn'] else game['player_two']
        other_player = game['player_two'] if game['turn'] else game['player_one']
        msg = f'{cur_player} has made a move!\n'
        msg += await self._print_board(game['board'])
        msg += f'Your turn to make a move, {other_player}!'
        await ctx.send(msg)


    async def _validate_move(self, ctx, move, game):
        # check whose turn it is
        cur_player = game['player_one'] if game['turn'] else game['player_two']
        if ctx.author.nick != cur_player:
            await ctx.send(f'It\'s not your turn you bufoon')
            return None, None, False
        board = game['board']
        try:
            arr = move.split(',')
            x = int(arr[0])
            y = int(arr[1])
            if x not in [0, 1, 2] or y not in [0, 1, 2]:
                await ctx.send(f'Move out of range: {x},{y}')
                return None, None, False
            # check if piece is already placed
            if board[y][x] != 0:
                await ctx.send(f'There is already a piece at this position.')
                return None, None, False
            return x, y, True
        except:
            await ctx.send(f'Invalid move: {move}')
            return None, None, False

    async def _new_game_message(self, ctx, game):
        msg  = 'New Tic Tac Toe game started!\n'
        msg += f'Player one: {game["player_one"]}\n'
        msg += f'Player two: {game["player_two"]}\n'
        msg += f'Turn: {game["player_one"] if game["turn"] else game["player_two"]}\n'
        msg += await self._empty_board()
        await ctx.send(msg)
    
    async def _empty_board(self):
        board  = '```\n'
        board += '-------------\n'
        board += '|   |   |   |\n'
        board += '-------------\n'
        board += '|   |   |   |\n'
        board += '-------------\n'
        board += '|   |   |   |\n'
        board += '-------------\n'
        board += '```'
        return board


    async def _create_game(self, ctx, id, opponent):
        game = {}
        game['player_one']  = ctx.author.nick
        game['player_two']  = opponent
        game['turn']        = True if random.randint(0,1) == 1 else False # True for player_one, False for player_two
        game['board']       = [[0 for _ in range(3)] for _ in range(3)]
        return game

    async def _validate_opponent(self, ctx, opponent) -> Tuple[Optional[str], bool]:
        members = [member.nick for member in ctx.guild.members if not member.bot]
        # check if opponent is given by id
        id, is_id = try_parse_int(opponent)
        if is_id and id is not None: # id
            if id >= len(members) or id < 0:
                await ctx.send(f'No member found with ID {id}')
                await self.list_members(ctx)
                return None, False
            return members[id], True
        else: # nickname
            if opponent not in members:
                await ctx.send(f'No member found with nickname {opponent}')
                await self.list_members(ctx)
                return None, False
            elif opponent == ctx.author.nick:
                await ctx.send(f'I\'m sorry that you don\'t have any friends :(')
                return None, False
            else:
                return opponent, True