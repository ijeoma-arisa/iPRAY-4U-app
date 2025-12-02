const today = new Date();
const options = {weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'};

document.querySelector('.current-date-js').innerHTML = today.toLocaleDateString('en-US', options);

// TO DO: Add time that updates every minute