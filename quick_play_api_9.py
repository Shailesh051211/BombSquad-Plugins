# ba_meta require api 9

"""
    by shailesh
    discord: shailesh_gabu_11/ShailesH
    version: 1.0

    Allows You Play CustomMinigames(The minigame which made by modders). 
"""

# Python Standerd Libraries.
from __future__ import annotations 
from typing import TYPE_CHECKING, override
from dataclasses import dataclass
from copy import copy

# Ballistica API's.
import bascenev1 as bs
import bauiv1 as bui

# Ballistica Standerd Libraries.
from bauiv1lib import popup
from bascenev1lib import mainmenu
from bascenev1lib.activity.multiteamvictory import TeamSeriesVictoryScoreScreenActivity

if TYPE_CHECKING:
    from typing import Any

# ba_meta export plugin 
class plg(bs.Plugin):
    """ Our plugin type """

    @dataclass
    class Minigame:
        gametype: type[bs.GameActivity]
        supported_sessiontypes: list[type[bs.Session]]
        selected_sessiontype: type[bs.Session]

    # contains all custom minigames if found.
    custom_minigames: list[Minigame] = []
    # User starts the minigame using our UI or not?
    quick_play: bool = False
    # The user selected gametype and its settings.
    _game_spec: dict[str, Any] = {}

    _editwindow_back_state: bui.MainWindowState | None = None

    @override
    def on_app_running(self) -> None:
        """ Called when app reach run state. """

        # loadding exported "bascenev1.GameActivity" classses.
        bui.app.meta.load_exported_classes(
            bs.GameActivity, 
            plg._list_custom_gametypes, # It'll call provided function with loaded gametypes as list. 
            completion_cb_in_bg_thread=True,
        )
        
    @override
    def has_settings_ui(self) -> bool:
        """ Called to ask if we have settings. """
        return True # Yes! we have UI to show.
        
    @override
    def show_settings_ui(self, source_widget: bui.Widget | None) -> None:
        """ Called to show our settings UI. """
        
        # The current main window.
        main_window = bui.app.ui_v1.get_main_window()
        
        # no-op if we're not in control.
        if not main_window.main_window_has_control():
            return
        # replacing..
        main_window.main_window_replace(SettingsWindow(origin_widget=source_widget)) 
    
    def _list_custom_gametypes(gametypes: list[type[bs.GameActivity]]) -> None:
        """ Called to list custom/plugin's minigame from all exported gametypes. """
        
        sessiontypes = [
            bs.DualTeamSession, 
            bs.FreeForAllSession,
        ]
        for gametype in gametypes:
            # standerd/default gametypes are exported from "bascenev1lib/game/".
            # and custom gametypes are exported from "mods fold or workspace".  
            # Using that difference we can differ the standerd and custom gametypes.
            if not gametype.__module__.startswith("bascenev1lib"): 
                # incase we got same gametypes from mods and workspace.
                if any([
                    gametype.name.strip().lower() == mg.gametype.name.strip().lower() # hmm.. comparing names..
                    for mg in plg.custom_minigames]):
                    continue
                # Finding supported sessiontypes for minigame.
                supported_sessiontypes = [
                    sessiontype for sessiontype in sessiontypes
                    if gametype.supports_session_type(sessiontype)
                ]
                # incase got Coop or custom sessions.
                if not supported_sessiontypes: 
                    continue
                # At first selecting first session as defualt.
                selected_sessiontype = supported_sessiontypes[0]
                # Adding Minigame dataclass with upper info.
                plg.custom_minigames.append(
                    plg.Minigame(
                        gametype=gametype,
                        supported_sessiontypes=supported_sessiontypes,
                        selected_sessiontype=selected_sessiontype,
                    )
                )
                
    def _completion_call(
        minigame: plg.Minigame, 
        config: dict[str, Any], 
        from_window: bui.MainWindow
    ) -> None:
        """ Called when a user press back or play btn of PlaylistEditGameWindow emit from minigame 'play' btn. """

        # no-op if we're not in control.
        if not from_window.main_window_has_control():
            return
        
        assert plg._editwindow_back_state is not None
        from_window.main_window_back_state = plg._editwindow_back_state

        # If user press the back button, the confing will be empty.
        if not config:
            # head back the our SettingsWindow if they press back.
            from_window.main_window_back()
            plg._editwindow_back_state = None # reset.

        else: # Else They press the 'Play' Button.
            
            # close the winodow.
            from_window.main_window_close(transition="out_left")

            # When we'll come back from quick play want to set our window.
            # so let's save our window state.
            bui.app.classic.saved_ui_state = copy(plg._editwindow_back_state)
            plg._editwindow_back_state = None # reset.

            plg._game_spec["type"] = minigame.gametype
            plg._game_spec["settings"] = config["settings"].copy()

            # Attempt to host selected sessiontype..
            try:
                sessiontype = minigame.selected_sessiontype
                bs.new_host_session(sessiontype)
                plg.quick_play = True # set.
            except Exception:            
                # Else drop back into a main menu session.
                bs.new_host_session(mainmenu.MainMenuSession)


