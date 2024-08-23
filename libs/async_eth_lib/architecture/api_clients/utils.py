import libs.async_eth_lib.models.exceptions as exceptions


def api_key_required(func):
    """Check if the Blockscan API key is specified"""

    def func_wrapper(self, *args, **kwargs):
        if not self.api_key:
            raise exceptions.ApiException(
                'To use this function, you must specify the explorer API key!'
            )

        else:
            return func(self, *args, **kwargs)

    return func_wrapper
