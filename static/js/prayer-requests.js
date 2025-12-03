function displayTime(){
  const today = new Date();
  const options = {weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'};
  
  document.querySelector('.current-date-js').innerHTML = today.toLocaleDateString('en-US', options);
}

// TO DO: Add time that updates every minute
async function loadPrayerRequests() {
  const response = await fetch("/people");
  const persons = await response.json();

  const list = document.getElementById('prayer-request-list');

  persons.forEach(person => {
    
    const personListItem = document.createElement("li");
    personListItem.textContent = `${person.name}\t|\t${person.relationship_id}`;

    // const prayerUnorderedList = document.createElement("ul");

    // person.prayer_requests.forEach(prayer => {
    //   const prayerListItem =  document.createElement("li");
    //   prayerListItem.textContent = `${prayer.text}: [${prayer.has_prayed ? "X" : ""}]`;
    //   prayerUnorderedList.appendChild(prayerListItem);
    // });

    // personListItem.appendChild(prayerUnorderedList);

    list.appendChild(personListItem);
  });
}

function initPage(){
  displayTime();
  loadPrayerRequests();
}

initPage();
