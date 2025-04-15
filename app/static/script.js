let currentDifficulty;
let currentBoard;
let boardMask;
let history = [];
let timerInterval;
let seconds = 0;
let lang = document.documentElement.lang;

const winMessagesEN = [
    "Congratulations! 🎉",
    "Well done! 🎉",
    "Great job! 👍",
    "You did it! 👏",
    "Puzzle solved! 🧩",
    "Victory! 🏆",
    "Success! ✅",
    "Nicely done! 🙌",
    "Impressive! 😲",
    "Huge W! 💪",
    "You cracked the code! 🔓",
    "Winner winner, Sudoku dinner! 🍽️",
    "Sherlock would be proud. 🕵️‍♂️",
    "Brains of steel! 🤯",
    "Your brain deserves a trophy. 🏅",
    "Big brain moment! 🧠",
    "GG, nice solve bro. 👏",
    "And they said it couldn’t be done. 🤷‍♂️"
];

const winMessagesPL = [
    "Gratulacje! 🎉",
    "Dobra robota! 🎉",
    "Świetna robota! 👍",
    "Udało się! 👏",
    "Zagadkę rozwiązano! 🧩",
    "Zwycięstwo! 🏆",
    "Sukces! ✅",
    "Świetnie Ci poszło! 🙌",
    "Imponujące! 😲",
    "Huge W! 💪",
    "Złamałeś kod! 🔓",
    "Winner winner, Sudoku dinner! 🍽️",
    "Sherlock byłby dumny. 🕵️‍♂️",
    "Mózg ze stali! 🤯",
    "Twój mózg zasługuje na trofeum. 🏅",
    "Big brain moment! 🧠",
    "GG, dobra robota, byku. 👏",
    "A mówili, że się nie da. 🤷‍♂️"
];

// czysci historie
function clearHistory(){
    history = [];
}

// funkcja glowna uruchamiajaca gre
async function startGame(difficulty) {
    const container = document.getElementById("game-container");
    currentDifficulty = difficulty;
    
    const puzzle = await getPuzzle(difficulty);
    if (puzzle) {
        container.classList.remove("d-none");
        createBoard(puzzle);
        stopTimer();
        startTimer();
    } else {
        container.classList.add("d-none");
        document.getElementById("alert").classList.remove("d-none");
        closeErrorAlert();
    }
}

// funkcja wczytujaca plansze sudoku z pliku
async function getPuzzle(name) {
    const filename = `../vendor/sudoku-exchange-puzzle-bank/${name}.txt`;
    try {
        const response = await fetch(filename);
        if (!response.ok) throw new Error("Nie udało się pobrać planszy.");

        const text = await response.text();

        const puzzleData = text.split('\n');
        const count = puzzleData.length - 1;

        const randomIndex = Math.floor(Math.random() * count);

        const puzzle = puzzleData[randomIndex].split(' ');

        return puzzle[1];

    } catch (err) {
        console.error("Błąd ładowania planszy:", err);
        return null;
    }
}

// funkcja tworzaca maske bezpieczenstwa
function createBoardMask(board){
    return board
        .split('')
        .map(char => char === '0' ? '0' : '1')
        .join('');
}

// funkcja tworzaca maske '1' zeby zablokowac edycje komorek
function generateFullBoardMask() {
    return '1'.repeat(81);
}

// funkcja tworzaca plansze
function createBoard(board) {
    const table = document.getElementById("sudoku-table");
    table.innerHTML = ""; // czysci poprzednia plansze
    let cellIndex = 0;

    currentBoard = board;
    console.log(board);
    boardMask = createBoardMask(board);
    //console.log(boardMask);
    clearHistory();

    // przeksztalcenie stringa w tablicę 9x9
    const board2D = [];
    for (let i = 0; i < 9; i++) {
        const row = board.slice(i * 9, (i + 1) * 9).split('');
        board2D.push(row);
    }

    board2D.forEach((row, rowIndex) => {
        const tr = document.createElement("tr");
        row.forEach((cell, colIndex) => {
            const td = document.createElement("td");
            td.id = `r${rowIndex}c${colIndex}`
			td.classList.add("sudoku-cell");

            if (cell === '0') {
                td.textContent = "";
                td.setAttribute("contenteditable", "true");
            } else {
                td.textContent = cell;
                td.setAttribute("contenteditable", "false");
				td.classList.add("static");
            }

            td.dataset.index = cellIndex;
            td.dataset.row = rowIndex;
            td.dataset.col = colIndex;
            td.addEventListener("click", () => {
                highlightRelatedCells(rowIndex, colIndex);
                inputValidation();
            });
            td.addEventListener("input", () => {
                td.textContent = td.textContent.replace(/[^1-9]/g, '');
                saveBoardState();
                checkSolution();
            });
            tr.appendChild(td);
            cellIndex++;
        });
        table.appendChild(tr);
    });
    saveBoardState();
}

