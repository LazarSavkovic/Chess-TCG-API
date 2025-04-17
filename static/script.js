let userId = null;
const userH2 = document.getElementById('userH2')
const turnH5 = document.getElementById('turnH5')
const endTurnBtn = document.getElementById("endTurnBtn")
userH2.innerText = `User: ${userId}`
const cellSize = 10;
const pathParts = window.location.pathname.split('/'); 
const roomId = pathParts[pathParts.length - 1]; 
const gameId = "demo"; // static for now
const protocol = location.protocol === 'https:' ? 'wss' : 'ws';
const ws = new WebSocket(`${protocol}://${location.host}/game/${roomId}`);



function showRotationPrompt() {
  const isPortrait = window.innerHeight > window.innerWidth;
  document.getElementById('rotatePrompt').style.display = isPortrait ? 'flex' : 'none';
}

window.addEventListener('resize', showRotationPrompt);
showRotationPrompt();


const boardEl = document.getElementById('board');
let selected = null;
let board = [];
let landBoard = [];
let hand1 = [];
let hand2 = [];
let graveyard1 = [];
let graveyard2 = [];
let mana = { '1': 50, '2': 50 };
let centerTileControl = {
  '1': 0,
  '2': 0
}

let turn = '1';
let selectedHandIndex = null;
let lastSummonedPos = null;

function flipDirection(dir) {
  const flipMap = {
    "forward": "back",
    "back": "forward",
    "left": "right",
    "right": "left",
    "forward-left": "back-right",
    "forward-right": "back-left",
    "back-left": "forward-right",
    "back-right": "forward-left"
  };
  return flipMap[dir] || dir;
}


endTurnBtn.onclick = () => {
  ws.send(JSON.stringify({ type: 'end-turn', user_id: userId }));
};



ws.onerror = (e) => {
  console.error("[WebSocket Error]", e);
};

ws.onclose = (e) => {
  console.warn("[WebSocket Closed]", e);
};



ws.onopen = () => {
  ws.send(JSON.stringify({ user_id: userId }));
};
function playSound(id) {
  const audio = document.getElementById(id);
  if (audio) audio.play();
}
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('[WebSocket] Incoming:', data);

  // 🔑 Set user ID
  if (data.user_id && !userId) {
    userId = data.user_id;
    document.getElementById('userH2').innerText = `User: ${userId}`;
  }

  // 🎯 Handle special message: awaiting input
  if (data.type === 'awaiting-input') {
    const { card_id, slot, valid_targets } = data;
    console.log(valid_targets)
    notify('yellow', `Select a target for ${card_id}`);

    window.pendingSorcery = {slot,  card_id };

    valid_targets.forEach(([x, y]) => {
      const cell = document.querySelector(`.cell[data-x="${x}"][data-y="${y}"]`);
      if (cell) {
        cell.classList.add(userId === '1' ? 'can-move-blue' : 'can-move-orange');
      }
    });
    return
    
  }

  if (data.type === 'discard-to-end-turn') {

    notify('yellow', `Discard card from hand to end turn`);

    window.pendingDiscard = true;
    renderHand()

    return

  }

  // 🛑 Exit early only if not a game update message
  if (!data.board && data.type !== 'game-over') return;

  // 🎮 Update game state
  if (data.board) board = data.board;
  if (data.land_board) landBoard = data.land_board;

  if (data.center_tile_control) {
    centerTileControl = data.center_tile_control;
  }
  

  if (data.turn && data.turn !== turn) {
    notify('green', data.turn === userId ? "Your turn" : "Opponent's turn");
  }
  turn = data.turn;

  if (data.hand1) hand1 = data.hand1;
  if (data.hand2) hand2 = data.hand2;

  if (data.deck_sizes) {
    const myCount = data.deck_sizes[userId];
    const opponentId = userId === '1' ? '2' : '1';
    const oppCount = data.deck_sizes[opponentId];

    document.getElementById('deckCount').innerText = `${myCount} card${myCount === 1 ? '' : 's'}`;
    document.getElementById('opponentDeckCount').innerText = `${oppCount} card${oppCount === 1 ? '' : 's'}`;
  }

  if (data.mana) {
    mana = data.mana;
    const opponentId = userId === '1' ? '2' : '1';

    document.getElementById('manaH6').innerText = `Mana: ${mana[userId]}`;
    document.getElementById('opponentManaH6').innerText = `Opponent Mana: ${mana[opponentId]}`;
  }

  if (data.graveyard) {
    graveyard1 = data.graveyard['1'] || graveyard1;
    graveyard2 = data.graveyard['2'] || graveyard2;
  }

  // 🔊 Sound effects
  if (data.success) {
    if (data.info?.includes("summoned")) {
      playSound("spawnSound");
      lastSummonedPos = data.to ? data.to.join("-") : null;
    } else {
      lastSummonedPos = null;
    }

    if (data.info?.includes("Move successful")) playSound("moveSound");
    if (data.info?.includes("defeated") || data.info?.includes("killed")) playSound("deathSound");
    if (data.info?.includes("attacked directly")) playSound("deathSound");
    if (data.info?.includes("activated") || data.info?.includes("cast")) playSound("spawnSound");
  }

  // 🏁 Handle game over
  if (data.type === 'game-over') {
    const result = data.game_over?.result;
    if (result === 'victory') notify("green", "🏆 Victory! You win!");
    if (result === 'defeat') notify("red", "💀 You lose!");
    document.getElementById("endTurnBtn").disabled = true;
    boardEl.style.pointerEvents = 'none';
  }

