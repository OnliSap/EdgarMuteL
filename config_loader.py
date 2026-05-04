import os
import configparser

def get_config(filename="settings.ini"):
    config = configparser.ConfigParser()
    
    
    default_settings = {
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
    

    if not os.path.exists(filename):
        # Создаем одну секцию для стилей, чтобы не путаться
        config['STYLES'] = default_settings
        with open(filename, 'w', encoding='utf-8') as configfile:
            config.write(configfile)
    else:
        config.read(filename, encoding='utf-8')
    
    return config