// funkcja walidujaca wprowadzane dane
function inputValidation(){
    document.addEventListener('keydown', (event) => {
        const activeCell = document.querySelector('.sudoku-cell.active');
        if (!activeCell) return;

        const i = parseInt(activeCell.dataset.index);

        // tylko jeśli pole jest edytowalne (czyli '0' w masce)
        if (boardMask[i] === '0') {
            const key = event.key;

            // tylko cyfry 1-9, backspace i delete
            if (!/^[1-9]$/.test(key) && key !== 'Backspace' && key !== 'Delete') {
                event.preventDefault();
                return;
            }

            // jeśli już jest cyfra, nie pozwalamy wpisać kolejnej
            if (activeCell.textContent.length >= 1 && /^[1-9]$/.test(key)) {
                event.preventDefault();
                return;
            }

        } else {
            // nieedytowalne pole – blokuj
            event.preventDefault();
            return;
        }
    });
}

// funkcja podswietlajaca wszystkie komorki w pionie i poziomie oraz takie same cyfry
function highlightRelatedCells(row, col) {
    const allCells = document.querySelectorAll('.sudoku-cell');
    allCells.forEach(cell => {
        cell.classList.remove('highlighted', 'same-number'),
        cell.classList.remove('active');
    });

    const selectedCell = document.getElementById(`r${row}c${col}`);
    const selectedValue = selectedCell.textContent || selectedCell.value;

    for (let i = 0; i < 9; i++) {
        document.getElementById(`r${row}c${i}`)?.classList.add('highlighted');
    }

    for (let i = 0; i < 9; i++) {
        document.getElementById(`r${i}c${col}`)?.classList.add('highlighted');
    }

    document.getElementById(`r${row}c${col}`)?.classList.add('active');

    if (selectedValue !== '') {
        allCells.forEach(cell => {
            if (cell.textContent === selectedValue) {
                cell.classList.add('same-number');
            }
        });
    }
}

// funkcja ustawiajaca w aktywnej komorce liczbe z przycisku
function setNumber(number) {
    if (isNaN(number) || number < 1 || number > 9) {
        number = ''; // Niepoprawna wartość — wyczyść
    }

    const activeCell = document.querySelector('.sudoku-cell.active'); // Znajdź aktywną komórkę
    if (activeCell) {
        if(activeCell.contentEditable === 'true'){
            activeCell.textContent = number; // Wstaw cyfrę do komórki
            saveBoardState();
        }
    }
}

// funkcja zapisujaca aktualny stan planszy
function saveBoardState() {
    const boardState = [];
    const allCells = document.querySelectorAll('.sudoku-cell');
    allCells.forEach(cell => {
        if (cell.hasAttribute('contenteditable')) {
            boardState.push(cell.textContent || '');
        }
    });
    history.push(boardState);
    //console.log(history);
}

// funkcja cofajaca do poprzedniego stanu planszy w liscie
function undo() {
    if (history.length > 1) {
        history.pop(); // Usuń ostatni stan (bo to aktualny stan)
        const previousState = history[history.length - 1]; // Pobierz poprzedni stan

        const allCells = document.querySelectorAll('.sudoku-cell');
        let index = 0;
        allCells.forEach(cell => {
            if (cell.hasAttribute('contenteditable')) {
                cell.textContent = previousState[index] || ''; // Przywróć poprzednią wartość
                index++;
            }
        });
    }
}

