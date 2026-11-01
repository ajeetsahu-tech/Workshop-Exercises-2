// Premium front‑end logic for Equipment Maintenance Dashboard
// Uses Fetch API to load data from Flask back‑end and renders glass‑morphism cards.

const API_BASE = '/api';

function createCard(title, fields) {
  const card = document.createElement('div');
  card.className = 'card';
  const h3 = document.createElement('h3');
  h3.textContent = title;
  card.appendChild(h3);
  for (const [key, value] of Object.entries(fields)) {
    const p = document.createElement('p');
    p.innerHTML = `<strong>${key}:</strong> ${value}`;
    card.appendChild(p);
  }
  return card;
}

async function loadEquipment() {
  const res = await fetch(`${API_BASE}/equipment`);
  const data = await res.json();
  const container = document.getElementById('equipment-list');
  container.innerHTML = '';
  data.forEach(eq => {
    const card = createCard(eq.name, {
      Category: eq.category || 'N/A',
      Location: eq.location || 'N/A',
      Status: eq.status || 'active'
    });
    container.appendChild(card);
  });
}

async function loadTechnicians() {
  const res = await fetch(`${API_BASE}/technicians`);
  const data = await res.json();
  const container = document.getElementById('technician-list');
  container.innerHTML = '';
  data.forEach(t => {
    const card = createCard(`${t.first_name} ${t.last_name}`, {
      Email: t.email,
      Phone: t.phone || 'N/A',
      Expertise: t.expertise || 'General'
    });
    container.appendChild(card);
  });
}

async function loadRequests() {
  const res = await fetch(`${API_BASE}/requests`);
  const data = await res.json();
  const container = document.getElementById('request-list');
  container.innerHTML = '';
  data.forEach(r => {
    const card = createCard(`Request #${r.request_id}`, {
      EquipmentID: r.equipment_id,
      ReportedBy: r.reported_by,
      Status: r.status,
      Description: r.description
    });
    container.appendChild(card);
  });
}

function init() {
  loadEquipment();
  loadTechnicians();
  loadRequests();
}

window.addEventListener('DOMContentLoaded', init);
