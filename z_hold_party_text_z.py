# ba_meta require api 9

"""
    by shailesh
    discord: shailesh_gabu_11/ShailesH
    
    Function:
        Holds text message of party window's text field.
"""

from __future__ import annotations 
from typing import cast

import bauiv1 as bui
from bauiv1lib.party import PartyWindow
    
# ba_meta export babase.Plugin
class plg(bui.Plugin):
    """ Our plugin type for the game """
    
    # The party window text field's text; that to be hold.
    text: str = ""
    def new_init(func: function) -> function:
        def wrapper(*args, **kwargs):
            func(*args, **kwargs) # original code
            bui.textwidget(edit=args[0]._text_field, text=plg.text)
        
        return wrapper
        
    PartyWindow.__init__ = new_init(PartyWindow.__init__)    

    def new_close(func):
        def wrapper(*args, **kwargs) -> None:
            
            plg.text = cast(str, bui.textwidget(query=args[0]._text_field)).strip()
            func(*args, **kwargs) # original code
            
        return wrapper
        
    PartyWindow.close = new_close(PartyWindow.close)