// funkcja resetujaca gre (wczytuje te sama plansze)
function resetBoard() {
    if (!(/^1{81}$/.test(boardMask))){
        const table = document.getElementById("sudoku-table");
        table.innerHTML = ""; // wyczyść poprzednią planszę
        let cellIndex = 0;

        clearHistory();
        startTimer();

        const board2D = [];
        for (let i = 0; i < 9; i++) {
            const row = currentBoard.slice(i * 9, (i + 1) * 9).split('');
            board2D.push(row);
        }

        board2D.forEach((row, rowIndex) => {
            const tr = document.createElement("tr");
            row.forEach((cell, colIndex) => {
                const td = document.createElement("td");
                td.id = `r${rowIndex}c${colIndex}`
                td.classList.add("sudoku-cell");

                if (cell === '0') {
                    td.textContent = "";
                    td.setAttribute("contenteditable", "true");
                } else {
                    td.textContent = cell;
                    td.setAttribute("contenteditable", "false");
                    td.classList.add("static");
                }

                td.dataset.index = cellIndex;
                td.dataset.row = rowIndex;
                td.dataset.col = colIndex;
                td.addEventListener("click", () => {
                    highlightRelatedCells(rowIndex, colIndex);
                    inputValidation();
                });
                td.addEventListener("input", () => {
                    saveBoardState();
                    checkSolution();
                });
                tr.appendChild(td);
                cellIndex++;
            });
            table.appendChild(tr);
        });
        saveBoardState();
    }
}

// funkcja sprawdzajaca czy wszystkie pola sa uzupelnione
function checkSolution() {
    const allCells = document.querySelectorAll('.sudoku-cell');
    let solution = '';
    
    // Sprawdzamy, czy wszystkie komórki są wypełnione
    const allFilled = Array.from(allCells).every(cell => {
        return cell.textContent !== '' && cell.textContent !== '0'; // Zakładając, że 0 jest traktowane jako puste
    });

    if (allFilled) {
        allCells.forEach(cell => {
            const value = cell.textContent.trim();
            solution += value === '' ? '0' : value;
        });
        if(solutionChecker(solution)){
            stopTimer();

            if(lang === "en"){
                const randomMsg = winMessagesEN[Math.floor(Math.random() * winMessagesEN.length)]

                document.getElementById("result-alert").classList.remove('d-none');
                
                document.getElementById("win-title").textContent=randomMsg;
                
                if (seconds >= 3600) {
                    const hours = Math.floor(seconds / 3600);
                    const minutes = Math.floor((seconds % 3600) / 60);
                    const remainingSeconds = seconds % 60;
                    document.getElementById("win-message").textContent=`You've just solved ${currentDifficulty} sudoku puzzle in ${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(remainingSeconds).padStart(2, '0')}`;
                } else {
                    const minutes = Math.floor(seconds / 60);
                    const remainingSeconds = seconds % 60;
                    document.getElementById("win-message").textContent=`You've just solved ${currentDifficulty} sudoku puzzle in ${String(minutes).padStart(2, '0')}:${String(remainingSeconds).padStart(2, '0')}`;
                }
            } else if(lang === "pl"){
                const randomMsg = winMessagesPL[Math.floor(Math.random() * winMessagesPL.length)]

                document.getElementById("result-alert").classList.remove('d-none');
                
                document.getElementById("win-title").textContent=randomMsg;

                let translatedDifficulty;

                if(currentDifficulty === "easy") translatedDifficulty = "łatwą";
                else if(currentDifficulty === "medium") translatedDifficulty = "średniozaawansowaną";
                else if(currentDifficulty === "hard") translatedDifficulty = "trudną";
                else if(currentDifficulty === "diabolical") translatedDifficulty = "ekspercką";
                
                if (seconds >= 3600) {
                    const hours = Math.floor(seconds / 3600);
                    const minutes = Math.floor((seconds % 3600) / 60);
                    const remainingSeconds = seconds % 60;
                    document.getElementById("win-message").textContent=`Właśnie rozwiązałeś ${translatedDifficulty} krzyżówkę sudoku w ${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(remainingSeconds).padStart(2, '0')}`;
                } else {
                    const minutes = Math.floor(seconds / 60);
                    const remainingSeconds = seconds % 60;
                    document.getElementById("win-message").textContent=`Właśnie rozwiązałeś ${translatedDifficulty} krzyżówkę sudoku w ${String(minutes).padStart(2, '0')}:${String(remainingSeconds).padStart(2, '0')}`;
                }
            }

            document.querySelectorAll('.sudoku-cell').forEach(cell => {
                cell.contentEditable = 'false';
            });
            
            boardMask = generateFullBoardMask();
            clearHistory();
            saveBoardState();

            if(userID){
                const loggedUserId = userID;
                const difficulty = currentDifficulty;
                const gameCompletionDate = new Date().toISOString();
                const gameTime = seconds;

                const isUserIDValid = typeof loggedUserId === 'number';
                const isDifficultyValid = typeof difficulty === 'string' && (difficulty === 'easy' || 
                                                                             difficulty === 'medium' || 
                                                                             difficulty === 'hard' || 
                                                                             difficulty === 'diabolical');
                const isDateValid = typeof gameCompletionDate === 'string' && !isNaN(Date.parse(gameCompletionDate));
                const isTimeValid = typeof gameTime === 'number' && gameTime >= 0;

                if(isUserIDValid && isDifficultyValid && isDateValid && isTimeValid){
                    const data = {
                        user_id: loggedUserId,
                        difficulty: difficulty,
                        date_played: gameCompletionDate,
                        time_finished: gameTime
                    };
    
                    fetch('/save_result', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(data)
                    })
                    .then(res => res.json())
                    .then(response => {
                        console.log("Serwer odpowiedział:", response);
                    })
                    .catch(error => {
                        console.error("Błąd wysyłki do backendu:", error);
                    });
                }
            }
        }
    }
}

