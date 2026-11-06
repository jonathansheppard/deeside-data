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