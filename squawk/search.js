(function () {
  var i = document.getElementById('sq-q'), m = document.getElementById('sq-msg'), out = document.getElementById('sq-res');
  if (!i) return;
  var rows = [].slice.call(document.querySelectorAll('#sq-full tr[data-lo]')).map(function (r) {
    var c = r.querySelectorAll('td');
    return {lo: r.dataset.lo, hi: r.dataset.hi, code: c[0].textContent, who: c[1].textContent, what: c[2].textContent,
            w: parseInt(r.dataset.hi, 8) - parseInt(r.dataset.lo, 8)};
  });
  function esc(t) { return t.replace(/[&<>]/g, function (ch) { return {'&': '&amp;', '<': '&lt;', '>': '&gt;'}[ch]; }); }
  i.addEventListener('input', function () {
    var q = i.value.replace(/\D/g, '').slice(0, 4);
    out.innerHTML = '';
    if (!q) { m.textContent = ''; return; }
    if (/[89]/.test(q)) { m.textContent = 'Squawk codes only use the digits 0 to 7, so there is no code ' + q + '.'; return; }
    var hits = rows.filter(function (r) { return q.length === 4 ? (q >= r.lo && q <= r.hi) : r.lo.indexOf(q) === 0; });
    hits.sort(function (x, y) { return x.w - y.w || (x.lo < y.lo ? -1 : 1); });
    if (!hits.length) { m.textContent = q.length === 4 ? 'No UK allocation found for ' + q + '. It may be a code assigned by another country.' : ''; return; }
    m.textContent = hits.length + (hits.length === 1 ? ' match' : ' matches') + (hits.length > 8 ? ', showing the 8 most specific' : '') + (q.length === 4 && hits.length > 1 ? '. Several units can share a block of codes; the most specific is first.' : '');
    out.innerHTML = '<table class="sq-t">' + hits.slice(0, 8).map(function (r) {
      return '<tr><td><strong>' + esc(r.code) + '</strong></td><td>' + esc(r.who) + '</td><td>' + esc(r.what) + '</td></tr>';
    }).join('') + '</table>';
  });
})();
(function () {
  var box = document.getElementById('sq-live');
  if (!box || !window.fetch) return;
  function esc(t) { return String(t).replace(/[&<>]/g, function (ch) { return {'&': '&amp;', '<': '&lt;', '>': '&gt;'}[ch]; }); }
  function tm(s) { return new Date(s).toLocaleTimeString('en-GB', {timeZone: 'Europe/London', hour: '2-digit', minute: '2-digit'}); }
  function dt(s) { return new Date(s).toLocaleDateString('en-GB', {timeZone: 'Europe/London', weekday: 'short', day: 'numeric', month: 'short'}) + ' ' + tm(s); }
  function line(e) { return esc(e.kind) + ', ' + esc(e.aircraft) + (e.where ? ', ' + esc(e.where) : '') + (e.alt ? ' at ' + esc(e.alt) : '') + (e.from_hawarden ? ', from Hawarden' : ''); }
  fetch('https://65-109-143-26.sslip.io/live/squawks.json?t=' + Math.floor(Date.now() / 60000)).then(function (r) { return r.json(); }).then(function (d) {
    if ((Date.now() - new Date(d.updated)) / 60000 > 30) return;
    var now = d.active.length
      ? '<p style="margin:6px 0;padding:8px 10px;background:#fff4e0;color:#7c3a03;font-weight:600">Right now: ' + line(d.active[d.active.length - 1]) + ', seen ' + tm(d.active[d.active.length - 1].at) + '.</p>'
      : '<p style="margin:6px 0">No emergency squawks in our region right now.</p>';
    var list = d.recent.length ? '<ul style="margin:6px 0 6px 18px;padding:0">' + d.recent.slice(0, 6).map(function (e) {
      return '<li style="margin:2px 0"><strong>' + dt(e.at) + '</strong>: ' + line(e) + '</li>'; }).join('') + '</ul>' : '';
    var since = new Date(d.since).toLocaleDateString('en-GB', {timeZone: 'Europe/London', day: 'numeric', month: 'long', year: 'numeric'});
    box.innerHTML = '<strong>Emergency squawks seen in our region</strong> <span class="sq-note">updated ' + tm(d.updated) + '</span>' + now +
      (list ? '<div class="sq-note" style="margin-top:8px">Most recent:</div>' + list : '') +
      '<p class="sq-note" style="margin:6px 0 0">Checked every 2 minutes across ' + esc(d.area) + '. Most are precautionary or radio problems and end with a normal landing. ' +
      d.last30 + ' in the last 30 days (our records start ' + since + '). Source: ' + esc(d.source) + '.</p>';
    box.style.display = '';
  }).catch(function () {});
})();