# ba_meta require api 9

"""
    by shailesh
    discord: shailesh_gabu_11/ShailesH
    
    Function:
        Allow to mute/unmute specific member.
    
    Logic:
    	- Create a separate mute/unmute button for all members.
        - whenever button activate, gather all info that member...
           And update mute state of that member and button accordingly.
        - then whenever a msg appear in chat, extract the chatter name.
        - if that chatter name in gathered info and the chatter is muted.
              don't show message
        - else
             show message
    
    Query:    
        Why is there 'z' at first and last in file name?
            first 'z' reason >
              because want to compile this file at last.  
              so this plugin can be compatible with other party window plugins.
            last 'z' reason >
              Nothing... for decoration purpose.
"""

from __future__ import annotations 

# Python Libraries.
import math

# Ballistica API.
import bauiv1 as bui
import bascenev1 as bs

# Ballistica Libraries.
from bauiv1lib.party import PartyWindow
from bascenev1lib.mainmenu import MainMenuActivity

# Umm....
from baclassic._appsubsystem import ClassicAppSubsystem


# Gonna use decorators to make this plugin compitibale with others.

# PartyWindow.on_chat_message
def new_ocm(func: function) -> function:
    
    def wrapper(*args, **kwargs) -> None:
        
        func(*args, **kwargs) # original 
        args[0]._update() # update instant.
        
    return wrapper
    
#----------------------------------------------------------------------------------------------------------------
# PartyWindow._update
def new_update(func: function) -> function:
    
    def wrapper(*args, **kwargs) -> None:
    
        # original code.
        func(*args, **kwargs)
        
        # clearing old.
        for widget in plg.widgets:
            widget.delete()
        plg.widgets = []
        
        if not args[0]._roster: return
        
        if not bui.app.config.resolve("Chat Muted"):
            for widget in args[0]._chat_texts:
                widget.delete()
            args[0]._chat_texts = []
        
            for msg in bs.get_chat_messages():
                name = msg[0:msg.rfind(':')]
                if plg.display_msg(name, args[0]._roster):
                    args[0]._add_msg(msg)
        
        # some eric code to find position.
        colmns = min(len(args[0]._roster), 3)
        rows = int(math.ceil(len(args[0]._roster) / colmns))
        c_width_total = args[0]._width * 0.9
        c_width = c_width_total / 3
        c_height = 24
        max_width = c_width * 0.85
        
        start_y = args[0]._height - 73
        start_x = args[0]._width * 0.53 - c_width_total * 0.5
        if colmns < 3:
            start_x += max_width / 2 + 13
        
        for y in range(rows):
            for x in range(colmns):
            
                index = y * colmns + x
                if index >= len(args[0]._roster):
                    break
                    
                client_name = args[0]._roster[index]["display_string"]
                if client_name == plg.our_display_name: # skip ourself.
                    continue
                
                players = args[0]._roster[index]["players"]
                if players:
                    plr_name = players[0]["name_full"]
                else:
                    plr_name = client_name
                # remove icon if it has.
                plr_name = plg.remove_private_use_chars(plr_name)
                    
                pos = (
                     start_x + c_width * x + max_width,
                     start_y - c_height * y
                )
                audio = bui.buttonwidget(
                    parent=args[0]._root_widget,
                    position=pos,
                    size=(17, 17),
                    label='',
                    color=(1, 1, 1),
                    texture=bui.gettexture("audioIcon"),
                    on_activate_call=(
                        bui.Call(
                            _on_press, 
                            client_name, plr_name, 
                            True, 
                            args[0],
                        )
                    ),
                )
                plg.widgets.append(audio)
                
                if plg.muted_clients.get(client_name, [False])[0]:
                    bui.buttonwidget(
                        edit=audio,
                        on_activate_call=(
                            bui.Call(
                                _on_press, 
                                client_name, plr_name, 
                                False, 
                                args[0],
                            )
                        ),
                    )
                    cross = bui.imagewidget(
                        parent=args[0]._root_widget,
                        position=(pos[0]+3, pos[1]+4),
                        size=(10, 10),
                        color=(1, 0, 0),
                        texture=bui.gettexture("crossOut"),
                    )
                    plg.widgets.append(cross)
                    if len(plr_name) > 10: 
                        plr_name = plr_name[:10] + '...'
                    if plr_name not in plg.muted_clients[client_name][1:]:
                        plg.muted_clients[client_name].append(plr_name)
                     
    return wrapper