// STEP 1: Capture previous positions
const previousCards = {};
document.querySelectorAll('[id^="card-"]').forEach(el => {
  previousCards[el.id] = el.getBoundingClientRect();
});

  // 🖼️ Render updates
  renderHand();
  renderOpponentHand();
  renderBoard();
  renderGraveyards();

// STEP 2: After DOM updates
requestAnimationFrame(() => {
  document.querySelectorAll('[id^="card-"]').forEach(el => {


    
    const newRect = el.getBoundingClientRect();
    const oldRect = previousCards[el.id];
    if (!oldRect) return;

    const dx = oldRect.left - newRect.left;
    const dy = oldRect.top - newRect.top;

    // Clone the element for animation
    const clone = el.cloneNode(true);
    const parent = el.parentNode;
        // Hide the real card while the clone animates
el.style.visibility = 'hidden';
    const { width, height } = newRect;

    Object.assign(clone.style, {
      position: "absolute",
      width: `${width}px`,
      height: `${height}px`,
      top: `${oldRect.top}px`,
      left: `${oldRect.left}px`,
      margin: 0,
      zIndex: 9999,
      pointerEvents: "none",
    });

    document.body.appendChild(clone);

    gsap.to(clone, {
      top: newRect.top,
      left: newRect.left,
      duration: 0.4,
      ease: "power2.out",
      onComplete: () => {
        clone.remove();
        el.style.visibility = 'visible';
        el.style.transform = ''; // 🔥 clear inline transform to restore hover effect
      }
    });
  });
});

  if (data.moves_left !== undefined) {
    document.getElementById('movesLeft').innerText = `Moves left: ${data.moves_left}`;
  }

  // ⚠️ Error message
  if (data.info && !data.success) {
    notify('red', data.info);
  }
};