class SettingsWindow(bui.MainWindow):
    """ Settings Window for our plugin """

    def __init__(
        self,
        transition: str = "in_right",
        origin_widget: bui.Widget | None = None
    ) -> None:

        uiscale = bui.app.ui_v1.uiscale
        plg.quick_play = False # reset.
        
        # root.
        self.width = 850.0 if uiscale is bui.UIScale.SMALL else 700.0
        self.height = 550.0
        super().__init__(
            root_widget=bui.containerwidget(
                size=(self.width, self.height),
                toolbar_visibility=(
                    'menu_minimal'
                    if uiscale is bui.UIScale.SMALL
                    else 'menu_full'
                ),
                scale=(
                    1.15 if uiscale is bui.UIScale.MEDIUM
                    else 1.6 if uiscale is bui.UIScale.SMALL
                    else 1.0
                ),
            ),
            transition=transition,
            origin_widget=origin_widget
        ) 
        # The covered space info from up to down.
        # It will be helpful in ui drawing.
        self._covered_space: float = 0.0 
        
        # Elements drawing.
        self.draw_head(uiscale)
        self.draw_body(uiscale)
    
    def draw_head(self, uiscale: bui.UIScale) -> None:
    
        self._draw_head_btns(uiscale)
        self._draw_title_text(uiscale) 

    def _draw_head_btns(self, uiscale: bui.UIScale) -> None:
        """ back button UI """  

        x_pad = 90.0 if uiscale is bui.UIScale.SMALL else 50.0
        y_pad = 110.0 if uiscale is bui.UIScale.SMALL else 60.0
    
        x_pos = x_pad
        y_pos = self.height - y_pad 

        # if we're in mobile..
        if uiscale is bui.UIScale.SMALL:
            self._back_btn = None
            bui.containerwidget(
                edit=self._root_widget, on_cancel_call=self.main_window_back
            )
        else:
            btn_size = 40.0
            self._back_btn = bui.buttonwidget(
                parent=self._root_widget,
                position=(x_pos, y_pos),
                size=(btn_size, btn_size),
                button_type='backSmall',
                label=bui.charstr(bui.SpecialChar.BACK),
                autoselect=True,
                on_activate_call=self.main_window_back,
            )
            bui.containerwidget(
                edit=self._root_widget, cancel_button=self._back_btn
            )
        self._covered_space = self.height - y_pos 
    
    def _draw_title_text(self, uiscale: bui.UIScale) -> None:
        """ Title text UI """

        x_pos = self.width * 0.5
        y_pos = self.height - self._covered_space + 35.0 

        bui.textwidget(
        	parent=self._root_widget,
        	position=(x_pos, y_pos),
        	text=bui.Lstr(value="Minigames"),
        	size=(0, 0), # Doesn't need cursor activity..
        	color=(1.0, 1.0, 1.0, 0.7),
        	h_align="center", 
        )
        
    def draw_body(self, uiscale: bui.UIScale) -> None:  
        """ scroll widget """
        
        _remain_space = self.height - self._covered_space  

        _scrollwidth = (self.width * 0.75
            if uiscale is bui.UIScale.SMALL else self.width * 0.85)
        _scrollheight = (_remain_space * 0.75 
            if uiscale is bui.UIScale.SMALL else _remain_space * 0.85)

        ypad = 50.0 if uiscale is bui.UIScale.SMALL else 30.0

        _scroll_xpos = (self.width-_scrollwidth)/2
        _scroll_ypos = (_remain_space-_scrollheight)/2 + ypad

        self._scrollwidget = bui.scrollwidget(
        	parent=self._root_widget,
        	position=(_scroll_xpos, _scroll_ypos),
        	size=(_scrollwidth, _scrollheight),
        	highlight=False,
        	simple_culling_v=20.0,
        	selection_loops_to_parent=True,
        	claims_left_right=True
        )
        bui.widget(edit=self._scrollwidget, right_widget=self._scrollwidget)
        bui.containerwidget(
            edit=self._root_widget, selected_child=self._scrollwidget)  

        self._covered_space += _scrollheight

        if plg.custom_minigames:
            self._draw_scroll_body(_scrollwidth)
        else:
            # No minigames found text.
            bui.textwidget(
                parent=self._root_widget,
                size=(0.0, 0.0),
                position=(self.width/2, self.height/2),
                v_align="center",
                h_align="center",
                text=bui.Lstr(value="No minigames found!"),
                color=(0.6, 0.6, 0.6)
            )
            bui.containerwidget(
                edit=self._root_widget,
                selected_child=self._back_btn,
            )

    def _draw_scroll_body(self, sub_width: float) -> None:
        """ sub-container UI """

        line_height = 50.0
        sub_height = (len(plg.custom_minigames)+1) * line_height

        _scroll_container = bui.containerwidget(
        	parent=self._scrollwidget,
        	background=False,
        	size=(sub_width, sub_height),
        )   
       
        _height = line_height - 20.0
        _xpos = sub_width * 0.63
        _line_center = line_height/2 - _height/2

        top_y = sub_height - line_height
        for minigame in plg.custom_minigames:
            # minigame name text.
            gametext = bui.textwidget(
                parent=_scroll_container,
                position=(15.0, top_y-_line_center),
                size=(_xpos, _height),
                v_align="center",
                text=minigame.gametype.get_display_string(),
                maxwidth=_xpos,
                selectable=True,
                click_activate=True,
                autoselect=True,
            )
            bui.textwidget(
                edit=gametext,
                on_activate_call=bui.Call(self._show_game_desc, minigame, gametext),
            )
            # sessiontype button.
            sbtn = bui.buttonwidget(
                parent=_scroll_container,
                size=(100, _height),
                position=(_xpos, top_y-_line_center),
                label=bui.Lstr(
                    value=minigame.selected_sessiontype.__name__[:-7]),
                color=(0.6, 0.3, 0.1),
                autoselect=True,
            )
            bui.buttonwidget(
                edit=sbtn,
                on_activate_call=bui.Call(self._show_sessiontypes, minigame, sbtn),
            )
            # Play button.
            bui.buttonwidget(
                parent=_scroll_container,
                size=(70, _height),
                position=(_xpos+120, top_y-_line_center),
                label=bui.Lstr(resource="playText"),
                color=(0.0, 0.8, 0.4),
                autoselect=True,
                on_activate_call=bui.Call(self._show_edit_game, minigame),
            )
            top_y -= line_height

        children = _scroll_container.get_children()
        # keybaord navs.
        # left to right and right to left.
        for i in range(0, len(children), 3):
            bui.widget(
                edit=children[i],
                left_widget=children[i+2]
            )
            bui.widget(
                edit=children[i+2],
                right_widget=children[i]
            )
        # top to bottum and bottum to top.
        for i in range(-1, -4, -1):
            bui.widget(
                edit=children[i],
                down_widget=children[i+3]
            )
            bui.widget(
                edit=children[i+3],
                up_widget=children[i]
            )
        # Allow getting back to the back button.
        bui.widget(
            edit=children[0],
            up_widget=self._back_btn
        )
    
    def _show_game_desc(
        self, minigame: plg.Minigame, origin_text: bui.Widget
    ) -> None:
        """ Called to show mingame discription. """
        _ShowDiscriptionWindow(origin_text=origin_text, minigame=minigame)
            
    def _show_sessiontypes(
        self, minigame: plg.Minigame, btn: bui.buttonwidget
    ) -> None:
        """ Called to show/select minigame supported sessiontypes. """
        _PopupMenuWindow(origin_button=btn, minigame=minigame)
    
    def _show_edit_game(self, minigame: plg.Minigame) -> None:
        """ Called to show minigame edit options. """

        from bauiv1lib.playlist.editgame import PlaylistEditGameWindow

        # no-op if we don't have control.
        if not self.main_window_has_control():
            return

        window = PlaylistEditGameWindow(
            gametype=minigame.gametype,
            sessiontype=minigame.selected_sessiontype,
            config=None,
            completion_call=bui.Call(plg._completion_call, minigame)
        )

        self.main_window_replace(window)

        plg._editwindow_back_state = window.main_window_back_state
        # wnat to show 'play' text.
        bui.buttonwidget(
            edit=window._root_widget.get_children()[1],
            label=bui.Lstr(resource="playText")
        )
       
    @override
    def get_main_window_state(self) -> bui.MainWindowState:
        # Support recreating our window for back/refresh purposes.
        cls = type(self)
        return bui.BasicMainWindowState(
            create_call=lambda transition, origin_widget: cls(
                transition=transition, origin_widget=origin_widget
            )
        )


