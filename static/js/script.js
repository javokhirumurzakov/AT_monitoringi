 const gauge = document.getElementById("gauge");
    const ring = document.getElementById("ring");
    const needle = document.getElementById("needle");
    const valueEl = document.getElementById("value");
    const statusEl = document.getElementById("status");

    // 50 ta soxta IP
    let devices = Array.from({ length: 50 }, (_, i) => ({
      ip: `192.168.0.${i + 1}`,
      active: Math.random() > 0.2
    }));

    function getOnlinePercent() {
      let online = devices.filter(d => d.active).length;
      return Math.round((online / devices.length) * 100);
    }

    function setGauge(value) {
      ring.style.setProperty("--value", value);
      const angle = (value / 100) * 180 - 90;
      needle.style.transform = `rotate(${angle}deg)`;
      valueEl.textContent = value;
    }

    async function pingAllDevices() {
      gauge.classList.add("tekshirilmoqda");
      statusEl.textContent = "Ping jo'natilmoqda...";
      let simulatedValue = 0;

      for (let i = 0; i < devices.length; i++) {
        await new Promise(r => setTimeout(r, 600));
        simulatedValue = Math.round((i / devices.length) * 100);
        setGauge(simulatedValue);
      }

      devices.forEach(d => {
        d.active = Math.random() > 0.3;
      });

      const newPercent = getOnlinePercent();
      setGauge(newPercent);
      statusEl.textContent = "Yakunlandi ✅";
      gauge.classList.remove("tekshirilmoqda");
    }

    pingAllDevices();
    setInterval(pingAllDevices, 120000);



async function createPdf(title, text, date) {
  const { jsPDF } = window.jspdf;
  const doc = new jsPDF({ unit: "mm", format: "a4" });

  // Sarlavha
  doc.setFont("helvetica", "bold");
  doc.setFontSize(18);
  doc.setTextColor(41, 128, 185);
  doc.text(title, 20, 30);

  // Matn
  doc.setFont("helvetica", "normal");
  doc.setFontSize(12);
  const pageWidth = doc.internal.pageSize.getWidth() - 40;
  const wrappedText = doc.splitTextToSize(text, pageWidth);
  doc.text(wrappedText, 20, 45);

  // Sana
  doc.setFont("helvetica", "italic");
  doc.setTextColor(100);
  doc.text("Sana: " + date, 20, 120);

  // Faylni saqlash
  doc.save(title.replace(/\s+/g, "_") + ".pdf");
}

// Har bir tugmaga listener qo‘shamiz
document.querySelectorAll(".download-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    const title = btn.dataset.title || "Hisobot";
    const text = btn.dataset.text || "Matn mavjud emas";
    const date = btn.dataset.date || "";
    createPdf(title, text, date);
  });
});






  const mainModal = new bootstrap.Modal(document.getElementById('exampleModal-2'));
  const detailModal = new bootstrap.Modal(document.getElementById('exampleModal'));

  // Batafsil tugmasi bosilganda
  document.getElementById('openDetail').addEventListener('click', () => {
    detailModal.show(); // faqat ikkinchi modalni ochamiz
  });

  // Ikkinchi modal yopilganda, fon o‘z holiga qaytsin
  document.getElementById('exampleModal').addEventListener('hidden.bs.modal', () => {
    document.body.classList.add('modal-open'); // bu satr asosiy modalni yopilmay qolishiga yordam beradi
  });


  const send_duty_region = document.querySelector('#region_section_send');
  let regionSection = document.querySelector('.region-section-form');
  let regionSectionSectionData = document.querySelector('.region-section-form-data');
  send_duty_region.addEventListener('click', ()=>{
      regionSection.classList.add('active');
      regionSectionSectionData.classList.remove('active')
  })