def _on_press(
        client_name: str, 
        name: str, 
        mute: bool,
        party_window: PartyWindow
    ) -> None:
    """ Called to mute/unmute party members """
    
    client_names = plg.muted_clients.get(client_name, False)
    if not client_names:
        plg.muted_clients[client_name] = [mute, client_name]
    
    if mute:  
        plg.muted_clients[client_name][0] = True
        if len(name) > 10: 
            name = name[:10] + '...'
        if name not in plg.muted_clients[client_name]:
            plg.muted_clients[client_name].append(name)
    else:
        plg.muted_clients[client_name][0] = False
    
    if bui.app.config.resolve("Chat Muted"):
        cfg = bui.app.config
        cfg["Chat Muted"] = False
        cfg.apply_and_commit()
        party_window._display_old_msgs = True
        
    party_window._update() # update party

#----------------------------------------------------------------------------------------------------------------
# PartyWindow.popup_menu_selected_choice
def new_pmsc(func: function) -> function:
    
    def wrapper(*args, **kwargs) -> None:
        # original code.
        func(*args, **kwargs)
        
        is_menu = args[0]._popup_type == "menu"
        is_chat_update = "mute" in args[2]
        if is_menu and is_chat_update:
            roster = bs.get_game_roster()
            mute_state = bui.app.config.resolve("Chat Muted")
            for client in roster:
                display_str = client["display_string"]
                exists = plg.muted_clients.get(display_str, False)
                if exists:
                    plg.muted_clients[display_str][0] = mute_state
                else:
                    plg.muted_clients[display_str] = [mute_state, display_str]
  
            args[0]._update() # update party
            
    return wrapper

#----------------------------------------------------------------------------------------------------------------
# PartyWindow.close
def new_close(func: function) -> function:
    
    def wrapper(*args, **kwargs) -> None:
        # original code.
        func(*args, **kwargs)
        
        bs.apptimer(0.2, set_fake_party)
    
    return wrapper

def set_fake_party() -> None:

    classic = bs.app.classic
    classic.party_window = FakeParty() 

#----------------------------------------------------------------------------------------------------------------
# MainMenuActivity.__init__
def new_mm_init(func: function) -> function:
    
    def wrapper(*args, **kwargs) -> None:
        # original code.
        func(*args, **kwargs)
        
        if plg.our_display_name == '':
            # getting our self...
            plg.our_display_name = (
                bs.app.plus.get_v1_account_display_string()
            )
            set_fake_party()
 
    return wrapper

#----------------------------------------------------------------------------------------------------------------
# ClassicAppSubsystem.party_icon_activate
def new_party_press(func: function) -> function:
    
    def wrapper(*args, **kwargs) -> None:
        
        classic = bs.app.classic
        party_window = classic.party_window
        if isinstance(party_window, FakeParty):
            classic.party_window = None
        
        # original code.
        func(*args, **kwargs)
    
    return wrapper

#----------------------------------------------------------------------------------------------------------------
class FakeParty:
    """ Pretend to be fake while partywindow close... """
    def __init__(self) -> None:
         bui.set_party_window_open(True)
         
    def __call__(self) -> FakeParty:
        return self
    
    def on_chat_message(self, msg: str) -> None:
        """ ...So we can get msg when someone send message """
        name = msg[0:msg.rfind(':')]
        roster = bs.get_game_roster()
        if plg.display_msg(name, roster):
            bui.screenmessage(msg, color=(0.2, 0.5, 0.2)) 

# ba_meta export plugin
class plg(bui.Plugin):
    """ Our plugin type for the game """
    
    # The user display string.
    our_display_name: str = ""
    # contains clients info(names)
    muted_clients: dict[str, list] = {}
    # contains speaker type button and cross image widgets.
    widgets: list[bui.Widget] = []
    
    # wrapping...
    PartyWindow.close = new_close(PartyWindow.close)
    PartyWindow._update = new_update(PartyWindow._update)
    PartyWindow.on_chat_message = (
        new_ocm(PartyWindow.on_chat_message)
    )
    PartyWindow.popup_menu_selected_choice = (
        new_pmsc(PartyWindow.popup_menu_selected_choice)
    )
    
    MainMenuActivity.__init__ = new_mm_init(MainMenuActivity.__init__)
    ClassicAppSubsystem.party_icon_activate = (
        new_party_press(ClassicAppSubsystem.party_icon_activate)
    )
    
    def display_msg(name: str, roster: list) -> bool:
        """Called to check if given name is muted or not in plg.muted clients"""
        show_msg = True
        for client in roster:
            display_str = client["display_string"]
            client_names = plg.muted_clients.get(display_str, [False]) 
            if client_names[0] and name in client_names[1:]:
                show_msg = False
                break
                
        return show_msg
    
    def remove_private_use_chars(text: str) -> str:
        return "".join(c for c in text if not (0xE000 <= ord(c) <= 0xF8FF))
        
        