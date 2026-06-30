import os
import configparser
import sys


def get_config_path(filename="settings.ini"):
    if os.path.isabs(filename):
        return filename

    if getattr(sys, "frozen", False):
        launcher_path = os.path.abspath(sys.argv[0])
        base_dir = os.path.dirname(launcher_path)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_dir, filename)


def get_config(filename="settings.ini"):
    config_path = get_config_path(filename)
    config = configparser.ConfigParser()
    
    dark_theme = {
        'background': '#0f172a',
        'qcombobox': """
            background: #1e293b; 
            color: #f8fafc; 
            padding: 8px; 
            border-radius: 8px; 
            border: 2px solid #334155; 
            font-size: 14px;
        """,
        'qcombobox_downarrow': """
            image: none; 
            border-left: 5px solid transparent; 
            border-right: 5px solid transparent; 
            border-top: 5px solid #94a3b8; 
            margin-right: 10px;
        """,
        'qcombobox_menu': """
            background-color: #1e293b;
            color: #f8fafc;
            selection-background-color: #6366f1;
            selection-color: white;
            border: 2px solid #334155;
            outline: 0px;
        """,
        'qlineedit': """
            background: #1e293b;
            color: #f8fafc;
            padding: 10px;
            border-radius: 10px;
            border: 2px solid #334155;
        """,
        'header_color': '#10b981',
        'label_color': '#94a3b8'
    }
    
    white_theme = {
        'background': '#ffffff',
        'qcombobox': """
            background: #ffffff; 
            color: #1e293b; 
            padding: 8px; 
            border-radius: 8px; 
            border: 1px solid #cbd5e1; 
            font-size: 14px;
        """,
        'qcombobox_downarrow': """
            image: none; 
            border-left: 5px solid transparent; 
            border-right: 5px solid transparent; 
            border-top: 5px solid #64748b; 
            margin-right: 10px;
        """,
        'qcombobox_menu': """
            background-color: #ffffff;
            color: #1e293b;
            selection-background-color: #3b82f6;
            selection-color: white;
            border: 1px solid #cbd5e1;
            outline: 0px;
        """,
        'qlineedit': """
            background: #ffffff;
            color: #1e293b;
            padding: 10px;
            border-radius: 10px;
            border: 1px solid #cbd5e1;
        """,
        'header_color': '#1e293b',
        'label_color': '#475569'
    }

    user = {
        'theme_index': '0'
    }

    os.makedirs(os.path.dirname(config_path), exist_ok=True)

    if not os.path.exists(config_path):
        config['dark_theme'] = dark_theme
        config['white_theme'] = white_theme
        config['user'] = user
        with open(config_path, 'w', encoding='utf-8') as configfile:
            config.write(configfile)
    else:
        config.read(config_path, encoding='utf-8')
    
    return config


def theme_change(config, theme_index, filename="settings.ini"):
    config['user']['theme_index'] = str(theme_index)
    config_path = get_config_path(filename)
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, 'w', encoding='utf-8') as configfile:
        config.write(configfile)
        

def get_bot_config(filename="bot_settings.ini"):
    config_path = get_config_path(filename)
    config = configparser.ConfigParser()

    bot_config = {
        'token': "",
        'guild_id': "0",
        'log_channel_id': "0",
        'first_startup': "True"
    }
    
    os.makedirs(os.path.dirname(config_path), exist_ok=True)

    if not os.path.exists(config_path):
        config['bot'] = bot_config
        with open(config_path, 'w', encoding='utf-8') as configfile:
            config.write(configfile)
    else:
        config.read(config_path, encoding='utf-8')
    return config