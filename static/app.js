const DOMAIN = 'http://localhost:';
const PORT = 5001;
const POST_ROUTE = 'user-data';

document.addEventListener('DOMContentLoaded', async () => {
    await populateUserDropdown();
});

const recommendationBtn = document.getElementById('recommendation-btn');

recommendationBtn.addEventListener('click', async () => sendRequest());

function decreaseValue() {
    var value = parseInt(document.getElementById('neighbor-input').value);
    value = isNaN(value) ? 0 : value;
    value--;
    document.getElementById('neighbor-input').value = value < 0 ? 0 : value;
}

function increaseValue() {
    var value = parseInt(document.getElementById('neighbor-input').value);
    value = isNaN(value) ? 0 : value;
    value++;
    document.getElementById('neighbor-input').value = value;
}

function decreaseValue2() {
    var value = parseInt(document.getElementById('amount-input').value);
    value = isNaN(value) ? 0 : value;
    value--;
    document.getElementById('amount-input').value = value < 0 ? 0 : value;
}

function increaseValue2() {
    var value = parseInt(document.getElementById('amount-input').value);
    value = isNaN(value) ? 0 : value;
    value++;
    document.getElementById('amount-input').value = value;
}

const sendRequest = async () => {
    const name = document.getElementById('name-dropdown').value;
    const numberOfNeighbors = parseInt(document.getElementById('neighbor-input').value);
    const numberOfEvents = parseInt(document.getElementById('amount-input').value);
    const aggregationMethod = document.getElementById('aggregation-dropdown').value;

    if (!name || numberOfNeighbors <= 0 || numberOfEvents <= 0) {
        alert('Por favor, complete todos los campos correctamente.');
        return;
    }

    const userRequest = {
        usuario: name,
        vecinos: numberOfNeighbors,
        aggregation: aggregationMethod,
        N: numberOfEvents
    };

    await postEndpoint(userRequest);
};

const postEndpoint = async (request) => {
    try {
        const raw = await fetch(`${DOMAIN}${PORT}/${POST_ROUTE}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(request)
        });

        const response = await raw.json();

        if (response.error) {
            alert(response.error);
            return;
        }

        const neighborsElement = document.getElementById('cards-neighbors');
        const eventsElement = document.getElementById('cards-events');

        let neighborsHTML = '';
        let eventsHTML = '';

        response.vecinos.forEach(neighbor => {
            neighborsHTML += `<div class="neighbor">${neighbor}</div>`;
        });

        response.resultados.forEach(event => {
            eventsHTML += `<div class="event">
                                <p>${event[0]}</p>
                                <p>${event[1]}</p>
                                <p>${event[2]}</p>
                                <p>${event[3]}</p>
                           </div>`;
        });

        neighborsElement.innerHTML = neighborsHTML;
        eventsElement.innerHTML = eventsHTML;

        toggleScreens();

    } catch (error) {
        console.log(error);
    }
};

const populateUserDropdown = async () => {
    const dropdown = document.getElementById('name-dropdown');

    try {
        const response = await fetch(`${DOMAIN}${PORT}/list-users`);
        const data = await response.json();

        if (data.error) {
            console.error(data.error);
            return;
        }

        const users = data.usuarios;
        users.forEach(user => {
            const option = document.createElement('option');
            option.text = user;
            option.value = user;
            dropdown.appendChild(option);
        });
    } catch (error) {
        console.error('Error fetching users:', error);
    }
};

function toggleScreens() {
    const screen1 = document.querySelector('.data-filter');
    const screen2 = document.querySelector('.data-container');

    if (screen1.style.display === "none") {
        screen1.style.display = "block";
        screen2.style.display = "none";
    } else {
        screen1.style.display = "none";
        screen2.style.display = "block";
    }
}

function backPage() {
    const screen1 = document.querySelector('.data-filter');
    const screen2 = document.querySelector('.data-container');

    screen1.style.display = "block"
    screen2.style.display = "none"
}
