// Phone-number formatter for the inquiry form input.
//
// Pure function: takes a raw input string, returns the formatted string.
// Behavior:
//   - Input starting with '+' is passed through (international), truncated
//     at 25 chars only as a safety cap.
//   - Otherwise, non-digit characters are stripped and:
//       - If the first digit is '1' (US country code), format as
//         "1 (XXX) XXX-XXXX" and cap at 11 digits.
//       - Else format as "(XXX) XXX-XXXX" and cap at 10 digits.
//
// Loaded in the browser as a plain <script>; sets window.formatPhone.
// Also exported via module.exports so Node can require it for tests.
//
// ES5 only — must work in older mobile browsers identically to the rest
// of inquiry-validator.js.

(function (root) {
  function formatPhone(raw) {
    if (typeof raw !== 'string') raw = String(raw == null ? '' : raw);

    // International bypass.
    if (raw.charAt(0) === '+') {
      return raw.length > 25 ? raw.slice(0, 25) : raw;
    }

    var digits = raw.replace(/\D/g, '');
    if (digits.length === 0) return '';

    var leading1 = digits.charAt(0) === '1';
    var maxDigits = leading1 ? 11 : 10;
    if (digits.length > maxDigits) digits = digits.slice(0, maxDigits);

    if (leading1) {
      if (digits.length === 1) return '1';
      if (digits.length <= 4) return '1 (' + digits.slice(1);
      if (digits.length <= 7) {
        return '1 (' + digits.slice(1, 4) + ') ' + digits.slice(4);
      }
      return '1 (' + digits.slice(1, 4) + ') ' + digits.slice(4, 7) + '-' + digits.slice(7);
    }

    if (digits.length <= 3) return '(' + digits;
    if (digits.length <= 6) return '(' + digits.slice(0, 3) + ') ' + digits.slice(3);
    return '(' + digits.slice(0, 3) + ') ' + digits.slice(3, 6) + '-' + digits.slice(6);
  }

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = { formatPhone: formatPhone };
  }
  root.formatPhone = formatPhone;
})(typeof window !== 'undefined' ? window : globalThis);