function renderHand() {
  const handDiv = document.getElementById('hand');
  handDiv.innerHTML = '';

  const playerHand = userId === '1' ? hand1 : hand2;

  playerHand.forEach((card, i) => {
    const cardEl = document.createElement('div');
    cardEl.className = `hand-card user-${card.owner}`;
    cardEl.style.backgroundImage = `url(${card.image})`;
    cardEl.style.backgroundSize = 'cover';
    cardEl.style.backgroundPosition = 'center';
    cardEl.style.position = 'relative';
    cardEl.style.color = 'white';
    cardEl.style.textShadow = '0 0 4px black';
    cardEl.id = `card-${card.id}`;
    if (card.owner === userId) {
      // Add shared preview on hover
      cardEl.onmouseenter = () => {
        showCardPreview(card);
        cardEl.classList.add('hovered');
      };
      
      cardEl.onmouseleave = () => {
        cardEl.classList.remove('hovered');
      };


      // 👾 Monster Card
      if (card.type === 'monster') {
        const info = document.createElement('div');
        info.className = 'card-info';
        info.innerText = `${card.name}\n${card.attack} / ${card.defense}`;
        styleCardInfo(info);
        cardEl.appendChild(info);

        cardEl.onclick = () => {
          selectedHandIndex = i;
          highlightSummonZones();
        };
      }

      // 🔥 Sorcery Card
      else if (card.type === 'sorcery') {
        const info = document.createElement('div');
        info.className = 'card-info';
        info.innerText = `${card.name}\n(Sorcery)`;
        styleCardInfo(info);
        cardEl.appendChild(info);

        const label = document.createElement('div');
        label.innerText = 'SORCERY';
        label.style.position = 'absolute';
        label.style.bottom = '0.3vh';
        label.style.left = '0.3vw';
        label.style.padding = '0.3vh 0.6vw';
        label.style.background = 'rgba(255, 255, 255, 0.2)';
        label.style.fontSize = '1.0vw';
        label.style.color = 'white';
        label.style.borderRadius = '0.16vw';
        cardEl.appendChild(label);

        cardEl.onclick = () => {
          selectedHandIndex = i;
          // For now, no special highlight
          highlightPlaceActivateZones();  // 👈 new behavior
        };
      }

      else if (card.type === 'land') {
        const info = document.createElement('div');
        info.className = 'card-info';
        info.innerText = `${card.name}\n(Land)`;
        styleCardInfo(info);
        cardEl.appendChild(info);

        const label = document.createElement('div');
        label.innerText = 'LAND';
        label.style.position = 'absolute';
        label.style.bottom = '0.3vh';
        label.style.left = '0.3vw';
        label.style.padding = '0.3vh 0.6vw';
        label.style.background = 'rgba(255, 255, 255, 0.2)';
        label.style.fontSize = '1.0vw';
        label.style.color = 'white';
        label.style.borderRadius = '0.16vw';
        cardEl.appendChild(label);

        cardEl.onclick = () => {
          selectedHandIndex = i;
          // For now, no special highlight
          highlightPlaceActivateZones();  // 👈 new behavior
        };
      }

      // 🪨 Unknown type fallback
      else {
        const info = document.createElement('div');
        info.className = 'card-info';
        info.innerText = card.name;
        styleCardInfo(info);
        cardEl.appendChild(info);
      }

      if (window.pendingDiscard){

        cardEl.onclick = () => {
          ws.send(JSON.stringify({ type: 'end-turn-with-discard', user_id: card.owner, slot: i }));
        }
      } 

    } else {
      cardEl.innerText = '🂠'; // Back of opponent card
    }

    handDiv.appendChild(cardEl);
  });

  if (window.pendingDiscard) {
    window.pendingDiscard = false;
  }
}

function styleCardInfo(info) {
  info.style.position = 'absolute';
  info.style.top = '1vh';
  info.style.left = '0.5vw';
  info.style.right = '0.5vw';
  info.style.fontSize = '1.12vw';
  info.style.background = 'rgba(0, 0, 0, 0.5)';
  info.style.borderRadius = '0.62vw';
}


function renderOpponentHand() {
  const opponentHandDiv = document.getElementById('opponent-hand');
  opponentHandDiv.innerHTML = '';

  const opponentHand = userId === '1' ? hand2 : hand1;

  opponentHand.forEach((card, i) => {
    const cardEl = document.createElement('div');
    cardEl.className = `hand-card opponent-card user-${card.owner}`;
    cardEl.innerText = '🂠'; // optional or just leave blank
    opponentHandDiv.appendChild(cardEl);
  });
}

