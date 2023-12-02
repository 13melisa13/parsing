import locale

BASE_API = 'http://37.77.106.193:8000/'
# BASE_API = 'http://prodamgaraj.ru:8000/'
# BASE_API = 'https://ddm5q4hn-8000.euw.devtunnels.ms/'
locale.setlocale(locale.LC_TIME, 'ru_RU')
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36 OPR/60.0.3255.170",
    "accept": "*/*"
}
