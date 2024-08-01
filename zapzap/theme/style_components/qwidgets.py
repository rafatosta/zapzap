QWIDGETS = """
* {
 
}

QLabel{
    color: {windowText};
    
}

QStackedWidget {	
    background-color: {window};
}

QToolTip {
    color: #F0F2F5;
    background-color: #202C33;
    padding:2px;
   
}

QLineEdit{
    color: {windowText};
    background: {frame_background};
    border: 1px solid; 
    border-color: {frame_border};
    border-radius: 5px;
    padding: 5px;
}

QComboBox {
    color: {windowText};
    combobox-popup: 0;
    background: {frame_background};
    background-color: {frame_background};
   
    border: 1px solid; 
    border-color: {frame_border};
    border-radius: 5px;
    padding: 5px ;
    selection-background-color: #D0D0D0;
    selection-color: #000000;
}

QComboBox:editable {
    color: {windowText};
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
    margin-right: 0.41em;
}

QComboBox QAbstractItemView {
    /*color: {windowText};
    background: {window};
    padding-left: 5px;
    border: none;*/
    color: {windowText};
    background-color: {window};
    selection-background-color: #008069;
    outline-color: 0em;
    border-radius: 0.09em;
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

QScrollArea .QWidget{
    background-color: {window};
    background: {window};
}

QFrame[frameShape="4"] {
    border: none;
    border-bottom: 1px solid {frame_border};
}
QFrame[frameShape="5"] {
    border: none;
    border-left: 1px solid {frame_border};
}

QMenu {
    color: {windowText};
    margin: 0.09em;
    background-color: {window};
}
"""
