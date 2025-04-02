// Sidebar Toggle Functions
var mySidebar = document.getElementById("mySidebar");
var overlayBg = document.getElementById("myOverlay");

function w3_open() {
    if (mySidebar.style.display === 'block') {
        mySidebar.style.display = 'none';
        overlayBg.style.display = "none";
    } else {
        mySidebar.style.display = 'block';
        overlayBg.style.display = "block";
    }
}

function w3_close() {
    mySidebar.style.display = "none";
    overlayBg.style.display = "none";
}

// Form Management Functions
function openForm() {
    document.getElementById("Chart").style.display = "none";
    document.getElementById("tagForm").style.display = "block";
    resetForm();  // Reset form elements
}

function cancelForm() {
    document.getElementById("Chart").style.display = "block";
    document.getElementById("tagForm").style.display = "none";
    resetForm();  // Reset form elements
}

function resetForm() {
    // Reset all form inputs
    document.getElementById("nameInput").value = "";
    document.getElementById("formTag1Btn").innerText = "Select";
    document.getElementById("formTag1Input").value = "";
    document.getElementById("tag2Input").value = "";
    document.getElementById("lookupName").value = "";
    document.getElementById("lookupMededelingen").value = "";
    document.getElementById("lookupAfBij").value = "";
    document.getElementById("lookupCode").value = "";
    document.getElementById("lookupMutatiesoort").value = "";
}

function submitTag() {
    let name = document.getElementById("nameInput").value.trim();
    let tag1 = document.getElementById("formTag1Input").value.trim();
    let tag2 = document.getElementById("tag2Input").value.trim();
    let lookupName = document.getElementById("lookupName").value.trim();
    let lookupMededelingen = document.getElementById("lookupMededelingen").value.trim();
    let lookupAfBij = document.getElementById("lookupAfBij").value.trim();
    let lookupCode = document.getElementById("lookupCode").value.trim();
    let lookupMutatiesoort = document.getElementById("lookupMutatiesoort").value.trim();

    if (!name) {
        alert("Please enter a name!");
        return;
    }

    let newTag = {
        [name]: {
            "tags": [tag1, tag2].filter(tag => tag !== ""),
            "lookup": {
                "Naam / Omschrijving": lookupName,
                "Mededelingen": lookupMededelingen,
                "Af Bij": lookupAfBij,
                "Code": lookupCode,
                "Mutatiesoort": lookupMutatiesoort
            }
        }
    };

    fetch('/add-tag', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newTag)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === "success") {
            cancelForm();  // Hide form on success
            alert('Database updated successfully!');
            location.reload();  // Refresh the page
        }
    })
    .catch(error => console.error("Error adding tag:", error));
}

// Dropdown Tag Selection (Form)
function updateFormTag(event, tag) {
    event.preventDefault();
    document.getElementById("formTag1Btn").innerText = tag;
    document.getElementById("formTag1Input").value = tag;
}

// Update Tag in Table (Edit Functionality)
function updateTag(event, tag, element) {
    const row = element.closest('tr');
    const tag1Cell = row.querySelector('.tag1');
    const dropdownButton = tag1Cell.querySelector('.dropbtn');
    if (tag1Cell) {
        tag1Cell.setAttribute('data-selected-tag', tag);
    }
    if (dropdownButton) {
        dropdownButton.textContent = tag;
    }
}

// Submit Data from Table to Server
function submitData() {
    const dataToSend = [];
    const rows = document.querySelectorAll('tr[data-row-id]');

    rows.forEach(row => {
        const tag1Cell = row.querySelector('.tag1');
        const tag2Cell = row.querySelector('.tag2');
        const uniqueIDCell = row.querySelector('.uniqueID');

        if (tag1Cell && tag2Cell && uniqueIDCell) {
            const tag1 = tag1Cell.getAttribute('data-selected-tag');
            const tag2 = tag2Cell.textContent.trim();
            const uniqueID = uniqueIDCell.textContent.trim();

            if (tag1) {
                dataToSend.push({ tag1, tag2, uniqueID });
            }
        }
    });

    if (dataToSend.length > 0) {
        fetch('/update_tags', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ data: dataToSend })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert('Database updated successfully!');
                location.reload();  // Refresh the page
            } else {
                alert('Error: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Failed to update the database');
        });
    } else {
        alert('No changes to update');
    }
}
