from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'game-secret'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# 遊戲狀態儲存 (支援五人 + 一房主)
rooms = {}
TOKENS = ["水豚 🦝", "貓咪 🐈", "狗狗 🐕", "兔子 🐇", "小鳥 🐦", "熊熊 🐻"]

def generate_decimal_question(q_type):
    """生成小六程度的小數應用題"""
    if q_type == "折扣":
        price = random.randint(10, 50) * 10
        discount = random.choice([0.7, 0.8, 0.9])
        ans = round(price * discount, 1)
        return {"q": f"商品原價 {price} 元，黑心商人打 {int(discount*10)} 折，請問要付多少元？", "a": ans}
    elif q_type == "計算":
        a = round(random.uniform(1.1, 9.9), 1)
        b = round(random.uniform(1.1, 5.0), 1)
        return {"q": f"請計算: {a} + {b} = ?", "a": round(a + b, 1)}
    elif q_type == "Boss":
        a = round(random.uniform(10.0, 50.0), 1)
        b = random.choice([0.2, 0.5, 4.0])
        return {"q": f"Boss 挑戰 (小數除法): {a} ÷ {b} = ?", "a": round(a / b, 1)}
    else: # 機會命運/比價
        return {"q": f"機會題: 0.5 x 100 = ?", "a": 50}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('join')
def on_join(data):
    room = data['room']
    player_name = data['name']
    join_room(room)
    
    if room not in rooms:
        rooms[room] = {'players': [], 'turn': 0}
        
    players = rooms[room]['players']
    if len(players) < 6:
        token = TOKENS[len(players)]
        players.append({
            'id': request.sid, 'name': player_name, 
            'token': token, 'pos': 0, 'money': 2000
        })
        emit('update_state', rooms[room], to=room)

@socketio.on('roll_dice')
def on_roll_dice(data):
    room = data['room']
    game = rooms[room]
    
    # 簡化輪替邏輯：更新當前玩家位置
    current_player = game['players'][game['turn'] % len(game['players'])]
    if request.sid == current_player['id']:
        steps = random.randint(1, 6)
        current_player['pos'] = (current_player['pos'] + steps) % 20 # 假設棋盤20格
        
        # 決定題目類型
        event_type = random.choice(["計算", "折扣", "Boss", "機會"])
        question = generate_decimal_question(event_type)
        
        emit('dice_result', {'name': current_player['name'], 'steps': steps}, to=room)
        emit('question_event', {'player_id': current_player['id'], 'q_data': question}, to=room)
        emit('update_state', game, to=room)

@socketio.on('answer_question')
def on_answer(data):
    room = data['room']
    game = rooms[room]
    current_player = game['players'][game['turn'] % len(game['players'])]
    
    if float(data['answer']) == float(data['correct_answer']):
        current_player['money'] += 200 # 答對獎勵或成功購買
        result_msg = "答對了！數學很棒！"
    else:
        current_player['money'] -= 100 # 答錯扣錢
        result_msg = f"答錯了！正確答案是 {data['correct_answer']}"
        
    game['turn'] += 1 # 換下一位
    emit('answer_result', {'msg': result_msg}, to=room)
    emit('update_state', game, to=room)

if __name__ == '__main__':
    socketio.run(app, debug=True)