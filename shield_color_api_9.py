# ba_meta require api 9

"""
    by shailesh_gabu_11/ShailesH
    
    Changes the shield-color same as your in-game character color.
""" 

import bascenev1 as bs
from bascenev1lib.actor.spaz import Spaz

# ba_meta export babase.Plugin
class plg(bs.Plugin):
    
    def new_equip_shield(func):
        def wrapper(*args, **kwargs):
            
            func(*args, **kwargs) # original code
            
            # make it 25% darker to reduce intensity of shield light
            r = args[0].node.color[0] * 0.75
            g = args[0].node.color[1] * 0.75
            b = args[0].node.color[2] * 0.75
            
            args[0].shield.color = (r, g, b)
        
        return wrapper
    
    Spaz.equip_shields = new_equip_shield(Spaz.equip_shields)