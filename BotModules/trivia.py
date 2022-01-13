from socket import MsgFlag
from typing import Optional, Tuple
from discord.ext import commands
import requests
import json
from random import shuffle
import traceback

#####################
#       UTILS       #
#####################
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
        self.questions: Optional[dict] = None
        self.question_counter = 0
        self.total_questions = 0
        self.score = {}
        self.has_guessed = {}
        self.options = {}
        self.correct_answer = ''
        self.question = ''
        self.guesses = {}

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

    @commands.command(name='trivia-categories')
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
    
    @commands.command(name='trivia-new')
    async def new_game(self, ctx, *args):
        # check if an active game is already running
        if self.is_playing:
            await ctx.send('A game is already running')
            return
        # parse args
        args, valid = await self._parse_args(ctx, args)
        if not valid:
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
        
        # start new game
        self.questions = questions
        self.question_counter = 1
        self.total_questions = params['amount']
        self.is_playing = True
        self.score = {member.nick : 0 for member in ctx.guild.members if not member.bot}
        self.has_guessed = {member.nick : False for member in ctx.guild.members if not member.bot}
        self.guesses = {member.nick : -1 for member in ctx.guild.members if not member.bot}

        await self._print_question(ctx)

    @commands.command(name='guess')
    async def guess(self, ctx, guess):
        # check if game is running
        if not self.is_playing:
            await ctx.send('No game is currently running.')
            return
        guesser = ctx.author.nick
        if self.has_guessed[guesser]:
            await ctx.send(f'You already guessed {self.guesses[guesser]}')
        
        # check if valid guess
        guess, valid = await self._is_valid_guess(ctx, guess)
        if not valid or guess is None:
            return
        
        # note down guess
        self.has_guessed[guesser] = True
        self.guesses[guesser] = guess # maybe change this
        await ctx.send(f'{guesser} has guessed {guess}!')

        if self._all_have_guessed():
            await self._show_results_for_question(ctx)
            await self._advance_question(ctx)


    def _update_score(self):
        for guesser, guess in self.guesses.items():
            if guess == self.correct:
                self.score[guesser] += 1

    async def _show_results_for_question(self, ctx):
        self._update_score()
        msg  = 'Everyone have guessed!\n'
        msg += f'The correct answer was: {self.correct}\n'
        msg += 'Score:\n'
        msg += '```\n'
        for person, score in self.score.items():
            msg += f'{person}: {score}\n'
        msg += '```'
        await ctx.send(msg)


    async def _advance_question(self, ctx):
        self.question_counter += 1
        if self.question_counter > self.total_questions:
            await self._print_results(ctx)
            self._reset()
        self.has_guessed = {member.nick : False for member in ctx.guild.members if not member.bot}
        self.guesses = {member.nick : -1 for member in ctx.guild.members if not member.bot}

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
            msg += f'{person} : {score}\n'
        msg += '```\n'
        msg += 'The winner(s) were: ' + ', '.join(winners)
        await ctx.send(msg)

    def _all_have_guessed(self):
        return all(self.has_guessed.values())

    async def _is_valid_guess(self, ctx, guess):
        guess, is_int = try_parse_int(guess)
        if is_int and guess is not None:
            if guess <= 0 and guess < len(self.options):
                return guess, True
            else:
                await ctx.send(f'Invalid guess: {guess}')
                return None, False
        else:
            await ctx.send(f'Invalid guess {guess}')
            return None, False

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
        msg  = f'Question {self.question_counter}/{self.total_questions}'
        msg += '```\n'
        msg += f'{self.question}\n'
        for idx, option in enumerate(self.options):
            msg += f'{idx}: {option}\n'
        msg += '```'
        await ctx.send(msg)


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
                await ctx.send('All question has been shown for this session, resetting session token. Please try again.')
                return None, False
        
        questions = {idx + 1 : question for idx, question in enumerate(data['results'])}
        return questions, True
    def _create_params(self, args):
        params = {}
        for key, val in args.items():
            if val is None:
                continue
            params[key] = val
        return params

    
    async def _parse_args(self, ctx, args) -> Tuple[Optional[dict], bool]:
        # default args
        args = {
            'category'   : None,
            'amount'     : 10,
            'difficulty' : None,
            'type'       : None
        }
        category = None
        amount = 10
        difficulty = None
        type = None
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
                        args['category'] = c
                    else:
                        await ctx.send(f'Invalid category: {val}')
                        return None, False
                case 'a' | 'amount':
                    a, is_int = try_parse_int(val)
                    if is_int and a is not None:
                        if a >= 1 and a <= 50:
                            args['amount'] = a
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
                            args['difficulty'] = d
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
                            args['type'] = t
                        else:
                            await ctx.send(f'Invalid type: {t}')
                            return None, False
                    else:
                        await ctx.send(f'Invalid type {val}')
                        return None, False
        return args, True


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