function renderGraveyards() {
  const myGraveyard = document.getElementById('graveyard');
  const oppGraveyard = document.getElementById('opponent-graveyard');

  myGraveyard.innerHTML = '';
  oppGraveyard.innerHTML = '';

  const myGrave = userId === '1' ? graveyard1 : graveyard2;
  const oppGrave = userId === '1' ? graveyard2 : graveyard1;

  myGrave.forEach((card, index) => {
    const cardDiv = document.createElement('div');
    cardDiv.className = 'grave-card';
    cardDiv.style.backgroundImage = `url(${card.image})`;
    cardDiv.title = card.name;
    cardDiv.id = `card-${card.id}`;
  
    // Stack effect: each card is shifted 2px up and left
    cardDiv.style.top = `${-index * 2}px`;
    cardDiv.style.left = `${-index * 2}px`;
  
    myGraveyard.appendChild(cardDiv);
  });
  
  oppGrave.forEach((card, index) => {
    const cardDiv = document.createElement('div');
    cardDiv.className = 'grave-card';
    cardDiv.style.backgroundImage = `url(${card.image})`;
    cardDiv.title = card.name;
    cardDiv.id = `card-${card.id}`;
    cardDiv.style.top = `${-index * 2}px`;
    cardDiv.style.left = `${-index * 2}px`;
  
    oppGraveyard.appendChild(cardDiv);
  });
  
}



