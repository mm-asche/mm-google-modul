/* Holzwerk Hanssen – Grundfunktionen aller Seiten
 *
 * Tracking-Hinweis: Dieses Skript schreibt NUR Consent-Ereignisse in den dataLayer
 * (wie es ein Cookie-Tool auch tun würde). Klicks, Formulare, Scrolltiefe usw.
 * soll GTM selbst erfassen – genau das ist der Übungsstoff.
 */
(function () {
  'use strict';

  // ---------------------------------------------------------------- Navigation
  var toggle = document.getElementById('nav-toggle');
  if (toggle) {
    toggle.addEventListener('click', function () {
      var offen = document.body.classList.toggle('nav-offen');
      toggle.setAttribute('aria-expanded', offen ? 'true' : 'false');
    });
  }

  // ---------------------------------------------------------------- Warenkorb-Zähler
  function warenkorbZahl() {
    var zahl = document.getElementById('warenkorb-zahl');
    if (!zahl) return;
    var korb = [];
    try { korb = JSON.parse(localStorage.getItem('hh_warenkorb')) || []; } catch (e) {}
    var n = korb.reduce(function (s, p) { return s + (p.menge || 0); }, 0);
    zahl.textContent = n;
    zahl.hidden = n === 0;
  }
  warenkorbZahl();
  window.addEventListener('hh:warenkorb', warenkorbZahl);

  // ---------------------------------------------------------------- Consent-Banner
  var banner = document.getElementById('consent-banner');
  if (banner) {
    var details = document.getElementById('consent-details');
    var chkStat = document.getElementById('consent-statistik');
    var chkMark = document.getElementById('consent-marketing');
    var btnSpeichern = document.getElementById('consent-speichern');
    var btnEinst = document.getElementById('consent-einstellungen');

    var gespeichert = null;
    try { gespeichert = JSON.parse(localStorage.getItem('hh_consent')); } catch (e) {}

    var zeigen = function () {
      if (gespeichert) { chkStat.checked = !!gespeichert.statistik; chkMark.checked = !!gespeichert.marketing; }
      banner.hidden = false;
    };
    if (!gespeichert) zeigen();

    var speichern = function (statistik, marketing, art) {
      gespeichert = { statistik: statistik, marketing: marketing, zeit: new Date().toISOString() };
      try { localStorage.setItem('hh_consent', JSON.stringify(gespeichert)); } catch (e) {}
      var m = marketing ? 'granted' : 'denied';
      window.gtag('consent', 'update', {
        analytics_storage: statistik ? 'granted' : 'denied',
        ad_storage: m, ad_user_data: m, ad_personalization: m
      });
      window.dataLayer.push({
        event: 'consent_aktualisiert',
        consent_art: art,
        consent_statistik: statistik ? 'ja' : 'nein',
        consent_marketing: marketing ? 'ja' : 'nein'
      });
      banner.hidden = true;
      document.dispatchEvent(new CustomEvent('hh:consent', { detail: gespeichert }));
    };

    document.getElementById('consent-alle').addEventListener('click', function () { speichern(true, true, 'alle'); });
    document.getElementById('consent-ablehnen').addEventListener('click', function () { speichern(false, false, 'notwendig'); });
    btnEinst.addEventListener('click', function () {
      details.hidden = false; btnSpeichern.hidden = false; btnEinst.hidden = true;
    });
    btnSpeichern.addEventListener('click', function () { speichern(chkStat.checked, chkMark.checked, 'auswahl'); });

    var link = document.getElementById('cookie-einstellungen');
    if (link) link.addEventListener('click', function (ev) { ev.preventDefault(); zeigen(); });
  }

  // ---------------------------------------------------------------- Anfrage-Links mit Leistung vorbelegen
  // (Leistungsseiten verlinken auf /anfrage/?leistung=kuechen – das Formular liest den Parameter aus)

  // ---------------------------------------------------------------- AJAX-Rückrufformular (Kontaktseite)
  // Absichtlich KEIN <form>: Der GTM-Trigger „Formularsendung“ greift hier nicht.
  // Erfolg wird nur als DOM-Ereignis „demoform:gesendet“ gemeldet – ein Listener-Tag in GTM
  // muss daraus einen dataLayer-Eintrag machen (gleiches Verhalten wie die alte Testseite).
  var ajax = document.getElementById('form-ajax');
  if (ajax) {
    var ok = document.getElementById('ajax-erfolg');
    var err = document.getElementById('ajax-fehler');
    var knopf = document.getElementById('ajax-button');
    var feld = function (n) { return ajax.querySelector('[name="' + n + '"]'); };

    knopf.addEventListener('click', function () {
      var pflicht = ajax.querySelectorAll('[required]');
      for (var i = 0; i < pflicht.length; i++) { if (!pflicht[i].reportValidity()) return; }
      err.hidden = true;
      knopf.disabled = true;
      knopf.textContent = 'Wird gesendet …';
      var daten = new URLSearchParams({
        'form-name': 'rueckruf-ajax',
        name: feld('name').value, telefon: feld('telefon').value, uhrzeit: feld('uhrzeit').value
      });
      fetch('/', { method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, body: daten.toString() })
        .then(function (res) {
          if (!res.ok) throw new Error('HTTP ' + res.status);
          ajax.hidden = true;
          ok.hidden = false;
          document.dispatchEvent(new CustomEvent('demoform:gesendet', {
            detail: { formName: 'rueckruf-ajax', uhrzeit: feld('uhrzeit').value }
          }));
        })
        .catch(function () {
          err.hidden = false;
          knopf.disabled = false;
          knopf.textContent = 'Rückruf anfordern';
        });
    });
  }

  // ---------------------------------------------------------------- YouTube erst nach Einwilligung (video_modus „nach_einwilligung“)
  var video = document.querySelector('[data-youtube-src]');
  if (video) {
    var laden = function () {
      if (video.querySelector('iframe')) return;
      video.innerHTML = '<iframe id="youtube-ueber-uns" src="' + video.getAttribute('data-youtube-src') +
        '" title="Video" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>';
    };
    var c = null;
    try { c = JSON.parse(localStorage.getItem('hh_consent')); } catch (e) {}
    if (c && c.marketing) laden();
    document.addEventListener('hh:consent', function (ev) { if (ev.detail && ev.detail.marketing) laden(); });
    video.addEventListener('click', function (ev) { if (ev.target.id === 'video-laden') laden(); });
  }

  // ---------------------------------------------------------------- Aktuelles Jahr
  var jahr = document.querySelectorAll('.js-jahr');
  for (var j = 0; j < jahr.length; j++) jahr[j].textContent = new Date().getFullYear();
})();
