MENU_HOME = """
#menuUsers{
    background-color: {window};
    background-clip: border;
    border-image: none;
}

#menuUsers .QPushButton {	
    background-position: center;
    background-repeat: no-repeat;
    height: 30px;
    qproperty-flat: true;
    qproperty-iconSize: 20px; 
}
#menuUsers .QPushButton:hover {	
    background-color: rgba(225, 225, 225, 0.3); 
    border-radius: 2px;
}
#menuUsers .QPushButton:pressed {	
    background-color: {window}; 
    border-radius: 2px;
}

#btnHomeSetting{
    qproperty-icon: url({path}/gear-six.svg);
}
#btnHomePerfil{
    qproperty-icon: url({path}/user.svg);
}
#btnHomeNewChat{
    qproperty-icon: url({path}/chat.svg);
}
#btnHomeNewAccount{
    qproperty-icon: url({path}/user-plus.svg);
}
#btnHomeNewChatPhone{
    qproperty-icon: url({path}/phone-plus.svg);
}
"""
