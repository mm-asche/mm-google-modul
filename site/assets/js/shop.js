/* Holzwerk Hanssen – Mini-Shop (Demo, keine echte Zahlung)
 *
 * Tracking-Hinweis: Wie ein echtes Shopsystem (WooCommerce, Shopware, Shopify …) schreibt
 * dieser Shop die E-Commerce-Ereignisse nach GA4-Empfehlung in den dataLayer:
 *   view_item_list, select_item, view_item, add_to_cart, remove_from_cart,
 *   view_cart, begin_checkout, add_shipping_info, add_payment_info, purchase
 * In GTM braucht es dafür einen GA4-Ereignis-Tag mit „E-Commerce-Daten senden“ (Datenschicht)
 * und einen Trigger „Benutzerdefiniertes Ereignis“ auf die Ereignisnamen.
 * Der Warenkorb liegt im localStorage des Browsers, Bestellungen gehen nirgendwohin.
 */
(function () {
  'use strict';
  var SHOP = window.HH_SHOP;
  if (!SHOP) return;
  var W = 'EUR';

  // ---------------------------------------------------------------- Helfer
  function geld(n) { return n.toFixed(2).replace('.', ',') + ' €'; }
  function runde(n) { return Math.round(n * 100) / 100; }
  function $(id) { return document.getElementById(id); }

  function lies() {
    try { return JSON.parse(localStorage.getItem('hh_warenkorb')) || []; } catch (e) { return []; }
  }
  function schreib(korb) {
    try { localStorage.setItem('hh_warenkorb', JSON.stringify(korb)); } catch (e) {}
    window.dispatchEvent(new Event('hh:warenkorb'));
  }

  function artikel(id, menge, extra) {
    var p = SHOP.produkte[id];
    var a = { item_id: id, item_name: p.name, item_brand: 'Holzwerk Hanssen', item_category: p.kategorie, price: p.preis, quantity: menge || 1 };
    if (extra) for (var k in extra) a[k] = extra[k];
    return a;
  }

  function melde(ereignis, ecommerce) {
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({ ecommerce: null }); // vorheriges E-Commerce-Objekt leeren (Google-Empfehlung)
    window.dataLayer.push({ event: ereignis, ecommerce: ecommerce });
  }

  function summe(korb) {
    return runde(korb.reduce(function (s, a) { return s + SHOP.produkte[a.id].preis * a.menge; }, 0));
  }
  function nurDigital(korb) {
    return korb.length > 0 && korb.every(function (a) { return SHOP.produkte[a.id].digital; });
  }
  function versand(korb, art) {
    if (art === 'abholung' || nurDigital(korb)) return 0;
    return summe(korb) >= SHOP.versand.kostenlos_ab ? 0 : SHOP.versand.standard;
  }
  function korbArtikel(korb) {
    return korb.map(function (a, i) { return artikel(a.id, a.menge, { index: i }); });
  }

  function hinzufuegen(id, menge, liste) {
    var korb = lies();
    var vorhanden = korb.filter(function (a) { return a.id === id; })[0];
    if (vorhanden) vorhanden.menge = Math.min(vorhanden.menge + menge, 20);
    else korb.push({ id: id, menge: menge });
    schreib(korb);
    var extra = liste ? { item_list_name: liste } : null;
    melde('add_to_cart', { currency: W, value: runde(SHOP.produkte[id].preis * menge), items: [artikel(id, menge, extra)] });
  }

  // ---------------------------------------------------------------- Produktlisten
  var listen = document.querySelectorAll('[data-ecommerce-liste]');
  Array.prototype.forEach.call(listen, function (liste) {
    var name = liste.getAttribute('data-ecommerce-liste');
    var items = Array.prototype.map.call(liste.querySelectorAll('.js-produkt-link'), function (a, i) {
      return artikel(a.getAttribute('data-produkt'), 1, { index: i, item_list_name: name });
    });
    if (items.length) melde('view_item_list', { item_list_name: name, items: items });
  });

  document.addEventListener('click', function (ev) {
    var link = ev.target.closest('.js-produkt-link');
    if (link) {
      melde('select_item', {
        item_list_name: link.getAttribute('data-liste'),
        items: [artikel(link.getAttribute('data-produkt'), 1, { index: +link.getAttribute('data-index'), item_list_name: link.getAttribute('data-liste') })]
      });
    }
    var knopf = ev.target.closest('.js-in-warenkorb');
    if (knopf) {
      hinzufuegen(knopf.getAttribute('data-produkt'), 1, knopf.getAttribute('data-liste'));
      var alt = knopf.textContent;
      knopf.textContent = '✓ Im Warenkorb';
      knopf.disabled = true;
      setTimeout(function () { knopf.textContent = alt; knopf.disabled = false; }, 1600);
    }
  });

  // ---------------------------------------------------------------- Produktseite
  var detail = document.querySelector('[data-produkt-seite]');
  if (detail) {
    var pid = detail.getAttribute('data-produkt-seite');
    melde('view_item', { currency: W, value: SHOP.produkte[pid].preis, items: [artikel(pid, 1)] });
    $('produkt-in-warenkorb').addEventListener('click', function () {
      var menge = Math.max(1, Math.min(20, parseInt($('produkt-menge').value, 10) || 1));
      hinzufuegen(pid, menge);
      $('produkt-hinzugefuegt').hidden = false;
    });
  }

  // ---------------------------------------------------------------- Warenkorb
  var korbBox = $('warenkorb-inhalt');
  if (korbBox) {
    var zeichneKorb = function () {
      var korb = lies();
      var leer = $('warenkorb-leer');
      var voll = $('warenkorb-voll');
      leer.hidden = korb.length > 0;
      voll.hidden = korb.length === 0;
      if (!korb.length) return;
      korbBox.innerHTML = korb.map(function (a) {
        var p = SHOP.produkte[a.id];
        return '<tr><td><div class="korb-produkt"><img src="/assets/bilder/' + p.bild + '" alt=""><a href="/shop/' + p.slug + '/">' + p.name + '</a></div></td>' +
          '<td>' + geld(p.preis) + '</td>' +
          '<td><input type="number" min="1" max="20" value="' + a.menge + '" data-menge="' + a.id + '" aria-label="Menge"></td>' +
          '<td><strong>' + geld(p.preis * a.menge) + '</strong></td>' +
          '<td><button type="button" class="korb-entfernen" data-entfernen="' + a.id + '">Entfernen</button></td></tr>';
      }).join('');
      var v = versand(korb, 'standard');
      $('korb-zwischensumme').textContent = geld(summe(korb));
      $('korb-versand').textContent = v === 0 ? 'kostenlos' : geld(v);
      $('korb-gesamt').textContent = geld(summe(korb) + v);
      var fehlt = SHOP.versand.kostenlos_ab - summe(korb);
      $('korb-versandhinweis').textContent = (fehlt > 0 && !nurDigital(korb))
        ? 'Noch ' + geld(fehlt) + ' bis zum kostenlosen Versand.' : 'Ihre Bestellung wird versandkostenfrei geliefert.';
    };
    zeichneKorb();
    var start = lies();
    melde('view_cart', { currency: W, value: summe(start), items: korbArtikel(start) });

    korbBox.addEventListener('change', function (ev) {
      var id = ev.target.getAttribute('data-menge');
      if (!id) return;
      var korb = lies();
      var a = korb.filter(function (x) { return x.id === id; })[0];
      var neu = Math.max(1, Math.min(20, parseInt(ev.target.value, 10) || 1));
      var diff = neu - a.menge;
      a.menge = neu;
      schreib(korb);
      if (diff !== 0) {
        melde(diff > 0 ? 'add_to_cart' : 'remove_from_cart',
          { currency: W, value: runde(SHOP.produkte[id].preis * Math.abs(diff)), items: [artikel(id, Math.abs(diff))] });
      }
      zeichneKorb();
    });
    korbBox.addEventListener('click', function (ev) {
      var id = ev.target.getAttribute('data-entfernen');
      if (!id) return;
      var korb = lies();
      var a = korb.filter(function (x) { return x.id === id; })[0];
      schreib(korb.filter(function (x) { return x.id !== id; }));
      melde('remove_from_cart', { currency: W, value: runde(SHOP.produkte[id].preis * a.menge), items: [artikel(id, a.menge)] });
      zeichneKorb();
    });
  }

  // ---------------------------------------------------------------- Kasse
  var kasse = $('form-kasse');
  if (kasse) {
    var korbK = lies();
    if (!korbK.length) { location.replace('/shop/warenkorb/'); return; }

    var gewaehlt = function (name) { var r = kasse.querySelector('[name="' + name + '"]:checked'); return r ? r.value : ''; };
    var zeichneUebersicht = function () {
      var v = versand(korbK, gewaehlt('versand'));
      $('kasse-positionen').innerHTML = korbK.map(function (a) {
        var p = SHOP.produkte[a.id];
        return '<li><span>' + a.menge + ' × ' + p.name + '</span><span>' + geld(p.preis * a.menge) + '</span></li>';
      }).join('');
      $('kasse-zwischensumme').textContent = geld(summe(korbK));
      $('kasse-versand').textContent = v === 0 ? 'kostenlos' : geld(v);
      $('kasse-gesamt').textContent = geld(summe(korbK) + v);
      $('kasse-mwst').textContent = geld((summe(korbK) + v) / 1.19 * 0.19);
    };
    zeichneUebersicht();
    melde('begin_checkout', { currency: W, value: summe(korbK), items: korbArtikel(korbK) });

    var gemeldet = { versand: false, zahlung: false };
    var meldeVersand = function () {
      if (gemeldet.versand) return; gemeldet.versand = true;
      melde('add_shipping_info', { currency: W, value: summe(korbK), shipping_tier: gewaehlt('versand'), items: korbArtikel(korbK) });
    };
    var meldeZahlung = function () {
      if (gemeldet.zahlung) return; gemeldet.zahlung = true;
      melde('add_payment_info', { currency: W, value: summe(korbK), payment_type: gewaehlt('zahlung'), items: korbArtikel(korbK) });
    };
    kasse.addEventListener('change', function (ev) {
      if (ev.target.name === 'versand') { zeichneUebersicht(); meldeVersand(); }
      if (ev.target.name === 'zahlung') meldeZahlung();
    });

    kasse.addEventListener('submit', function (ev) {
      ev.preventDefault();
      meldeVersand();
      meldeZahlung();
      var v = versand(korbK, gewaehlt('versand'));
      var gesamt = runde(summe(korbK) + v);
      var bestellung = {
        transaction_id: 'HH-' + Date.now().toString(36).toUpperCase() + '-' + Math.floor(Math.random() * 900 + 100),
        value: summe(korbK),
        tax: runde(gesamt / 1.19 * 0.19),
        shipping: v,
        currency: W,
        payment_type: gewaehlt('zahlung'),
        shipping_tier: gewaehlt('versand'),
        items: korbArtikel(korbK),
        gesamt: gesamt,
        email: ($('kasse-email') || {}).value || ''
      };
      try { sessionStorage.setItem('hh_bestellung', JSON.stringify(bestellung)); } catch (e) {}
      schreib([]);
      location.href = '/shop/bestellung-bestaetigt/';
    });
  }

  // ---------------------------------------------------------------- Bestellbestätigung
  var best = $('bestellung-bestaetigt');
  if (best) {
    var b = null;
    try { b = JSON.parse(sessionStorage.getItem('hh_bestellung')); } catch (e) {}
    if (!b) { $('bestellung-keine').hidden = false; return; }
    best.hidden = false;
    $('bestellnummer').textContent = b.transaction_id;
    $('bestellsumme').textContent = geld(b.gesamt);
    $('bestell-email').textContent = b.email || 'Ihre E-Mail-Adresse';
    // Doppelte Käufe beim Neuladen verhindern: purchase nur einmal je Bestellnummer melden
    if (!b.gemeldet) {
      melde('purchase', {
        transaction_id: b.transaction_id, value: b.value, tax: b.tax, shipping: b.shipping,
        currency: b.currency, items: b.items
      });
      b.gemeldet = true;
      try { sessionStorage.setItem('hh_bestellung', JSON.stringify(b)); } catch (e) {}
    }
  }
})();
