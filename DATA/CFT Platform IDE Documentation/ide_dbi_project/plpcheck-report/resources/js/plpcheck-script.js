const TAG_MAP = {
	'DBI': 'DBI',
	'JAVA': 'JAVA',
	'PLSQL': 'PLSQL',
	'STYLE': 'STYLE',
	'SQL': 'SQL',
	'WEB': 'ЦФТ Веб-Навигатор (WEB)'
};

const RESTRICTION_MAP = {
	'oracle': 'Подключение к Oracle'
};

const searchInput = document.getElementById('searchInput');
const statsLabel = document.getElementById('statsLabel');
const cards = Array.from(document.querySelectorAll('.check-card'));
const sidebarNav = document.getElementById('sidebarNav');
const tagsContainer = document.getElementById('filter-group-tags');
const restrictionsContainer = document.getElementById('filter-group-restrictions');

function updateStats(visibleCount) {
	statsLabel.textContent = `Показано: ${visibleCount} / ${cards.length}`;
}

function initFilters() {
	const tags = new Map();
	const restrictions = new Map();
	
	cards.forEach(card => {
		card.querySelectorAll('.type-badge').forEach(badge => {
			const tagText = badge.textContent.trim().toUpperCase();
			if (tagText) {
				tags.set(tagText, (tags.get(tagText) || 0) + 1);
			}
		});
		
		const restrictionAlert = card.querySelector('.check-content .alert-box[data-restriction-key]');
		if (restrictionAlert) {
			const resKey = restrictionAlert.dataset.restrictionKey;
			if (resKey) {
				restrictions.set(resKey, (restrictions.get(resKey) || 0) + 1);
			}
		}
	});
	
	let tagHtml = '';
	Object.keys(TAG_MAP).forEach(key => {
		const name = TAG_MAP[key] || key;
		const count = tags.get(key);
		tagHtml += `
			<label>
				<input type="checkbox" name="tag" value="${key}">
				<span>${name}</span>
				<span class="count">${count}</span>
			</label>
		`;
	});
	tagsContainer.innerHTML = tagHtml || '<span style="color: var(--color-fg-muted); font-size: 14px;">Нет тегов для фильтрации</span>';
	
	let resHtml = '';
	Object.keys(RESTRICTION_MAP).forEach(key => {
		const name = RESTRICTION_MAP[key] || key;
		const count = restrictions.get(key);
		resHtml += `
			<label>
				<input type="checkbox" name="restriction" value="${key}">
				<span>${name}</span>
				<span class="count">${count}</span>
			</label>
		`;
	})
	
	if (resHtml) {
		restrictionsContainer.innerHTML = resHtml;
		restrictionsContainer.style.display = 'block';
	} else {
		restrictionsContainer.style.display = 'none';
	}
}

function filterRules() {
	const query = searchInput.value.toLowerCase().trim();
	const checkedTags = Array.from(tagsContainer.querySelectorAll('input:checked')).map(cb => cb.value);
	const checkedRestrictions = Array.from(restrictionsContainer.querySelectorAll('input:checked')).map(cb => cb.value);
	
	let visibleCount = 0;
	
	cards.forEach(card => {
		const cardText = card.innerText.toLowerCase();
		//const types = card.getAttribute('t')
		
		const cardBadgeElements = card.querySelectorAll('.type-badge');
		const cardTags = Array.from(cardBadgeElements).map(b => b.textContent.trim().toUpperCase());
		
		const cardResKey = card.querySelector('.check-content .alert-box[data-restriction-key]')?.dataset.restrictionKey || '';
		
		
		const matchesText = cardText.includes(query);
		const matchesTags = checkedTags.every(filterTag => cardTags.includes(filterTag));
		const matchesRestriction = checkedRestrictions.length === 0 || checkedRestrictions.includes(cardResKey);
		const isVisible = matchesText && matchesTags && matchesRestriction;
		
		card.classList.toggle('hidden', !isVisible);
		if (isVisible) {
			visibleCount++;
		}
	});
	updateStats(visibleCount);
}

function resetFilters(targetGroup) {
	let container = null;
	if (targetGroup === 'tags') {
		container = tagsContainer;
	} else if (targetGroup === 'restrictions') {
		container = restrictionsContainer;
	}
	
	if (container) {
		container.querySelectorAll('input:checked').forEach(cb => cb.checked = false);
		filterRules();
	}
}

searchInput.addEventListener('input', filterRules);
sidebarNav.addEventListener('change', filterRules);

sidebarNav.addEventListener('click', (event) => {
	if (event.target.classList.contains('btn-reset-filters')) {
		resetFilters(event.target.dataset.target);
	}
})

window.filterBy = function(typeStr, event) {
	event.preventDefault();
	event.stopPropagation();
	
	
	const targetCheckbox = tagsContainer.querySelector(`input[value="${typeStr.toUpperCase()}"]`);
	console.log(tagsContainer);
	if (targetCheckbox) {
		// Uncheck all others
		tagsContainer.querySelectorAll('input:checked').forEach(cb => cb.checked = false);
		targetCheckbox.checked = true;
		filterRules();
	} else {
		searchInput.value = typeStr;
		filterRules();
	}
	
	document.querySelector('.main-content').scrollTo({ top: 0, behaviour: 'smooth' });
};

window.toggleAll = function(shouldOpen) {
	const visibleCards = document.querySelectorAll('.check-card:not(.hidden)');
	visibleCards.forEach(card => {
		if (shouldOpen) card.setAttribute('open', '');
		else card.removeAttribute('open');
	});
};

document.addEventListener('DOMContentLoaded', () => {
	initFilters();
	updateStats(cards.length);
});