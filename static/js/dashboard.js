async function fetchDashboardData() {
    try {
        const res = await fetch('/api/dashboard/');
        const data = await res.json();

        renderCalendar(data.calendar, data.calendar[0]?.total || 0);
        renderDashboard(data.today);
        renderKanban(data.kanban);
        selectDay(1);
    } catch (err) {
        console.error('Erro ao buscar dados:', err);
    }
}

function renderCalendar(monthData, totalRooms) {
    const calendar = document.getElementById('calendar');
    calendar.innerHTML = `
        <div class="calendar-header">Dom</div>
        <div class="calendar-header">Seg</div>
        <div class="calendar-header">Ter</div>
        <div class="calendar-header">Qua</div>
        <div class="calendar-header">Qui</div>
        <div class="calendar-header">Sex</div>
        <div class="calendar-header">Sáb</div>
    `;

    monthData.forEach(d => {
        const dayDiv = document.createElement('div');
        dayDiv.classList.add('day');

        let availabilityClass = 'availability-high';
        if (d.free <= 1) availabilityClass = 'availability-low';
        else if (d.free <= 2) availabilityClass = 'availability-medium';

        dayDiv.innerHTML = `<strong>${d.day}</strong>
            <span class="free-info ${availabilityClass}">${d.free}/${totalRooms}</span>`;
        dayDiv.onclick = () => selectDay(d.day);
        calendar.appendChild(dayDiv);
    });
}

function renderDashboard(today) {
    document.getElementById('freeRooms').textContent = today.free.length;
    document.getElementById('occupiedRooms').textContent = today.occupied.length;
    document.getElementById('checkinsToday').textContent = today.checkins.length;

    document.getElementById('checkoutsToday').textContent =
        today.occupied.length + today.checkins.length;

    fillList('freeList', today.free);
    fillList('occupiedList', today.occupied);
    fillList('checkinList', today.checkins);
}

function fillList(id, data) {
    const ul = document.getElementById(id);
    ul.innerHTML = '';
    data.forEach(r => {
        const li = document.createElement('li');
        li.textContent = `${r.room} - ${r.checkout}`;
        ul.appendChild(li);
    });
}

function renderKanban(kanban) {
    const grid = document.getElementById('kanbanGrid');
    grid.innerHTML = '';

    kanban.forEach(column => {
        const colDiv = document.createElement('div');
        colDiv.classList.add('kanban-column');
        colDiv.innerHTML = `<h4>${column.title}</h4>`;
        column.items.forEach(item => {
            const itemDiv = document.createElement('div');
            itemDiv.classList.add('kanban-item');
            itemDiv.textContent = item;
            colDiv.appendChild(itemDiv);
        });
        grid.appendChild(colDiv);
    });
}

// Seleciona o primeiro dia por padrão
function selectDay(day) {
    document.querySelectorAll('.day').forEach(d => d.classList.remove('selected'));
    const calendar = document.getElementById('calendar');
    const dayDiv = Array.from(calendar.children).find(div => div.innerHTML.includes(`<strong>${day}</strong>`));
    if (dayDiv) dayDiv.classList.add('selected');
}

// Inicializa
fetchDashboardData();
