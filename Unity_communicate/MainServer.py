'''

初始化和启动Tornado服务器。
初始化地图管理服务、玩家管理服务和游戏逻辑处理器。
设置路由和WebSocket连接处理
'''

import tornado.ioloop
import tornado.web
import tornado.websocket
from tornado.options import define, options

# 假设其他服务组件已经被定义在相应的文件中
# from MapService import MapService
# from PlayerService import PlayerService
# from GameLogicProcessor import GameLogicProcessor

define("port", default=8888, help="run on the given port", type=int)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/websocket", WebSocketHandler),
        ]
        settings = dict(
            debug=True,
        )
        super(Application, self).__init__(handlers, **settings)

        # 初始化服务组件
        # self.map_service = MapService()
        # self.player_service = PlayerService()
        # self.game_logic_processor = GameLogicProcessor()


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print("WebSocket opened")
        # 这里可以添加玩家连接的逻辑，例如：
        # application.player_service.on_player_connect(self)

    def on_message(self, message):
        print("Received message:", message)
        # 这里处理接收到的消息，根据消息类型调用不同的服务处理
        # 例如，更新玩家位置或处理游戏内事件

    def on_close(self):
        print("WebSocket closed")
        # 这里可以添加玩家断开连接的逻辑，例如：
        # application.player_service.on_player_disconnect(self)


def main():
    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)
    print(f"Server is running on http://localhost:{options.port}")
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
