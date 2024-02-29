import json

class Player:
    def __init__(self, player_id, nickname, position):
        self.player_id = player_id
        self.nickname = nickname
        self.position = position

class PlayerService:
    def __init__(self, data_file='playerdata.json'):
        self.data_file = data_file
        self.players = {}  # 使用字典来存储玩家对象，键为player_id
        self.load_players()

    def load_players(self):
        """从JSON文件加载玩家数据到内存。"""
        try:
            with open(self.data_file, 'r') as file:
                data = json.load(file)
                for player_id, info in data.items():
                    self.players[player_id] = Player(player_id, info['nickname'], info['position'])
        except FileNotFoundError:
            print(f"Warning: {self.data_file} not found. Starting with an empty player list.")

    def save_players(self):
        """将玩家数据保存到JSON文件。"""
        data = {player_id: {'nickname': player.nickname, 'position': player.position} for player_id, player in self.players.items()}
        with open(self.data_file, 'w') as file:
            json.dump(data, file, indent=4)

    def on_player_connect(self, player_id):
        """玩家连接处理逻辑。如果玩家不存在，则创建新玩家。"""
        if player_id not in self.players:
            # 默认新玩家信息，可以根据需要进行调整
            self.players[player_id] = Player(player_id, "NewPlayer", [0, 0])
            self.save_players()

    def on_player_disconnect(self, player_id):
        """玩家断开连接处理逻辑。"""
        # 这里可以添加断开连接时需要执行的操作，例如保存数据
        self.save_players()

    def update_player_position(self, player_id, new_position):
        """更新玩家位置，并定期保存玩家数据。"""
        if player_id in self.players:
            self.players[player_id].position = new_position
            self.save_players()
        else:
            print(f"Player {player_id} not found for position update.")

# 示例使用
if __name__ == "__main__":
    player_service = PlayerService()
    player_service.on_player_connect("player1")
    player_service.update_player_position("player1", [200, 300])
    print(f"Player 1's new position: {player_service.players['player1'].position}")
    player_service.on_player_disconnect("player1")