function renderBoard() {
  document.querySelectorAll('.summon-zone').forEach(cell => {
    cell.classList.remove('summon-zone');
  });
  if (turn === userId){
    turnH5.innerText = "Your turn";
 

  } else {  
    turnH5.innerText = (turn === userId) ? "Your turn" : "Opponent's turn";
 
  }
 boardEl.innerHTML = '';

  const numRows = board.length;
  const numCols = board[0]?.length || 0;

  boardEl.style.gridTemplateColumns = `repeat(${numCols}, ${cellSize}vh)`;
  boardEl.style.gridTemplateRows = `repeat(${numRows}, ${cellSize}vh)`;

  const flipped = userId === '2';
  const rowRange = flipped ? [...Array(numRows).keys()].reverse() : [...Array(numRows).keys()];
  const colRange = flipped ? [...Array(numCols).keys()].reverse() : [...Array(numCols).keys()];



  for (let x of rowRange) {
    for (let y of colRange) {
      const cell = document.createElement('div');



      cell.className = 'cell ' + ((x + y) % 2 === 0 ? 'white' : 'black');
      cell.dataset.x = x;
      cell.dataset.y = y;

      const isCenter = x === 3 && y === 3;
      if (isCenter) {
        const centerCount = centerTileControl || { '1': 0, '2': 0 };
        const count1 = centerCount['1'];
        const count2 = centerCount['2'];
        const owner = count1 > 0 && count2 === 0 ? '1'
                    : count2 > 0 && count1 === 0 ? '2'
                    : null;
      
        const label = document.createElement('div');
        label.id = 'centerCounter';
        label.className = 'center-counter';
      
        if (owner === '1') label.classList.add('blue');
        else if (owner === '2') label.classList.add('orange');
      
        // 👇 Always show one of the counts, even if both are 0
        label.innerText = owner === '1' ? count1
                         : owner === '2' ? count2
                         : 0;
      
        cell.appendChild(label);
      }
      

      const overlay = document.createElement('div');
      overlay.className = 'cell-overlay';
      cell.appendChild(overlay);

      const boardCard = board[x][y];
      const landCard = landBoard[x][y];

      for (let card of [landCard, boardCard ]){
        if (card) {
          const cardFrame = document.createElement('div');
          cardFrame.className = `card-frame ${card.owner === '1' ? 'user-1' : 'user-2'}`;
  
          if (`${x}-${y}` === lastSummonedPos) {
            cardFrame.classList.add("just-summoned");
            // Remove the class after animation ends
            cardFrame.addEventListener("animationend", () => {
              cardFrame.classList.remove("just-summoned");
            });
          }
          const imageDiv = document.createElement('div');
          imageDiv.className = 'card-image';
          imageDiv.style.backgroundImage = `url(${card.image})`;
  
          if (card.owner !== userId) {
            imageDiv.classList.add('flipped-image');
          }
  
          cardFrame.appendChild(imageDiv);
  
  
          cardFrame.style.position = 'relative';
          cardFrame.style.color = 'white';
          cardFrame.style.textShadow = '0 0 3px black';
          cardFrame.style.backdropFilter = 'brightness(0.8)';
          const overlay = document.createElement('div');
          overlay.className = 'overlay';
          cardFrame.appendChild(overlay);
  
          const nameDiv = document.createElement('div');
          nameDiv.className = 'card-name';
          nameDiv.textContent = card.name;
          cardFrame.appendChild(nameDiv);
  
          // 👉 Add the name as a tooltip
          cardFrame.title = card.name;
  
          cardFrame.onmouseenter = () => {
            showCardPreview(card);
          };
  
          
          const statsDiv = document.createElement('div');
          statsDiv.className = 'stats';
          cardFrame.appendChild(statsDiv);
  
  
          if (card.attack !== undefined && card.defense !== undefined) {
            const attackSpan = document.createElement('span');
            const defenseSpan = document.createElement('span');
          
            // Check for attack change
            if (card.attack > card.original_attack) {
              attackSpan.style.color = 'lime';
            } else if (card.attack < card.original_attack) {
              attackSpan.style.color = 'red';
            }
          
            // Check for defense change
            if (card.defense > card.original_defense) {
              defenseSpan.style.color = 'lime';
            } else if (card.defense < card.original_defense) {
              defenseSpan.style.color = 'red';
            }
          
            attackSpan.textContent = card.attack;
            defenseSpan.textContent = card.defense;
          
            statsDiv.appendChild(attackSpan);
            statsDiv.appendChild(document.createTextNode(' / '));
            statsDiv.appendChild(defenseSpan);
          }
          
          cardFrame.id = `card-${card.id}`;

          if (card.type == 'land'){
            cardFrame.style.transform = "rotate(45deg)"
          }
  
          cell.appendChild(cardFrame);
  
          if (card.movement) {
            for (const dir in card.movement) {
              if (card.movement[dir]) {
                const finalDir = card.owner === userId ? dir : flipDirection(dir);
                const arrow = document.createElement('div');
                arrow.className = `movement movement-${finalDir}`;
                arrow.style.borderColor = (card.movement[dir] === 'any') ? 'red' : 'lime';
                cardFrame.appendChild(arrow);
              }
            }
          } else if (card.creation_needs && Array.isArray(card.creation_needs)) {
            for (const dir of card.creation_needs) {
              const finalDir = card.owner === userId ? dir : flipDirection(dir);
              const arrow = document.createElement('div');
              arrow.className = `movement movement-${finalDir}`;
              arrow.style.borderColor = 'white';
              cardFrame.appendChild(arrow);
            }
          }
          
  
        }
      }


      if (x === 3 && y === 3) {
        const centerCounter = document.createElement('div');
        centerCounter.id = 'centerCounter';
        centerCounter.className = 'center-counter';
        cell.appendChild(centerCounter);
      }

      cell.onclick = () => handleClick(x, y, cell);
      boardEl.appendChild(cell);
    }
  }

  if (selectedHandIndex !== null) {
    highlightSummonZones();
  }

  
  console.log('rendered')

}

