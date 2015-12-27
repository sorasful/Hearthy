import asyncore

from hearthstone.enums import GameTag

from hearthy.proxy import intercept
from pegasus.game_pb2 import PowerHistory, Tag

class SquirrelHandler(intercept.InterceptHandler):
    def __init__(self, use_premium=False):
        super().__init__()
        self._use_premium = use_premium

    def on_packet(self, epid, packet):
        if isinstance(packet, PowerHistory):
            for entry in packet.list:
                if entry.HasField('show_entity'):
                    entry.show_entity.name = 'EX1_tk28' # squirrel

                    if self._use_premium:
                        for tag in entry.show_entity.tags:
                            if tag.name == GameTag.PREMIUM:
                                tag.value = 1
                                break
                        else:
                            entry.show_entity.tags.add(name=GameTag.PREMIUM, value=1)

        return intercept.INTERCEPT_ACCEPT

if __name__ == '__main__':
    import argparse
    from hearthy.proxy.proxy import Proxy

    parser = argparse.ArgumentParser(description='Transform all cards into squirrels')
    parser.add_argument('--premium', action='store_const', default=False, const=True,
                        help='Make the squirrels premium')
    parser.add_argument('--port', type=int, default=5412)
    parser.add_argument('--host', default='0.0.0.0')

    args = parser.parse_args()

    proxy_handler = intercept.InterceptProxyHandler(SquirrelHandler,
                                                    use_premium=args.premium)
    proxy = Proxy((args.host, args.port), handler=proxy_handler)

    asyncore.loop()
