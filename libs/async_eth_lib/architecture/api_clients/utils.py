from ...models import exceptions as exceptions


def api_key_required(func):
    """Check if the Blockscan API key is specified"""

    def func_wrapper(self, *args, **kwargs):
        if not self.api_key:
            raise exceptions.ApiException(
                'To use this function, you must specify all required explorer API keys!'
            )

        else:
            return func(self, *args, **kwargs)

    return func_wrapper
