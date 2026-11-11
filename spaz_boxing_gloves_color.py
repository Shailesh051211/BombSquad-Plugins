# ba_meta require api 9

"""
    by shailesh
    discord: shailesh_gabu_11/shailesh
    version: 1.0.0

    tested in 1.8.7 bombsquad version

    Well, i was looking through the scripts
        and noticed some attrs that can change boxing-gloves color. lol

    So, Here it is...
    Changes the boxing-gloves color same as your in-game character(spaz) color.

    Made for fun. Not recommended, but your choice.
"""

from __future__ import annotations

import bascenev1 as bs
import bascenev1lib.actor.spaz as stdspaz

# ba_meta export babase.Plugin
class plg(bs.Plugin):

    def new_init(func):
        def wrapper(*args, **kwargs):

            func(*args, **kwargs) # original

            # set texture to white, so we can apply color accurately
            args[0].node.boxing_gloves_color_texture = bs.gettexture("white")

            r, g, b = args[0].node.color # spaz color

            # add little colors to avoid zero-division-error and also to avoid one-two side scale.
            r = r if r != 0.0 else 0.01
            g = g if g != 0.0 else 0.01
            b = b if b != 0.0 else 0.01

            # don't think so this time need relative-luminance, don't need perfect-accurate colors
            # avg ration of colors for equal distribution
            spaz_intensity = (r + g + b) / 3.0

            # dark-version of color look nice for boxing-gloves
            target_intensity = 0.22

            # logically shouldn't worry about ZeroDevisionError unless computer make mistake.
            scale = target_intensity / spaz_intensity
            scale = min(scale, 0.5 / max(r, g, b)) # scale reduction if possible

            # we only need to assign once, it'll keep until spaz node existence
            args[0].node.boxing_gloves_color = (r * scale, g * scale, b * scale)

        return wrapper

    stdspaz.Spaz.__init__ = new_init(stdspaz.Spaz.__init__)
