from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from logic.forms import UserForm
from datamodel import constants
from datamodel.models import Game, GameStatus, Move, Counter
from django.views.decorators.http import require_http_methods


@require_http_methods(['GET'])
def index(request):
    return render(request, 'mouse_cat/index.html')


def anonymous_required(f):
    def wrapped(request):
        if request.user.is_authenticated:
            return HttpResponseForbidden(
                errorHTTP(request, exception='Action restricted to anonymous users'))
        else:
            return f(request)
    return wrapped


@require_http_methods(['GET', 'POST'])
@anonymous_required
def login_service(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        # /!\
        # Usar return service
        # /!\
        return_service = request.POST.get('return_service')

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return redirect(reverse('logic:'))
            else:
                # /!\
                # Añadir mensaje de cuenta desabilitada
                # /!\
                return render(request, 'mouse_cat/login.html')
        else:
            # /!\
            # Añadir mensaje de datos incorrectos
            # /!\
            return render(request, 'mouse_cat/login.html')
    else:
        return render(request, 'mouse_cat/login.html')


@require_http_methods(['GET'])
@login_required
def logout_service(request):
    context_dict = { 'user': request.user.username }
    logout(request)
    return render(request, context_dict)


@require_http_methods(['GET', 'POST'])
@login_required
def signup_service(request):
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)

        if user_form.is_valid():
            user = user_form.save()

            user.set_password(user.password)
            user.save()

            user = authenticate(username=user.username, password=user.password)
        else:
            print(user_form.errors)
    else:
        user_form = UserForm()

    context_dict = { 'user_form': user_form }
    return render(request, 'mouse_cat/signup.html', context_dict)


# /!\
# Actualizar en todas las funciones(?)
# /!\
@require_http_methods(['GET'])
def counter_service(request):
    if 'counter_session' in request.session:
        counter_session = request.session['counter_session']+1
    else:
        counter_session = 1

    request.session['counter_session'] = counter_session

    counter_global = Counter.objects.inc()

    context_dict = { 'counter_session': counter_session, 'counter_global': counter_global }
    return render(request, 'mouse_cat/counter.html', context_dict)


@require_http_methods(['GET'])
@login_required
def create_game_service(request):
    game = Game(cat_user=request.user)
    game.save()
    context_dict = { 'game': game }
    return render(request, 'mouse_cat/new_game.html', context_dict)


@require_http_methods(['GET'])
@login_required
def join_game_service(request):
    open_games = Game.objects.filter(game_status=GameStatus.CREATED).order_by('-id')
    if len(open_games) > 0:
        game = open_games[0]
        game.mouse_user = request.user
        game.save()
        context_dict = { 'game': game }
    else:
        context_dict = { 'msg_error': 'No open games found|No se han encontrados partidas abiertas' }        
    return render(request, 'mouse_cat/join_game.html', context_dict)


@require_http_methods(['GET', 'POST'])
@login_required
def select_game_service(request):
    if request.method == 'POST':
        # /!\
        # Revisar que la partida pertenezca al usuario, el nombre del argumento de POST y que game existe (como dar el mensaje de error?)
        # /!\
        game_id = request.POST.get('game.id')
        request.session['game_selected'] = game_id
        return redirect(reverse('logic:game'))
    else:
        as_cat = Game.objects.filter(cat_user=request.user)
        if len(as_cat) == 0:
            as_cat = None
        as_mouse = Game.objects.filter(mouse_user=request.mouse)
        if len(as_mouse) == 0:
            as_mouse = None

        context_dict = { 'as_cat': as_cat, 'as_mouse': as_mouse }
        return render(request, 'mouse_cat/select_game.html', context_dict)


@require_http_methods(['GET'])
@login_required
def show_game_service(request):
    # /!\
    # Revisar que exista la variable game_selected y que sea una partida válida
    # /!\
    game_id = request.session['game_selected']
    game = Game.objects.filter(id=game_id)

    board = [0]*64
    board[game.cat1] = 1
    board[game.cat2] = 1
    board[game.cat3] = 1
    board[game.cat4] = 1
    board[game.mouse] = -1
    
    # /!\
    # En teoría también se necesita el usuario actual, pero no veo que se use en game.html
    # Falta move_form (?)
    # /!\
    context_dict = { 'game': game, 'board': board }
    return render(request, 'mouse_cat/game.html', context_dict)


@require_http_methods(['POST'])
@login_required
def move_service(request):
    # /!\
    # Revisar que exista la variable game_selected y que sea una partida válida
    # Averiguar nombres de los movimientos
    # /!\
    player = request.user
    game_id = request.session['game_selected']
    game = Game.objects.filter(id=game_id)
    initial_pos = request.POST.get('initial_pos')
    final_pos = request.POST.get('final_pos')
    
    if game.cat_turn is True:
        # /!\
        # if ningún game.cat == initial_pos:
        #     error
        # /!\
        # Comprobación de movimientos válidos
        game.cat1 = final_pos
        #       ^ No necesariamente el 1
    else:
        # /!\
        # if game.mouse != initial_pos:
        #     error
        # /!\
        # Comprobación de movimientos válidos
        game.mouse = final_pos

    game.cat_turn = not game.cat_turn
    game.save()
    return redirect(reverse('logic:game'))



# /!\
# Usar el error para algo
# /!\
def errorHTTP(request, exception=None):
    context_dict = {}
    context_dict[constants.ERROR_MESSAGE_ID] = exception
    return render(request, 'mouse_cat/error.html', context_dict)
