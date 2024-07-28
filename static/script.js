document.getElementById('upload-form').addEventListener('submit', async function(event) {
    event.preventDefault();

    const fileInput = document.getElementById('file-input');
    const budgetInput = document.getElementById('budget-input');

    const formData = new FormData();

    if (fileInput.files.length > 0) {
        formData.append('file', fileInput.files[0]);
    } else {
        formData.append('file', new Blob(), ''); // Appending empty file to ensure `None` is sent
    }

    if (budgetInput.value) {
        formData.append('Budget', budgetInput.value);
    } else {
        formData.append('Budget', ''); // Appending empty value to ensure `None` is sent
    }

    try {
        const response = await fetch('/upload-data/', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const result = await response.json();
            alert(result.message);
            displayTable();
        } else {
            const error = await response.text();
            alert(`Failed to upload file and/or set budget: ${error}`);
        }
    } catch (error) {
        alert(`An error occurred: ${error.message}`);
    }
});

async function fetchData() {
    try {
        const response = await fetch('/process-csv/');
        if (response.ok) {
            const jsonData = await response.json();
            return jsonData;
        } else {
            const error = await response.text();
            alert(`Failed to fetch data: ${error}`);
            return null;
        }
    } catch (error) {
        alert(`An error occurred: ${error.message}`);
        return null;
    }
}

function createTableFromJSON(json) {
    const table = document.createElement('table');
    table.classList.add('table', 'table-bordered', 'table-striped');

    const thead = table.createTHead();
    const headerRow = thead.insertRow();
    json.columns.forEach(col => {
        const th = document.createElement('th');
        th.textContent = col;
        headerRow.appendChild(th);
    });

    const tbody = table.createTBody();
    json.data.forEach(rowData => {
        const row = tbody.insertRow();
        rowData.forEach(cellData => {
            const cell = row.insertCell();
            cell.textContent = cellData;
        });
    });

    return table;
}

async function displayTable() {
    const jsonData = await fetchData();
    if (jsonData) {
        const table = createTableFromJSON(jsonData);
        const tableContainer = document.getElementById('table-container');
        tableContainer.innerHTML = '';  // Clear any existing content
        tableContainer.appendChild(table);
    }
}

// Initial display of the table
displayTable();
