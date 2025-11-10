fetch("/prayer-requests")
  .then(res => res.json())
  .then(prayerRequests => {
    const list = document.getElementById('prayer-request-list');
    prayerRequests.forEach(prayerRequest => {
      const li = document.createElement("li");
      li.textContent = `${prayerRequest.id}: ${prayerRequest.person} ${prayerRequest.text} [${prayerRequest.prayed ? "X": " "}]`;
      list.appendChild(li);
    });
  });