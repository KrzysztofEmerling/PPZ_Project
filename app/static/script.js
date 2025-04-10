function selection(){
    let selectedNumber = null;                   
    function setNumber(number) {
        selectedNumber = number;
    }
                        
    function fillCell(cellId) {
        const cell = document.getElementById(cellId);
        if (selectedNumber !== null && cell.value === "") {
            cell.value = selectedNumber;
        }
    }
}
let selectedNumber = null;
let selectedCellId = null;
let isEraserMode = false;
let sudokuSolution = null; // <- Uzupełnij to rozwiązaniem lub załaduj z backendu

function createBoard() {
    const table = document.getElementById('sudoku-table');
    table.innerHTML = '';

    for (let row = 0; row < 9; row++) {
        const tr = document.createElement('tr');
        for (let col = 0; col < 9; col++) {
            const td = document.createElement('td');
            const id = `R${row}C${col}`;
            const input = document.createElement('input');

            input.type = 'text';
            input.maxLength = 1;
            input.pattern = '[1-9]';

            input.classList.add('sudoku-cell');
            input.id = id;
            input.value = '';
            input.readOnly = false;
            input.addEventListener('input', (e) => {
                const val = e.target.value;
                if (!/^[1-9]?$/.test(val)) {
                    e.target.value = ''; // usuwa nieprawidłowe znaki
                }
            });
            
            input.addEventListener('keypress', (e) => {
                if (!/[1-9]/.test(e.key)) {
                    e.preventDefault(); // blokuje wpisanie innych znaków
                }
            });
            

            const inShadedBox = (Math.floor(row / 3) + Math.floor(col / 3)) % 2 === 0;
            if (inShadedBox) input.classList.add('section-3x3');

            input.addEventListener('click', () => selectCell(id));

            td.appendChild(input);
            tr.appendChild(td);
        }
        table.appendChild(tr);
    }
}

function selectCell(cellId) {
    if (selectedCellId) {
        document.getElementById(selectedCellId).classList.remove('selected-cell');
    }

    selectedCellId = cellId;
    const cell = document.getElementById(cellId);

    if (!cell.readOnly) {
        cell.classList.add('selected-cell');

        if (isEraserMode) {
            cell.value = '';
            isEraserMode = false;
            document.body.style.cursor = 'default';
            return;
        }

        if (selectedNumber !== null && cell.value === '') {
            cell.value = selectedNumber;
        }

        highlightRelatedCells(cellId);
    }
}

function setNumber(number) {
    selectedNumber = number;
    isEraserMode = false;
    document.body.style.cursor = 'default';
}

function eraseSelection() {
    isEraserMode = true;
    selectedNumber = null;
    document.body.style.cursor = 'cell'; // opcjonalny efekt kursora
}

function resetBoard() {
    for (let row = 0; row < 9; row++) {
        for (let col = 0; col < 9; col++) {
            const cell = document.getElementById(`R${row}C${col}`);
            if (cell && !cell.readOnly) {
                cell.value = '';
            }
        }
    }
}

function showHint() {
    if (!selectedCellId || !sudokuSolution) {
        alert('Podpowiedź niedostępna – brak rozwiązania.');
        return;
    }

    const row = parseInt(selectedCellId.substring(1, 2));
    const col = parseInt(selectedCellId.substring(3, 4));
    const cell = document.getElementById(selectedCellId);

    if (!cell.readOnly && cell.value === '') {
        cell.value = sudokuSolution[row][col];
    }
}

function highlightRelatedCells(cellId) {
    const allCells = document.querySelectorAll('.sudoku-cell');
    allCells.forEach(cell => {
        cell.classList.remove('highlighted', 'same-number');
    });

    const row = parseInt(cellId.substring(1, 2));
    const col = parseInt(cellId.substring(3, 4));
    const selectedCell = document.getElementById(cellId);
    const selectedValue = selectedCell.value;

    for (let i = 0; i < 9; i++) {
        document.getElementById(`R${row}C${i}`)?.classList.add('highlighted');
        document.getElementById(`R${i}C${col}`)?.classList.add('highlighted');
    }

    if (selectedValue !== '') {
        allCells.forEach(cell => {
            if (cell.value === selectedValue) {
                cell.classList.add('same-number');
            }
        });
    }
}
// Funkcja pobierająca losowy numer planszy dla danego poziomu
function getRandomIndex(max) {
    return Math.floor(Math.random() * max) + 1; // od 1 do max
}

// Funkcja pobierająca i przetwarzająca planszę z pliku txt
async function getPuzzle(name) {
    const numberOfPuzzles = 3; // zmień jeśli masz więcej plansz
    const randomIndex = getRandomIndex(numberOfPuzzles);
    const fileName = `${name}-${randomIndex}.txt`;

    try {
        const response = await fetch(`Pulpit/${easy50.txt}`);
        if (!response.ok) throw new Error("Nie udało się pobrać planszy.");

        const text = await response.text();
        const rows = text.trim().split("\n");
        const puzzle = rows.map(row => row.split(",").map(Number));

        // Walidacja planszy (czy to 9x9)
        if (
            puzzle.length !== 9 ||
            puzzle.some(row => row.length !== 9 || row.some(n => isNaN(n)))
        ) {
            throw new Error("Nieprawidłowy format planszy.");
        }

        return puzzle;

    } catch (err) {
        console.error("Błąd ładowania planszy:", err);
        return null;
    }
}

// Główna funkcja po kliknięciu guzika trudności
async function startGame(difficulty) {
    const container = document.getElementById("game-container");
    container.classList.remove("d-none");

    // Wyświetl info o ładowaniu
    const boardArea = document.getElementById("sudoku-table");
    boardArea.innerHTML = `<tr><td colspan="9" class="text-white text-center">Wczytywanie planszy...</td></tr>`;

    const puzzle = await getPuzzle(difficulty);
    if (puzzle) {
        createBoard(puzzle);
    } else {
        boardArea.innerHTML = `<tr><td colspan="9" class="text-danger text-center">Błąd wczytywania planszy.</td></tr>`;
    }
}

// Przykładowa funkcja generowania planszy 9x9
function createBoard(board) {
    const table = document.getElementById("sudoku-table");
    table.innerHTML = ""; // wyczyść poprzednią planszę

    board.forEach((row, rowIndex) => {
        const tr = document.createElement("tr");
        row.forEach((cell, colIndex) => {
            const td = document.createElement("td");
            td.textContent = cell === 0 ? "" : cell;
            td.classList.add("sudoku-cell");
            td.dataset.row = rowIndex;
            td.dataset.col = colIndex;
            tr.appendChild(td);
        });
        table.appendChild(tr);
    });
}




function closeAlert() {
    setTimeout(function() {
        const alertElement = document.getElementById('alert');
        if (alertElement) {
            alertElement.classList.remove('show');
            alertElement.classList.add('fade');
        }
    }, 5000);
}