// funkcja sprawdzajaca czy podane liczby sa rozwiazaniem tej planszy sudoku
function solutionChecker(solution) {

    const board2D = [];
    for (let i = 0; i < 9; i++) {
        const row = solution.slice(i * 9, (i + 1) * 9).split('');
        board2D.push(row);
    }

    for (let row = 0; row < 9; row++) {
        const seen = new Set();
        for (let col = 0; col < 9; col++) {
            const value = board2D[row][col];
            //console.log(`Checking value ${value} at row ${row}, col ${col}`);
            if (seen.has(value)) {
                //console.log(`Duplicate found in row: ${row} value: ${value}`);
                return false;
            }
            seen.add(value);
        }
        //console.log("Row " + row + " unique values: " + Array.from(seen));
    }

    for (let col = 0; col < 9; col++) {
        const seen = new Set();
        for (let row = 0; row < 9; row++) {
            const value = board2D[row][col];
            //console.log(`Checking value ${value} at col ${col}, row ${row}`);
            if (seen.has(value)) {
                //console.log(`Duplicate found in column: ${col} value: ${value}`);
                return false;
            }
            seen.add(value);
        }
        //console.log("Column " + col + " unique values: " + Array.from(seen));
    }

    for (let startRow = 0; startRow < 9; startRow += 3) {
        for (let startCol = 0; startCol < 9; startCol += 3) {
            const seen = new Set();
            //console.log(`Checking 3x3 box starting at (${startRow}, ${startCol})`);
            for (let row = 0; row < 3; row++) {
                for (let col = 0; col < 3; col++) {
                    const value = board2D[startRow + row][startCol + col];
                    //console.log(`Checking value ${value} in 3x3 box`);
                    if (seen.has(value)) {
                        //console.log(`Duplicate found in 3x3 box: value ${value}`);
                        return false;
                    }
                    seen.add(value);
                }
            }
            //console.log("3x3 box " + (startRow / 3) + ", " + (startCol / 3) + " unique values: " + Array.from(seen));
        }
    }
    return true; // Wszystkie warunki spełnione
}

// funkcja uruchamiajaca stoper
function startTimer() {
    if (timerInterval) { clearInterval(timerInterval); }

    document.getElementById("timer").textContent = "00:00";
    seconds = 0;

    timerInterval = setInterval(() => {
        seconds++; 
        const minutes = Math.floor(seconds / 60);
        const displaySeconds = seconds % 60;

        document.getElementById("timer").textContent = `${String(minutes).padStart(2, '0')}:${String(displaySeconds).padStart(2, '0')}`;
    }, 1000);
}

// funkcja zatrzymujaca stoper
function stopTimer() {
    clearInterval(timerInterval);
}

// funkcje dotyczace alertow
function closeAlert() {
    setTimeout(function() {
        const alertElement = document.getElementById('alert');
        if (alertElement) {
            alertElement.classList.remove('show');
            alertElement.classList.add('fade');
        }
    }, 5000);
}

function closeErrorAlert(){
    setTimeout(function() {
        const alertElement = document.getElementById('alert');
        if (alertElement) {
            alertElement.classList.add('d-none');
            alertElement.classList.add('show');
            alertElement.classList.remove('fade');
        }
    }, 6000);
}

function hideErrorDisplay(){
    document.getElementById('alert').classList.add('d-none');
}

function hideResultDisplay(){
    document.getElementById('result-alert').classList.add('d-none');
}