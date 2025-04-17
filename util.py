
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


