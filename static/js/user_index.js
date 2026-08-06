

      //PATS uchun open close
     function openCustomModal(id) {
      document.getElementById(id).style.display = 'block';
    }

    // Modalni yopish
    function closeCustomModal(id) {
      document.getElementById(id).style.display = 'none';
    }

//BAZASTANSIYA uchun open close
    function openCustomModal11(id) {
      document.getElementById(id).style.display = 'block';
    }

    // Modalni yopish
    function closeCustomModal11(id) {
      document.getElementById(id).style.display = 'none';
    }
//gats uchun open close
    function openCustomModal2(id) {
      document.getElementById(id).style.display = 'block';
    }

    // Modalni yopish
    function closeCustomModal2(id) {
      document.getElementById(id).style.display = 'none';
    }
//vlan uchun open close
    function openCustomModal3(id) {
      document.getElementById(id).style.display = 'block';
    }

    // Modalni yopish
    function closeCustomModal3(id) {
      document.getElementById(id).style.display = 'none';
    }
//navbatchilar uchun open close
    function openCustomModal4(id) {
      document.getElementById(id).style.display = 'block';
    }

    // Modalni yopish
    function closeCustomModal4(id) {
      document.getElementById(id).style.display = 'none';
    }
//abonentlar uchun open close
    function openCustomModal5(id) {
      document.getElementById(id).style.display = 'block';
    }

    // Modalni yopish
    function closeCustomModal5(id) {
      document.getElementById(id).style.display = 'none';
    }

