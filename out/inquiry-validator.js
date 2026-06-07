// Form-validation enhancement for the inquiry form. Fails OPEN — any
// exception here lets the browser fall back to native submission. We
// must never block the form.
// ES5 only; no arrow fns, no NodeList.forEach, no optional chaining.
(function(){
  var form = document.querySelector('form[name="inquiry"]');
  if (!form) return;
  var nativeValidationOff = false;
  var safeWarn = function(msg, err){
    if (window.console && console.warn) {
      try { console.warn(msg, err); } catch (e) {}
    }
  };
  try {
    // Feature-detect: if the browser lacks Constraint Validation, do nothing
    // and leave native form submission entirely in charge.
    var probe = document.createElement('input');
    if (!('validity' in probe) || !('checkValidity' in probe)) return;

    var inputs = form.querySelectorAll('input, select, textarea');
    if (!inputs || typeof inputs.length !== 'number') return;

    form.noValidate = true;
    nativeValidationOff = true;

    var skip = function(el){
      if (!el) return true;
      if (el.type === 'hidden') return true;
      if (el.name === 'company') return true; // honeypot
      if (!('validity' in el)) return true;
      return false;
    };

    var getMessage = function(el){
      // Custom-validity messages (e.g. cross-field "phone OR email") take
      // priority over the per-field data-error fallback.
      if (el.validity && el.validity.customError && el.validationMessage) {
        return el.validationMessage;
      }
      var ds = el.getAttribute ? el.getAttribute('data-error') : null;
      if (ds) return ds;
      if (el.title) return el.title;
      if (el.validationMessage) return el.validationMessage;
      return 'Please check this field.';
    };

    var paint = function(el){
      if (!el || !el.id) return;
      var err = document.getElementById(el.id + '-error');
      if (!err) return;
      if (el.validity && el.validity.valid) {
        err.textContent = '';
        el.removeAttribute('aria-invalid');
      } else {
        err.textContent = getMessage(el);
        el.setAttribute('aria-invalid', 'true');
      }
    };

    var attach = function(el){
      el.addEventListener('blur', function(){
        try { paint(el); } catch (e) { safeWarn('blur paint failed', e); }
      });
      el.addEventListener('input', function(){
        try { if (el.validity && el.validity.valid) paint(el); } catch (e) {}
      });
    };

    for (var i = 0; i < inputs.length; i++) {
      if (!skip(inputs[i])) attach(inputs[i]);
    }

    // Cross-field rule: at least one of phone / email must be provided.
    // Implemented via setCustomValidity on phone so the existing paint
    // pipeline surfaces it. Re-checked on input of either field.
    var phoneEl = form.querySelector('#phone');
    var emailEl = form.querySelector('#email');
    var checkContactMethod = function(){
      if (!phoneEl || !emailEl) return;
      var phoneVal = (phoneEl.value || '').replace(/\s/g, '');
      var emailVal = (emailEl.value || '').replace(/\s/g, '');
      if (!phoneVal && !emailVal) {
        try { phoneEl.setCustomValidity('Phone or email is required so I can reply.'); } catch (e) {}
      } else {
        try { phoneEl.setCustomValidity(''); } catch (e) {}
      }
    };
    if (phoneEl) phoneEl.addEventListener('input', function(){ try { checkContactMethod(); paint(phoneEl); } catch (e) {} });
    if (emailEl) emailEl.addEventListener('input', function(){ try { checkContactMethod(); paint(phoneEl); } catch (e) {} });

    // Phone auto-formatter (US "(XXX) XXX-XXXX", '+' prefix passes through).
    // Defined in static/phone-format.js. If the file failed to load, skip
    // silently — the input still works, just without auto-formatting.
    if (phoneEl && typeof window.formatPhone === 'function') {
      phoneEl.addEventListener('input', function(){
        try {
          var next = window.formatPhone(phoneEl.value);
          if (next !== phoneEl.value) {
            phoneEl.value = next;
            try { phoneEl.setSelectionRange(next.length, next.length); } catch (e) {}
          }
        } catch (e) {
          safeWarn('phone formatter failed open', e);
        }
      });
    }

    form.addEventListener('submit', function(e){
      try {
        // Re-evaluate the phone-or-email rule before walking field validity
        // so a stale customValidity from earlier interaction doesn't linger.
        checkContactMethod();
        var first = null;
        for (var j = 0; j < inputs.length; j++) {
          var el = inputs[j];
          if (skip(el)) continue;
          paint(el);
          if (el.validity && !el.validity.valid && !first) first = el;
        }
        if (first) {
          e.preventDefault();
          try { first.focus(); } catch (ee) {}
        }
      } catch (err) {
        // Fail open: never block submission due to our JS.
        safeWarn('submit-handler failed open', err);
      }
    });
  } catch (err) {
    // Setup failed — restore native validation so the form still works.
    if (nativeValidationOff && form) {
      try { form.noValidate = false; } catch (e) {}
    }
    safeWarn('inquiry validator setup failed', err);
  }
})();