class _PopupMenuWindow(popup.PopupMenuWindow):
    """ PopupMenuWindow to show and select Available sessiontypes of a minigame. """

    def __init__(
        self,  
        origin_button: bui.widget,
        minigame: plg.Minigame
    ):
        self._origin_btn = origin_button
        self._minigame = minigame

        choices = [ 
            sessiontype.__name__.removesuffix("Session")
            for sessiontype in minigame.supported_sessiontypes 
        ]
        curr_choice = minigame.selected_sessiontype.__name__[:-7]
        
        super().__init__(
            position=origin_button.get_screen_space_center(), 
            choices=choices, 
            current_choice=curr_choice, 
            delegate=self
        )
        # Same color as button.
        bui.containerwidget(
            edit=self.root_widget,
            color=(0.6, 0.3, 0.1)
        )
    
    def popup_menu_selected_choice(
        self, popup_window: popup.PopupMenuWindow, choice: str
    ) -> None:
        """ Called when a choice is selected in the popup. """
        del popup_window  # unused

        minigame = self._minigame
        # No changes if new selection == old selection.
        if choice in minigame.selected_sessiontype.__name__:
            return
        # btn update.
        bui.buttonwidget(
            edit=self._origin_btn,
            label=bui.Lstr(value=choice)
        )
        # find selected sessiontype and update the selected sessiontype.
        for sessiontype in minigame.supported_sessiontypes:
            if choice in sessiontype.__name__:
                minigame.selected_sessiontype = sessiontype
                break

    def popup_menu_closing(self, popup_window: popup.PopupWindow) -> None:
        """ Called when the popup is closing."""


