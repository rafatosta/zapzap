
SettingsMenu = """
#leftMenu
{	
    background-color: {window};
}
#menu .QPushButton {
    color: {windowText};
    background-position: left center;
    background-repeat: no-repeat;
    text-align: left;
    border: 8px solid {window};
    font: 12pt;
    height: 30px;
    qproperty-iconSize: 20px; 
}

#menu .QPushButton:hover,
#menu .QPushButton:pressed  {
    border: 8px solid {highlight};
    border-radius: 5px;
    background-color: {highlight};
}

#btn_general{
    qproperty-icon: url({path}/system.svg);
}
#btn_account{
    qproperty-icon: url({path}/manage_accounts.svg);
}
#btn_personalization{
    qproperty-icon: url({path}/appearance.svg);
}
#btn_notifications{
    qproperty-icon: url({path}/notifications.svg);
}
#btn_advanced{
    qproperty-icon: url({path}/wrench.svg);
}
#btn_donations{
    qproperty-icon: url({path}/donations.svg);
}
#btn_about{
    qproperty-icon: url({path}/about.svg);
}
#btn_quit{
    qproperty-icon: url({path}/sign-out.svg);
}
#btn_network{
    qproperty-icon: url({path}/network.svg);
}
"""

SettingsWindows = """
#setting_frame {
    background-color: {window};
    border: 5px solid {window};
    border-radius: 10px; 
}

#settingMargin{   
    border : 0;
    background: rgba(0, 0, 0,0.8);
}
"""

CloseButton = """
#btn_close{
    background-position: center;
    background-repeat: no-repeat;
    background-color: {window}; 
    qproperty-flat: true;
    qproperty-iconSize: 30px; 
    qproperty-icon: url({path_btn_titlebar}/btn_close.svg);
}
#btn_close:hover,
#btn_close:pressed {
    background-color: {window}; 
}
"""

Buttons = """
#btnOpenSWhatsapp,
#btn_webpage,
#btnNewUser,
#btnReportIssue,
#btnLeanMore,
#btn_ok  {
    background-color: #008069;
    border-radius: 5px;
    font: 12pt;
    height: 35px;
    font-weight: bold;
    color: #ffffff;
    padding: 0px 10px 0px 10px;
}

#btnOpenSWhatsapp:hover,
#btn_webpage:hover,
#btnNewUser:hover,
#btnReportIssue:hover,
#btnLeanMore:hover,
#btn_ok:hover {
    background-color: #199979;
    border-color: #199979;
}

#btn_ok:disabled,
#btn_restore:disabled {
    background-color: {frame_border};
    border-color: {frame_border};
    color: {frame_border};
}

#btn_paypal,
#btn_pix,
#btn_kofi,
#btn_gitSponor {	
    border: 1px solid {frame_border};
    border-radius: 5px;
    background-color: #F0F2F5;
}

#btn_paypal:hover,
#btn_pix:hover,
#btn_kofi:hover,
#btn_gitSponor:hover {
    color: {link};
    border: 3px solid {link};
    background-color: #FFFFFF;
}

#btn_restore{
    background-color: red;
    border-radius: 5px;
    font: 12pt;
    height: 35px;
    font-weight: bold;
    color: #ffffff;
    padding: 0px 10px 0px 10px;
}     
"""

Checkbox = """
#showNotifications::indicator,
#disableUser::indicator,
#deleteUser::indicator
    {
        width: 24px;
        height: 24px;
    }

#showNotifications::indicator:unchecked{
    border-image: url({path}/bell-slash.svg);
}
    #showNotifications::indicator:checked{
    border-image: url({path}/bell-ringing.svg);
}
#disableUser::indicator:unchecked{
    border-image: url({path}/eye-slash.svg);
}
    #disableUser::indicator:checked{
    border-image: url({path}/eye.svg);
}
#deleteUser::indicator:unchecked{
    border-image: url({path}/trash.svg);
}
    #deleteUser::indicator:checked{
    border-image: url({path}/trash.svg);
}
"""

Frame = """
#frameCardUser{
    border: 1px solid {frame_border};
    border-radius: 5px;   
}
"""

SETTINGS = SettingsMenu + SettingsWindows + \
    CloseButton + Buttons + Checkbox + Frame
