# ba_meta require api 9

"""
    by shailesh
    discord: shailesh_gabu_11/shailesh

    version: 1.0.0

    Changes the shield-color same as your in-game character color,
       with Adjustable shield-color brightness.

    I have set default shield-color-brightness that I think will look nice for all standard maps,
    But you can always change brightness if you think this is to bright or dull --
        -- in this-plugin-settings(settings> advance> plugins> this-plugin-settings-button)
    There is also a toggle which resets the shield color to defualt

    NOTE: overall map scene color affects the shield-color,
          so it might not visible in some custom maps or scene colors,
          but you can try different brightness for visibility i guess
"""

from __future__ import annotations
from typing import override

import bauiv1 as bui
import bascenev1 as bs
from bauiv1lib import popup
from bascenev1lib.actor import spaz as stdspaz


MAX_COLOR_RANGE = 1.8
CONFIG_KEY = "GS:shield_brightness"

# ba_meta export babase.Plugin
class plg(bs.Plugin):

    _use_defualt_shield_color = False
    _shield_brightness = bui.app.config.get(CONFIG_KEY, 0.44) # defualt = 0.44

    @override
    def has_settings_ui(self) -> bool:
        return True

    @override
    def show_settings_ui(self, origin_widget: bui.Widget) -> None:
        SettingsWindow(origin_widget=origin_widget)


    def new_equip_shields(func):
        def wrapper(*args, **kwargs):

            _res = func(*args, **kwargs) # original

            if plg._use_defualt_shield_color:
                return _res

            r, g, b = args[0].node.color # spaz color
            # add little colors if it's 0.0 to reduce one side scale
            r = r if r != 0.0 else 0.02
            b = b if b != 0.0 else 0.02
            g = g if g != 0.0 else 0.02

            # old standard luminance formula which tells approx-brightness
            spaz_luminance = 0.299*r + 0.587*g + 0.114*b

            # the target brightness that'll be set to the color
            # the higher the value, the brightter the color
            target_luminance = plg._shield_brightness

            if spaz_luminance <= 0.01: # filter black like colors that barely visible
                r = g = b = target_luminance # change it to white for visibility
            else:

                scale = target_luminance / spaz_luminance
                max_cl = max(r, g, b)
                scale = min(scale, MAX_COLOR_RANGE / max_cl) # reduce scale to not exceed 1.8

                # safe minimize, might loose colors for high scale
                r = min(r * scale, MAX_COLOR_RANGE)
                g = min(g * scale, MAX_COLOR_RANGE)
                b = min(b * scale, MAX_COLOR_RANGE)

            args[0].shield.color = (r, g, b)

            return _res
        return wrapper

    stdspaz.Spaz.equip_shields = new_equip_shields(stdspaz.Spaz.equip_shields)


class SettingsWindow(popup.PopupWindow):

    def __init__(self, origin_widget: bui.Widget):

        self._transitioning_out = False
        uiscale = bui.app.ui_v1.uiscale

        vs_width, vs_height = bui.get_virtual_screen_size()
        self._width = vs_width * 0.3
        self._height = self._width

        origin = origin_widget.get_screen_space_center()
        focus_position = (0.0, 0.0)
        if uiscale is not bui.UIScale.SMALL:
            focus_position = origin

        super().__init__(
            position=origin,
            size=(self._width, self._height),
            scale=(
                1.0 if uiscale is bui.UIScale.SMALL
                else 0.7 if uiscale is bui.UIScale.MEDIUM
                else 0.5
            ),
            focus_position=focus_position,
            bg_color=(0.40, 0.40, 0.55),
            darken_behind=False # Too Dark
        )

        # title
        bui.textwidget(
            parent=self.root_widget,
            position=(self._width * 0.5, self._height * 0.92),
            size=(0, 0),
            color=(0.8, 0.9, 1.0),
            text="Settings",
            h_align="center",
            v_align="center"
        )
        # close
        self._close_btn = bui.buttonwidget(
            parent=self.root_widget,
            position=(self._width * 0.1, self._height * 0.88),
            size=(30, 30),
            label=bui.SpecialChar.CLOSE.value,
            on_activate_call=self.on_popup_cancel,
            autoselect=True
        )
        bui.containerwidget(
            edit=self.root_widget, cancel_button=self._close_btn
        )
        # checkbox toggle
        bui.checkboxwidget(
            parent=self.root_widget,
            size=(self._width * 0.7, 40),
            position=(
                self._width/2 - (self._width*0.7)/2,
                self._height * 0.7
            ),
            text="use default shield color",
            value=plg._use_defualt_shield_color,
            on_value_change_call=self._set_shield_color_use,
        )
        # section line text
        bui.textwidget(
            parent=self.root_widget,
            position=(10, self._height * 0.67),
            size=(0, 0),
            scale=1.8,
            color=(0.5, 0.5, 0.7),
            text= '_' * 20,
            h_align="left",
            v_align="center"
        )
        # brightness_text
        self.brightness_text = bui.textwidget(
            parent=self.root_widget,
            position=(self._width * 0.2, self._height * 0.4),
            size=(0, 0),
            color=(1.0, 1.0, 1.0),
            text=f"shield brightness: {plg._shield_brightness * 100.0:.0f}%",
            h_align="left",
            v_align="center"
        )
        # slider
        self._slider = bui.sliderwidget(
            parent=self.root_widget,
            size=(self._width * 0.7, 40),
            position=(
                self._width/2 - (self._width*0.7)/2,
                self._height * 0.25
            ),
            value=plg._shield_brightness,
            min_value=0.40,
            max_value=1.50,
            increment=0.01,
            enabled=not plg._use_defualt_shield_color,
            on_drag_call=self._on_drag,
            on_change_call=self._on_drag_change
        )

    def _set_shield_color_use(self, value: bool) -> None:
        plg._use_defualt_shield_color = value
        bui.sliderwidget(edit=self._slider, enabled=not value)

    def _on_drag(self, value: float) -> None:
        bui.textwidget(
            edit=self.brightness_text,
            text=f"shield brightness: {value * 100.0:.0f}%"
        )

    def _on_drag_change(self, value: float) -> None:
        plg._shield_brightness = value

        bui.app.config[CONFIG_KEY] = value
        bui.app.config.commit()

        # let's change brightness if we're inside the game
        fg_activity = bs.get_foreground_host_activity()
        if isinstance(fg_activity, bs.GameActivity):
            for player in fg_activity.players:
                if not player.is_alive():
                    continue

                if (shield := player.actor.shield) is not None:

                    r, g, b = shield.color
                    curr_luminanace = 0.299*r + 0.587*g + 0.114*b

                    scale = plg._shield_brightness / curr_luminanace
                    scale = min(scale, MAX_COLOR_RANGE / max(r, g, b))

                    r = min(r * scale, MAX_COLOR_RANGE)
                    g = min(g * scale, MAX_COLOR_RANGE)
                    b = min(b * scale, MAX_COLOR_RANGE)

                    shield.color = (r, g, b)

    @override
    def on_popup_cancel(self) -> None:

        if not self.root_widget or self._transitioning_out:
            return

        if not self._transitioning_out:
            self._transitioning_out = True

        bui.getsound("swish").play()
        bui.containerwidget(edit=self.root_widget, transition="out_scale")
