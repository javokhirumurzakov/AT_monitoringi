const MAX_FILE_SIZE = 20 * 1024 * 1024;

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('#regions li').forEach(li => {
    li.addEventListener('click', () => {
      document.querySelectorAll('#regions li').forEach(e => e.classList.remove('active'));
      li.classList.add('active');
      loadRegionData(li.dataset.id);
    });
  });

  loadRegionData('all');
  loadChat();
  setInterval(loadChat, 4000);
});

async function loadRegionData(regionId) {
  const res = await fetch(`/api/data/${regionId}/`);
  const data = await res.json();

  document.getElementById('stats').innerHTML = `
    <div class="box">🛰️ Qurilmalar: ${data.total_devices}</div>
    <div class="box">✅ Ishlayotgan: ${data.active_devices}</div>
    <div class="box">❌ Ishlamayotgan: ${data.inactive_devices}</div>
    <div class="box">👥 Foydalanuvchilar: ${data.total_users}</div>
    <div class="box">🎯 Tadbirlar: ${data.total_events}</div>
  `;

  const total = data.total_devices || 1;
  const percent = Math.round((data.active_devices / total) * 100);
  drawChart(percent);
}

function drawChart(percent) {
  const ctx = document.getElementById('deviceChart').getContext('2d');
  new Chart(ctx, {
    type: 'doughnut',
    data: {
      datasets: [{
        data: [percent, 100 - percent],
        backgroundColor: ['#22c55e', '#ef4444']
      }]
    },
    options: {
      cutout: '70%',
      plugins: { legend: { display: false } }
    }
  });
  document.getElementById('chart-center').innerText = percent + '%';
}

function handleFileSelect() {
  const fileInput = document.getElementById('chat-file');
  const info = document.getElementById('file-info');
  if (fileInput.files.length > 0) {
    const file = fileInput.files[0];
    if (file.size > MAX_FILE_SIZE) {
      alert(`❌ Fayl hajmi 20 MB dan oshmasligi kerak. Siz tanlagan fayl ${(file.size / (1024 * 1024)).toFixed(1)} MB`);
      fileInput.value = '';
      info.textContent = '';
      return;
    }
    info.textContent = `📎 ${file.name} (${(file.size / (1024 * 1024)).toFixed(1)} MB)`;
  } else info.textContent = '';
}

async function sendMessage(e) {
  e.preventDefault();
  const text = document.getElementById('chat-text').value.trim();
  const fileInput = document.getElementById('chat-file');
  const file = fileInput.files[0];

  if (!text && !file) return;
  if (file && file.size > MAX_FILE_SIZE) {
    alert('Fayl hajmi 20 MB dan oshmasligi kerak.');
    return;
  }

  const fd = new FormData();
  fd.append('text', text);
  if (file) fd.append('file', file);

  const res = await fetch('/api/chat/', {
    method: 'POST',
    headers: { 'X-CSRFToken': CSRF_TOKEN },
    body: fd
  });
  if (res.ok) {
    document.getElementById('chat-text').value = '';
    fileInput.value = '';
    document.getElementById('file-info').textContent = '';
    loadChat();
  }
}

async function loadChat() {
  const res = await fetch('/api/chat/');
  const data = await res.json();
  const box = document.getElementById('chat-box');
  box.innerHTML = data.map(m => `
    <div class="msg">
      <b>${m.sender}</b>: ${m.text || ''}
      ${m.file ? `<div><a href="${m.file}" target="_blank">📎 Fayl</a></div>` : ''}
    </div>
  `).join('');
}
