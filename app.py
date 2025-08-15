from flask import Flask, render_template,  redirect
from flask_sock import Sock
import json
import uuid
from game import ChessGame
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
sock = Sock(app)

user_assignments = {}
connected_users = {}
games = {}

# ---------- Helpers (no behavior change) ----------

def _ser_board(game):
    return [[p.to_dict() if p else None for p in row] for row in game.board]

def _ser_land_board(game):
    return [[p.to_dict() if p else None for p in row] for row in game.land_board]

def _ser_hand(game, pid):
    return [c.to_dict() for c in game.hands[pid]]

def _ser_graveyard(game):
    return {
        '1': [c.to_dict() for c in game.graveyard['1']],
        '2': [c.to_dict() for c in game.graveyard['2']],
    }

def _ser_land_decks(game):
    return {
        '1': [c.to_dict() for c in game.land_decks['1']],
        '2': [c.to_dict() for c in game.land_decks['2']],
    }

def _deck_sizes(game):
    return {
        '1': len(game.decks['1']),
        '2': len(game.decks['2']),
    }

def _actions_this_turn(game):
    return {
        '1': {
            'summoned': '1' in game.summoned_this_turn,
            'sorcery_used': '1' in game.sorcery_used_this_turn,
            'land_placed': '1' in game.land_placed_this_turn,
        },
        '2': {
            'summoned': '2' in game.summoned_this_turn,
            'sorcery_used': '2' in game.sorcery_used_this_turn,
            'land_placed': '2' in game.land_placed_this_turn,
        },
        # Optional: perspective-friendly flags
        'current': {
            'summoned': game.current_player in game.summoned_this_turn,
            'sorcery_used': game.current_player in game.sorcery_used_this_turn,
            'land_placed': game.current_player in game.land_placed_this_turn,
        }
    }

def _base_state(game):
    # Matches what you were sending everywhere
    return {
        'board': _ser_board(game),
        'land_board': _ser_land_board(game),
        'hand1': _ser_hand(game, '1'),
        'hand2': _ser_hand(game, '2'),
        'turn': game.current_player,
        'mana': game.mana,
        'graveyard': _ser_graveyard(game),
        'land_decks': _ser_land_decks(game),
        'deck_sizes': _deck_sizes(game),
        'center_tile_control': game.center_tile_control,
        'actions_this_turn': _actions_this_turn(game),  # ← add this
    }

def _send(ws, msg_type, game, extra=None):
    payload = {'type': msg_type, **_base_state(game)}
    if extra: payload.update(extra)
    ws.send(json.dumps(payload))

def _broadcast(game_id, msg_type, game, extra=None):
    for ws_conn in connected_users.get(game_id, {}).values():
        _send(ws_conn, msg_type, game, extra)

def _broadcast_per_viewer(game_id, builder):
    """builder(uid, game)->(msg_type, extra_dict) so you can vary 'type' per-recipient."""
    conns = connected_users.get(game_id, {})
    game = games[game_id]
    for uid, ws_conn in conns.items():
        msg_type, extra = builder(uid, game)
        _send(ws_conn, msg_type, game, extra)


