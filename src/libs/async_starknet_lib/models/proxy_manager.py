from curl_cffi import requests

from .exceptions import InvalidProxy


class ProxyManager:
    @staticmethod
    def init_proxy(
        proxy: str,
        check_proxy: bool = False
    ) -> str | None:
        proxy = ProxyManager.normalize_proxy(proxy)

        if check_proxy:
            your_ip = requests.get(
                url='http://eth0.me',
                proxies={'http': proxy, 'https': proxy},
                timeout=10
            ).text.rstrip()

            if your_ip not in proxy:
                raise InvalidProxy(
                    f"Proxy doesn't work! It's IP is {your_ip}"
                )
        
        return proxy

    @staticmethod
    def normalize_proxy(proxy: str = '') -> str:
        if proxy and 'http' not in proxy:
            proxy = f'http://{proxy}'

        return proxy