class _ShowDiscriptionWindow(popup.PopupWindow):
    """ PopupWindow to show Destription of a minigame. """

    def __init__(
        self, 
        origin_text: bui.widget,
        minigame: plg.Minigame
    ) -> None:

        gametype = minigame.gametype
        sessiontype = minigame.selected_sessiontype
        
        width = 450
        height = 120 + 20 * gametype.description.count('\n')

        super().__init__(
            position=(-120.0, origin_text.get_screen_space_center()[1]),
            size=(width, height) ,
            bg_color=(0.4, 0.4, 0.5),           
        )
        # description text.
        bui.textwidget(
            parent=self.root_widget,
            size=(0, 0),
            position=(width/2, height-5.0),
            text=bui.Lstr(value="Description"),
            h_align="center",
            color=(0.5, 1.0, 0.5)
        )
        # The 'description' provided by minigame's devloper, test.
        bui.textwidget(
            parent=self.root_widget,
            size=(0, 0),
            position=(width/2, height-50.0),
            maxwidth=width*0.9,
            text=gametype.get_description_display_string(sessiontype),
            h_align="center",
            color=(0.3, 1.0, 0.3),
        )
        # close button.
        btn_size = 30.0
        bui.buttonwidget(
            parent=self.root_widget,
            size=(btn_size, btn_size),
            position=(20.0, height-btn_size-13.0),
            texture=bui.gettexture("crossOut"),
            autoselect=True,
            on_activate_call=self.on_popup_cancel,
            label=""
        )

    @override
    def on_popup_cancel(self) -> None:
        """ Called when the popup is canceled. """
        bui.containerwidget(edit=self.root_widget, transition='out_scale')
        
