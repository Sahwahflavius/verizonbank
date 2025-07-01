"use strict";

var receiverInput = document.getElementById('receiver');
var receiverNameText = document.getElementById('receiverName');
var receiverPopup = document.getElementById('receiverPopup');
var confirmReceiverBtn = document.getElementById('confirmReceiverBtn');
var submitBtn = document.getElementById('submitBtn');
var confirmed = false;
var lookupTimeout;
receiverInput.addEventListener('input', function () {
  confirmed = false;
  submitBtn.disabled = true;
  receiverPopup.style.display = 'none';
  clearTimeout(lookupTimeout);
  var value = receiverInput.value.trim();
  if (value.length < 6) return;
  lookupTimeout = setTimeout(function _callee() {
    var res, data;
    return regeneratorRuntime.async(function _callee$(_context) {
      while (1) {
        switch (_context.prev = _context.next) {
          case 0:
            _context.prev = 0;
            _context.next = 3;
            return regeneratorRuntime.awrap(fetch('/get-user-by-identifier', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json'
              },
              body: JSON.stringify({
                identifier: value
              })
            }));

          case 3:
            res = _context.sent;
            _context.next = 6;
            return regeneratorRuntime.awrap(res.json());

          case 6:
            data = _context.sent;

            if (res.ok && data.name) {
              receiverNameText.innerText = "Receiver Name: ".concat(data.name);
              receiverPopup.style.display = 'block';
            } else {
              receiverNameText.innerText = 'User not found';
              receiverPopup.style.display = 'block';
            }

            _context.next = 14;
            break;

          case 10:
            _context.prev = 10;
            _context.t0 = _context["catch"](0);
            receiverNameText.innerText = 'Lookup error';
            receiverPopup.style.display = 'block';

          case 14:
          case "end":
            return _context.stop();
        }
      }
    }, null, null, [[0, 10]]);
  }, 500);
});
confirmReceiverBtn.addEventListener('click', function () {
  confirmed = true;
  receiverPopup.style.display = 'none';
  submitBtn.disabled = false;
});
document.getElementById('transferForm').addEventListener('submit', function _callee2(e) {
  var receiver, amount, res, result;
  return regeneratorRuntime.async(function _callee2$(_context2) {
    while (1) {
      switch (_context2.prev = _context2.next) {
        case 0:
          e.preventDefault();

          if (confirmed) {
            _context2.next = 3;
            break;
          }

          return _context2.abrupt("return", alert("Please confirm receiver before transferring."));

        case 3:
          receiver = receiverInput.value.trim();
          amount = document.getElementById('amount').value;
          _context2.next = 7;
          return regeneratorRuntime.awrap(fetch('/transfer', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              receiver: receiver,
              amount: amount
            })
          }));

        case 7:
          res = _context2.sent;
          _context2.next = 10;
          return regeneratorRuntime.awrap(res.json());

        case 10:
          result = _context2.sent;
          document.getElementById('result').innerText = JSON.stringify(result, null, 2);

        case 12:
        case "end":
          return _context2.stop();
      }
    }
  });
});
var userId = "{{ user.id|tojson|safe }}"; // Server-side rendered user ID as a string

document.getElementById('b2wTransferForm').addEventListener('submit', function _callee3(event) {
  var phoneInput, amountInput, resultDiv, phonePattern, transferData, response, data;
  return regeneratorRuntime.async(function _callee3$(_context3) {
    while (1) {
      switch (_context3.prev = _context3.next) {
        case 0:
          event.preventDefault();
          phoneInput = document.getElementById('mtnPhone');
          amountInput = document.getElementById('transferAmount');
          resultDiv = document.getElementById('b2wResult'); // Clear previous result

          resultDiv.innerHTML = ''; // Validate phone input with regex pattern

          phonePattern = /^\+2376\d{8}$/;

          if (phonePattern.test(phoneInput.value.trim())) {
            _context3.next = 9;
            break;
          }

          resultDiv.innerHTML = '<div class="alert alert-danger">Please enter a valid MTN Mobile Money phone number (e.g. +2376XXXXXXXX).</div>';
          return _context3.abrupt("return");

        case 9:
          transferData = {
            user_id: userId,
            phone: phoneInput.value.trim(),
            amount: parseFloat(amountInput.value)
          };

          if (!(transferData.amount <= 0)) {
            _context3.next = 13;
            break;
          }

          resultDiv.innerHTML = '<div class="alert alert-danger">Please enter a valid amount greater than zero.</div>';
          return _context3.abrupt("return");

        case 13:
          // Disable submit button while processing
          this.querySelector('button[type="submit"]').disabled = true;
          _context3.prev = 14;
          _context3.next = 17;
          return regeneratorRuntime.awrap(fetch('/withdraw', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(transferData)
          }));

        case 17:
          response = _context3.sent;
          _context3.next = 20;
          return regeneratorRuntime.awrap(response.json());

        case 20:
          data = _context3.sent;

          if (response.ok) {
            resultDiv.innerHTML = "<div class=\"alert alert-success\">Transfer successful! Transaction ID: ".concat(data.transactionId || 'N/A', "</div>");
            this.reset();
          } else {
            resultDiv.innerHTML = "<div class=\"alert alert-danger\">Transfer failed: ".concat(data.error || 'Unknown error', "</div>");
          }

          _context3.next = 26;
          break;

        case 24:
          _context3.prev = 24;
          _context3.t0 = _context3["catch"](14);

        case 26:
          _context3.prev = 26;
          this.querySelector('button[type="submit"]').disabled = false;
          return _context3.finish(26);

        case 29:
        case "end":
          return _context3.stop();
      }
    }
  }, null, this, [[14, 24, 26, 29]]);
});