function showCardPreview(card) {
  const preview = document.getElementById('cardPreview');
  preview.innerHTML = '';

  const cardEl = document.createElement('div');
  cardEl.classList.add('play-card');

  // Set font size based on screen width
  cardEl.style.fontSize = window.innerWidth < 1120 ? '8px' : '14px';


  // Add theme class based on type
  if (card.type === 'monster') {
    cardEl.classList.add('monster-card');
  } else if (card.type === 'sorcery') {
    cardEl.classList.add('sorcery-card');
  } else if (card.type === 'land') {
    cardEl.classList.add('land-card');
  }

  const content = document.createElement('div');
  content.className = 'card-content';

  // 🔺 Directional Arrows (Monster = red/yellow, Sorcery/Land = white)
  if (card.movement) {
    for (const dir in card.movement) {
      if (card.movement[dir]) {
        const arrow = document.createElement('div');
        arrow.className = `arrow ${dir}`;
        arrow.classList.add(card.movement[dir] === 'any' ? 'red' : 'yellow');
        content.appendChild(arrow);
      }
    }
  } else if ((card.type === 'sorcery') && Array.isArray(card.activation_needs)) {
    for (const dir of card.activation_needs) {
      const arrow = document.createElement('div');
      arrow.className = `arrow ${dir} white`;
      content.appendChild(arrow);
    }
  } else if ((card.type === 'land') && Array.isArray(card.creation_needs)) {
    for (const dir of card.creation_needs) {
      const arrow = document.createElement('div');
      arrow.className = `arrow ${dir} white`;
      content.appendChild(arrow);
    }
  }

  // 🧠 Title + Mana Cost
  const title = document.createElement('div');
  title.className = 'title-bar';
  title.innerHTML = `${card.name}<div class="mana-cost">🩸 ${card.mana || 0}</div>`;
  content.appendChild(title);

  // 🎨 Image Area
  const image = document.createElement('div');
  image.className = 'card-image';
  if (card.image) {
    image.style.backgroundImage = `url(${card.image})`;
    image.style.backgroundSize = 'cover';
    image.style.backgroundPosition = 'center';
  }
  content.appendChild(image);

  // 🧬 Type Line
  const typeLine = document.createElement('div');
  typeLine.className = 'type-line';
  typeLine.innerText = card.subtype || (card.type ? `(${card.type})` : '');
  content.appendChild(typeLine);

  // 📜 Rules Text
  const rules = document.createElement('div');
  rules.className = 'rules-text';
  rules.innerText = card.text || card.description || 'No effect.';
  content.appendChild(rules);

  // 🛡️ Stats (Only for Monsters)
  const stats = document.createElement('div');
  stats.className = 'stats-bar';
  if (card.attack && card.defense) {
    stats.innerHTML = `<span>ATK: ${card.attack}</span><span>DEF: ${card.defense}</span>`;
  } else {
    stats.innerHTML = `<span></span><span></span>`;
  }
  content.appendChild(stats);

  // 🧩 Assemble
  cardEl.appendChild(content);
  preview.appendChild(cardEl);
}





function highlightSummonZones() {
  const validCols = [0, 3, 6];
  const summonRow = userId === '1' ? 6 : 0;

  validCols.forEach(col => {
    const selector = `.cell[data-x="${summonRow}"][data-y="${col}"]`;
    const cell = document.querySelector(selector);
    if (cell) {
      cell.classList.add('summon-zone');
    }
  });
}

function highlightMoves(x, y, card) {
  clearMoveHighlights();

  const movement = card.movement;
  const directions = {
    "forward": userId == 1 ? [-1, 0]: [1, 0],
    "back":  userId == 1 ? [1, 0]: [-1, 0],
    "left": userId == 1 ? [0, -1] : [0, 1],
    "right": userId == 1 ?  [0, 1] : [0, -1],
    "forward-left": userId == 1 ?  [-1, -1] : [1, 1],
    "forward-right":  userId == 1 ? [-1, 1] : [1, -1],
    "back-left": userId == 1 ?  [1, -1]: [-1, 1],
    "back-right": userId == 1 ?  [1, 1]: [-1, -1],
  };

  const maxRange = 7;

  for (const dir in movement) {
    const vector = directions[dir];
    if (!vector) continue;

    const range = movement[dir] === 'any' ? maxRange : movement[dir];

    for (let step = 1; step <= range; step++) {
      const nx = x + vector[0] * step;
      const ny = y + vector[1] * step;
      if (nx < 0 || nx >= 7 || ny < 0 || ny >= 7) break;

      const cell = document.querySelector(`.cell[data-x="${nx}"][data-y="${ny}"]`);
      if (!cell) break;

      const overlay = cell.querySelector('.cell-overlay');
      const occupant = board[nx][ny];
      if (occupant) {
        if (occupant.owner !== userId) {
          overlay.classList.add(userId === '1' ? 'can-attack-blue' : 'can-attack-orange');
        }
        break;
      }

      overlay.classList.add(userId === '1' ? 'can-move-blue' : 'can-move-orange');
    }
  }
}


