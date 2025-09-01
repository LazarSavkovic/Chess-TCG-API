from flask import Flask, render_template,  redirect
from flask_sock import Sock
import json
import uuid
from game import ChessGame
from flask_cors import CORS
import traceback, faulthandler
from flask import Flask, request, jsonify, abort
from models import db, User, Deck, DeckPile, DeckCard, PileType
from functools import wraps
import inspect
from cards import Monster, Land, Sorcery  # import your base classes
# Both gave choices & readied -> validate & start
from game import validate_deck_payload
from simple_websocket.errors import ConnectionClosed



faulthandler.enable()

app = Flask(__name__)
CORS(app)
sock = Sock(app)

# dev: SQLite; prod: set to your Postgres URL
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///dev.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)



# --- helpers ---------------------------------------------------------------

def _all_subclasses(cls):
    out = set()
    for sub in cls.__subclasses__():
        out.add(sub)
        out |= _all_subclasses(sub)
    return out

# keep only stable, catalog-y fields; strip instance id/owner
WANTED_FIELDS = {
    "card_id","type","name","role","mana","image","text","attack","defense",
    "activation_needs","creation_needs","movement"
}

def _slim(d: dict) -> dict:
    return {k: v for k, v in d.items() if k in WANTED_FIELDS}

# cache so we don’t rebuild every request (hot-reload clears this)
_CARD_CATALOG = None

def build_card_catalog():
    global _CARD_CATALOG
    if _CARD_CATALOG is not None:
        return _CARD_CATALOG

    catalog = []
    for base in (Monster, Land, Sorcery):
        for cls in sorted(_all_subclasses(base), key=lambda c: c.__name__):
            # Most of your cards only need owner
            try:
                inst = cls(owner="1")
            except TypeError:
                # If a special constructor appears, skip it (or handle here)
                continue
            d = inst.to_dict()
            d.pop("id", None)     # per-instance uuid
            d.pop("owner", None)  # not needed for catalog
            # prefer class attr name if to_dict omitted it
            if "name" not in d and getattr(cls, "name", None):
                d["name"] = cls.name
            catalog.append(_slim(d))

    _CARD_CATALOG = catalog
    return _CARD_CATALOG

# --- routes ----------------------------------------------------------------

@app.get("/api/cards")
def api_cards():
    """
    Optional filters:
      /api/cards?type=monster|sorcery|land&role=blue&q=search
    """
    print('heeeere')
    data = build_card_catalog()
    q_type = (request.args.get("type") or "").lower()
    q_role = (request.args.get("role") or "").lower()
    q      = (request.args.get("q") or "").lower()

    def ok(c):
        if q_type and (c.get("type","").lower() != q_type): return False
        if q_role and (c.get("role","").lower() != q_role): return False
        if q:
            hay = f"{c.get('name','')} {c.get('card_id','')} {c.get('text','')}".lower()
            if q not in hay: return False
        return True

    return jsonify([c for c in data if ok(c)])

@app.post("/api/cards/reload")
def api_cards_reload():
    """If you edit cards.py at runtime, call this to rebuild the cache."""
    global _CARD_CATALOG
    _CARD_CATALOG = None
    return jsonify({"ok": True, "reloaded": True})


# --- Auth: trust Clerk user id from a verified header or JWT middleware upstream ---
# For now, keep it simple: FE sends Clerk user id in a header after verifying with Clerk.
CLERK_HEADER = "X-Clerk-User-Id"

def require_user(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        clerk_user_id = request.headers.get(CLERK_HEADER)
        if not clerk_user_id:
            abort(401)
        user = User.query.filter_by(clerk_user_id=clerk_user_id).first()
        if not user:
            user = User(clerk_user_id=clerk_user_id)
            db.session.add(user)
            db.session.commit()
        request.user = user
        return f(*args, **kwargs)
    return wrapper

@app.route("/api/decks", methods=["GET"])
@require_user
def list_decks():
    decks = (Deck.query
             .filter_by(user_id=request.user.id)
             .order_by(Deck.created_at.desc())
             .all())
    return jsonify([{
        "id": str(d.id), "name": d.name, "description": d.description,
        "is_active": d.is_active, "created_at": d.created_at.isoformat()
    } for d in decks])

@app.route("/api/decks", methods=["POST"])
@require_user
def create_deck():
    data = request.get_json(force=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "name required"}), 400
    desc = data.get("description")

    deck = Deck(user_id=request.user.id, name=name, description=desc)
    db.session.add(deck)
    db.session.flush()  # get deck.id

    # Create default piles
    for p in (PileType.MAIN, PileType.LAND):
        db.session.add(DeckPile(deck_id=deck.id, pile_type=p))
    db.session.commit()

    return jsonify({"id": str(deck.id), "name": deck.name}), 201