//firewall uchun open close
    function openCustomModal6(id) {
      document.getElementById(id).style.display = 'block';
    }

    // Modalni yopish
    function closeCustomModal6(id) {
      document.getElementById(id).style.display = 'none';
    }



    /* GLOBALS */
    const CSRF = '{{ csrf_token }}';
    const USER_FULL = "{{ user_obj.get_full_name|default:user_obj.username|escapejs }}";
    const USER_ID = {{ user_obj.id }};
    const MAX_FILE_SIZE = 20 * 1024 * 1024;
    let currentRegion = {{ user_obj.region.id }};
    let donutChart;

    /* Helpers */
    function qs(sel, base=document) { return base.querySelector(sel); }
    function qsa(sel, base=document) { return Array.from(base.querySelectorAll(sel)); }
    function openModal(id){ qs('#'+id).style.display='flex'; }
    function closeModal(id){ qs('#'+id).style.display='none'; }

    /* REGION selection */
    function onRegionClick(btn){
      const nodes = qsa('.region-btn');
      nodes.forEach(n=>n.classList.remove('active'));
      btn.classList.add('active');
      currentRegion = btn.dataset.id;
      loadRegionData(currentRegion);
    }


    /* LOAD region data */
    async function loadRegionData(regionId='{user_obj.region__id }'){
      try{
        const res = await fetch(`/api/region-user/${regionId}/`);
        const data = await res.json();

        // top small boxes for device types + totals
        const dt = data.device_types || {};
        console.log("malumotlar = ",dt);
        const statsHtml =`
         <div class="stat custom-btn" onclick="openCustomModal11('myModal12')">Baza Stansiya<br><strong>${dt.BazaStansiya||0}</strong></div>
      <div class="stat custom-btn" onclick="openCustomModal('myModal13')">Panasonic ATS<br><strong>${dt.PATS||0}</strong></div>
      <div class="stat custom-btn" onclick="openCustomModal2('myModal14')">Grandstream ATS<br><strong>${dt.GATS||0}</strong></div>
      <div class="stat custom-btn" onclick="openCustomModal6('myModal18')">Firewall<br><strong>${dt.Firewall||0}</strong></div>
      <div class="stat custom-btn" onclick="openCustomModal5('myModal17')">Abonentlar<br><strong>${dt.Abonent||0}</strong></div>
      <div class="stat custom-btn" onclick="openCustomModal3('myModal15')">VLAN<br><strong>${dt.L3VLAN||0}</strong></div>
      <div class="stat custom-btn" onclick="openCustomModal4('myModal16')">Navbatchilar ro'yhati<br><strong>${data.region_users||0}</strong></div>
      <div class="stat custom-btn">Tadbir<br><strong>${data.region_events||0}</strong></div>
    `;
        qs('#top-stats').innerHTML = statsHtml;

        // events list (with details button)
        const events = data.events_summary || [];
        console.log("Eventlar ruyhati = ",events);
        if(events.length===0) qs('#events-list').innerHTML = '<div class="muted">Tadbirlar royhati bosh</div>';
        else {
          qs('#events-list').innerHTML = events.map(ev => {
            return `<div style="padding:8px;border-bottom:1px solid #f1f5f9" onclick="openEventDetails(${ev.id})">
                      <strong>${ev.theme}</strong> <span class="muted">(${ev.user__username})</span>
                    </div>`;
          }).join('');
        }

        // top 5 users
        const currentRegion = '{{ user_obj.region.name }}';
        {#console.log("joriy hududdddd=",currentRegion);#}
        const users = data.users_summary || [];

        const regionalUsers = users.filter(u =>
        (u.region__name === currentRegion)
    );
        {#console.log(data.users_summary);#}
        regionalUsers.sort((a,b)=> (b.score||0) - (a.score||0));
        const top5 = regionalUsers.slice(0,5);
        qs('#top-users').innerHTML = top5.length ? top5.map((u,i)=>`<li>${i+1}. ${u.first_name || ''} ${u.last_name || ''} — ⭐${u.score||0}</li>`).join('') : '<li class="muted">hududida foydalanuvchi topilmadi</li>';



        // devices list
        const devices = data.region_devices;
        console.log("qurilmalar= ",devices);
        // show simple listing
        {#qs('#device-list').innerHTML = (data.device_types ? Object.entries(data.device_types).map(([k,v]) => `<div class="muted">${k}: ${v}</div>`).join('') : '');#}
        {##}
        {#// inactive list#}
        const inactive = data.inactive_list || [];
        if(inactive.length===0) qs('#inactive-list').innerHTML = '<i>Hammasi ishlayapti 🎉</i>';
        else qs('#inactive-list').innerHTML = inactive.map(d=>`<div>🔴 ${d.name} — ${d.ip_address} — ${d.region__name}</div>`).join('');

        // counts
        qs('#num-active').innerText = data.active_devices || 0;
        qs('#num-inactive').innerText = data.inactive_devices || 0;
        qs('#num-total').innerText = data.region_devices || 0;
        qs('#donut-pct').innerText = (data.percent!==undefined ? data.percent : 100) + '%';

        // draw donut
        drawDonut(data.active_devices||0, data.inactive_devices||0);

      }catch(err){ console.error('Load region data err', err); }
    }

    /* DONUT chart */
    function drawDonut(active, inactive){
      const ctx = qs('#deviceDonut').getContext('2d');
      if(donutChart) donutChart.destroy();
      donutChart = new Chart(ctx, {
        type:'doughnut',
        data:{
          labels:['Ishlayapti','Ishlamayapti'],
          datasets:[{data:[active, inactive], backgroundColor:['#10b981','#ef4444'] }]
        },
        options:{ cutout:'70%', plugins:{legend:{position:'bottom'}} }
      });
    }

    /* EVENT details modal */
    async function openEventDetails(id){
      try{
        const res = await fetch(`/api/events/${id}/`);
        const ev = await res.json();
        qs('#event-modal-title').innerText = ev.name;
        qs('#event-modal-body').innerHTML = `
          <div><strong>Sana:</strong> ${ev.theme}</div>
          <div style="margin-top:8px"><strong>Tavsif:</strong><div>${ev.main_body||'<i>yo‘q</i>'}</div></div>
          <div style="margin-top:8px"><strong>Yaratgan:</strong> ${ev.timestamp || '—'}</div>
          <div style="margin-top:8px"><strong>Holat:</strong> ${ev.is_finished ? 'Tugatildi' : 'Faol'}</div>
          ${ev.created_by === USER_FULL ? `<div style="margin-top:8px">
            <button class="btn secondary" onclick="finishEvent(${ev.id})">Tugatish</button>
          </div>` : ''}
        `;
        openModal('event-modal');
      }catch(err){ console.error(err); alert('Tadbir ma\'lumotini yuklashda xatolik'); }
    }





    /* CHAT functionality */
    async function loadChat(){
      try{
        const res = await fetch('/api/chat/');
        const msgs = await res.json();
        const container = qs('#chat-messages');
        container.innerHTML = '';
        msgs.forEach(m=>{
          const div = document.createElement('div');
          div.className = 'bubble ' + (m.sender_id === USER_ID ? 'me':'other');
          let html = '';
          if(m.text) html += `<div style="color: black;">${escapeHtml(m.text)}</div>`;
          if(m.file) {
            const lower = m.file.toLowerCase();
            if(lower.match(/\.(jpg|jpeg|png|gif)$/) || m.file.includes('image')) html += `<img src="${m.file}" width="200px" height="160px" />`;
            else if(lower.match(/\.(mp4|webm|ogg)$/) || m.file.includes('video')) html += `<video controls src="${m.file}" width="200px"></video>`;
            else html += `<div><a href="${m.file}" target="_blank">📎 Fayl</a></div>`;
          }
          html += `<span class="meta" style="color: black;">${escapeHtml(m.sender)} ${m.created_at? '• ' + new Date(m.created_at).toLocaleString():''}</span>`;
          {#if(m.can_edit) html += `<div style="margin-top:6px"><button class="btn" onclick="openEditMsg(${m.id}, '${escapeJsString(m.text)}')">Tahrirlash</button></div>`;#}
          div.innerHTML = html;
          container.appendChild(div);
        });
        container.scrollTop = container.scrollHeight;
      }catch(err){ console.error(err); }
    }
    function escapeHtml(s){ if(!s) return ''; return s.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;'); }
    function escapeJsString(s){ if(!s) return ''; return s.replaceAll("'","\\'").replaceAll("\n","\\n"); }

    /* File select preview + limit */
    function handleFileSelect(){
      const fi = qs('#chat-file');
      const info = qs('#file-info');
      if(!fi.files || fi.files.length===0){ info.innerText=''; return; }
      const file = fi.files[0];
      if(file.size > MAX_FILE_SIZE){ alert('Fayl 20MB dan katta bo\'lmasin'); fi.value=''; info.innerText=''; return; }
      let icon='📎';
      if(file.type.startsWith('image/')) icon='🖼️'; else if(file.type.startsWith('video/')) icon='🎬';
      info.innerText = `${icon} ${file.name} (${(file.size/1024/1024).toFixed(1)} MB)`;
    }
    async function sendChat(e){
      e.preventDefault();
      const text = qs('#chat-text').value.trim();
      const fileInput = qs('#chat-file');
      const file = fileInput.files[0];
      if(!text && !file) return;
      if(file && file.size > MAX_FILE_SIZE){ alert('Fayl 20MB dan katta'); return; }
      const fd = new FormData();
      fd.append('text', text);
      if(file) fd.append('file', file);
      const res = await fetch('/api/chat/', { method:'POST', headers:{'X-CSRFToken':CSRF}, body: fd });
      if(res.ok){ qs('#chat-text').value=''; fileInput.value=''; qs('#file-info').innerText=''; loadChat(); }
    }

    /* edit message */
    function openEditMsg(id, text){
      qs('#edit-msg-id').value = id;
      qs('#edit-msg-text').value = text || '';
      openModal('edit-msg-modal');
    }
    async function submitEditMsg(e){
      e.preventDefault();
      const id = qs('#edit-msg-id').value;
      const text = qs('#edit-msg-text').value;
      const fd = new FormData();
      fd.append('_method','PUT');
      fd.append('text', text);
      const res = await fetch(`/api/chat/${id}/edit/`, { method:'POST', headers:{'X-CSRFToken':CSRF}, body: fd });
      if(res.ok){ closeModal('edit-msg-modal'); loadChat(); }
      else alert('Tahrirlash xatolik berdi');
    }
    /* init */
    window.addEventListener('load', ()=>{
      loadRegionData('{{ user_obj.region.id }}');
      loadChat();
      setInterval(loadChat, 60000);
    });




//PATS uchun open close
     function openCustomModal(id) {
      document.getElementById(id).style.display = 'block';
    }

    // Modalni yopish
    function closeCustomModal(id) {
      document.getElementById(id).style.display = 'none';
    }

//BAZASTANSIYA uchun open close
    function openCustomModal11(id) {
      document.getElementById(id).style.display = 'block';
    }

    // Modalni yopish
    function closeCustomModal11(id) {
      document.getElementById(id).style.display = 'none';
    }
//gats uchun open close
    function openCustomModal2(id) {
      document.getElementById(id).style.display = 'block';
    }

    // Modalni yopish
    function closeCustomModal2(id) {
      document.getElementById(id).style.display = 'none';
    }
//vlan uchun open close
    function openCustomModal3(id) {
      document.getElementById(id).style.display = 'block';
    }

    // Modalni yopish
    function closeCustomModal3(id) {
      document.getElementById(id).style.display = 'none';
    }
//navbatchilar uchun open close
    function openCustomModal4(id) {
      document.getElementById(id).style.display = 'block';
    }

    // Modalni yopish
    function closeCustomModal4(id) {
      document.getElementById(id).style.display = 'none';
    }
//abonentlar uchun open close
    function openCustomModal5(id) {
      document.getElementById(id).style.display = 'block';
    }

    // Modalni yopish
    function closeCustomModal5(id) {
      document.getElementById(id).style.display = 'none';
    }

//firewall uchun open close
    function openCustomModal6(id) {
      document.getElementById(id).style.display = 'block';
    }

    // Modalni yopish
    function closeCustomModal6(id) {
      document.getElementById(id).style.display = 'none';
    }
//================================================Begining BaseStations in top list with modals==================================================
async function openCustomModal11(id) {
  const modal = document.getElementById(id);
  const content = modal.querySelector('.custom-modal-content');
  // Faqat BazaStansiya modali uchun
  if (id === 'myModal12') {
    try {
      const res = await fetch(`/api/bazastansiyalar/${currentRegion}/`);
      const devices = await res.json();
        console.log('natijalar ==  ',devices);
      if (devices.length === 0) {
        content.innerHTML = `
          <span class="custom-modal-close" onclick="closeCustomModal11('${id}')">&times;</span>
          <h2>Baza stansiyalar</h2>
          <p class="muted">Hech qanday baza stansiya topilmadi.</p>
        `;
      } else {
        const listHtml = devices.map(d => `
          <div onclick="openDeviceDetail11(${d.id})" style="padding:6px;border-bottom:1px solid #eee;cursor:pointer">
            <strong>${d.name}</strong>
            <span class="muted">${d.ip_address}</span>
            ${d.is_active ? '<span style="color:yellow"> ●</span>' : '<span style="color:red"> ●</span>'}
          </div>
        `).join('');
        content.innerHTML = `
          <span class="custom-modal-close" onclick="closeCustomModal11('${id}')">&times;</span>
          <h2>Baza stansiyalar</h2>
          <div style="max-height:400px;overflow-y:auto">${listHtml}</div>
        `;
      }
    } catch (err) {
      console.error("Baza stansiyalarni olishda xatolik:", err);
      content.innerHTML = `<p style="color:red">Ma’lumotni olishda xatolik yuz berdi.</p>`;
    }
  }
  modal.style.display = 'flex';
}

//Exactly one BS about
async function openDeviceDetail11(id) {
  try {
    const res = await fetch(`/api/bazastansiya/${id}/`);
    const dev = await res.json();
    const modal = document.getElementById('myModal12');
    const content = modal.querySelector('.custom-modal-content');
    content.innerHTML = `
      <span class="custom-modal-close" onclick="openCustomModal11('myModal12')">&times;</span>
      <h2>${dev.name}</h2>
      <p><strong>IP manzil:</strong> ${dev.ip_address}</p>
      <p><strong>Hudud:</strong> ${dev.region}</p>
      <p><strong>Holat:</strong> ${dev.is_active ? 'Aktiv' : 'Noaktiv'}</p>
      <p><strong>So‘nggi tekshiruv:</strong> ${dev.last_checked}</p>
      <p><strong>Tur:</strong> ${dev.type}</p>
      <button onclick="openCustomModal11('myModal12')" class="btn secondary">⬅️ Orqaga</button>
    `;
  } catch (err) {
    console.error("Baza stansiya detallarini olishda xatolik:", err);
    alert('Ma’lumotni yuklashda xatolik!');
  }
}

//================================================Ending BaseStations in top list with modals==================================================

//================================================Begining PATS in top list with modals==================================================
async function openCustomModal(id) {
  const modal = document.getElementById(id);
  const content = modal.querySelector('.custom-modal-content');
  // Faqat BazaStansiya modali uchun
  if (id === 'myModal13') {
    try {
      const res = await fetch(`/api/patslar/${currentRegion}/`);
      const devices = await res.json();
      if (devices.length === 0) {
        content.innerHTML = `
          <span class="custom-modal-close" onclick="closeCustomModal('${id}')">&times;</span>
          <h2>pats stansiyalar</h2>
          <p class="muted">Hech qanday pats topilmadi.</p>
        `;
      } else {
        const listHtml = devices.map(d => `
          <div onclick="openDeviceDetail(${d.id})" style="padding:6px;border-bottom:1px solid #eee;cursor:pointer">
            <strong>${d.name}</strong>
            <span class="muted">${d.ip_address}</span>
            ${d.is_active ? '<span style="color:yellow"> ●</span>' : '<span style="color:red"> ●</span>'}
          </div>
        `).join('');
        content.innerHTML = `
          <span class="custom-modal-close" onclick="closeCustomModal('${id}')">&times;</span>
          <h2>pats stansiyalar</h2>
          <div style="max-height:400px;overflow-y:auto">${listHtml}</div>
        `;
      }
    } catch (err) {
      console.error("Baza stansiyalarni olishda xatolik:", err);
      content.innerHTML = `<p style="color:red">Ma’lumotni olishda xatolik yuz berdi.</p>`;
    }
  }
  modal.style.display = 'flex';
}

//Exactly one BS about
async function openDeviceDetail(id) {
  try {
    const res = await fetch(`/api/pats/${id}/`);
    const dev = await res.json();
    const modal = document.getElementById('myModal13');
    const content = modal.querySelector('.custom-modal-content');
    content.innerHTML = `
      <span class="custom-modal-close" onclick="openCustomModal('myModal13')">&times;</span>
      <h2>${dev.name}</h2>
      <p><strong>IP manzil:</strong> ${dev.ip_address}</p>
      <p><strong>Hudud:</strong> ${dev.region}</p>
      <p><strong>Holat:</strong> ${dev.is_active ? 'Aktiv' : 'Noaktiv'}</p>
      <p><strong>So‘nggi tekshiruv:</strong> ${dev.last_checked}</p>
      <p><strong>Tur:</strong> ${dev.type}</p>
      <button onclick="openCustomModal('myModal13')" class="btn secondary">⬅️ Orqaga</button>
    `;
  } catch (err) {
    console.error("pats detallarini olishda xatolik:", err);
    alert('Ma’lumotni yuklashda xatolik!');
  }
}
//================================================Ending PATS in top list with modals==================================================





//================================================Begining gats in top list with modals==================================================
async function openCustomModal2(id, regionId='all') {
  const modal = document.getElementById(id);
  const content = modal.querySelector('.custom-modal-content');
  // Faqat BazaStansiya modali uchun
  if (id === 'myModal14') {
    try {
      const res = await fetch(`/api/gatslar/${currentRegion}/`);
      const devices = await res.json();
      if (devices.length === 0) {
        content.innerHTML = `
          <span class="custom-modal-close" onclick="closeCustomModal2('${id}')">&times;</span>
          <h2>Baza stansiyalar</h2>
          <p class="muted">Hech qanday baza stansiya topilmadi.</p>
        `;
      } else {
        const listHtml = devices.map(d => `
          <div onclick="openDeviceDetail2(${d.id})" style="padding:6px;border-bottom:1px solid #eee;cursor:pointer">
            <strong>${d.name}</strong>
            <span class="muted">${d.ip_address}</span>
            ${d.is_active ? '<span style="color:yellow"> ●</span>' : '<span style="color:red"> ●</span>'}
          </div>
        `).join('');
        content.innerHTML = `
          <span class="custom-modal-close" onclick="closeCustomModal2('${id}')">&times;</span>
          <h2>Baza stansiyalar</h2>
          <div style="max-height:400px;overflow-y:auto">${listHtml}</div>
        `;
      }
    } catch (err) {
      console.error("Baza stansiyalarni olishda xatolik:", err);
      content.innerHTML = `<p style="color:red">Ma’lumotni olishda xatolik yuz berdi.</p>`;
    }
  }
  modal.style.display = 'flex';
}

//Exactly one BS about
async function openDeviceDetail2(id) {
  try {
    const res = await fetch(`/api/bazastansiya/${id}/`);
    const dev = await res.json();
    const modal = document.getElementById('myModal14');
    const content = modal.querySelector('.custom-modal-content');
    content.innerHTML = `
      <span class="custom-modal-close" onclick="openCustomModal2('myModal14')">&times;</span>
      <h2>${dev.name}</h2>
      <p><strong>IP manzil:</strong> ${dev.ip_address}</p>
      <p><strong>Hudud:</strong> ${dev.region}</p>
      <p><strong>Holat:</strong> ${dev.is_active ? 'Aktiv' : 'Noaktiv'}</p>
      <p><strong>So‘nggi tekshiruv:</strong> ${dev.last_checked}</p>
      <p><strong>Tur:</strong> ${dev.type}</p>
      <button onclick="openCustomModal2('myModal14')" class="btn secondary">⬅️ Orqaga</button>
    `;
  } catch (err) {
    console.error("gaTS detallarini olishda xatolik:", err);
    alert('Ma’lumotni yuklashda xatolik!');
  }
}

//================================================Ending gats in top list with modals==================================================




//================================================Begining vlan in top list with modals==================================================
async function openCustomModal3(id) {
  const modal = document.getElementById(id);
  const content = modal.querySelector('.custom-modal-content');
  // Faqat BazaStansiya modali uchun
  if (id === 'myModal15') {
    try {
      const res = await fetch(`/api/vlanlar/${currentRegion}/`);
      const devices = await res.json();
      if (devices.length === 0) {
        content.innerHTML = `
          <span class="custom-modal-close" onclick="closeCustomModal3('${id}')">&times;</span>
          <h2>Baza stansiyalar</h2>
          <p class="muted">Hech qanday baza stansiya topilmadi.</p>
        `;
      } else {
        const listHtml = devices.map(d => `
          <div onclick="openDeviceDetail3(${d.id})" style="padding:6px;border-bottom:1px solid #eee;cursor:pointer">
            <strong>${d.name}</strong>
            <span class="muted">${d.ip_address}</span>
            ${d.is_active ? '<span style="color:yellow"> ●</span>' : '<span style="color:red"> ●</span>'}
          </div>
        `).join('');
        content.innerHTML = `
          <span class="custom-modal-close" onclick="closeCustomModal3('${id}')">&times;</span>
          <h2>Baza stansiyalar</h2>
          <div style="max-height:400px;overflow-y:auto">${listHtml}</div>
        `;
      }
    } catch (err) {
      console.error("Baza stansiyalarni olishda xatolik:", err);
      content.innerHTML = `<p style="color:red">Ma’lumotni olishda xatolik yuz berdi.</p>`;
    }
  }
  modal.style.display = 'flex';
}

//Exactly one BS about
async function openDeviceDetail3(id) {
  try {
    const res = await fetch(`/api/vlan/${id}/`);
    const dev = await res.json();
    const modal = document.getElementById('myModal15');
    const content = modal.querySelector('.custom-modal-content');
    content.innerHTML = `
      <span class="custom-modal-close" onclick="openCustomModal3('myModal15')">&times;</span>
      <h2>${dev.name}</h2>
      <p><strong>IP manzil:</strong> ${dev.ip_address}</p>
      <p><strong>Hudud:</strong> ${dev.region}</p>
      <p><strong>Holat:</strong> ${dev.is_active ? 'Aktiv' : 'Noaktiv'}</p>
      <p><strong>So‘nggi tekshiruv:</strong> ${dev.last_checked}</p>
      <p><strong>Tur:</strong> ${dev.type}</p>
      <button onclick="openCustomModal3('myModal15')" class="btn secondary">⬅️ Orqaga</button>
    `;
  } catch (err) {
    console.error("gaTS detallarini olishda xatolik:", err);
    alert('Ma’lumotni yuklashda xatolik!');
  }
}

//================================================Ending vlan in top list with modals==================================================


//================================================Begining dutys in top list with modals==================================================
async function openCustomModal4(id, regionId='all') {
  const modal = document.getElementById(id);
  const content = modal.querySelector('.custom-modal-content');
  // Faqat BazaStansiya modali uchun
  if (id === 'myModal16') {
    try {
      const res = await fetch(`/api/dutylar/${currentRegion}/`);
      const devices = await res.json();
      if (devices.length === 0) {
        content.innerHTML = `
          <span class="custom-modal-close" onclick="closeCustomModal4('${id}')">&times;</span>
          <h2>Baza stansiyalar</h2>
          <p class="muted">Hech qanday baza stansiya topilmadi.</p>
        `;
      } else {
        const listHtml = devices.map(d => `
          <div onclick="openDeviceDetail4(${d.id})" style="padding:6px;border-bottom:1px solid #eee;cursor:pointer">
            <strong>${d.username}</strong>
            {#<span class="muted">${d.ip_address}</span>#}
            {#${d.is_active ? '<span style="color:yellow"> ●</span>' : '<span style="color:red"> ●</span>'}#}
          </div>
        `).join('');
        content.innerHTML = `
          <span class="custom-modal-close" onclick="closeCustomModal4('${id}')">&times;</span>
          <h2>Baza stansiyalar</h2>
          <div style="max-height:400px;overflow-y:auto">${listHtml}</div>
        `;
      }
    } catch (err) {
      console.error("Baza stansiyalarni olishda xatolik:", err);
      content.innerHTML = `<p style="color:red">Ma’lumotni olishda xatolik yuz berdi.</p>`;
    }
  }
  modal.style.display = 'flex';
}


//Exactly one BS about
async function openDeviceDetail4(id) {
  try {
    const res = await fetch(`/api/duty/${id}/`);
    const dev = await res.json();
    const modal = document.getElementById('myModal16');
    const content = modal.querySelector('.custom-modal-content');
    content.innerHTML = `
      <span class="custom-modal-close" onclick="openCustomModal4('myModal16')">&times;</span>
      <h2>${dev.username}</h2>
      <center><img src="${dev.photo}" width="200"></center>

      <button onclick="openCustomModal4('myModal16')" class="btn secondary">⬅️ Orqaga</button>
    `;
  } catch (err) {
    console.error("gaTS detallarini olishda xatolik:", err);
    alert('Ma’lumotni yuklashda xatolik!');
  }
}

//================================================Ending dutys in top list with modals==================================================




//================================================Begining vlan in top list with modals==================================================
async function openCustomModal5(id) {
  const modal = document.getElementById(id);
  const content = modal.querySelector('.custom-modal-content');
  // Faqat BazaStansiya modali uchun
  if (id === 'myModal17') {
    try {
      const res = await fetch(`/api/abonentlar/${currentRegion}/`);
      const devices = await res.json();
      if (devices.length === 0) {
        content.innerHTML = `
          <span class="custom-modal-close" onclick="closeCustomModal5('${id}')">&times;</span>
          <h2>Baza stansiyalar</h2>
          <p class="muted">Hech qanday abonent topilmadi.</p>
        `;
      } else {
        const listHtml = devices.map(d => `
          <div onclick="openDeviceDetail5(${d.id})" style="padding:6px;border-bottom:1px solid #eee;cursor:pointer">
            <strong>${d.name}</strong>
            <span class="muted">${d.ip_address}</span>
            ${d.is_active ? '<span style="color:yellow"> ●</span>' : '<span style="color:red"> ●</span>'}
          </div>
        `).join('');
        content.innerHTML = `
          <span class="custom-modal-close" onclick="closeCustomModal5('${id}')">&times;</span>
          <h2>Baza stansiyalar</h2>
          <div style="max-height:400px;overflow-y:auto">${listHtml}</div>
        `;
      }
    } catch (err) {
      console.error("abonentlarni olishda xatolik:", err);
      content.innerHTML = `<p style="color:red">Ma’lumotni olishda xatolik yuz berdi.</p>`;
    }
  }
  modal.style.display = 'flex';
}

//Exactly one BS about
async function openDeviceDetail5(id) {
  try {
    const res = await fetch(`/api/abonent/${id}/`);
    const dev = await res.json();
    const modal = document.getElementById('myModal17');
    const content = modal.querySelector('.custom-modal-content');
    content.innerHTML = `
      <span class="custom-modal-close" onclick="openCustomModal5('myModal17')">&times;</span>
      <h2>${dev.name}</h2>
      <p><strong>IP manzil:</strong> ${dev.ip_address}</p>
      <p><strong>Hudud:</strong> ${dev.region}</p>
      <p><strong>Holat:</strong> ${dev.is_active ? 'Aktiv' : 'Noaktiv'}</p>
      <p><strong>So‘nggi tekshiruv:</strong> ${dev.last_checked}</p>
      <p><strong>Tur:</strong> ${dev.type}</p>
      <button onclick="openCustomModal5('myModal17')" class="btn secondary">⬅️ Orqaga</button>
    `;
  } catch (err) {
    console.error("gaTS detallarini olishda xatolik:", err);
    alert('Ma’lumotni yuklashda xatolik!');
  }
}

//================================================Ending vlan in top list with modals==================================================





//================================================Begining firewall in top list with modals==================================================
async function openCustomModal6(id, regionId='all') {
  const modal = document.getElementById(id);
  const content = modal.querySelector('.custom-modal-content');
  // Faqat firewall modali uchun
  if (id === 'myModal18') {
    try {
      const res = await fetch(`/api/firewalls/${currentRegion}/`);
      const devices = await res.json();
       console.log('info=',devices);
      if (devices.length === 0) {
        content.innerHTML = `
          <span class="custom-modal-close" onclick="closeCustomModal6('${id}')">&times;</span>
          <h2>Baza stansiyalar</h2>
          <p class="muted">Hech qanday  firewall topilmadi.</p>
        `;
      } else {
        const listHtml = devices.map(d => `
          <div onclick="openDeviceDetail6(${d.id})" style="padding:6px;border-bottom:1px solid #eee;cursor:pointer">
            <strong>${d.name}</strong>
            <span class="muted">${d.ip_address}</span>
            ${d.is_active ? '<span style="color:yellow"> ●</span>' : '<span style="color:red"> ●</span>'}
          </div>
        `).join('');
        content.innerHTML = `
          <span class="custom-modal-close" onclick="closeCustomModal6('${id}')">&times;</span>
          <h2>Baza stansiyalar</h2>
          <div style="max-height:400px;overflow-y:auto">${listHtml}</div>
        `;
      }
    } catch (err) {
      console.error("Baza stansiyalarni olishda xatolik:", err);
      content.innerHTML = `<p style="color:red">Ma’lumotni olishda xatolik yuz berdi.</p>`;
    }
  }
  modal.style.display = 'flex';
}

//Exactly one BS about
async function openDeviceDetail6(id) {
  try {
    const res = await fetch(`/api/firewall/${id}/`);
    const dev = await res.json();
    const modal = document.getElementById('myModal18');
    const content = modal.querySelector('.custom-modal-content');
    content.innerHTML = `
      <span class="custom-modal-close" onclick="openCustomModal6('myModal18')">&times;</span>
      <h2>${dev.name}</h2>
      <p><strong>IP manzil:</strong> ${dev.ip_address}</p>
      <p><strong>Hudud:</strong> ${dev.region}</p>
      <p><strong>Holat:</strong> ${dev.is_active ? 'Aktiv' : 'Noaktiv'}</p>
      <p><strong>So‘nggi tekshiruv:</strong> ${dev.last_checked}</p>
      <p><strong>Tur:</strong> ${dev.type}</p>
      <button onclick="openCustomModal6('myModal18')" class="btn secondary">⬅️ Orqaga</button>
    `;
  } catch (err) {
    console.error("firewall detallarini olishda xatolik:", err);
    alert('Ma’lumotni yuklashda xatolik!');
  }
}

//================================================Ending firewall in top list with modals==================================================



setInterval(() => {
    const now = new Date();
    if (now.getHours() === 9 && now.getMinutes() === 0) {
        location.reload();
    }
}, 60000);