
from card_types import Monster

def get_concrete_subclasses(cls):
    subclasses = cls.__subclasses__()
    if not subclasses:
        return [cls]
    result = []
    for subclass in subclasses:
        result.extend(get_concrete_subclasses(subclass))
    return result

import inspect
import cards

def get_playable_card_classes():
    from card_types import Card
    all_subclasses = get_concrete_subclasses(Card)
    return [cls for cls in all_subclasses if inspect.getmodule(cls) == cards]


from random import shuffle

def build_capped_deck(class_list, owner_id, deck_size, max_copies=3):
    # sanity check: is it even possible?
    if len(class_list) * max_copies < deck_size:
        raise ValueError(
            f"Not enough unique classes: need at least "
            f"{(deck_size + max_copies - 1)//max_copies} unique, got {len(class_list)}"
        )
    # create pool with at most max_copies of each class
    pool = [cls for cls in class_list for _ in range(max_copies)]
    shuffle(pool)
    chosen = pool[:deck_size]
    return [cls(owner_id) for cls in chosen]