@app.route("/api/decks/<deck_id>", methods=["GET"])
@require_user
def get_deck(deck_id):
    deck = Deck.query.filter_by(id=deck_id, user_id=request.user.id).first_or_404()
    piles = DeckPile.query.filter_by(deck_id=deck.id).all()
    result = {
        "id": str(deck.id),
        "name": deck.name,
        "description": deck.description,
        "is_active": deck.is_active,
        "piles": {}
    }
    for p in piles:
        cards = (DeckCard.query
                 .filter_by(pile_id=p.id)
                 .order_by(DeckCard.position.asc().nulls_last(), DeckCard.card_id.asc())
                 .all())
        result["piles"][p.pile_type.value] = [{"card_id": c.card_id, "qty": c.qty, "position": c.position} for c in cards]
    return jsonify(result)

@app.route("/api/decks/<deck_id>", methods=["PUT"])
@require_user
def update_deck(deck_id):
    deck = Deck.query.filter_by(id=deck_id, user_id=request.user.id).first_or_404()
    data = request.get_json(force=True) or {}
    if "name" in data: deck.name = data["name"].strip() or deck.name
    if "description" in data: deck.description = data["description"]
    if "is_active" in data:
        # make this the only active deck for the user if set true
        if data["is_active"]:
            Deck.query.filter(Deck.user_id==request.user.id, Deck.id!=deck.id).update({"is_active": False})
        deck.is_active = bool(data["is_active"])
    db.session.commit()
    return jsonify({"ok": True})

@app.route("/api/decks/<deck_id>/cards", methods=["POST"])
@require_user
def replace_pile_cards(deck_id):
    """
    Body:
    {
      "pile": "MAIN" | "LAND" | "SIDE",
      "cards": [{"card_id":"bonecrawler","qty":3,"position":null}, ...]
    }
    This REPLACES the pile contents (idempotent).
    """
    data = request.get_json(force=True) or {}
    pile_name = (data.get("pile") or "").upper()
    try:
        pile_type = PileType[pile_name]
    except Exception:
        return jsonify({"error":"invalid pile"}), 400

    deck = Deck.query.filter_by(id=deck_id, user_id=request.user.id).first_or_404()
    pile = DeckPile.query.filter_by(deck_id=deck.id, pile_type=pile_type).first()
    if not pile:
        pile = DeckPile(deck_id=deck.id, pile_type=pile_type)
        db.session.add(pile)
        db.session.flush()

    # wipe and replace
    DeckCard.query.filter_by(pile_id=pile.id).delete()
    cards = data.get("cards") or []
    for i, entry in enumerate(cards):
        cid = entry.get("card_id")
        qty = int(entry.get("qty", 1))
        pos = entry.get("position", i)
        if not cid or qty <= 0:
            continue
        db.session.add(DeckCard(pile_id=pile.id, card_id=cid, qty=qty, position=pos))

    db.session.commit()
    return jsonify({"ok": True})

@app.route("/api/decks/<deck_id>", methods=["DELETE"])
@require_user
def delete_deck(deck_id):
    deck = Deck.query.filter_by(id=deck_id, user_id=request.user.id).first_or_404()
    db.session.delete(deck)
    db.session.commit()
    return jsonify({"ok": True})



user_assignments = {}
connected_users = {}
games = {}
# app.py (game socket handler additions)

rooms = {}  # game_id -> {"phase": "lobby"|"playing", "choices": {"1": None, "2": None}, "ready": {"1": False, "2": False}}

def _room(game_id):
    if game_id not in rooms:
        rooms[game_id] = {
            "phase": "lobby",
            "choices": {'1': None, '2': None},   # stores uploaded payloads (or deck_ids)
            "ready": {'1': False, '2': False},
        }
    return rooms[game_id]

