import os
import configparser

def get_config(filename="settings.ini"):
    config = configparser.ConfigParser()
    
    
    dark_theme = {
        'QComboBox': """
            background: #1e293b; 
            color: #f8fafc; 
            padding: 8px; 
            border-radius: 8px; 
            border: 2px solid #334155; 
            font-size: 14px;
        """,
        'QComboBox_downarrow': """
            image: none; 
            border-left: 5px solid transparent; 
            border-right: 5px solid transparent; 
            border-top: 5px solid #94a3b8; 
            margin-right: 10px;
        """,
        'QComboBox_menu': """
            background-color: #1e293b;
            color: #f8fafc;
            selection-background-color: #6366f1;
            selection-color: white;
            border: 2px solid #334155;
            outline: 0px;
        """
    }
    
    white_theme = {
        'QComboBox': """
            background: #ffffff; 
            color: #1e293b; 
            padding: 8px; 
            border-radius: 8px; 
            border: 1px solid #cbd5e1; 
            font-size: 14px;
        """,
        'QComboBox_downarrow': """
            image: none; 
            border-left: 5px solid transparent; 
            border-right: 5px solid transparent; 
            border-top: 5px solid #64748b; 
            margin-right: 10px;
        """,
        'QComboBox_menu': """
            background-color: #ffffff;
            color: #1e293b;
            selection-background-color: #3b82f6;
            selection-color: white;
            border: 1px solid #cbd5e1;
            outline: 0px;
        """
    }

    user = {
        'theme_index': 0
    }

    if not os.path.exists(filename):
        # Создаем одну секцию для стилей, чтобы не путаться
        config['dark_theme'] = dark_theme
        config['white_theme'] = white_theme
        config['user'] = user
        with open(filename, 'w', encoding='utf-8') as configfile:
            config.write(configfile)
    else:
        config.read(filename, encoding='utf-8')
    
    return config


def theme_change(config, theme_index):
    config['user']['theme_index'] = str(theme_index)
    with open("settings.ini", 'w', encoding='utf-8') as configfile:
        config.write(configfile)