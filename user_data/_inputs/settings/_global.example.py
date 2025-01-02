# Секретная фраза, которая будет использоваться для шифрования ваших приватных данных
# Эта же фраза будет использоваться и для их расшифровки по этому не удаляйте её!
# Пример: 'abyrvalg'
SECRET_PHRASE = ''

# Приватный ключ от Ankr RPC
# Пример: a70406a97dsakjh27412t9fdashkjdll8w2hkjdnaskda9124ydcaf1505
ANKR_API_KEY = ''


# Приватный ключ от Anti-Catpcha - https://anti-captcha.com/
ANTICAPTCHA_KEY = ''

# Приватный ключ от 2Catpcha - https://2captcha.com/
TWO_CAPTCHA_KEY = ''


# Приватные данные для экстренных telegram уведомлений
TELEGRAM = {
    # Создаём тут -> https://t.me/BotFather
    # Пример: 3351122561:BBAh5G_Xdkljlkf2fkjansfdaskjnfwk1
    'token': {
        'modules_info': '',  # уведомления про выполнение модулей
        'critical_errors': '', # уведомления с критическими ошибками, которые возможно нужно исправить самому (например, пополнить баланс)
    },

    # Узнать можно тут -> https://t.me/getmyid_bot
    # Пример: [721667338, 721667339]
    'IDs': {
        'modules_info': [],
        'critical_errors': [],
    },
}

OKX = {
    'accounts': {
        'account_1': {
            'api_key': '',
            'api_secret': '',
            'passphrase': '',
        },
        'account_2': {
            'api_key': '',
            'api_secret': '',
            'passphrase': '',
        },
    },
    # Пример: http://login:pass@ip:port
    'proxy': ''
}

# Приватные данные от Binance
BINANCE = {
    # Создать можно тут -> https://www.binance.com/en/binance-api
    'secret_key': '',
    'api_key': '',

    # Пример: http://login:pass@ip:port
    'proxy': ''
}

# Приватные данные от Bitget
BITGET = {
    'secret_key': '',
    'api_key': '',
    'passphrase': '',

    # Пример: http://login:pass@ip:port
    'proxy': ''
}

# Приватные данные от Gate
GATE = {
    'secret_key': '',
    'api_key': '',

    # Пример: http://login:pass@ip:port
    'proxy': ''
}

## =========================== Don't touch this ===========================
MODULES_SETTINGS_FILE_PATH = ['user_data', '_inputs', 'json', 'settings.json']