#------------------------------------------------------------
# Want to change/add some code in orignal code.


# The 'bascenev1.MultiTeamSession.on_activity_end' function.
def _new_multisession_on_activity_end(func: function) -> function:
    """ Called when an session activity is ended. """
    def wrapper(*args, **kwrags) -> None:
       
        if plg.quick_play:
            # Aahaaaa! looks like session has been successfully hosted.
            if isinstance(args[1], bs.JoinActivity):
                # here we go....
                gametype = plg._game_spec["type"]
                game_settings = plg._game_spec["settings"].copy()
                game_activity = bs.newactivity(gametype, game_settings)
                
                # hmm... eric code.
                # (Re)register all players and wire stats to our next activity.
                for player in args[0].sessionplayers:
                    # ..but only ones who have been placed on a team
                    # (ie: no longer sitting in the lobby).
                    try:
                        has_team = player.sessionteam is not None
                    except bs.NotFoundError:
                        has_team = False
                    if has_team:
                        args[0].stats.register_sessionplayer(player)

                args[0].stats.setactivity(game_activity)
                # Now flip the current activity.
                args[0].setactivity(game_activity)
            
            elif isinstance(args[1], bs.TeamGameActivity):
                # Single game single length.
                args[0]._series_length = int(1)
                args[0]._ffa_series_length = int(1)

                winner = args[2].winnergroups[0].teams[0]
                winner.customdata["score"] += 1
                        
                # for our quick play we only need to play a single game.
                # So let's head to final score screen activity when game ends.
                args[0].setactivity(
                    bs.newactivity(
                        TeamSeriesVictoryScoreScreenActivity,
                        {'winner': winner},
                    )
                )
            
            elif isinstance(args[1], TeamSeriesVictoryScoreScreenActivity):
                args[0].end() # End the sesion.
        else:
            # orignal code.
            func(*args, **kwrags)

    return wrapper

# wrapping...
bs.MultiTeamSession.on_activity_end = (
    _new_multisession_on_activity_end(bs.MultiTeamSession.on_activity_end)
)

# The 'bascenev1lib.activity.multiteamvictory.TeamSeriesVictoryScoreScreenActivity._show_winner' function.
# Wanna show "'Player/Team' WINS THE GAME!" instead of "'Player/Team' WINS THE SERIES!" text.
# also Wanna show "Press any button to exit.." instead of "Press any button to play again..." text.
def _new_tsvssa_show_winner(func: function) -> function:
    """ Called to show our team or player winner of the game. """
    def wrapper(*args, **kwrags) -> None:
        
        # orignal code.
        func(*args, **kwrags)

        if plg.quick_play:
            from bascenev1lib.actor.zoomtext import ZoomText
            from bascenev1lib.actor.text import Text
            # _FIXME: Try to find other efficient and accurate way.. if there is. 
            try:
                nodes = bs.getnodes()
                zoomtexts = [
                    node.getdelegate(ZoomText) for node in nodes
                    if node.getdelegate(ZoomText) is not None
                ]
                # prob: for other languages?
                zoomtexts[-1].node.text = "GAME!"

                texts = [
                    node.getdelegate(Text) for node in nodes
                    if node.getdelegate(Text) is not None
                ]
                texts[0].node.text = "Press any button to exit..."
            except Exception:
                pass
            
    return wrapper

# wrapping...
TeamSeriesVictoryScoreScreenActivity._show_winner = (
    _new_tsvssa_show_winner(TeamSeriesVictoryScoreScreenActivity._show_winner)
)

# _FIXME: For QuickPlay don't need to run playlist selection code.
