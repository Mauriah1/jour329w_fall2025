let tags = [];
let sortDescending = true;

async function loadTags() {
    try {
        const response = await fetch('../../data/tags.json');
        tags = await response.json();
        renderTags();
    } catch (error) {
        document.querySelector('#tags-table tbody').innerHTML = '<tr><td colspan="2">Failed to load tags.</td></tr>';
    }
}

function renderTags(filtered = null) {
    let displayTags = filtered || tags;
    displayTags = [...displayTags].sort((a, b) => sortDescending ? b.count - a.count : a.count - b.count);
    const tbody = document.querySelector('#tags-table tbody');
    tbody.innerHTML = displayTags.map(tag => `
        <tr>
            <td>${tag.name}</td>
            <td>${tag.count}</td>
        </tr>
    `).join('');
}

document.addEventListener('DOMContentLoaded', () => {
    loadTags();
    document.getElementById('search').addEventListener('input', (e) => {
        const q = e.target.value.toLowerCase();
        const filtered = tags.filter(tag => tag.name.toLowerCase().includes(q));
        renderTags(filtered);
    });
    document.getElementById('count-header').addEventListener('click', () => {
        sortDescending = !sortDescending;
        renderTags();
        document.getElementById('count-header').innerHTML = `Count ${sortDescending ? '&#8595;' : '&#8593;'}`;
    });
});
