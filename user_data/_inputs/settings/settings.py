from src._types.settings import DefaultSettings, Shuffle


class Settings(DefaultSettings):
    # =============================================================
    # ======================= Main settings =======================
    # =============================================================

    # Список маршрутов, которые запустятся один за другим
    routes = [
        'l0_warmup',
    ]
    shuffle = Shuffle(
        wallets=True,
        modules=True
    )
