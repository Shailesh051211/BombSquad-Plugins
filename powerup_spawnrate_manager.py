# ba_meta require api 9

"""
    By shailesh.
    discord: shailesh_gabu_11/shailesh

    This plugin allows you to increase or decrease \
             individual power-ups' weightage for spawn-rate via a simple UI.

    To use goto plugin window then press settings of this plugin
    or just type "/pmw" in chat

    inform me at discord if you find any errors/bugs
"""

from typing import override

import bauiv1 as bui
import bascenev1 as bs
import bascenev1lib as bslib

from bauiv1lib import popup

# unhealthy way to define :)
POWERUP_ID_NAME_TEX = [
    ["punch",        "Punch",        bui._classicassets.textures.powerup_punch],
    ["shield",       "Shield",       bui._classicassets.textures.powerup_shield],
    ["health",       "Health",       bui._classicassets.textures.powerup_health],
    ["curse",        "Curse",        bui._classicassets.textures.powerup_curse],
    ["triple_bombs", "Triple-Bombs", bui._classicassets.textures.powerup_bomb],
    ["ice_bombs",    "Ice-Bombs",    bui._classicassets.textures.powerup_ice_bombs],
    ["impact_bombs", "Impact-Bombs", bui._classicassets.textures.powerup_impact_bombs],
    ["sticky_bombs", "Sticky-Bombs", bui._classicassets.textures.powerup_sticky_bombs],
    ["land_mines",   "Land-Mines",   bui._classicassets.textures.powerup_land_mines],
]

