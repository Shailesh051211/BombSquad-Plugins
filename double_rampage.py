# ba_meta require api 9

"""
    by shailesh
    discord: shailesh_gabu_11/shailesh
    
    Adds Double Rampage map in the game with proper defs - 
        and railing(edge-protection) support
"""

from __future__ import annotations
from typing import override

import bascenev1 as bs
from bascenev1lib.maps import Rampage


class DoubleRampage(Rampage):
    """ Rampage with an extra ramp """
    class MapData:

        points = {}
        boxes = {}
        # All data are hand crafted
        # bound-box:
        #     first three is center position of box
        #     second three is rotation of box
        #     third three is size of box
        boxes["edge_box"] = (
            (0.291104, 5.537708, -6.157013)
            + (0.0, 0.0, 0.0)
            + (12.57718032, 4.645176013, 8.537109)
        )
        boxes["map_bounds"] = (
            (0.291104, 5.537708, -6.157013)
            + (0.0, 0.0, 0.0)
            + (23.54502348, 14.19991443, 18.12026172)
        )
        boxes["area_of_interest_bounds"] = (
            (0.291104, 5.537708, -6.157013)
            + (0.0, 0.0, 0.0)
            + (19.90053969, 10.34051135, 12.24331608)
        )

        points["tnt1"] = (0.245347, 5.534434, -6.374638)

        points["flag_default"] = (0.245347, 5.534434, -6.374638)
        points["flag1"] = (-5.276147, 5.529284, -9.561724)
        points["flag2"] = (5.817107, 5.531593, -3.048772)
        points["flag3"] = (5.883397, 5.515189, -9.649832)
        points["flag4"] = (-5.134181, 5.501352, -3.149968)

        # A box-area-spawn; first three center pos and others are sizes
        points["spawn1"] = (
            (-5.276147, 5.529284, -9.561724)
            + (0.9186962739, 1.0, 0.5153189341)
        )
        points["spawn2"] = (
            (5.817107, 5.531593, -3.048772)
            + (0.9186962739, 1.0, 0.5153189341)
        )
        points["spawn3"] = (
            (5.883397, 5.515189, -9.649832)
            + (0.9186962739, 1.0, 0.5153189341)
        )
        points["spawn4"] = (
            (-5.134181, 5.501352, -3.149968)
            + (0.9186962739, 1.0, 0.5153189341)
        )

        points["ffa_spawn1"] = (
            (0.278531, 5.523247, -3.797650)
            + (6.626174027, 1.0, 0.5153189341)
        )
        points["ffa_spawn2"] = (
            (-4.961596, 5.501921, -6.402463)
            + (0.917174027, 1.0, 4.0)
        )
        points["ffa_spawn3"] = (
            (0.367067, 5.512387, -9.689061)
            + (6.626174027, 1.0, 0.5153189341)
        )
        points["ffa_spawn4"] = (
            (5.985625, 5.522724, -6.366706)
            + (0.917174027, 1.0, 4.0)
        )

        points["powerup_spawn1"] = (0.278531, 5.523247, -3.797650)
        points["powerup_spawn2"] = (-4.961596, 5.501921, -6.402463)
        points["powerup_spawn3"] = (0.367067, 5.512387, -9.689061)
        points["powerup_spawn4"] = (5.985625, 5.522724, -6.366706)

        points["shadow_lower_bottom"] = (5.580073911, 3.136491026, 5.341226521)
        points["shadow_lower_top"] = (5.580073911, 4.321758709, 5.341226521)
        points["shadow_upper_bottom"] = (5.274539479, 8.425373402, 5.341226521)
        points["shadow_upper_top"] = (5.274539479, 11.93458162, 5.341226521)

    # base overrides
    defs = MapData
    name = "Double Rampage"

    @override
    @classmethod
    def get_play_types(cls) -> list[str]:
        """Return valid play types for this map."""
        return ["melee", "team_flag", "conquest", "keep_away"]

    def __init__(self):
        super().__init__()

        # second ramp
        self.node2 = bs.newnode(
            "terrain",
            delegate=self,
            attrs={
                "collision_mesh": self.node.collision_mesh,
                "mesh": self.node.mesh,
                "color_texture": self.node.color_texture,
                "materials": self.node.materials,
            },
        )
        self.node2.position = (0.0, 0.0, -4.4)

        # saving copy of railing materials before killin
        railing_mat = list(self.railing.materials)
        self.railing.delete()
        del self.railing
        """
        # debug drawing
        bs.newnode(
            "locator",
            attrs={
                "shape": "box",
                "position": (0.245347, 5.1, -2),
                "color": (0, 1, 0),
                "draw_beauty": True,
                "size": (15, 0.1, 0.0001),
                "additive": False
            }
        )
        """
        # crafting new railings
        self.railing1 = bs.newnode(
            "region",
            delegate=self,
            attrs={
                "type": "box",
                "position": (0.245347, 5.1, -2),
                "scale": (15, 0.1, 0.0001),
                "materials": railing_mat
            }
        )
        self.railing2 = bs.newnode(
            "region",
            delegate=self,
            attrs={
                "type": "box",
                "position": (0.245347, 5.1, -10.8),
                "scale": (15, 0.1, 0.0001),
                "materials": railing_mat
            }
        )

# ba_meta export babase.Plugin
class plg(bs.Plugin):
    """ Plugin type for the GAME """
    bs.register_map(DoubleRampage)
