// Unit tests for phone-format.js.
// Run:  node --test tests/phone-format.test.js
// (Node 18+ ships node:test in stdlib; zero deps.)

const test = require('node:test');
const assert = require('node:assert/strict');

const { formatPhone } = require('../site/phone-format.js');

test('empty and whitespace inputs', () => {
  assert.equal(formatPhone(''), '');
  assert.equal(formatPhone('   '), '');
  assert.equal(formatPhone('abc'), '');
});

test('defensive: non-string inputs', () => {
  assert.equal(formatPhone(null), '');
  assert.equal(formatPhone(undefined), '');
  assert.equal(formatPhone(2015550123), '(201) 555-0123');
});

test('progressive typing — US, no leading 1', () => {
  assert.equal(formatPhone('2'), '(2');
  assert.equal(formatPhone('20'), '(20');
  assert.equal(formatPhone('201'), '(201');
  assert.equal(formatPhone('2015'), '(201) 5');
  assert.equal(formatPhone('20155'), '(201) 55');
  assert.equal(formatPhone('201555'), '(201) 555');
  assert.equal(formatPhone('2015550'), '(201) 555-0');
  assert.equal(formatPhone('20155501'), '(201) 555-01');
  assert.equal(formatPhone('201555012'), '(201) 555-012');
  assert.equal(formatPhone('2015550123'), '(201) 555-0123');
});

test('US no-leading-1: digits past 10 are dropped', () => {
  assert.equal(formatPhone('20155501234'), '(201) 555-0123');
  assert.equal(formatPhone('20155501239999'), '(201) 555-0123');
});

test('progressive typing — US with leading 1', () => {
  assert.equal(formatPhone('1'), '1');
  assert.equal(formatPhone('12'), '1 (2');
  assert.equal(formatPhone('120'), '1 (20');
  assert.equal(formatPhone('1201'), '1 (201');
  assert.equal(formatPhone('12015'), '1 (201) 5');
  assert.equal(formatPhone('1201555'), '1 (201) 555');
  assert.equal(formatPhone('12015550'), '1 (201) 555-0');
  assert.equal(formatPhone('12015550123'), '1 (201) 555-0123');
});

test('US with leading 1: digits past 11 are dropped', () => {
  assert.equal(formatPhone('120155501234'), '1 (201) 555-0123');
  assert.equal(formatPhone('1201555012399'), '1 (201) 555-0123');
});

test('idempotent: re-formatting an already-formatted string yields itself', () => {
  assert.equal(formatPhone('(201) 555-0123'), '(201) 555-0123');
  assert.equal(formatPhone('1 (201) 555-0123'), '1 (201) 555-0123');
});

test('common separators get normalized', () => {
  assert.equal(formatPhone('201-555-0123'), '(201) 555-0123');
  assert.equal(formatPhone('201.555.0123'), '(201) 555-0123');
  assert.equal(formatPhone('201 555 0123'), '(201) 555-0123');
  assert.equal(formatPhone('2015550123'), '(201) 555-0123');
  assert.equal(formatPhone('(201)5550123'), '(201) 555-0123');
});

test('leading-1 variants get normalized', () => {
  assert.equal(formatPhone('1-201-555-0123'), '1 (201) 555-0123');
  assert.equal(formatPhone('1.201.555.0123'), '1 (201) 555-0123');
  assert.equal(formatPhone('1 201 555 0123'), '1 (201) 555-0123');
  assert.equal(formatPhone('1(201)5550123'), '1 (201) 555-0123');
});

test('garbage characters between digits are stripped', () => {
  assert.equal(formatPhone('abc201def555ghi0123'), '(201) 555-0123');
  assert.equal(formatPhone('phone: 201-555-0123 ext 42'), '(201) 555-0123');
});

test('international ("+" prefix) passes through untouched', () => {
  assert.equal(formatPhone('+'), '+');
  assert.equal(formatPhone('+1'), '+1');
  assert.equal(formatPhone('+1 201 555 0123'), '+1 201 555 0123');
  assert.equal(formatPhone('+44 20 1234 5678'), '+44 20 1234 5678');
  assert.equal(formatPhone('+972-50-1234567'), '+972-50-1234567');
  assert.equal(formatPhone('+91 98765 43210'), '+91 98765 43210');
});

test('international: absurdly long inputs are safety-capped at 25 chars', () => {
  const longJunk = '+1' + '2'.repeat(50);
  const got = formatPhone(longJunk);
  assert.equal(got.length, 25);
  assert.equal(got.charAt(0), '+');
});

test('backspace behavior: deletes a separator, reformats correctly', () => {
  // User had "(201) 555-0123", deleted the closing ')'
  // → "(201 555-0123" → strip → 9 digits "201555012" → reformat
  assert.equal(formatPhone('(201 555-012'), '(201) 555-012');
  // User had "(201) 5", deleted the space → "(201)5"
  assert.equal(formatPhone('(201)5'), '(201) 5');
});

test('mid-string insertion: caps at max-digits (trailing digit dropped)', () => {
  // Was "(201) 555-0123" (10 digits); user inserted '5' after ')' →
  // "(201)5 555-0123" → strip → "20155550123" (11 digits, no leading 1)
  // → cap at 10 → "2015555012" → "(201) 555-5012".
  // Note: dropping the *last* user-typed digit is the trade-off of
  // letting users edit in the middle. Cursor lands at end after format.
  assert.equal(formatPhone('(201)5 555-0123'), '(201) 555-5012');
});

test('paste behavior: raw 10-digit string becomes formatted', () => {
  assert.equal(formatPhone('2015550123'), '(201) 555-0123');
});

test('paste behavior: pre-formatted strings stay stable', () => {
  assert.equal(formatPhone('(201) 555-0123'), '(201) 555-0123');
  assert.equal(formatPhone('(201) 555-0123'), formatPhone(formatPhone('(201) 555-0123')));
});

test('paste behavior: international strings pass through', () => {
  assert.equal(formatPhone('+44 20 1234 5678'), '+44 20 1234 5678');
});

test('output of formatter matches the form pattern regex', () => {
  // Mirror the pattern attribute on the inquire-form phone input.
  const pattern = new RegExp(
    '^(?=(?:\\D*\\d){10})[\\d\\s\\(\\)\\.\\-+]{10,30}$',
    'v',
  );
  const cases = [
    '2015550123',
    '201-555-0123',
    '(201) 555-0123',
    '12015550123',
    '1 (201) 555-0123',
    '+1 201 555 0123',
    '+44 20 1234 5678',
  ];
  for (const c of cases) {
    const formatted = formatPhone(c);
    assert.ok(
      pattern.test(formatted),
      `formatted "${formatted}" (from "${c}") must satisfy the form pattern`,
    );
  }
});

test('all-zero digits format correctly', () => {
  assert.equal(formatPhone('0000000000'), '(000) 000-0000');
});

test('partial leading 1 alone stays as "1"', () => {
  // Just '1' should not yet expand to "1 (" — we wait for at least 2 digits.
  assert.equal(formatPhone('1'), '1');
});