class SettingsWindow(bui.MainWindow):
    """ Settings Window for our plugin """
    def __init__(
        self,
        transition: str | None = None,
        origin_widget: bui.Widget | None = None
    ):

        assert bui.app.classic is not None
        uiscale = bui.app.ui_v1.uiscale

        screen_width, screen_height = bui.get_virtual_screen_size()
        self.width = (
            screen_width * 0.9
            if uiscale is bui.UIScale.SMALL
            else screen_width * 0.7
            if uiscale is bui.UIScale.MEDIUM
            else screen_width * 0.6
        )
        self.height = (
            screen_height * 0.9
            if uiscale is bui.UIScale.LARGE
            else screen_height
        )
        super().__init__(
            root_widget=bui.containerwidget(
                size=(self.width, self.height),
                toolbar_visibility=(
                    "menu_minimal"
                    if uiscale is bui.UIScale.SMALL
                    else "menu_full"
                ),
                scale=(
                   1.2
                   if uiscale is bui.UIScale.SMALL
                   else 0.9 if uiscale is bui.UIScale.MEDIUM
                   else 0.8
                )
            ),
            transition=transition,
            origin_widget=origin_widget,
            refresh_on_screen_size_changes=True
        )

        self._covered_space = 0

        self.draw_head(uiscale)
        self.draw_body(uiscale)

    def draw_head(self, uiscale: bui.UIScale) -> None:

        btn_size = 60

        x_pad = 90 if uiscale is bui.UIScale.SMALL else 80
        y_pad = 125 if uiscale is bui.UIScale.SMALL else 80

        back_xpos = x_pad
        btn_ypos = self.height - y_pad
        if uiscale is bui.UIScale.SMALL:
            self._back_btn = None
            bui.containerwidget(
                edit=self._root_widget, on_cancel_call=self.main_window_back
            )
        else:
            self._back_btn = bui.buttonwidget(
                parent=self._root_widget,
                position=(back_xpos, btn_ypos),
                size=(btn_size, btn_size),
                button_type='backSmall',
                label=bui.SpecialChar.BACK.value,
                autoselect=True,
                on_activate_call=self.main_window_back,
            )
            bui.containerwidget(
                edit=self._root_widget, cancel_button=self._back_btn
            )

        menu_xpos = self.width * 0.8
        self._menu_btn = bui.buttonwidget(
            parent=self._root_widget,
            position=(menu_xpos, btn_ypos),
            size=(btn_size, btn_size),
            label="•••",
            button_type="square",
            color=(0.3, 0.8, 0.3),
            right_widget=self._back_btn,
            left_widget=self._back_btn
        )
        bui.buttonwidget(
            edit=self._menu_btn,
            on_activate_call=lambda: self._show_menu(self._menu_btn)
        )

        if self._back_btn:
            bui.buttonwidget(edit=self._back_btn, right_widget=self._menu_btn)

        # title text
        xoff = back_xpos + btn_size
        title_xpos = xoff + ((menu_xpos - xoff) / 2)
        title_ypos = btn_ypos + btn_size/2
        bui.textwidget(
        	parent=self._root_widget,
        	position=(title_xpos, title_ypos),
        	text="Powerup Spawn-rate Manager",
        	size=(0, 0),
            scale=(
                1.4
                if uiscale is bui.UIScale.SMALL
                else 1.2 if uiscale is bui.UIScale.MEDIUM
                else 1.0
            ),
        	color=bui.app.ui_v1.title_color,
        	h_align="center",
            v_align="center"
        )

        self._covered_space = self.height - btn_ypos

    def draw_body(self, uiscale: bui.UIScale) -> None:
        """ scroll container widget """

        remain_space = self.height - self._covered_space

        self._scrollwidth = (self.width * 0.9
            if uiscale is bui.UIScale.SMALL else self.width * 0.85)
        self._scrollheight = (remain_space * 0.9
            if uiscale is bui.UIScale.SMALL else remain_space * 0.85)

        ypad = 25 if uiscale is bui.UIScale.SMALL else 30

        _scroll_xpos = (self.width - self._scrollwidth)/2
        _scroll_ypos = (remain_space - self._scrollheight)/2 + ypad

        self._scrollwidget = bui.scrollwidget(
        	parent=self._root_widget,
        	position=(_scroll_xpos, _scroll_ypos),
        	size=(self._scrollwidth, self._scrollheight),
        	highlight=False,
        	simple_culling_v=20.0,
        	selection_loops_to_parent=True,
        	claims_left_right=True,
            border_opacity=0.4,
        )

        self._draw_subcontainer(uiscale)

    def _draw_subcontainer(self, uiscale: bui.UIScale) -> None:

        plus_btns, minus_btns = [], []
        self._dist_texts: dist[str, bui.Widget] = {}
        self._persent_texts: dict[str, bui.Widget] = {}
        total_distribution = plg._get_total_distribution()

        row_height = 180 if uiscale is bui.UIScale.SMALL else 160

        sub_height = row_height * len(plg._powerup_dist)
        self._subcontainer = bui.containerwidget(
            parent=self._scrollwidget,
            size=(self._scrollwidth, sub_height),
            background=False
        )

        xpad = 80 if uiscale is bui.UIScale.SMALL else 40
        ypad = 40

        img_size = row_height - ypad*2
        btn_size = img_size * 0.5
        center_off = row_height / 2

        ypos = sub_height - row_height
        # image, buttons, texts
        for pid, name, texture in POWERUP_ID_NAME_TEX:

            bui.imagewidget(
                parent=self._subcontainer,
                position=(xpad, ypos + ypad),
                size=(img_size, img_size),
                texture=texture.get()
            )

            bui.textwidget(
                parent=self._subcontainer,
                position=(xpad * 2 + img_size, ypos + center_off),
                size=(0, 0),
                text=name,
                scale=1.2,
                color=(0.8, 0.9, 1.0, 1.0),
                v_align="center"
            )

            powerup_dist = plg._powerup_dist[pid]
            self._dist_texts[pid] = bui.textwidget(
                parent=self._subcontainer,
                position=(self._scrollwidth * 0.68, ypos + center_off),
                size=(0, 0),
                text=str(powerup_dist),
                v_align="center"
            )

            minus_btns.append(
                bui.buttonwidget(
                    parent=self._subcontainer,
                    position=(
                       self._scrollwidth * 0.6,
                       ypos + center_off - btn_size/2
                    ),
                    size=(btn_size, btn_size),
                    color=(0.65, 0.2, 0.2),
                    label='-',
                    button_type="square",
                    repeat=True,
                    on_activate_call=bui.CallPartial(self._update_dist, pid, -1)
                )
            )
            plus_btns.append(
                bui.buttonwidget(
                    parent=self._subcontainer,
                    position=(
                        self._scrollwidth * 0.74,
                        ypos + center_off - btn_size/2
                    ),
                    size=(btn_size, btn_size),
                    color=(0.2, 0.65, 0.2),
                    label='+',
                    button_type="square",
                    repeat=True,
                    on_activate_call=bui.CallPartial(self._update_dist, pid, 1)
                )
            )

            persent = powerup_dist / total_distribution * 100.0
            self._persent_texts[pid] = (
                bui.textwidget(
                    parent=self._subcontainer,
                    position=(self._scrollwidth * 0.85, ypos + center_off),
                    size=(0, 0),
                    text=f"{persent:.2f}%",
                    color=(0.8, 0.8, 1.0, 0.8),
                    v_align="center"
                )
            )
            ypos -= row_height

        # button navigation for pc
        btnslen = len(plus_btns)
        for index in range(btnslen):
            # For minus
            up_widget = self._back_btn if index == 0 else minus_btns[index-1]
            left_widget = right_widget = plus_btns[index]
            down_widget = None if index == btnslen - 1 else minus_btns[index+1]
            bui.buttonwidget(
                edit=minus_btns[index],
                up_widget=up_widget, down_widget=down_widget,
                left_widget=left_widget, right_widget=right_widget
            )
            # For plus
            up_widget = self._menu_btn if index == 0 else plus_btns[index-1]
            left_widget = right_widget = minus_btns[index]
            down_widget = None if index == btnslen - 1 else plus_btns[index+1]
            bui.buttonwidget(
                edit=plus_btns[index],
                up_widget=up_widget, down_widget=down_widget,
                left_widget=left_widget, right_widget=right_widget
            )

    def _update_dist(self, powerup: str, value: int) -> None:

        num = plg._powerup_dist[powerup]
        if value == 1 and num == 99:
            return
        if value == -1 and num == 0:
            return

        num = plg._powerup_dist[powerup] = num + value
        bui.textwidget(edit=self._dist_texts[powerup], text=str(num))

        self._update_persent_texts()

    def _update_dist_texts(self) -> None:
        for powerup, widget in self._dist_texts.items():
            bui.textwidget(edit=widget, text=str(plg._powerup_dist[powerup]))

    def _update_persent_texts(self) -> None:
        total_distribution = plg._get_total_distribution()
        for powerup, widget in self._persent_texts.items():
            persent = plg._powerup_dist[powerup] / total_distribution * 100.0
            bui.textwidget(edit=widget, text=f"{persent:.2f}%")

    def _do_reset(self) -> None:
        plg._powerup_dist = dict(bs._powerup.get_default_powerup_distribution())
        self._update_dist_texts()
        self._update_persent_texts()

    def _do_nopower(self) -> None:
        for powerup in plg._powerup_dist.keys():
            plg._powerup_dist[powerup] = 0

        self._update_dist_texts()
        self._update_persent_texts()

    def _show_menu(self, widget: bui.Widget) -> None:

        uiscale = bui.app.ui_v1.uiscale
        popup.PopupMenuWindow(
            position=widget.get_screen_space_center(),
            choices=["Reset", "No-Powerup"],
            current_choice="Reset",
            scale=(
                2.3 if uiscale is bui.UIScale.SMALL
                else 1.65 if uiscale is bui.UIScale.MEDIUM
                else 1.23
            ),
            delegate=self
        )

    def popup_menu_selected_choice(
        self, popup_window: popup.PopupMenuWindow, choice: str
    ) -> None:
        if choice == "Reset":
            self._do_reset()
        elif choice == "No-Powerup":
            self._do_nopower()

    def popup_menu_closing(self, popup_window: popup.PopupMenuWindow) -> None:
        """ call when popup menu closing """

    @override
    def on_main_window_close(self) -> None:
        plg._update_ingame_powerup_dist()

    @override
    def main_window_should_preserve_selection(self) -> bool:
        return False

    @override
    def get_main_window_state(self):
        # Support recreating our window for back/refresh purposes.
        cls = type(self)
        return bui.BasicMainWindowState(
            create_call=lambda transition, origin_widget: cls(
                transition=transition, origin_widget=origin_widget
            )
        )

