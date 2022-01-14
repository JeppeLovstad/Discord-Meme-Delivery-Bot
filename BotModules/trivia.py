from typing import Optional, Tuple
from discord.ext import commands
import requests
import json
from random import shuffle
import html
import asyncio

##################################
###           UTILS            ###
##################################
def try_parse_int(x) -> Tuple[Optional[int], bool]:
    try:
        x = int(x)
        return x, True
    except:
        return None, False

def try_parse_string(x) -> Tuple[Optional[str], bool]:
    try:
        x = str(x)
        return x, True
    except:
        return None, False

class Trivia(commands.Cog):
    def __init__(self, config, bot: commands.Bot):
        self.config = config
        self.bot = bot
        # api stuff
        self.url: str = 'https://opentdb.com/'
        self.session_token: Optional[str] = None
        self._generate_session_token()
        # categories
        self.categories: dict = self._get_categories()
        # game variables
        self.is_playing = False
        self.is_lobby = False
        self.lobby = []
        self.questions: Optional[dict] = None
        self.question_counter = 0
        self.total_questions = 0
        self.seconds = -1
        self.score = {}
        self.has_guessed = {}
        self.options = {}
        self.correct_answer = ''
        self.question = ''
        self.guesses = {}
        self.questions_finished = {}

    ##################################
    ###         COMMANDS           ###
    ##################################

    ###
    ### categories
    ###
    @commands.command(name='trivia-categories', aliases=['t-categories'])
    async def get_categories(self, ctx):
        if self.categories == {}:
            await ctx.send('No categories found.')
            return
        await ctx.send('Categories:')
        categories = '```\n'
        for id, category in self.categories.items():
            categories += f'{id}: {category}\n'
        categories += '```'
        await ctx.send(categories)

    ###
    ### new lobby
    ###
    @commands.command(name='trivia-new', aliases=['t-new'])
    async def new_game(self, ctx, *args):
        # check if an active game is already running
        if self.is_playing:
            await ctx.send('A game is already running')
            return
        # parse args
        args, valid = await self._parse_args(ctx, args)
        if not valid or args is None:
            return
        
        # create params for request
        params = self._create_params(args)

        # get questions
        response = requests.get(
            self.url + 'api.php',
            params=params
        )
        if response.status_code != 200:
            print(f'Call to get questions at {response.url} returned status code {response.status_code}')
            return
        data = json.loads(response.content)
        questions, valid = await self._parse_questions(ctx, data)
        if not valid:
            return
        
        # start lobby
        await self._start_lobby(ctx, args)

        # setup some game variables
        self.questions = questions
        self.total_questions = params['amount']
        self.questions_finished = {id : False for id in range(1, self.total_questions + 1)}
        self.question_counter = 1
        self.seconds = args['seconds']
        self.is_lobby = True

    ###
    ### start game
    ###
    @commands.command(name='trivia-start', aliases=['t-start'])
    async def start(self, ctx):
        if len(self.lobby) == 0:
            await ctx.send('There are no people in the lobby')
            return
        await self._start_game(ctx)

    ###
    ### cancel game/lobby
    ###
    @commands.command(name='trivia-cancel', aliases=['t-cancel'])
    async def cancel_lobby(self, ctx):
        if self.is_lobby:
            await ctx.send('Lobby cancelled.')
            self._reset()
            return
        if self.is_playing:
            await ctx.send('Game cancelled.')
            self._reset()
            return

    ###
    ### join lobby
    ###
    @commands.command(name='trivia-join', aliases=['t-join'])
    async def join_lobby(self, ctx):
        if self.is_playing:
            await ctx.send('You cannot join a game in session.')
            return
        person = ctx.author.nick
        if person in self.lobby:
            await ctx.send('You are already in the lobby you buffoon')
            return
        self.lobby.append(person)
        await ctx.send(f'{person} joined the lobby!')
        await self._print_lobby_members(ctx)

    ###
    ### leave lobby
    ###
    @commands.command(name='trivia-leave', aliases=['t-leave'])
    async def leave_lobby(self, ctx):
        person = ctx.author.nick
        if person not in self.lobby:
            await ctx.send('You are not in the lobby you buffoon')
            return
        self.lobby.remove(person)
        await ctx.send(f'{person} left the lobby!')
        await self._print_lobby_members(ctx)

    ###
    ### guess
    ###
    # @commands.Cog.listener(name='on_message')
    # async def guess_listener(self, guess):
    #     ctx = await self.bot.get_context(guess)
    #     if not self.is_playing:
    #         return
    #     person = ctx.
    #     if person not in self.lobby:
    #         return
    #     guess, is_int = try_parse_int(guess)
    #     if not is_int or guess is None:
    #         return
    #     await self.guess(ctx, guess)

    @commands.command(name='guess', aliases=['g'])
    async def guess(self, ctx, guess):
        # delete message so other people cant see what was guessed
        await ctx.message.delete()

        # check if game is running
        if not self.is_playing:
            await ctx.send('No game is currently running.')
            return
        guesser = ctx.author.nick
        
        if guesser not in self.lobby:
            await ctx.send('You are not playing you buffoon.')
            return

        if self.has_guessed[guesser]:
            await ctx.send(f'You already guessed.')
            return
        
        # check if valid guess
        guess, valid = await self._is_valid_guess(ctx, guess)
        if not valid or guess is None:
            return
        
        # note down guess
        self.has_guessed[guesser] = True
        self.guesses[guesser] = guess # maybe change this
        await ctx.send(f'{guesser} has guessed!')

        if self._all_have_guessed():
            await ctx.send('Everyone have guessed!')
            await self._show_results_for_question(ctx)
            await self._advance_question(ctx)

    ##################################
    ###            API             ###
    ##################################
    def _generate_session_token(self):
        response = requests.get(
            self.url + 'api_token.php',
            params={
                'command' : 'request'
            }
        )
        if response.status_code != 200:
            print(f'Call to generate session token at {response.url} returned status code {response.status_code}')
            self.session_token = None
            return
        data = json.loads(response.content)
        if data['response_code'] != 0:
            print(f'Error generating token: {data["response_code"]}')
            self.session_token = None
            return None
        token = data['token']
        self.session_token = token
    
    def _reset_session_token(self):
        if self.session_token is None:
            self.session_token = self._generate_session_token()
            return
        response = requests.get(
            self.url + 'api_token.php',
            params={
                'command' : 'reset',
                'token' : self.session_token
            }
        )
        if response.status_code != 200:
            print(f'Call to reset session token at {response.url} returned status code {response.status_code}')
            return
        data = json.loads(response.content)
        if data['response_code'] != 0:
            print(f'Error generating token: {data["response_code"]}')
            return
        token = data['token']
        self.session_token = token

    def _get_categories(self) -> dict:
        response = requests.get(
            self.url + 'api_category.php'
        )
        if response.status_code != 200:
            print(f'Call to get categories at {response.url} returned status code {response.status_code}')
            return {}
        data = json.loads(response.content)
        categories = {item['id'] : item['name'] for item in data['trivia_categories']}
        return categories

    ##################################
    ###           GAME             ###
    ##################################
    async def _start_game(self, ctx):
        # start new game
        self.is_playing = True
        self.score = {member : 0 for member in self.lobby}
        self.has_guessed = {member : False for member in self.lobby}
        self.guesses = {member : -1 for member in self.lobby}
        await self._print_question(ctx)

    def _update_score(self):
        for guesser, guess in self.guesses.items():
            if not self.has_guessed[guesser]:
                continue
            if self.options[guess] == self.correct:
                self.score[guesser] += 1

    async def _show_results_for_question(self, ctx):
        self._update_score()
        msg = f'The correct answer was: {self.correct}\n'
        msg += 'Score:\n'
        msg += '```\n'
        for person, score in self.score.items():
            msg += f'{person}: {score}\n'
        msg += '```'
        await ctx.send(msg)

    async def _advance_question(self, ctx):
        self.questions_finished[self.question_counter] = True
        self.question_counter += 1
        if self.question_counter > self.total_questions:
            await self._print_results(ctx)
            self._reset()
            return
        self.has_guessed = {member : False for member in self.lobby}
        self.guesses = {member : -1 for member in self.lobby}
        await self._print_question(ctx)

    def _get_winners(self):
        winners = []
        to_beat = -1
        for person, score in self.score.items():
            if score > to_beat:
                winners = [person]
                to_beat = score
            elif score >= to_beat:
                winners.append(person)
        return winners

    async def _print_results(self, ctx):
        winners = self._get_winners()
        msg  = 'The quiz is over!\n'
        msg += 'Final score:'
        msg += '```\n'
        for person, score in self.score.items():
            msg += f'{person}: {score}\n'
        msg += '```\n'
        msg += 'The winner(s) were: ' + ', '.join(winners)
        await ctx.send(msg)

    def _all_have_guessed(self):
        return all(self.has_guessed.values())

    def _prepare_question(self):
        if self.questions is None:
            return
        question = self.questions[self.question_counter]
        self.question = question['question']
        self.correct = question['correct_answer']
        options = question['incorrect_answers']
        options.append(self.correct)
        shuffle(options)
        self.options = options

    async def _print_question(self, ctx):
        self._prepare_question()
        msg  = f'Question {self.question_counter}/{self.total_questions}\n'
        msg += '```\n'
        msg += f'{html.unescape(self.question)}\n'
        for idx, option in enumerate(self.options):
            msg += f'{idx}: {html.unescape(option)}\n'
        msg += '```'
        await ctx.send(msg)
        await self._timer(ctx, self.question_counter)

    async def _timer(self, ctx, question_no):
        msg = await ctx.send(f'Time left: {self.seconds}')
        for timestamp in range(self.seconds-1, 0, -1):
            await msg.edit(content=f'Time left: {timestamp}')
            if not self.is_playing or self.questions_finished[question_no]:
                await msg.delete()
                return
            await asyncio.sleep(1)
        await msg.delete()
        if not self.questions_finished[question_no]:
            await ctx.send('Time\'s up!')
            await self._show_results_for_question(ctx)
            await self._advance_question(ctx)

    ##################################
    ###          LOBBY             ###
    ##################################
    async def _start_lobby(self, ctx, args):
        await self._print_lobby_message(ctx, args)
        self.is_lobby = True

    async def _print_lobby_members(self, ctx):
        if len(self.lobby) == 0:
            await ctx.send(f'Lobby is empty.')
            return
        msg  = 'Lobby:\n'
        msg += '```\n'
        for person in self.lobby:
            msg += f'{person}\n'
        msg += '```'
        await ctx.send(msg)

    async def _print_lobby_message(self, ctx, args):
        arg_formatter = {
            'category'      : 'Category',
            'amount'        : '# of questions',
            'difficulty'    : 'Difficulty',
            'type'          : 'Type',
            'seconds'       : 'Time (sec)'
        }
        msg  = f'Lobby started (type \'!join\' to join the lobby):\n'
        msg += '```\n'
        for key, val in args.items():
            if key == 'category':
                val = 'Any' if val is None else self.categories[val]
            else:
                val = 'Any' if val is None else val
            msg += f'{arg_formatter[key]}: {val}\n'
        msg += '```'
        await ctx.send(msg)
    
    ##################################
    ###       VALIDATION          ###
    ##################################
    def _valid_category(self, category) -> Tuple[Optional[int], bool]:
        # check if category is int
        val, is_int = try_parse_int(category)
        if is_int: # int
            if val in self.categories.keys():
                return val, True
            else:
                return None, False
        else:
            val = str(val)
            for id, category in self.categories.items():
                if val.lower() == category.lower():
                    return id, True
            return None, False

    async def _is_valid_guess(self, ctx, guess):
        val, is_int = try_parse_int(guess)
        if is_int and val is not None:
            if val >= 0 and val < len(self.options):
                return val, True
            else:
                await ctx.send(f'Guess out of range: {val}')
                return None, False
        else:
            await ctx.send(f'Invalid guess {guess}')
            return None, False
    
    ##################################
    ###           MISC             ###
    ##################################
    def _create_params(self, args):
        params = {}
        for key, val in args.items():
            if val is None:
                continue
            params[key] = val
        return params
    
    async def _parse_args(self, ctx, args) -> Tuple[Optional[dict], bool]:
        # default args
        parsed_args = {
            'category'   : None,
            'amount'     : 10,
            'difficulty' : None,
            'type'       : None,
            'seconds'    : 60
        }
        # parse args
        for arg in args:
            try:
                arr = arg.split('=')
                key = str(arr[0])
                val = arr[1]
            except:
                await ctx.send(f'Invalid arg: {arg}')
                return None, False
            match key:
                case 'c' | 'category':
                    c, valid = self._valid_category(val)
                    if valid:
                        parsed_args['category'] = c
                    else:
                        await ctx.send(f'Invalid category: {val}')
                        return None, False
                case 'a' | 'amount':
                    a, is_int = try_parse_int(val)
                    if is_int and a is not None:
                        if a >= 1 and a <= 50:
                            parsed_args['amount'] = a
                        else:
                            await ctx.send(f'Amount {a} out of range. Must be between 1 and 50')
                    else:
                        await ctx.send(f'Invalid amount: {val}')
                        return None, False
                case 'd' | 'difficulty':
                    d, is_str = try_parse_string(val)
                    if is_str and d is not None:
                        d = d.lower()
                        if d in ['easy', 'medium', 'hard']:
                            parsed_args['difficulty'] = d
                        else:
                            await ctx.send(f'Invalid difficulty: {d}')
                            return None, False
                    else:
                        await ctx.send(f'Invalid difficulty: {val}')
                        return None, False
                case 't' | 'type':
                    t, is_str = try_parse_string(val)
                    if is_str and t is not None:
                        t = t.lower()
                        if t in ['boolean', 'multiple']:
                            parsed_args['type'] = t
                        else:
                            await ctx.send(f'Invalid type: {t}')
                            return None, False
                    else:
                        await ctx.send(f'Invalid type {val}')
                        return None, False
                case 's' | 'seconds':
                    s, is_int = try_parse_int(val)
                    if is_int and s is not None:
                        if s > 0:
                            parsed_args['seconds'] = s
                        else:
                            await ctx.send(f'Seconds must be positive: {s}')
                            return None, False
                    else:
                        await ctx.send(f'Invalid seconds: {val}')
                        return None, False
                case _:
                    await ctx.send(f'Invalid key: {key}')
                    return None, False
        return parsed_args, True
    
    async def _parse_questions(self, ctx, data) -> Tuple[Optional[dict], bool]:
        code = data['response_code']
        match code:
            case 1:
                await ctx.send('Not enough questions available, try lowering the amount.')
                return None, False
            case 2:
                await ctx.send(f'Invalid parameter.')
                return None, False
            case 3:
                self._generate_session_token()
                await ctx.send('Invalid session token, generating new session token. Please try again.')
                return None, False
            case 4:
                self._reset_session_token()
                await ctx.send('All questions have been shown for this session, resetting session token. Please try again.')
                return None, False
        
        questions = {idx + 1 : question for idx, question in enumerate(data['results'])}
        return questions, True

    def _reset(self):
        self.is_playing = False
        self.questions = None
        self.question_counter = 0
        self.total_questions = 0
        self.score = {}
        self.has_guessed = {}
        self.options = {}
        self.correct_answer = ''
        self.question = ''
        self.guesses = {}
        self.seconds = -1
        self.questions_finished = {}
        self.is_lobby = False
        self.lobby = []
