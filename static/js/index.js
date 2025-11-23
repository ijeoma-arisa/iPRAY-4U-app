fetch("/prayer-requests")
  .then(res => res.json())
  .then(persons => {
    const list = document.getElementById('prayer-request-list');
    
    persons.forEach(person => {
      
      const personListItem = document.createElement("li");
      personListItem.textContent = `${person.name}\t|\t${person.relationship}`;

      const prayerUnorderedList = document.createElement("ul");

      person.prayer_requests.forEach(prayer => {
        const prayerListItem =  document.createElement("li");
        prayerListItem.textContent = `${prayer.text}: [${prayer.has_prayed ? "X" : ""}]`;
        prayerUnorderedList.appendChild(prayerListItem);
      });

      personListItem.appendChild(prayerUnorderedList);

      list.appendChild(personListItem);
    });
  });