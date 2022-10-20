const data = document.getElementById("info");
// Create an array of cars to send to the server:
const cars = [
  { make: "Porsche", model: "911S" },
  { make: "Mercedes-Benz", model: "220SE" },
  { make: "Jaguar", model: "Mark VII" },
];

window.addEventListener("load", (event) => {
  tg = window.Telegram.WebApp;
  const lol = [
    {
      make: tg.initDataUnsafe.user.id,
    },
  ];
  fetch("https://2877-213-87-160-33.eu.ngrok.io/receiver", {
    method: "POST",
    headers: {
      "Content-type": "application/json",
      Accept: "application/json",
    },
    // Strigify the payload into JSON:
    body: JSON.stringify(lol),
  })
    .then((res) => {
      if (res.ok) {
        return res.json();
      } else {
        alert("something is wrong");
      }
    })
    .then((jsonResponse) => {
      // Log the response data in the console
      console.log(jsonResponse);
    })
    .catch((err) => console.error(err));
});