function clearMoveHighlights() {
  document.querySelectorAll('.cell-overlay').forEach(overlay => {
    overlay.className = 'cell-overlay'; // Reset all
  });
}


async function handleClick(x, y, cell) {

  if (window.pendingSorcery) {
    const { slot } = window.pendingSorcery;
    ws.send(JSON.stringify({
      type: 'resolve-sorcery',
      slot: slot,
      target: [x, y]
    }));
  
    window.pendingSorcery = null;
    clearMoveHighlights();
    return;
  }
  


  const hand = userId === '1' ? hand1 : hand2;
  const selectedCard = hand[selectedHandIndex];

  // 🖐 Card in hand is selected
  if (selectedHandIndex !== null) {
    if (!selectedCard) return;

    if (selectedCard.mana > mana[userId]) {
      notify("red", "Not enough mana to use this card.");
      return;
    }

    if (selectedCard.type === 'monster') {
      const validCols = [0, 3, 6];
      const summonRow = userId === '1' ? 6 : 0;

      if (x === summonRow && validCols.includes(y)) {
        confirmAction(
          `Spend ${selectedCard.mana} mana to summon ${selectedCard.name}?`,
          "Yes, summon!",
          "Cancel",
           () => {
             ws.send(JSON.stringify({
              type: 'summon',
              user_id: userId,
              slot: selectedHandIndex,
              to: [x, y]
            }));
            selectedHandIndex = null;
            clearMoveHighlights();
          }
        );
      } else {
        notify("yellow", "Invalid summon position.");
      }

    } else if (selectedCard.type === 'sorcery') {
      // 👇 Full board activation allowed
      confirmAction(
        `Spend ${selectedCard.mana} mana to activate ${selectedCard.name} on this tile?`,
        "Activate!",
        "Cancel",
        () => {
          ws.send(JSON.stringify({
            type: 'activate-sorcery',
            user_id: userId,
            slot: selectedHandIndex,
            pos: [x, y]
          }));
          selectedHandIndex = null;
          clearMoveHighlights();
        }
      );
    } else if (selectedCard.type === 'land') {
      // 👇 Full board activation allowed
      confirmAction(
        `Spend ${selectedCard.mana} mana to create ${selectedCard.name} on this tile?`,
        "Create!",
        "Cancel",
        () => {
          ws.send(JSON.stringify({
            type: 'place-land',
            user_id: userId,
            slot: selectedHandIndex,
            pos: [x, y]
          }));
          selectedHandIndex = null;
          clearMoveHighlights();
        }
      );
    }

    return;
  }

  // 🧭 Board click (after selection)
  if (userId !== turn) return notify('red', 'Not your turn!');

  const card = board[x][y];

  if (selected) {
    const from = selected;
    const to = [x, y];
    ws.send(JSON.stringify({
      type: 'move',
      from,
      to,
      user_id: userId
    }));
    selected = null;
    clearMoveHighlights();
  } else {
    if (card && card.owner === userId) {
      const backRow = userId === '1' ? 0 : 6;

      // 👊 Direct attack
      if (x === backRow) {
        confirmAction(
          `Attack directly with ${card.name} and deal ${card.mana} damage?`,
          "Attack!",
          "Cancel",
          () => {
            ws.send(JSON.stringify({
              type: 'direct-attack',
              user_id: userId,
              pos: [x, y]
            }));
            
            selected = null;
          }, () => {
            selected = [x, y];
            cell.classList.add('selected');
            highlightMoves(x, y, card);
          }
        );
        return;
      }

      selected = [x, y];
      cell.classList.add('selected');
      highlightMoves(x, y, card);
    } else if (cell.innerText) {
      notify('red', 'Not your card');
    } else {
      notify('red', 'Please select a card');
    }
  }
}

