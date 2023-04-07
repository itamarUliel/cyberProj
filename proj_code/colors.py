import colorama
from colorama import Back, Fore
colorama.init(autoreset=True)

ERROR_COLOR = Fore.BLACK + Back.RED
OK_COLOR = Back.GREEN + Fore.BLACK
PENDING_COLOR = Back.LIGHTBLUE_EX + Fore.BLACK
DATA_COLOR = Back.LIGHTYELLOW_EX + Fore.GREEN