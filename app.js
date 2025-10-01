async function fetchTags() {
    const response = await fetch('data/tags.json');
    if (!response.ok) throw new Error('Could not load tags.json');
    return response.json();
}

function getTagColor(name) {
    // Generate a pastel color from the tag name
    let hash = 0;
    for (let i = 0; i < name.length; i++) {
        hash = name.charCodeAt(i) + ((hash << 5) - hash);
    }
    const h = Math.abs(hash) % 360;
    return `hsl(${h}, 70%, 65%)`;
}

function renderTags(tags, filter = '', sort = 'count-desc', grid = false) {
    const container = document.getElementById('tags-container');
    container.innerHTML = '';
    container.classList.toggle('grid', !!grid);
    let filtered = tags;
    if (filter) {
        const q = filter.toLowerCase();
        filtered = tags.filter(tag => tag.name.toLowerCase().includes(q));
    }
    // Sorting
    switch (sort) {
        case 'count-asc':
            filtered.sort((a, b) => a.count - b.count);
            break;
        case 'name-asc':
            filtered.sort((a, b) => a.name.localeCompare(b.name));
            break;
        case 'name-desc':
            filtered.sort((a, b) => b.name.localeCompare(a.name));
            break;
        case 'count-desc':
        default:
            filtered.sort((a, b) => b.count - a.count);
    }
    // Show tag counts
    const tagCounts = document.getElementById('tag-counts');
    if (tagCounts) {
        tagCounts.textContent = `Showing ${filtered.length} of ${tags.length} tags`;
    }
    if (filtered.length === 0) {
        container.innerHTML = '<div style="text-align:center;color:#888;">No tags found.</div>';
        return;
    }
    for (const tag of filtered) {
        const row = document.createElement('div');
        row.className = 'tag-row';
        row.setAttribute('tabindex', '0');
        row.setAttribute('role', 'button');
        row.setAttribute('aria-label', `Tag: ${tag.name}, count: ${tag.count}`);
        row.title = tag.description && tag.description.trim() ? tag.description : tag.name;
        // Set color
        const color = getTagColor(tag.name);
        row.innerHTML = `<span class=\"tag-name\" style=\"--tag-color: ${color}\">${tag.name}</span><span class=\"tag-count\">${tag.count}</span>`;
        // Clickable: open tag link if available
        if (tag.link) {
            row.addEventListener('click', () => {
                window.open(tag.link, '_blank', 'noopener');
            });
            row.addEventListener('keydown', e => {
                if (e.key === 'Enter' || e.key === ' ') {
                    window.open(tag.link, '_blank', 'noopener');
                }
            });
        }
        container.appendChild(row);
    }
}

function renderTagCloud(tags, filter = '', sort = 'count-desc') {
    const container = document.getElementById('tag-cloud-container');
    container.innerHTML = '';
    let filtered = tags;
    if (filter) {
        const q = filter.toLowerCase();
        filtered = tags.filter(tag => tag.name.toLowerCase().includes(q));
    }
    // Sorting
    switch (sort) {
        case 'count-asc':
            filtered.sort((a, b) => a.count - b.count);
            break;
        case 'name-asc':
            filtered.sort((a, b) => a.name.localeCompare(b.name));
            break;
        case 'name-desc':
            filtered.sort((a, b) => b.name.localeCompare(a.name));
            break;
        case 'count-desc':
        default:
            filtered.sort((a, b) => b.count - a.count);
    }
    if (filtered.length === 0) {
        container.innerHTML = '<div style="text-align:center;color:#888;">No tags found.</div>';
        return;
    }
    // Find min/max count for scaling
    const counts = filtered.map(t => t.count);
    const min = Math.min(...counts);
    const max = Math.max(...counts);
    for (const tag of filtered) {
        const span = document.createElement('span');
        span.className = 'tag-cloud-item';
        span.setAttribute('tabindex', '0');
        span.setAttribute('role', 'button');
        span.setAttribute('aria-label', `Tag: ${tag.name}, count: ${tag.count}`);
        span.title = tag.description && tag.description.trim() ? tag.description : tag.name;
        const color = getTagColor(tag.name);
        // Scale font size between 0.9em and 2.1em
        let size = 0.9 + (max > min ? (tag.count - min) / (max - min) : 0) * 1.2;
        span.style.setProperty('--tag-color', color);
        span.style.fontSize = size + 'em';
        span.innerHTML = `${tag.name} <span class="tag-count">${tag.count}</span>`;
        if (tag.link) {
            span.addEventListener('click', () => {
                window.open(tag.link, '_blank', 'noopener');
            });
            span.addEventListener('keydown', e => {
                if (e.key === 'Enter' || e.key === ' ') {
                    window.open(tag.link, '_blank', 'noopener');
                }
            });
        }
        container.appendChild(span);
    }
}

