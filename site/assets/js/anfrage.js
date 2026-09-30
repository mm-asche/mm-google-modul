/* Holzwerk Hanssen – mehrstufige Projektanfrage
 *
 * Tracking-Hinweis: Jeder Schritt ändert den URL-Anker (#schritt-2, #schritt-3).
 * In GTM löst das den Trigger „Verlaufsänderung“ aus (Variable „History New URL Fragment“).
 * Damit lassen sich Trichterschritte und abgebrochene Anfragen messen, ohne dass die
 * Seite selbst etwas in den dataLayer schreibt.
 * Das Formular ist ein echtes <form> (Netlify) und wird erst in Schritt 3 abgeschickt.
 */
(function () {
  'use strict';
  var form = document.getElementById('form-anfrage');
  if (!form) return;
  var schritte = form.querySelectorAll('[data-schritt]');
  var anzeige = document.querySelectorAll('.schritte-anzeige li');
  var aktuell = 1;

  // Leistung aus ?leistung=… vorbelegen (Links von den Leistungsseiten)
  var vorgabe = new URLSearchParams(location.search).get('leistung');
  if (vorgabe) {
    var radio = form.querySelector('input[name="leistung"][value="' + vorgabe + '"]');
    if (radio) radio.checked = true;
  }

  function zeige(n, ankerSetzen) {
    aktuell = n;
    Array.prototype.forEach.call(schritte, function (s) { s.hidden = +s.getAttribute('data-schritt') !== n; });
    Array.prototype.forEach.call(anzeige, function (li, i) {
      li.classList.toggle('aktiv', i + 1 === n);
      li.classList.toggle('erledigt', i + 1 < n);
    });
    if (ankerSetzen) {
      if (n === 1) history.pushState(null, '', location.pathname + location.search);
      else location.hash = 'schritt-' + n;
    }
    var kopf = document.getElementById('anfrage-kopf');
    if (kopf && ankerSetzen) kopf.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function gueltig(n) {
    var felder = form.querySelectorAll('[data-schritt="' + n + '"] [required]');
    for (var i = 0; i < felder.length; i++) { if (!felder[i].reportValidity()) return false; }
    return true;
  }

  form.addEventListener('click', function (ev) {
    var weiter = ev.target.closest('[data-weiter]');
    var zurueck = ev.target.closest('[data-zurueck]');
    if (weiter) { ev.preventDefault(); if (gueltig(aktuell)) zeige(aktuell + 1, true); }
    if (zurueck) { ev.preventDefault(); zeige(aktuell - 1, true); }
  });

  // Zurück-Taste des Browsers
  window.addEventListener('popstate', function () {
    var m = location.hash.match(/schritt-(\d)/);
    zeige(m ? +m[1] : 1, false);
  });

  // Beim Laden immer mit Schritt 1 beginnen
  if (location.hash) history.replaceState(null, '', location.pathname + location.search);
  zeige(1, false);
})();
