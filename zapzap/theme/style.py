from PyQt6.QtCore import QSettings
import zapzap


def buildTheme(p) -> str:
    QWIDGETS = """
        QWidget{
            color: {windowText};
            /*selection-background-color: #00A884;*/
            selection-color: {windowText};
            background-clip: border;
            border-image: none;
            font-family: Segoe UI
        }

        QStackedWidget {	
            background-color: {window};
        }

        QLineEdit{
            color: {windowText};
            background-color: {frame_border};
            border: 1px solid; 
            border-color: {frame_border};
            border-radius: 5px;
            padding: 5px;
            
        }
        QLineEdit:disabled {
            background-color:{frame_border};
        }   

        #btnDelete {
            color: #F0F2F5;
            background-color: rgb(192, 28, 40);
            border: 1px solid rgb(192, 28, 40);
            border-radius: 5px;
            font: 12pt;
            font-weight: bold;
            height: 35px;
        }
        
        #btnDisable
        {
            color: #F0F2F5;
            background-color: #585A5D;
            border: 1px solid #585A5D;
            border-radius: 5px;
            font: 12pt;
            font-weight: bold;
            height: 35px;
        }
        #btnDelete:hover,
        #btnDisable:hover
        {
            border: 2px solid #00A884;
            
        }

        #btnApply,
        #btnNewUser{
            color: #F0F2F5;
            background-color: #00A884;
            border: 1px solid #00A884;
            border-radius: 5px;
            font-weight: bold;
            height: 35px;
        }

        #btnApply:hover,
        #btnNewUser:hover {
            border: 2px solid #585A5D;
        }

        #btnApply:pressed,
        #btnNewUser:pressed  {
            background-color: #202C33;
            border-color: #202C33;
        }

        QComboBox {
            combobox-popup: 0;
            background: {window};
            height: 27px;
            border: 1px solid; 
            border-color: {frame_border};
            border-radius: 5px;
            padding: 5px ;
            selection-background-color: #D0D0D0;
            selection-color: #000000;
        }
        QComboBox:editable {
            background: {window};
        }
        QComboBox:!editable,
        QComboBox::drop-down:editable,
        QComboBox:!editable:on,
        QComboBox::drop-down:editable:on {
            background: {window};
        }
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            border-left: none;
        }
        QComboBox::down-arrow {
            width: 0.8em;
            height: 0.8em;
            border-image: url({path}/expand_more.svg);
        }
        QComboBox QAbstractItemView {
            background: {window};
            padding-left: 5px;
            border: none;
        }

        /* PopUp */

        #DownloadPopup .QPushButton{
            background-color: #008069;
            border-radius: 2px;
            font: 12pt;
            height: 30px;
            font-weight: bold;
            color: #ffffff;
        }

        #DownloadPopup .QPushButton:hover,
        #DownloadPopup .QPushButton:pressed {
             background-color: #199979;
             border-color: #199979;
        }

        /*PopUp phone*/

        #btnOk,
        #btnCancel {
            background-color: #008069;
            border-radius: 2px;
            font: 12pt;
            height: 30px;
            font-weight: bold;
            color: #ffffff;
        }

        #btnOk:hover,
        #btnOk:pressed,
        #btnCancel:hover,
        #btnCancel:pressed {
             background-color: #199979;
             border-color: #199979;
        }

        #btnPhoneHelper{	
            background: {frame_background_popup};
            color: {windowText};
            border-radius: 0px;
            font: 8pt;
            height: 30px;

        }

        #btnPhoneHelper:hover,
        #btnPhoneHelper:pressed {	
            background: {frame_background_popup};
            color: {windowText};
            border-radius: 0px;
            font: 8pt;
            height: 30px;
            font-weight: bold;
        }

        
        /* Popup Geral */
        #popupMargins{
            border-image: url({path}/borderDialog.png);
        }
        
        #popupFrame{
            color: {windowText};
            background-color: {frame_background_popup};
            border-radius: 2px;
        }
        

    """

    QMENU_BAR = """
        QMenuBar {
            background-color: {window};
            color: {windowText};
        }

        QMenuBar::item {
            background: transparent;
        }

        QMenuBar::item:selected {
            background: transparent;
        }

        QMenuBar::item:disabled {
            color: {disabled};
        }

        QMenuBar::item:pressed  {
            background-color: {highlight};
            color: {highlightedText};
            margin-bottom: -0.09em;
            padding-bottom: 0.09em;
        }
    """

    QMENU_BAR_Wayland = """
    QMenu {
            color: {windowText};
            margin: 0.09em;
            background-color: {window};
            border: 1px solid rgba(100, 100, 100, 70);     
        }
    """

    QMENU = """
        QMenu {
            color: {windowText};
            margin: 0.09em;
            background-color: {window};
        }

        QMenu::icon {
            margin: 0.23em;
        }

        QMenu::item  {
            /* Add extra padding on the right for the QMenu arrow */
            padding: 0.1em 0.5em 0.1em 0.5em;
            border: 0.09em solid transparent;
            background: transparent;
        }

        QMenu::item:selected {
            color: {highlightedText};
            background-color: {highlight};
        }

        QMenu::item:selected:disabled  {
            background-color: {disabled};
        }

        QMenu::item:disabled  {
            color: {disabled};
        }

        QMenu::indicator  {
            width: 0.8em;
            height: 0.8em;
            /* To align with QMenu::icon, which has a 0.23em margin. */
            margin-left: 0.3em;
            subcontrol-position: center left;
        }

        QMenu::indicator:non-exclusive:unchecked,
        QMenu::indicator:non-exclusive:unchecked:selected  {
            border-image: url({path}/checkbox_unchecked_disabled.svg);
        }

        QMenu::indicator:non-exclusive:checked,
        QMenu::indicator:non-exclusive:checked:selected  {
            border-image: url({path}/checkbox_checked.svg);
        }

        QMenuBar::item:focus:!disabled { }

        QMenu::separator {
            height: 0.03em;
            background-color: {disabled};
            padding-left: 0.2em;
            margin-top: 0.2em;
            margin-bottom: 0.2em;
            margin-left: 0.41em;
            margin-right: 0.41em;
        }
    """

    QCHECHBOX = """
        #checkSpellChecker{
            color: {windowText};
            margin-bottom: 0.09em;
            font: 14pt;
            font-weight: bold;
        }

        #check_zap_window{
            color: {windowText};
            margin-bottom: 0.09em;
            font: 14pt;
            font-weight: bold;
        }

        #disableTrayIcon{
            color: {windowText};
            margin-bottom: 0.09em;
            font: 12pt;
            font-weight: bold;
        }

        QCheckBox
        {
            color: {windowText};
            margin-bottom: 0.09em;
            font: 11pt;
        }

        QCheckBox:hover
        {
            color: #00A884;    
        }
        
        QCheckBox:disabled
        {
            color: {disabled};
        }

        QCheckBox::indicator
        {
            width: 24px;
            height: 24px;
        }

        QCheckBox::indicator:unchecked,
        QCheckBox::indicator:unchecked:focus
        {
            border-image: url({path}/checkbox_unchecked_disabled.svg);
        }
        QCheckBox::indicator:unchecked:hover,
        QCheckBox::indicator:unchecked:pressed
        {
            border: none;
            border-image: url({path}/checkbox_unchecked.svg);
        }

        QCheckBox::indicator:checked
        {
            border-image: url({path}/checkbox_checked.svg);
        }

        QCheckBox::indicator:checked:hover,
        QCheckBox::indicator:checked:focus,
        QCheckBox::indicator:checked:pressed
        {
            border: none;
            border-image: url({path}/checkbox_checked.svg);
        }

        QCheckBox::indicator:indeterminate
        {
            border-image: url({path}/checkbox_indeterminate.svg);
        }

        QCheckBox::indicator:indeterminate:focus,
        QCheckBox::indicator:indeterminate:hover,
        QCheckBox::indicator:indeterminate:pressed
        {
            border-image: url({path}/checkbox_indeterminate.svg);
        }

        QCheckBox::indicator:indeterminate:disabled
        {
            border-image: url({path}/checkbox_indeterminate_disabled.svg);
        }

        QCheckBox::indicator:checked:disabled
        {
            border-image: url({path}/checkbox_checked_disabled.svg);
        }

        QCheckBox::indicator:unchecked:disabled
        {
            border-image: url({path}/checkbox_unchecked_disabled.svg);
        }

    """

    QRADIONBUTTON = """
        QRadioButton
        {
            spacing: 0.23em;
            outline: none;
            color: {windowText};
            margin-bottom: 0.09em;
        }
        QRadioButton:disabled
        {
            color: {disabled};
        }

        QRadioButton:hover
        {
            color: #00A884;    
        }

        #frameAppearance .QRadioButton::indicator
        {
            width: 150px;
            height: 100px;
        }

        #rb_system::indicator:unchecked,
        #rb_system::indicator:unchecked:focus,
        #rb_system::indicator:unchecked:hover,
        #rb_system::indicator:unchecked:pressed
        {
            border-image: url({path}/theme_system_unchecked.svg);
        }

        #rb_system::indicator:checked,
        #rb_system::indicator:checked:hover,
        #rb_system::indicator:checked:focus,
        #rb_system::indicator:checked:pressed
        {
            border: none;
            outline: none;
            border-image: url({path}/theme_system_checked.svg);
        }

        #rb_light::indicator:unchecked,
        #rb_light::indicator:unchecked:focus,
        #rb_light::indicator:unchecked:hover,
        #rb_light::indicator:unchecked:pressed
        {
            border-image: url({path}/theme_light_unchecked.svg);
        }

        #rb_light::indicator:checked,
        #rb_light::indicator:checked:hover,
        #rb_light::indicator:checked:focus,
        #rb_light::indicator:checked:pressed
        {
            border: none;
            outline: none;
            border-image: url({path}/theme_light_checked.svg);
        }

        #rb_dark::indicator:checked,
        #rb_dark::indicator:checked:hover,
        #rb_dark::indicator:checked:focus,
        #rb_dark::indicator:checked:pressed
        {
            border: none;
            outline: none;
            border-image: url({path}/theme_dark_checked.svg);
        }

        #rb_dark::indicator:unchecked,
        #rb_dark::indicator:unchecked:focus,
        #rb_dark::indicator:unchecked:hover,
        #rb_dark::indicator:unchecked:pressed
        {
            border-image: url({path}/theme_dark_unchecked.svg);
        }

        #label_tray_def{
            border-image: url({path}/tray_default.svg);
        }
        #label_tray_light{
            border-image: url({path}/tray_light.svg);
        }
        #label_tray_dark{
            border-image: url({path}/tray_dark.svg);
        }

        /* FRAME TRAY*/

        #frameTray .QRadioButton::indicator {
        width: 11px;
        height: 11px;
        border-radius: 5px;
        }

        #frameTray .QRadioButton::indicator::unchecked{ 
        border: 2px solid; 
        border-color: {highlight};
        border-radius: 6px;
        background-color: {highlight}; 
        width: 11px; 
        height: 11px; 
        }

        #frameTray .QRadioButton::indicator::checked{ 
        border: 2px solid; 
        border-color: #00A884;
        border-radius: 6px;
        background-color: #00A884; 
        width: 11px; 
        height: 11px;
        }
    """

    QSCROLLAREA = """
        #system_scrollArea,
        #appearance_scrollArea,
        #notification_scrollArea,
        #donations_scrollArea,
        #about_scrollArea,
        #usersScrollArea  {
            background-color: {window};
            background: {window};
        }

        QScrollBar:horizontal
        {
            background-color:{window};
            height: 0.65em;
            margin: 0.13em 0.65em 0.13em 0.65em;
            border: 0.04em transparent {window};
            border-radius: 0.17em;
        }

        QScrollBar::handle:horizontal:hover,
        QScrollBar:vertical:hover
        {
        }

        QScrollBar::handle:horizontal
        {
            background-color: {highlight};
            border: 0.04em solid {highlight};
            min-width: 0.5em;
            border-radius: 0.17em;
        }

        QScrollBar::handle:vertical
        {
            background-color: {highlight};
            border: 0.04em solid {highlight};
            min-height: 0.5em;
            border-radius: 0.17em;
        }

        QScrollBar::handle:horizontal:hover,
        QScrollBar::handle:vertical:hover
        {
            background-color:#00BD95;
            border: 0.04em solid #00BD95;
        }
        

        QScrollBar::add-line:horizontal
        {
            margin: 0em 0.13em 0em 0.13em;
            border-image: url({path}/transparent.svg);
            width: 0.41em;
            height: 0.41em;
            subcontrol-position: right;
            subcontrol-origin: margin;
        }

        QScrollBar::sub-line:horizontal
        {
            margin: 0em 0.13em 0em 0.13em;
            border-image: url({path}/transparent.svg);
            width: 0.41em;
            height: 0.41em;
            subcontrol-position: left;
            subcontrol-origin: margin;
        }

        QScrollBar::add-line:horizontal:hover,
        QScrollBar::add-line:horizontal:on
        {
            border-image: url({path}/transparent.svg);
            width: 0.41em;
            height: 0.41em;
            subcontrol-position: right;
            subcontrol-origin: margin;
        }

        QScrollBar::sub-line:horizontal:hover,
        QScrollBar::sub-line:horizontal:on
        {
            border-image: url({path}/transparent.svg);
            width: 0.41em;
            height: 0.41em;
            subcontrol-position: left;
            subcontrol-origin: margin;
        }

        QScrollBar::up-arrow:horizontal,
        QScrollBar::down-arrow:horizontal,
        QScrollBar::add-page:horizontal,
        QScrollBar::sub-page:horizontal,        
        QScrollBar::up-arrow:vertical,
        QScrollBar::down-arrow:vertical,
        QScrollBar::add-page:vertical,
        QScrollBar::sub-page:vertical
        {
            background: none;
        }

        QScrollBar:vertical
        {
            background-color: {window};
            width: 0.65em;
            margin: 0.65em 0.13em 0.65em 0.13em;
            border: 0.04em transparent {window};
            border-radius: 0.17em;
        }

        QScrollBar::sub-line:vertical
        {
            margin: 0.13em 0em 0.13em 0em;
            border-image: url({path}/transparent.svg);
            height: 0.41em;
            width: 0.41em;
            subcontrol-position: top;
            subcontrol-origin: margin;
        }

        QScrollBar::add-line:vertical
        {
            margin: 0.13em 0em 0.13em 0em;
            border-image: url({path}/transparent.svg);
            height: 0.41em;
            width: 0.41em;
            subcontrol-position: bottom;
            subcontrol-origin: margin;
        }

        QScrollBar::sub-line:vertical:hover,
        QScrollBar::sub-line:vertical:on
        {
            border-image: url({path}/transparent.svg);
            height: 0.41em;
            width: 0.41em;
            subcontrol-position: top;
            subcontrol-origin: margin;
        }

        QScrollBar::add-line:vertical:hover,
        QScrollBar::add-line:vertical:on
        {
            border-image: url({path}/transparent.svg);
            height: 0.41em;
            width: 0.41em;
            subcontrol-position: bottom;
            subcontrol-origin: margin;
        }

        
    """

    SettingsMenu = """
        #leftMenu,
        #leftBar_2
        {	
            background-color: {window};
        }
        #menu .QPushButton {	
            background-position: left center;
            background-repeat: no-repeat;
            border: 8px solid {window};
            border-radius: 5px;
            text-align: left;
            padding-left: 44px;
            font: 12pt;
            height: 30px;
        }

        #menu .QPushButton:hover,
        #menu .QPushButton:pressed  {
            font: 13pt;
        }
        
        #btn_home{
            background-image: url({path}/home.svg);
        }
        #btn_users{
            background-image: url({path}/manage_accounts.svg);
        }
        #btn_system{
            background-image: url({path}/system.svg);
        }
        #btn_appearance{
            background-image: url({path}/appearance.svg);
        }
        #btn_notifications{
            background-image: url({path}/notifications.svg);
        }
        #btn_donations{
            background-image: url({path}/donations.svg);
        }
        #btn_about{
            background-image: url({path}/about.svg);
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
        """

    FrameSettingBorder = """
        #settings_stacked .QFrame {
            background-color: {frame_background};
            border: 1px solid {frame_border};
            border-radius: 5px;
        }

        #settings_stacked .QFrame:disabled {
            background-color:{frame_border};
        
        }
    """

    settings = QSettings(zapzap.__appname__, zapzap.__appname__)
    ZapDecoration = ""
    if settings.value("system/zapzap_decoration", False, bool):
        ZapDecoration = """

        #leftBox .QPushButton {	
            border: 0px solid {window};
            border-radius: 5px;
            text-align: center;
            height: 30px;
        }

        #leftBox .QPushButton:hover,
        #leftBox .QPushButton:pressed  {
            color: {link};
        }

        QStackedWidget {	
            background-color: {window};
            border: 3px solid {window}; 
            border-radius: 12px;
        }
        #appMargins{
            border-image: url({path}/border.png);
        }
        #app {	
            background-color: {window};
            border: 1px solid {frame_border}; 
            border-radius: 12px;
        }
        #headbar{	
            background-color: {window};
            border: 1px solid {window}; 
            border-radius: 12px;
        }

        #rightButtons .QPushButton {	
            background-position: center;
            background-repeat: no-repeat;
            border: 0px solid {window};
        }

        #leftButtons .QPushButton {	
            background-position: center;
            background-repeat: no-repeat;
            border: 0px solid {window};
        }
        /* CLOSE */
        #closeAppBtn,
        #closeAppBtn_left{
            background-image: url({path_btn_titlebar}/btn_close.svg);
        }

        #closeAppBtn:hover,
        #closeAppBtn_left:hover{
            background-image: url({path_btn_titlebar}/btn_close_hover.svg);
        }
        /* MAXIMIZE */
        #maximizeAppBtn,
        #maximizeAppBtn_left{
            background-image: url({path_btn_titlebar}/btn_maximize.svg);
        }

        #maximizeAppBtn:hover,
        #maximizeAppBtn_left:hover{
            background-image: url({path_btn_titlebar}/btn_maximize_hover.svg);
        }

        /* MINIMIZE */
        /* MAXIMIZE */
        #minimizeAppBtn,
        #minimizeAppBtn_left{
            background-image: url({path_btn_titlebar}/btn_minimize.svg);
        }

        #minimizeAppBtn:hover,
        #minimizeAppBtn_left:hover{
            background-image: url({path_btn_titlebar}/btn_minimize_hover.svg);
        }

        /* SETTINGS */

        #settingsTopBtn,
        #settingsTopBtn_left{
            background-image: url({path_btn_titlebar}/btn_settings.svg);
        }    
    """

    STYLE_SHEET = f"""
        {QWIDGETS}
        {QMENU_BAR}
        {QMENU}
        {QCHECHBOX}
        {QRADIONBUTTON}
        {QSCROLLAREA}
        {SettingsMenu}
        {FrameSettingBorder}
        {ZapDecoration}
        {QMENU_BAR_Wayland if settings.value("system/wayland", True, bool) else ""}
        """

    for chave, valor in p.getPallete().items():
        STYLE_SHEET = STYLE_SHEET.replace("{"+chave+"}", valor)

    return STYLE_SHEET