function renderPopularTags(tags, n = 5) {
    const container = document.getElementById('popular-tags');
    if (!container) return;
    const popular = tags
        .filter(tag => tag.count > 0)
        .sort((a, b) => b.count - a.count)
        .slice(0, n);
    container.innerHTML = '';
    if (popular.length === 0) {
        container.innerHTML = '<div style="text-align:center;color:#888;">No popular tags.</div>';
        return;
    }
    for (const tag of popular) {
        const row = document.createElement('div');
        row.className = 'tag-row';
        row.setAttribute('tabindex', '0');
        row.setAttribute('role', 'button');
        row.setAttribute('aria-label', `Tag: ${tag.name}, count: ${tag.count}`);
        row.title = tag.description && tag.description.trim() ? tag.description : tag.name;
        const color = getTagColor(tag.name);
        row.innerHTML = `<span class="tag-name" style="--tag-color: ${color}">${tag.name}</span><span class="tag-count">${tag.count}</span>`;
        if (tag.link) {
            row.addEventListener('click', () => {
                window.open(tag.link, '_blank', 'noopener');
            });
            row.addEventListener('keydown', e => {
                if (e.key === 'Enter' || e.key === ' ') {
                    window.open(tag.link, '_blank', 'noopener');
                }
            });
        }
        container.appendChild(row);
    }
}

document.addEventListener('DOMContentLoaded', async () => {
    let tags = [];
    try {
        tags = await fetchTags();
    } catch (e) {
        document.getElementById('tags-container').innerHTML = '<div style="color:red;text-align:center;">Failed to load tags.</div>';
        return;
    }
    renderPopularTags(tags, 5);
    let currentFilter = '';
    let currentSort = 'count-desc';
    let gridView = false;
    let cloudView = false;
    const searchInput = document.getElementById('search');
    const sortSelect = document.getElementById('sort-select');
    const toggleViewBtn = document.getElementById('toggle-view');
    const toggleCloudBtn = document.getElementById('toggle-cloud');
    const tagsContainer = document.getElementById('tags-container');
    const tagCloudContainer = document.getElementById('tag-cloud-container');
    function update() {
        if (cloudView) {
            tagsContainer.style.display = 'none';
            tagCloudContainer.style.display = '';
            renderTagCloud(tags, currentFilter, currentSort);
        } else {
            tagsContainer.style.display = '';
            tagCloudContainer.style.display = 'none';
            renderTags(tags, currentFilter, currentSort, gridView);
        }
    }
    searchInput.addEventListener('input', e => {
        currentFilter = e.target.value;
        update();
    });
    sortSelect.addEventListener('change', e => {
        currentSort = e.target.value;
        update();
    });
    toggleViewBtn.addEventListener('click', () => {
        gridView = !gridView;
        toggleViewBtn.setAttribute('aria-pressed', gridView ? 'true' : 'false');
        toggleViewBtn.textContent = gridView ? 'List View' : 'Grid View';
        update();
    });
    toggleCloudBtn.addEventListener('click', () => {
        cloudView = !cloudView;
        toggleCloudBtn.setAttribute('aria-pressed', cloudView ? 'true' : 'false');
        toggleCloudBtn.textContent = cloudView ? 'Normal View' : 'Tag Cloud';
        update();
    });
    update();
});
