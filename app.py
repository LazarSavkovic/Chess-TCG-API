from flask import Flask, render_template,  redirect
from flask_sock import Sock
import json
import uuid
from game import ChessGame


app = Flask(__name__)
sock = Sock(app)


user_assignments = {}
connected_users = {}
games = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create-room')
def create_room():
    room_id = str(uuid.uuid4())  # Generate a unique UUID
    return redirect(f'/room/{room_id}')  # Redirect to /room/{uuid}


@app.route('/room/<game_id>')
def room(game_id):
    return render_template('room.html')


@sock.route('/game/<game_id>')
def game(ws, game_id):
    if game_id not in games:
        games[game_id] = ChessGame()

    game = games[game_id]
    user_id = None

    # Ensure we have a persistent assignment for this game.
    if game_id not in user_assignments:
        user_assignments[game_id] = {}

    try:
        while True:
            message = ws.receive()
            if not message:
                break

            data = json.loads(message)

            if not user_id:
                # Ensure the connected_users map exists for this game.
                if game_id not in connected_users:
                    connected_users[game_id] = {}
                game_users = connected_users[game_id]

                # Get the username from the client (the client generated it if none existed)
                incoming_username = data.get('username')
                if not incoming_username:
                    ws.send(json.dumps({'type': 'error', 'message': 'Username is required'}))
                    return
                print('incoming_username', incoming_username)
                # Check if this username was already assigned a slot
                if incoming_username in user_assignments[game_id]:
                    user_id = user_assignments[game_id][incoming_username]
                else:
                    # Assign a new slot if available.
                    if '1' not in game_users:
                        user_id = '1'
                    elif '2' not in game_users:
                        user_id = '2'
                    else:
                        ws.send(json.dumps({'type': 'error', 'message': 'Game room is full'}))
                        return
                    # Save this assignment so that it persists on reconnects.
                    user_assignments[game_id][incoming_username] = user_id

                # Register this WebSocket connection.
                connected_users[game_id][user_id] = ws

                serialized_board = [[p.to_dict() if p else None for p in row] for row in game.board]
                serialized_land_board = [[p.to_dict() if p else None for p in row] for row in game.land_board]
                hand1 = [c.to_dict() for c in game.hands['1']]
                hand2 = [c.to_dict() for c in game.hands['2']]

                # Send initial board + hands
                ws.send(json.dumps({
                    'type': 'init',
                    'board': serialized_board,
                    'land_board': serialized_land_board,
                    'hand1': [c.to_dict() for c in game.hands['1']],
                    'hand2': [c.to_dict() for c in game.hands['2']],
                    'turn': game.current_player,
                    'mana': game.mana,
                    'graveyard': {
                        '1': [c.to_dict() for c in game.graveyard['1']],
                        '2': [c.to_dict() for c in game.graveyard['2']],
                    },
                    'deck_sizes': {
                        '1': len(game.decks['1']),
                        '2': len(game.decks['2']),
                    },
                    'center_tile_control': game.center_tile_control,
                    'username': incoming_username,
                    'user_id': user_id,
                    'user_assignments': user_assignments[game_id]

                }))


            elif data['type'] == 'move':
                from_pos = data['from']
                to_pos = data['to']
                success, info = game.move(from_pos, to_pos, user_id)
                serialized_board = [[p.to_dict() if p else None for p in row] for row in game.board]
                serialized_land_board = [[p.to_dict() if p else None for p in row] for row in game.land_board]

                if success:
                    for other_ws in connected_users[game_id].values():
                        other_ws.send(json.dumps({
                            'type': 'update',
                            'board': serialized_board,
                            'land_board': serialized_land_board,
                            'turn': game.current_player,
                            'success': success,
                            'hand1': [c.to_dict() for c in game.hands['1']],
                            'hand2': [c.to_dict() for c in game.hands['2']],
                            'info': info,
                            'from': from_pos,
                            'mana': game.mana,
                            'graveyard': {
                                '1': [c.to_dict() for c in game.graveyard['1']],
                                '2': [c.to_dict() for c in game.graveyard['2']],
                            },
                            'deck_sizes': {
                                '1': len(game.decks['1']),
                                '2': len(game.decks['2']),
                            },
                            'to': to_pos,
                            'user_id': user_id,
                            'moves_left': game.max_moves_per_turn - game.moves_this_turn,
                            'center_tile_control': game.center_tile_control,
                            'usernames': user_assignments[game_id]

                        }))
                else:
                    # Only notify the user who tried the move
                    ws.send(json.dumps({
                        'type': 'update',
                        'board': serialized_board,
                        'land_board': serialized_land_board,
                        'turn': game.current_player,
                        'success': success,
                        'info': info,
                        'hand1': [c.to_dict() for c in game.hands['1']],
                        'hand2': [c.to_dict() for c in game.hands['2']],
                        'from': from_pos,
                        'to': to_pos,
                        'mana': game.mana,
                        'graveyard': {
                            '1': [c.to_dict() for c in game.graveyard['1']],
                            '2': [c.to_dict() for c in game.graveyard['2']],
                            },
                        'deck_sizes': {
                                '1': len(game.decks['1']),
                                '2': len(game.decks['2']),
                            },
                        'user_id': user_id,
                        'moves_left': game.max_moves_per_turn - game.moves_this_turn,
                        'center_tile_control': game.center_tile_control,
                    'usernames': user_assignments[game_id]

                    }))
            elif (data['type'] == 'end-turn') or (data['type'] == 'end-turn-with-discard'):
                if data['type'] == 'end-turn-with-discard':

                    discarded_card = game.hands[user_id].pop(data['slot'])
                    game.graveyard[user_id].append(discarded_card)

                if len(game.hands[user_id]) > 5:

                    for uid, ws_conn in connected_users[game_id].items():
                        ws_conn.send(json.dumps({
                            'type': 'discard-to-end-turn' if uid == user_id else 'opponent-discarding',
                            'board': [[p.to_dict() if p else None for p in row] for row in game.board],
                            'land_board': [[p.to_dict() if p else None for p in row] for row in game.land_board],
                            'hand1': [c.to_dict() for c in game.hands['1']],
                            'hand2': [c.to_dict() for c in game.hands['2']],
                            'graveyard': {
                                '1': [c.to_dict() for c in game.graveyard['1']],
                                '2': [c.to_dict() for c in game.graveyard['2']],
                            },
                            'deck_sizes': {
                                '1': len(game.decks['1']),
                                '2': len(game.decks['2']),
                            },
                            'turn': game.current_player,
                            'success': True,
                            'mana': game.mana,
                            'info': f"Discarding needed to end turn!",
                            'moves_left': game.max_moves_per_turn - game.moves_this_turn,
                            'center_tile_control': game.center_tile_control,
                    'usernames': user_assignments[game_id]

                        }))

                elif game.center_tile_control[user_id] >= 6:
                    # This player wins
                    for uid, ws_conn in connected_users[game_id].items():
                        ws_conn.send(json.dumps({
                            'type': 'game-over',
                            'board': [[p.to_dict() if p else None for p in row] for row in game.board],
                            'land_board': [[p.to_dict() if p else None for p in row] for row in game.land_board],
                            'hand1': [c.to_dict() for c in game.hands['1']],
                            'hand2': [c.to_dict() for c in game.hands['2']],
                            'graveyard': {
                                '1': [c.to_dict() for c in game.graveyard['1']],
                                '2': [c.to_dict() for c in game.graveyard['2']],
                            },
                            'deck_sizes': {
                                '1': len(game.decks['1']),
                                '2': len(game.decks['2']),
                            },
                            'turn': game.current_player,
                            'success': True,
                            'mana': game.mana,
                            'info': f"Player {user_id} has controlled the center for 6 turns!",
                            'moves_left': game.max_moves_per_turn - game.moves_this_turn,
                            'game_over': {
                                'result': 'victory' if uid == user_id else 'defeat'
                            },
                            'center_tile_control': game.center_tile_control,
                    'usernames': user_assignments[game_id]

                        }))

                elif user_id == game.current_player:
                    game.toggle_turn()
                    serialized_board = [[p.to_dict() if p else None for p in row] for row in game.board]
                    serialized_land_board = [[p.to_dict() if p else None for p in row] for row in game.land_board]

                    for other_ws in connected_users[game_id].values():
                        other_ws.send(json.dumps({
                            'type': 'update',
                            'board': serialized_board,
                            'land_board': serialized_land_board,
                            'mana': game.mana,
                            'hand1': [c.to_dict() for c in game.hands['1']],
                            'hand2': [c.to_dict() for c in game.hands['2']],
                            'graveyard': {
                                '1': [c.to_dict() for c in game.graveyard['1']],
                                '2': [c.to_dict() for c in game.graveyard['2']],
                            },
                            'deck_sizes': {
                                    '1': len(game.decks['1']),
                                    '2': len(game.decks['2']),
                                },
                            'turn': game.current_player,
                            'info': f"Player {user_id} ended their turn.",
                            'success': True,
                            'moves_left': game.max_moves_per_turn - game.moves_this_turn,
                            'center_tile_control': game.center_tile_control,
                    'usernames': user_assignments[game_id]

                        }))

            elif data['type'] == 'summon':
                slot = data['slot']
                to_pos = data['to']
                success, info = game.summon_card(slot, to_pos, user_id)
                serialized_board = [[p.to_dict() if p else None for p in row] for row in game.board]
                serialized_land_board = [[p.to_dict() if p else None for p in row] for row in game.land_board]


                if success:
                    for ws_conn in connected_users[game_id].values():
                        ws_conn.send(json.dumps({
                            'type': 'update',
                            'board': serialized_board,
                            'land_board': serialized_land_board,
                            'hand1': [c.to_dict() for c in game.hands['1']],
                            'hand2': [c.to_dict() for c in game.hands['2']],
                            'turn': game.current_player,
                            'success': success,
                            'graveyard': {
                                '1': [c.to_dict() for c in game.graveyard['1']],
                                '2': [c.to_dict() for c in game.graveyard['2']],
                            },
                            'deck_sizes': {
                                '1': len(game.decks['1']),
                                '2': len(game.decks['2']),
                            },
                            'info': info,
                            'to': to_pos,
                            'mana': game.mana,
                            'center_tile_control': game.center_tile_control,
                    'usernames': user_assignments[game_id]

                        }))
                else:
                    # Only notify the player who attempted the summon
                    connected_users[game_id][user_id].send(json.dumps({
                        'type': 'update',
                        'board': serialized_board,
                        'land_board': serialized_land_board,
                        'hand1': [c.to_dict() for c in game.hands['1']],
                        'hand2': [c.to_dict() for c in game.hands['2']],
                        'turn': game.current_player,
                        'success': success,
                        'graveyard': {
                            '1': [c.to_dict() for c in game.graveyard['1']],
                            '2': [c.to_dict() for c in game.graveyard['2']],
                        },
                        'deck_sizes': {
                            '1': len(game.decks['1']),
                            '2': len(game.decks['2']),
                        },
                        'info': info,
                        'to': to_pos,
                        'mana': game.mana,
                        'center_tile_control': game.center_tile_control,
                    'usernames': user_assignments[game_id]

                    }))

            elif data['type'] == 'direct-attack':
                pos = data['pos']
                success, info, game_over = game.direct_attack(pos, user_id)
                x, y = pos
                card = game.board[x][y]
                serialized_board = [[p.to_dict() if p else None for p in row] for row in game.board]
                serialized_land_board = [[p.to_dict() if p else None for p in row] for row in game.land_board]

                if game_over:
                    winner = user_id
                    loser = '1' if user_id == '2' else '2'
                    for uid, ws_conn in connected_users[game_id].items():
                        ws_conn.send(json.dumps({
                            'type': 'game-over',
                            'board': serialized_board,
                            'land_board': serialized_land_board,
                            'hand1': [c.to_dict() for c in game.hands['1']],
                            'hand2': [c.to_dict() for c in game.hands['2']],
                            'graveyard': {
                                '1': [c.to_dict() for c in game.graveyard['1']],
                                '2': [c.to_dict() for c in game.graveyard['2']],
                            },
                            'deck_sizes': {
                                '1': len(game.decks['1']),
                                '2': len(game.decks['2']),
                            },
                            'turn': game.current_player,
                            'success': True,
                            'mana': game.mana,
                            'info': info,
                            'moves_left': game.max_moves_per_turn - game.moves_this_turn,
                            'game_over': {
                                'result': 'victory' if uid == winner else 'defeat'
                            },
                            'center_tile_control': game.center_tile_control,
                    'usernames': user_assignments[game_id]

                        }))
                    return
                else:
                    for other_ws in connected_users[game_id].values():
                        other_ws.send(json.dumps({
                            'type': 'update',
                            'board': serialized_board,
                            'land_board': serialized_land_board,
                            'hand1': [c.to_dict() for c in game.hands['1']],
                            'hand2': [c.to_dict() for c in game.hands['2']],
                            'graveyard': {
                                '1': [c.to_dict() for c in game.graveyard['1']],
                                '2': [c.to_dict() for c in game.graveyard['2']],
                            },
                            'deck_sizes': {
                                        '1': len(game.decks['1']),
                                        '2': len(game.decks['2']),
                                    },
                            'turn': game.current_player,
                            'success': success,
                            'card': card.to_dict(),
                            'mana': game.mana,
                            'info': info,
                            'moves_left': game.max_moves_per_turn - game.moves_this_turn,
                            'center_tile_control': game.center_tile_control,
                    'usernames': user_assignments[game_id]

                        }))

            elif data['type'] == 'activate-sorcery':
                if not user_id:
                    continue  # or raise, or wait — don't access hands/cards yet

                slot = data['slot']
                target = data.get('pos')  # optional
                card = game.hands[user_id][slot]
                success, info = game.game_can_activate_card(slot, user_id, target)
                if not success:

                    serialized_board = [[p.to_dict() if p else None for p in row] for row in game.board]
                    serialized_land_board = [[p.to_dict() if p else None for p in row] for row in game.land_board]
                    # Only notify the user who tried the move
                    ws.send(json.dumps({
                        'type': 'update',
                        'board': serialized_board,
                        'land_board': serialized_land_board,
                        'hand1': [c.to_dict() for c in game.hands['1']],
                        'hand2': [c.to_dict() for c in game.hands['2']],
                        'turn': game.current_player,
                        'success': success,
                        'graveyard': {
                            '1': [c.to_dict() for c in game.graveyard['1']],
                            '2': [c.to_dict() for c in game.graveyard['2']],
                        },
                        'mana': game.mana,
                        'info': info,
                        'deck_sizes': {
                            '1': len(game.decks['1']),
                            '2': len(game.decks['2']),
                        },
                        'moves_left': game.max_moves_per_turn - game.moves_this_turn,
                        'center_tile_control': game.center_tile_control,
                        'usernames': user_assignments[game_id]

                    }))
                else:

                    if callable(getattr(card, "requires_additional_input", None)) and card.requires_additional_input():

                        # 👇 Regular activate logic
                        success, info = True, f'{card.name} activated'
                        valid_targets = card.get_valid_targets(game, user_id)
                        serialized_board = [[p.to_dict() if p else None for p in row] for row in game.board]
                        serialized_land_board = [[p.to_dict() if p else None for p in row] for row in game.land_board]


                        connected_users[game_id][user_id].send(json.dumps({
                                'type': 'awaiting-input',
                                'board': serialized_board,
                                'land_board': serialized_land_board,
                                'hand1': [c.to_dict() for c in game.hands['1']],
                                'hand2': [c.to_dict() for c in game.hands['2']],
                                'turn': game.current_player,
                                'slot': slot,
                                'success': success,
                                'valid_targets': valid_targets,
                                'card_id': card.card_id,
                                'graveyard': {
                                    '1': [c.to_dict() for c in game.graveyard['1']],
                                    '2': [c.to_dict() for c in game.graveyard['2']],
                                },
                                'mana': game.mana,
                                'info': info,
                                'deck_sizes': {
                                    '1': len(game.decks['1']),
                                    '2': len(game.decks['2']),
                                },
                                'moves_left': game.max_moves_per_turn - game.moves_this_turn,
                                'center_tile_control': game.center_tile_control,
                                'usernames': user_assignments[game_id]

                            }))


                    elif callable(getattr(card, "requires_deck_tutoring", None)) and card.requires_deck_tutoring():

                        # 👇 Regular activate logic
                        success, info = True, f'{card.name} activated'
                        valid_tutoring_targets = card.get_valid_tutoring_targets(game, user_id)
                        serialized_board = [[p.to_dict() if p else None for p in row] for row in game.board]
                        serialized_land_board = [[p.to_dict() if p else None for p in row] for row in game.land_board]


                        connected_users[game_id][user_id].send(json.dumps({
                                'type': 'awaiting-deck-tutoring',
                                'board': serialized_board,
                                'land_board': serialized_land_board,
                                'hand1': [c.to_dict() for c in game.hands['1']],
                                'hand2': [c.to_dict() for c in game.hands['2']],
                                'turn': game.current_player,
                                'slot': slot,
                                'success': success,
                                'valid_tutoring_targets': [c.to_dict() for c in valid_tutoring_targets],
                                'card_id': card.card_id,
                                'graveyard': {
                                    '1': [c.to_dict() for c in game.graveyard['1']],
                                    '2': [c.to_dict() for c in game.graveyard['2']],
                                },
                                'mana': game.mana,
                                'info': info,
                                'deck_sizes': {
                                    '1': len(game.decks['1']),
                                    '2': len(game.decks['2']),
                                },
                                'moves_left': game.max_moves_per_turn - game.moves_this_turn,
                                'center_tile_control': game.center_tile_control,
                                'usernames': user_assignments[game_id]

                            }))
                    else:
                        # 👇 Regular activate logic
                        success, info = game.activate_sorcery(slot, user_id, target)
                        serialized_board = [[p.to_dict() if p else None for p in row] for row in game.board]


                        for ws_conn in connected_users[game_id].values():
                            ws_conn.send(json.dumps({
                                'type': 'update',
                                'board': serialized_board,
                                'land_board': serialized_land_board,
                                'hand1': [c.to_dict() for c in game.hands['1']],
                                'hand2': [c.to_dict() for c in game.hands['2']],
                                'turn': game.current_player,
                                'success': success,
                                'graveyard': {
                                    '1': [c.to_dict() for c in game.graveyard['1']],
                                    '2': [c.to_dict() for c in game.graveyard['2']],
                                },
                                'mana': game.mana,
                                'info': info,
                                'deck_sizes': {
                                    '1': len(game.decks['1']),
                                    '2': len(game.decks['2']),
                                },
                                'moves_left': game.max_moves_per_turn - game.moves_this_turn,
                                'center_tile_control': game.center_tile_control,
                    'usernames': user_assignments[game_id]

                            }))

            elif data['type'] == 'resolve-sorcery':
                    slot = data['slot']
                    card = game.hands[user_id][slot]

                    if hasattr(card, "resolve_with_input"):
                        target = data['target']
                        # 👇 Try resolving first — don't remove card or spend mana yet
                        success, info = card.resolve_with_input(game, user_id, target)

                        if success:
                            game.hands[user_id].pop(slot)
                            game.graveyard[user_id].append(card)
                            game.mana[user_id] -= card.mana
                            game.sorcery_used_this_turn.add(user_id)

                        serialized_board = [[p.to_dict() if p else None for p in row] for row in game.board]
                        serialized_land_board = [[p.to_dict() if p else None for p in row] for row in game.land_board]

                        for ws_conn in connected_users[game_id].values():
                            ws_conn.send(json.dumps({
                                'type': 'update',
                                'board': serialized_board,
                                'land_board': serialized_land_board,
                                'hand1': [c.to_dict() for c in game.hands['1']],
                                'hand2': [c.to_dict() for c in game.hands['2']],
                                'turn': game.current_player,
                                'success': success,
                                'mana': game.mana,
                                'graveyard': {
                                    '1': [c.to_dict() for c in game.graveyard['1']],
                                    '2': [c.to_dict() for c in game.graveyard['2']],
                                },
                                'deck_sizes': {
                                    '1': len(game.decks['1']),
                                    '2': len(game.decks['2']),
                                },
                                'info': info,
                                'moves_left': game.max_moves_per_turn - game.moves_this_turn,
                                'center_tile_control': game.center_tile_control,
                                'usernames': user_assignments[game_id]

                            }))

                    elif hasattr(card, "resolve_with_tutoring_input"):
                        card_id = data['card_id']
                        # 👇 Try resolving first — don't remove card or spend mana yet
                        success, info = card.resolve_with_tutoring_input(card_id, game, user_id)

                        if success:
                            game.hands[user_id].pop(slot)
                            game.graveyard[user_id].append(card)
                            game.mana[user_id] -= card.mana
                            game.sorcery_used_this_turn.add(user_id)

                        serialized_board = [[p.to_dict() if p else None for p in row] for row in game.board]
                        serialized_land_board = [[p.to_dict() if p else None for p in row] for row in game.land_board]

                        for ws_conn in connected_users[game_id].values():
                            ws_conn.send(json.dumps({
                                'type': 'update',
                                'board': serialized_board,
                                'land_board': serialized_land_board,
                                'hand1': [c.to_dict() for c in game.hands['1']],
                                'hand2': [c.to_dict() for c in game.hands['2']],
                                'turn': game.current_player,
                                'success': success,
                                'mana': game.mana,
                                'graveyard': {
                                    '1': [c.to_dict() for c in game.graveyard['1']],
                                    '2': [c.to_dict() for c in game.graveyard['2']],
                                },
                                'deck_sizes': {
                                    '1': len(game.decks['1']),
                                    '2': len(game.decks['2']),
                                },
                                'info': info,
                                'moves_left': game.max_moves_per_turn - game.moves_this_turn,
                                'center_tile_control': game.center_tile_control,
                                'usernames': user_assignments[game_id]

                            }))


            elif data['type'] == 'place-land':
                if not user_id:
                    continue  # or raise, or wait — don't access hands/cards yet

                slot = data['slot']
                target = data.get('pos')  # optional
                card = game.hands[user_id][slot]

                # 👇 Regular placement logic
                success, info = game.game_can_place_land(slot, user_id, target)
                if not success:
                    serialized_board = [[p.to_dict() if p else None for p in row] for row in game.board]
                    serialized_land_board = [[p.to_dict() if p else None for p in row] for row in game.land_board]

                    # Only notify the user who tried the move
                    ws.send(json.dumps({
                        'type': 'update',
                        'board': serialized_board,
                        'land_board': serialized_land_board,
                        'hand1': [c.to_dict() for c in game.hands['1']],
                        'hand2': [c.to_dict() for c in game.hands['2']],
                        'turn': game.current_player,
                        'success': success,
                        'graveyard': {
                            '1': [c.to_dict() for c in game.graveyard['1']],
                            '2': [c.to_dict() for c in game.graveyard['2']],
                        },
                        'mana': game.mana,
                        'info': info,
                        'deck_sizes': {
                            '1': len(game.decks['1']),
                            '2': len(game.decks['2']),
                        },
                        'moves_left': game.max_moves_per_turn - game.moves_this_turn,
                        'center_tile_control': game.center_tile_control,
                    'usernames': user_assignments[game_id]

                    }))
                else:


                    success, info = game.place_land(slot, user_id, target)
                    serialized_board = [[p.to_dict() if p else None for p in row] for row in game.board]
                    serialized_land_board = [[p.to_dict() if p else None for p in row] for row in game.land_board]

                    for ws_conn in connected_users[game_id].values():
                        ws_conn.send(json.dumps({
                            'type': 'update',
                            'board': serialized_board,
                            'land_board': serialized_land_board,
                            'hand1': [c.to_dict() for c in game.hands['1']],
                            'hand2': [c.to_dict() for c in game.hands['2']],
                            'turn': game.current_player,
                            'success': success,
                            'graveyard': {
                                '1': [c.to_dict() for c in game.graveyard['1']],
                                '2': [c.to_dict() for c in game.graveyard['2']],
                            },
                            'mana': game.mana,
                            'info': info,
                            'deck_sizes': {
                                '1': len(game.decks['1']),
                                '2': len(game.decks['2']),
                            },
                            'moves_left': game.max_moves_per_turn - game.moves_this_turn,
                            'center_tile_control': game.center_tile_control,
                    'usernames': user_assignments[game_id]

                        }))

            elif data['type'] == 'resolve-land':
                    slot = data['slot']
                    target = data['target']
                    card = game.hands[user_id][slot]

                    if hasattr(card, "resolve_with_input"):
                        # 👇 Try resolving first — don't remove card or spend mana yet
                        success, info = card.resolve_with_input(game, user_id, target)

                        if success:
                            game.hands[user_id].pop(slot)
                            game.graveyard[user_id].append(card)
                            game.mana[user_id] -= card.mana

                        serialized_board = [[p.to_dict() if p else None for p in row] for row in game.board]
                        serialized_land_board = [[p.to_dict() if p else None for p in row] for row in game.land_board]
                        for ws_conn in connected_users[game_id].values():
                            ws_conn.send(json.dumps({
                                'type': 'update',
                                'board': serialized_board,
                                'land_board': serialized_land_board,
                                'hand1': [c.to_dict() for c in game.hands['1']],
                                'hand2': [c.to_dict() for c in game.hands['2']],
                                'turn': game.current_player,
                                'success': success,
                                'mana': game.mana,
                                'graveyard': {
                                    '1': [c.to_dict() for c in game.graveyard['1']],
                                    '2': [c.to_dict() for c in game.graveyard['2']],
                                },
                                'deck_sizes': {
                                    '1': len(game.decks['1']),
                                    '2': len(game.decks['2']),
                                },
                                'info': info,
                                'moves_left': game.max_moves_per_turn - game.moves_this_turn,
                                'center_tile_control': game.center_tile_control,
                    'usernames': user_assignments[game_id]


                            }))

    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        if user_id and user_id in connected_users[game_id]:
            del connected_users[game_id][user_id]


if __name__ == '__main__':
    app.run(debug=True)