@app.route('/')
def index():
    return "Welcome to Chess TCG API"

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

                # Send initial board + hands (same fields as before)
                _send(ws, 'init', game, {
                    'username': incoming_username,
                    'user_id': user_id,
                    'user_assignments': user_assignments[game_id],
                })

            elif data['type'] == 'move':
                from_pos = data['from']
                to_pos = data['to']
                success, info = game.move(from_pos, to_pos, user_id)

                if success:
                    _broadcast(game_id, 'update', game, {
                        'success': success,
                        'info': info,
                        'from': from_pos,
                        'to': to_pos,
                        'user_id': user_id,
                        'moves_left': game.max_moves_per_turn - game.moves_this_turn,
                        'usernames': user_assignments[game_id],
                    })
                else:
                    # Only notify the user who tried the move
                    _send(ws, 'update', game, {
                        'success': success,
                        'info': info,
                        'from': from_pos,
                        'to': to_pos,
                        'user_id': user_id,
                        'moves_left': game.max_moves_per_turn - game.moves_this_turn,
                        'usernames': user_assignments[game_id],
                    })

            elif (data['type'] == 'end-turn') or (data['type'] == 'end-turn-with-discard'):
                if data['type'] == 'end-turn-with-discard':
                    discarded_card = game.hands[user_id].pop(data['slot'])
                    game.graveyard[user_id].append(discarded_card)

                if len(game.hands[user_id]) > 5:
                    # Same as before: actor gets 'discard-to-end-turn', opponent gets 'opponent-discarding'
                    def builder(uid, game_):
                        msg_type = 'discard-to-end-turn' if uid == user_id else 'opponent-discarding'
                        extra = {
                            'success': True,
                            'mana': game_.mana,
                            'info': "Discarding needed to end turn!",
                            'moves_left': game_.max_moves_per_turn - game_.moves_this_turn,
                            'usernames': user_assignments[game_id],
                        }
                        return msg_type, extra
                    _broadcast_per_viewer(game_id, builder)

                # elif game.center_tile_control[user_id] >= 7:
                #     # This player wins (same payload fields as before)
                #     def builder(uid, game_):
                #         extra = {
                #             'success': True,
                #             'mana': game_.mana,
                #             'info': f"Player {user_id} has controlled the center for 6 turns!",
                #             'moves_left': game_.max_moves_per_turn - game_.moves_this_turn,
                #             'game_over': {
                #                 'result': 'victory' if uid == user_id else 'defeat'
                #             },
                #             'usernames': user_assignments[game_id],
                #         }
                #         return 'game-over', extra
                #     _broadcast_per_viewer(game_id, builder)

                elif user_id == game.current_player:
                    game.toggle_turn()
                    _broadcast(game_id, 'update', game, {
                        'mana': game.mana,
                        'info': f"Player {user_id} ended their turn.",
                        'success': True,
                        'moves_left': game.max_moves_per_turn - game.moves_this_turn,
                        'usernames': user_assignments[game_id],
                    })

            elif data['type'] == 'summon':
                slot = data['slot']
                to_pos = data['to']
                success, info = game.summon_card(slot, to_pos, user_id)

                if success:
                    _broadcast(game_id, 'update', game, {
                        'success': success,
                        'info': info,
                        'to': to_pos,
                        'mana': game.mana,
                        'center_tile_control': game.center_tile_control,
                        'usernames': user_assignments[game_id],
                    })
                else:
                    # Only notify the player who attempted the summon
                    _send(connected_users[game_id][user_id], 'update', game, {
                        'success': success,
                        'info': info,
                        'to': to_pos,
                        'mana': game.mana,
                        'center_tile_control': game.center_tile_control,
                        'usernames': user_assignments[game_id],
                    })

            elif data['type'] == 'direct-attack':
                pos = data['pos']
                success, info, game_over = game.direct_attack(pos, user_id)
                x, y = pos
                card = game.board[x][y]  # same as before

                if game_over:
                    winner = user_id
                    def builder(uid, game_):
                        extra = {
                            'success': True,
                            'mana': game_.mana,
                            'info': info,
                            'moves_left': game_.max_moves_per_turn - game_.moves_this_turn,
                            'game_over': {
                                'result': 'victory' if uid == winner else 'defeat'
                            },
                            'usernames': user_assignments[game_id],
                        }
                        return 'game-over', extra
                    _broadcast_per_viewer(game_id, builder)
                    return
                else:
                    _broadcast(game_id, 'update', game, {
                        'success': success,
                        'card': card.to_dict() if card else None,
                        'mana': game.mana,
                        'info': info,
                        'moves_left': game.max_moves_per_turn - game.moves_this_turn,
                        'usernames': user_assignments[game_id],
                    })

            elif data['type'] == 'activate-sorcery':
                if not user_id:
                    continue  # or raise, or wait — don't access hands/cards yet

                slot = data['slot']
                pos = data.get('pos')  # optional
                card = game.hands[user_id][slot]
                success, info, is_free = game.game_can_activate_card(slot, user_id, pos)
                print(data)

                if not success:
                    # Only notify the user who tried the move
                    _send(ws, 'update', game, {
                        'success': success,
                        'pos': pos,
                        'mana': game.mana,
                        'info': info,
                        'moves_left': game.max_moves_per_turn - game.moves_this_turn,
                        'usernames': user_assignments[game_id],
                    })
                else:
                    if callable(getattr(card, "requires_additional_input", None)) and card.requires_additional_input():
                        valid_targets = card.get_valid_targets(game, user_id)
                        _send(connected_users[game_id][user_id], 'awaiting-input', game, {
                            'slot': slot,
                            'success': True,
                            'valid_targets': valid_targets,
                            'card_id': card.card_id,
                            'pos': pos,
                            'mana': game.mana,
                            'info': f'{card.name} activated',
                            'moves_left': game.moves_this_turn and (game.max_moves_per_turn - game.moves_this_turn) or game.max_moves_per_turn,
                            'usernames': user_assignments[game_id],
                        })
                    elif callable(getattr(card, "requires_deck_tutoring", None)) and card.requires_deck_tutoring():
                        valid_tutoring_targets = card.get_valid_tutoring_targets(game, user_id)
                        _send(connected_users[game_id][user_id], 'awaiting-deck-tutoring', game, {
                            'slot': slot,
                            'success': True,
                            'valid_tutoring_targets': [c.to_dict() for c in valid_tutoring_targets],
                            'card_id': card.card_id,
                            'mana': game.mana,
                            'info': f'{card.name} activated',
                            'moves_left': game.max_moves_per_turn - game.moves_this_turn,
                            'usernames': user_assignments[game_id],
                        })
                    else:
                        # Regular activate logic
                        success, info = game.activate_sorcery(slot, user_id, pos, reduce_mana=not is_free)
                        _broadcast(game_id, 'update', game, {
                            'success': success,
                            'mana': game.mana,
                            'info': info,
                            'moves_left': game.max_moves_per_turn - game.moves_this_turn,
                            'usernames': user_assignments[game_id],
                        })

            elif data['type'] == 'resolve-sorcery':
                slot = data['slot']
                card = game.hands[user_id][slot]
                pos = data.get('pos')  # optional
                success, info, is_free = game.game_can_activate_card(slot, user_id, pos)
                print(is_free, "is free")

                if hasattr(card, "resolve_with_input"):
                    target = data['target']
                    # Try resolving first — don't remove card or spend mana yet
                    success, info = card.resolve_with_input(game, user_id, target)
                    if success:
                        game.hands[user_id].pop(slot)
                        game.graveyard[user_id].append(card)
                        if not is_free:
                            game.mana[user_id] -= card.mana
                        game.sorcery_used_this_turn.add(user_id)

                    _broadcast(game_id, 'update', game, {
                        'success': success,
                        'mana': game.mana,
                        'info': info,
                        'moves_left': game.max_moves_per_turn - game.moves_this_turn,
                        'usernames': user_assignments[game_id],
                    })

                elif hasattr(card, "resolve_with_tutoring_input"):
                    card_id = data['card_id']
                    # Try resolving first — don't remove card or spend mana yet
                    success, info = card.resolve_with_tutoring_input(card_id, game, user_id)
                    if success:
                        game.hands[user_id].pop(slot)
                        game.graveyard[user_id].append(card)
                        game.mana[user_id] -= card.mana
                        game.sorcery_used_this_turn.add(user_id)

                    _broadcast(game_id, 'update', game, {
                        'success': success,
                        'mana': game.mana,
                        'info': info,
                        'moves_left': game.max_moves_per_turn - game.moves_this_turn,
                        'usernames': user_assignments[game_id],
                    })

            elif data['type'] == 'place-land':
                print(data)
                if not user_id:
                    continue  # or raise, or wait — don't access hands/cards yet

                slot = data['slot']
                pos = data.get('pos')  # optional

                # Regular placement logic
                success, info, is_free = game.game_can_place_land(slot, user_id, pos)
                if not success:
                    # Only notify the user who tried the move
                    _send(ws, 'update', game, {
                        'success': success,
                        'mana': game.mana,
                        'info': info,
                        'pos': pos,
                        'moves_left': game.max_moves_per_turn - game.moves_this_turn,
                        'usernames': user_assignments[game_id],
                    })
                else:
                    success, info = game.place_land(slot, user_id, pos, reduce_mana=not is_free)
                    _broadcast(game_id, 'update', game, {
                        'success': success,
                        'pos': pos,
                        'mana': game.mana,
                        'info': info,
                        'moves_left': game.max_moves_per_turn - game.moves_this_turn,
                        'usernames': user_assignments[game_id],
                    })

            elif data['type'] == 'resolve-land':
                slot = data['slot']
                target = data['target']
                card = game.hands[user_id][slot]

                success, info, is_free = game.game_can_place_land(slot, user_id, target)

                if hasattr(card, "resolve_with_input"):
                    # Try resolving first — don't remove card or spend mana yet
                    success, info = card.resolve_with_input(game, user_id, target)
                    if success:
                        game.hands[user_id].pop(slot)
                        game.graveyard[user_id].append(card)
                        if not is_free:
                            game.mana[user_id] -= card.mana

                    _broadcast(game_id, 'update', game, {
                        'success': success,
                        'mana': game.mana,
                        'info': info,
                        'moves_left': game.max_moves_per_turn - game.moves_this_turn,
                        'usernames': user_assignments[game_id],
                    })

    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        if user_id and user_id in connected_users[game_id]:
            del connected_users[game_id][user_id]


if __name__ == '__main__':
    app.run(debug=True)
