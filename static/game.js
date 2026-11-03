const socket = io();
let myRoom = '';
let myId = '';
let currentCorrectAnswer = 0;

function joinGame() {
    const name = document.getElementById('playerName').value;
    myRoom = document.getElementById('roomName').value;
    if(name && myRoom) {
        socket.emit('join', {name: name, room: myRoom});
        document.getElementById('login').style.display = 'none';
        document.getElementById('gameUI').style.display = 'flex';
        initBoard();
    }
}

function initBoard() {
    const board = document.getElementById('board');
    for(let i=0; i<20; i++) {
        let div = document.createElement('div');
        div.className = 'cell';
        div.id = 'cell-' + i;
        div.innerText = '第' + i + '格'; // 可擴充為商店、機會等
        board.appendChild(div);
    }
}

socket.on('update_state', (game) => {
    const list = document.getElementById('playerList');
    list.innerHTML = '';
    
    // 清除舊棋子
    document.querySelectorAll('.cell').forEach(c => {
        const text = c.innerText.split('\n')[0];
        c.innerText = text; 
    });

    game.players.forEach(p => {
        // 更新玩家列表
        let li = document.createElement('li');
        li.innerText = `${p.token} ${p.name} - $${p.money}`;
        list.appendChild(li);
        
        // 更新棋盤上的棋子
        let cell = document.getElementById('cell-' + p.pos);
        if(cell) cell.innerText += '\n' + p.token;
    });
});

function rollDice() {
    socket.emit('roll_dice', {room: myRoom});
}

socket.on('dice_result', (data) => {
    alert(`${data.name} 擲出了 ${data.steps} 點！`);
});

socket.on('question_event', (data) => {
    if(socket.id === data.player_id) {
        document.getElementById('questionModal').style.display = 'block';
        document.getElementById('qText').innerText = data.q_data.q;
        currentCorrectAnswer = data.q_data.a;
    }
});

function submitAnswer() {
    const ans = document.getElementById('qAnswer').value;
    socket.emit('answer_question', {
        room: myRoom, 
        answer: ans, 
        correct_answer: currentCorrectAnswer
    });
    document.getElementById('questionModal').style.display = 'none';
    document.getElementById('qAnswer').value = '';
}

socket.on('answer_result', (data) => {
    alert(data.msg);
});