# ------  Actual Functionalities
def _new_pbxfact_init(func):
    def wrapper(*args, **kwargs) -> None:

        func(*args, **kwargs)

        plg._ingame_powerup_dist = args[0]._powerupdist # reference catch
        plg._update_ingame_powerup_dist()

    return wrapper

bslib.actor.powerupbox.PowerupBoxFactory.__init__ = (
    _new_pbxfact_init(bslib.actor.powerupbox.PowerupBoxFactory.__init__)
)

# breakin' curse-health cycle when health weight is 0
def _new_pbxfact_get_rand_powerup(func):
    def wrapper(*args, **kwargs):

        if args[0]._lastpoweruptype == "curse":
            if plg._powerup_dist["health"] == 0:
                args[0]._lastpoweruptype = None

        return func(*args, **kwargs)
    return wrapper

bslib.actor.powerupbox.PowerupBoxFactory.get_random_powerup_type = (
    _new_pbxfact_get_rand_powerup(
        bslib.actor.powerupbox.PowerupBoxFactory.get_random_powerup_type
    )
)

def _new_std_drop_powerup(func):
    def wrapper(*args, **kwargs):
        if plg._ingame_powerup_dist: # avoid when distribution is 0
            return func(*args, **kwargs)
    return wrapper

bs.TeamGameActivity._standard_drop_powerup = (
    _new_std_drop_powerup(bs.TeamGameActivity._standard_drop_powerup)
)