def _broadcast_lobby(game_id):
    r = _room(game_id)
    if r['phase'] != 'lobby':
        return
    game = games.get(game_id)
    extra = {
        'phase': r['phase'],
        'choices': {k: bool(v) for k, v in r['choices'].items()},
        'ready': r['ready'],
        'usernames': user_assignments.get(game_id, {}),
    }
    _broadcast(game_id, 'lobby', game, extra)

def _maybe_start_match(game_id, game):
    r = _room(game_id)
    if r["phase"] != "lobby":
        return
    if not (r["choices"]['1'] and r["choices"]['2']):
        return
    if not (r["ready"]['1'] and r["ready"]['2']):
        return



    ok1, msg1 = validate_deck_payload(r["choices"]['1'])
    ok2, msg2 = validate_deck_payload(r["choices"]['2'])
    if not ok1 or not ok2:
        # notify failures to specific users if you want; for now, broadcast
        _broadcast(game_id, "lobby_error", game, {
                      "message": f"Deck invalid: P1={msg1}, P2={msg2}"
                                   })
        return

    p1 = r["choices"]['1']["piles"]
    p2 = r["choices"]['2']["piles"]
    game.apply_decks_and_start(
        p1.get("MAIN", []), p1.get("LAND", []),
        p2.get("MAIN", []), p2.get("LAND", []),
    )

    r["phase"] = "playing"
    # Send initial full state with type 'init' like you already do
    _broadcast(game_id, 'init', game, {
        'usernames': user_assignments.get(game_id, {}),
        'message': 'Match started',
        'phase': 'playing',   # <-- add
    })


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
    conns = connected_users.get(game_id, {})
    dead = []
    for uid, ws_conn in list(conns.items()):
        try:
            _send(ws_conn, msg_type, game, extra)
        except Exception:
            dead.append(uid)
    for uid in dead:
        conns.pop(uid, None)


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
            try:
                message = ws.receive()
            except ConnectionClosed as cc:
                # Normal client disconnect (page change, StrictMode unmount, tab close, etc.)
                break


            if not message:
                break

            try:
                data = json.loads(message)
            except Exception:
                # Not JSON? Ignore this frame and keep waiting.
                try:
                    ws.send(json.dumps({'type': 'error', 'message': 'Expected JSON'}))
                except Exception:
                    pass
                continue

            if not user_id:
                # Ensure the connected_users map exists for this game.
                if game_id not in connected_users:
                    connected_users[game_id] = {}
                game_users = connected_users[game_id]

                # Get the username from the client (the client generated it if none existed)
                incoming_username = data.get('username')

                if not incoming_username:
                    # Ignore and wait for a proper identify packet; do NOT close the socket.
                    try:
                        ws.send(json.dumps({'type': 'error', 'message': 'Username is required'}))
                    except Exception:
                        pass
                    continue
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
                    'phase': _room(game_id)['phase'],  # 'lobby' on handshake
                })
                _broadcast_lobby(game_id)

            elif data['type'] == 'choose_deck':
                # Client sends an exported deck JSON payload directly:
                # { type:'choose_deck', deck: {version, name, piles:{MAIN, SIDE, LAND}} }
                r = _room(game_id)
                deck_payload = data.get('deck')
                if not deck_payload:
                    _send(ws, 'lobby_error', games[game_id], {"message": "Missing deck payload"})
                    continue
                r["choices"][user_id] = deck_payload
                r["ready"][user_id] = False  # reset ready on new choice
                print('')
                _broadcast_lobby(game_id)

            elif data['type'] == 'ready':
                r = _room(game_id)
                r["ready"][user_id] = True
                _broadcast_lobby(game_id)
                _maybe_start_match(game_id, game)


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
                            'card': card.to_dict(),
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
                            'pos': pos,
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
                            'card_id': card.card_id,
                            'pos': pos,
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
                        'card_id': card.card_id,
                        'pos': pos,
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
        # Full Python traceback (with line numbers)
        print("\n=== WebSocket exception ===")
        print("game_id:", game_id, "user_id:", user_id)
        print("Last received message:", locals().get("data", None))
        traceback.print_exc()
        # Optionally send to the client, so you see it in the browser console
        try:
            ws.send(json.dumps({
                "type": "server-error",
                "error": str(e),
                "traceback": traceback.format_exc(),
            }))
        except Exception:
            pass

    finally:
        if user_id and user_id in connected_users.get(game_id, {}):
            del connected_users[game_id][user_id]


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