function highlightPlaceActivateZones() {
  clearMoveHighlights();

  const hand = userId === '1' ? hand1 : hand2;
  const card = hand[selectedHandIndex];
  const needs = card?.activation_needs || card?.creation_needs;
  if (!card || !Array.isArray(needs)) return;

  const directions = {
    "forward": userId === '1' ? [-1, 0] : [1, 0],
    "back": userId === '1' ? [1, 0] : [-1, 0],
    "left": userId === '1' ? [0, -1] : [0, 1],
    "right": userId === '1' ? [0, 1] : [0, -1],
    "forward-left": userId === '1' ? [-1, -1] : [1, 1],
    "forward-right": userId === '1' ? [-1, 1] : [1, -1],
    "back-left": userId === '1' ? [1, -1] : [-1, 1],
    "back-right": userId === '1' ? [1, 1] : [-1, -1]
  };

  const flipDirection = {
    "forward": "back",
    "back": "forward",
    "left": "right",
    "right": "left",
    "forward-left": "back-right",
    "forward-right": "back-left",
    "back-left": "forward-right",
    "back-right": "forward-left"
  };

  for (let x = 0; x < board.length; x++) {
    for (let y = 0; y < board[0].length; y++) {
      let satisfiesAll = true;

      for (const dir of needs) {
        const [dx, dy] = directions[dir];
        const tx = x + dx;
        const ty = y + dy;

        if (tx < 0 || tx >= 7 || ty < 0 || ty >= 7) {
          satisfiesAll = false;
          break;
        }

        const neighbor = board[tx][ty];
        const land = landBoard?.[tx]?.[ty];
        let valid = false;

        if (neighbor && neighbor.type === 'monster') {
          const baseOpposite = flipDirection[dir];
          const effectiveDir = neighbor.owner === userId ? baseOpposite : flipDirection[baseOpposite];
          const movementVal = neighbor.movement?.[effectiveDir];
          if (movementVal === 1 || movementVal === 'any') {
            valid = true;
          }
        }

        if (land && land.creation_needs?.includes(flipDirection[dir])) {
          valid = true;
        }

        if (!valid) {
          satisfiesAll = false;
          break;
        }
      }

      if (satisfiesAll) {
        const cell = document.querySelector(`.cell[data-x="${x}"][data-y="${y}"]`);
        if (cell) {
          const overlay = cell.querySelector('.cell-overlay');
          overlay.classList.add(userId === '1' ? 'can-move-blue' : 'can-move-orange');
        }
      }
    }
  }
}






function notify(color, message) {
  const container = document.getElementById('notification-container');
  const note = document.createElement('div');
  note.className = `notification ${color}`;
  note.textContent = message;

  container.appendChild(note);

  setTimeout(() => {
    note.remove();
  }, 3000); // Clean up after animation
}

function confirmAction(message, yesMessage, noMessage, onYes, onNo = () => {}) {
  const overlay = document.getElementById('confirmation-overlay');
  const messageEl = document.getElementById('confirmation-message');
  const yesBtn = document.getElementById('confirm-yes');
  const noBtn = document.getElementById('confirm-no');
  yesBtn.innerText = yesMessage;
  noBtn.innerText = noMessage;

  messageEl.textContent = message;
  overlay.style.display = 'flex';

  const cleanup = () => {
    overlay.style.display = 'none';
    yesBtn.onclick = null;
    noBtn.onclick = null;
  };

  yesBtn.onclick = () => {
    cleanup();
    onYes();
  };

  noBtn.onclick = () => {
    cleanup();
    onNo();
  };
}



function clearSelection() {
  selected = null;
  selectedHandIndex = null;
  clearMoveHighlights();
  document.querySelectorAll('.selected').forEach(el => el.classList.remove('selected'));
  document.querySelectorAll('.summon-zone').forEach(el => el.classList.remove('summon-zone'));
}

document.addEventListener('contextmenu', (e) => {
  e.preventDefault();
  clearSelection();
});

let touchTimer = null;

document.addEventListener('touchstart', () => {
  touchTimer = setTimeout(() => {
    clearSelection();
  }, 600); // Long press = 600ms
});

document.addEventListener('touchend', () => {
  clearTimeout(touchTimer);
});