def _new_chatmessage(func):
    def wrapper(*args, **kwargs):

        fg_activity = bs.get_foreground_host_activity()
        if fg_activity and args[0].strip() == "/pmw":
            plg.set_settings_window(transition="in_scale")
            if bui.app.classic.party_window:
                bs.apptimer(0.1, bui.app.classic.party_window().close)

        return func(*args, **kwargs)
    return wrapper

bs.chatmessage = _new_chatmessage(bs.chatmessage)

# ba_meta export babase.Plugin
class plg(bs.Plugin):

    _powerup_dist = dict(bs._powerup.get_default_powerup_distribution())

    # inside minigame distribution reference list
    _ingame_powerup_dist: list[str] | None = None

    def _get_total_distribution() -> int:
        total = sum(plg._powerup_dist.values())
        return total if total else 1 # To avoid zero division error

    def _update_ingame_powerup_dist() -> None:
        if plg._ingame_powerup_dist is None:
            return

        fg_activity = bs.get_foreground_host_activity()
        if not isinstance(fg_activity, bs.TeamGameActivity):
            return

        plg._ingame_powerup_dist.clear()
        for powerup in plg._powerup_dist:
            plist = [powerup] * plg._powerup_dist[powerup]
            plg._ingame_powerup_dist.extend(plist)

    @override
    def has_settings_ui(self) -> bool:
        return True

    @override
    def show_settings_ui(self, source_widget: bui.Widget) -> None:

        plg.set_settings_window(None, source_widget)

    def set_settings_window(
        transition: str | None = None,
        source_widget: bui.Widget | None = None
    ) -> None:

        main_window = bui.app.ui_v1.get_main_window()
        if main_window is None:
            bui.app.ui_v1.set_main_window(
                SettingsWindow(transition=transition),
                back_state=None,
                is_top_level=True,
                suppress_warning=True
            )
            return

        if isinstance(main_window, SettingsWindow):
            return

        # no-op if we're not in control.
        if not main_window.main_window_has_control():
            return

        call = lambda: SettingsWindow(transition, source_widget)
        main_window.main_window_replace(call)
