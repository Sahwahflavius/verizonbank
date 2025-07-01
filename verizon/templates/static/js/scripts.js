
  const receiverInput = document.getElementById('receiver');
  const receiverNameText = document.getElementById('receiverName');
  const receiverPopup = document.getElementById('receiverPopup');
  const confirmReceiverBtn = document.getElementById('confirmReceiverBtn');
  const submitBtn = document.getElementById('submitBtn');
  let confirmed = false;
  let lookupTimeout;

  receiverInput.addEventListener('input', () => {
    confirmed = false;
    submitBtn.disabled = true;
    receiverPopup.style.display = 'none';
    clearTimeout(lookupTimeout);
    const value = receiverInput.value.trim();
    if (value.length < 6) return;

    lookupTimeout = setTimeout(async () => {
      try {
        const res = await fetch('/get-user-by-identifier', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ identifier: value })
        });
        const data = await res.json();
        if (res.ok && data.name) {
          receiverNameText.innerText = `Receiver Name: ${data.name}`;
          receiverPopup.style.display = 'block';
        } else {
          receiverNameText.innerText = 'User not found';
          receiverPopup.style.display = 'block';
        }
      } catch (err) {
        receiverNameText.innerText = 'Lookup error';
        receiverPopup.style.display = 'block';
      }
    }, 500);
  });

  confirmReceiverBtn.addEventListener('click', () => {
    confirmed = true;
    receiverPopup.style.display = 'none';
    submitBtn.disabled = false;
  });

  document.getElementById('transferForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!confirmed) return alert("Please confirm receiver before transferring.");
    const receiver = receiverInput.value.trim();
    const amount = document.getElementById('amount').value;
    const res = await fetch('/transfer', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ receiver, amount })
    });
    const result = await res.json();
    document.getElementById('result').innerText = JSON.stringify(result, null, 2);
  });



  const userId = "{{ user.id|tojson|safe }}";  // Server-side rendered user ID as a string

  document.getElementById('b2wTransferForm').addEventListener('submit', async function(event) {
    event.preventDefault();

    const phoneInput = document.getElementById('mtnPhone');
    const amountInput = document.getElementById('transferAmount');
    const resultDiv = document.getElementById('b2wResult');

    // Clear previous result
    resultDiv.innerHTML = '';

    // Validate phone input with regex pattern
    const phonePattern = /^\+2376\d{8}$/;
    if (!phonePattern.test(phoneInput.value.trim())) {
      resultDiv.innerHTML = '<div class="alert alert-danger">Please enter a valid MTN Mobile Money phone number (e.g. +2376XXXXXXXX).</div>';
      return;
    }

    const transferData = {
      user_id: userId,
      phone: phoneInput.value.trim(),
      amount: parseFloat(amountInput.value)
    };

    if (transferData.amount <= 0) {
      resultDiv.innerHTML = '<div class="alert alert-danger">Please enter a valid amount greater than zero.</div>';
      return;
    }

    // Disable submit button while processing
    this.querySelector('button[type="submit"]').disabled = true;

    try {
      // Example POST request to your backend API endpoint
      const response = await fetch('/withdraw', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(transferData)
      });

      const data = await response.json();

      if (response.ok) {
        resultDiv.innerHTML = `<div class="alert alert-success">Transfer successful! Transaction ID: ${data.transactionId || 'N/A'}</div>`;
        this.reset();
      } else {
        resultDiv.innerHTML = `<div class="alert alert-danger">Transfer failed: ${data.error || 'Unknown error'}</div>`;
      }
    } catch (error) {
      //resultDiv.innerHTML = `<div class="alert alert-danger">Network error: ${error.message}</div>`;
   } finally {
      this.querySelector('button[type="submit"]').disabled = false;
   }
  }
  );

 

