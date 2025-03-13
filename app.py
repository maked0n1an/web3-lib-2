# import asyncio
# import sys
# import time

# from questionary import (
#     questionary,
#     Choice
# )

# from utils.console_utils import (
#     center_output, end_of_work
# )
# from data.config import EXPORT_FILE
# from data.models import Settings
# from functions.activity import activity
# from functions.Import import Import
# from src.libs.py_eth_async.data import config
# from loguru import logger
# from utils.miscellaneous.create_files import create_files


# def is_bot_setuped_to_start():
#     is_conditions_met = True

#     if len(Import.get_wallets_from_csv(csv_path=EXPORT_FILE)) == 0:
#         center_output("Not filled data in 'files/import.csv'!")
#         is_conditions_met = False

#     return end_of_work(is_conditions_met)


# def measure_time_for_all_work(start_time: float):
#     end_time = round(time.time() - start_time, 2)
#     seconds = round(end_time % 60, 2)
#     minutes = int(end_time // 60) if end_time > 60 else 0
#     hours = int(end_time // 3600) if end_time > 3600 else 0

#     logger.info(
#         (
#             f"Spent time: "
#             f"{hours} hours {minutes} minutes {seconds} seconds"
#         )
#     )


# def get_module():
#     result = questionary.select(
#         "Select a method to get started",
#         choices=[
#             Choice("1) Import wallets from the spreadsheet to the DB",
#                    Import.init_wallets),
#             Choice("2) Start L0 warming-up", start_script),
#             Choice("3) Exit", "exit"),
#         ],
#         qmark="⚙️ ",
#         pointer="✅ "
#     ).ask()
#     if result == "exit":
#         exit_label = "========= Exited ========="
#         center_output(exit_label)
#         sys.exit()

#     return result


# async def start_script():
#     if not all([
#         config.AVALANCHE_API_KEY,
#         config.ARBITRUM_API_KEY,
#         config.BSC_API_KEY,
#         config.CELO_API_KEY,
#         config.OPTIMISM_API_KEY,
#         config.POLYGON_API_KEY,
#     ]):
#         logger.error(f'Заполните апи ключи екслпореров в .env файле')
#     tasks = [
#         asyncio.create_task(activity()),
#     ]
#     return await asyncio.wait(tasks)


# async def run_module(module):
#     return await module()

# if __name__ == '__main__':
#     create_files()
#     is_bot_setuped_to_start()
    
#     main_settings = Settings()
#     module = get_module()

#     start_time = time.time()
#     logger.info("The bot started to measure time for all work")

#     asyncio.run(run_module(module))

#     measure_time_for_all_work(start_time)
#     end_of_work()
#     # except KeyboardInterrupt:
#     #     print()
#     #
#     # except ValueError as err:
#     #     logger.error(f"Value error: {err}")
#     #
#     # except BaseException as e:
#     #     logger.exception(f'\nSomething went wrong: {e}')
