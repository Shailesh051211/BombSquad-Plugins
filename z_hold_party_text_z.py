# ba_meta require api 9

"""
    by shailesh
    discord: shailesh_gabu_11/shailesh
    
    keeps text message of party window's text field.
"""

from __future__ import annotations 
from typing import cast

import bauiv1 as bui
from bauiv1lib import party
    
# ba_meta export babase.Plugin
class plg(bui.Plugin):
    """ Our plugin type for the game """
    
    text: str = "" # saved text
    
    def new_init(func):
        def wrapper(*args, **kwargs):
            _res = func(*args, **kwargs) # original code
            bui.textwidget(edit=args[0]._text_field, text=plg.text)
            return _res
        return wrapper
        
    party.PartyWindow.__init__ = new_init(party.PartyWindow.__init__)    

    def new_close(func):
        def wrapper(*args, **kwargs) -> None:
            plg.text = cast(str, bui.textwidget(query=args[0]._text_field)).strip()
            return func(*args, **kwargs) # original code
        return wrapper
        
    party.PartyWindow.close = new_close(party.PartyWindow.close)
