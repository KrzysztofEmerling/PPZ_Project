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

function create(){
    for (let row = 1; row <= 9; row++) {
        document.write('<tr>');
        for (let col = 1; col <= 9; col++) {
            let id = `R${row}C${col}`;
            document.write(`<td class="cell r${row} c${col}"><input type="number" class="sudoku-cell" id="${id}" onclick="fillCell('${id}')"></td>`);
        }
        document.write('</tr>');
    }
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