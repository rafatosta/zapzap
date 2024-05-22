POPUP = """
/* PopUp */

#DownloadPopup .QPushButton{
    background-color: #008069;
    border-radius: 5px;
    font: 12pt;
    height: 35px;
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
    border-radius: 5px;
    font: 12pt;
    height: 35px;
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
    height: 35px;

}

#btnPhoneHelper:hover,
#btnPhoneHelper:pressed {	
    background: {frame_background_popup};
    color: {windowText};
    border-radius: 0px;
    font: 8pt;
    height: 35px;
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
