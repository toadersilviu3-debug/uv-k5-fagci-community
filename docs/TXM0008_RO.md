# TXM0008 — meniul TX individual în stație

Versiune experimentală, 14 octombrie 2026, bazată pe TXP0007.
Păstrează blocarea TX din CHIRP, controlul AM, salvarea Spectrum/VFO, profilurile
RX, editarea numelui și SOS.

## Utilizare direct din stație

1. Selectează canalul memorat dorit pe linia A/B folosită pentru TX.
2. Apasă **M → 5 → 1**: apare meniul **51 — TX-CH**.
3. Apasă **M** pentru editare.
4. Alege cu săgețile **OFF** (numai recepție) sau **ON** (TX permis pe canal).
5. Apasă **M** pentru salvare. **EXIT** anulează modificarea nesalvată.

Ecranul afișează **CH-xxx**, astfel încât să vezi canalul vizat. Setarea se aplică
imediat după salvare și rămâne după repornire. Ambele VFO-uri sunt actualizate
dacă folosesc același canal.

**ON nu anulează limitele generale de emisie.** Dacă ALL_TX este DISABLE,
apare **GLOBAL OFF** și emisia rămâne blocată.

În VFO sau fără un canal memorat valid, meniul afișează **MR ONLY** și nu permite
editarea. Aceeași frecvență introdusă separat în VFO ori într-un alt canal este
independentă. În Cross-band contează canalul folosit efectiv pentru TX.

PTT, tastele laterale și F sunt ignorate cât timp editezi TX-CH. Meniul fixează
canalul la intrarea în editare, pentru a evita salvarea pe altă linie dacă se
schimbă VFO-ul curent. Nu există emisie automată la alegerea ON.

## Instalare

- Instalează **firmware_TXM0008.bin** cu utilitarul pentru imagini brute folosit
  anterior; **firmware_TXM0008.packed.bin** este pentru utilitare care cer formatul împachetat.
- Nu este necesară resetarea EEPROM. Păstrează copia ta de configurație/calibrare.
- Canalele și marcajele TX existente din TXP0007 sunt păstrate. Meniul folosește
  exact același format EEPROM; nu alocă octeți EEPROM suplimentari.
- Pentru CHIRP, încarcă **uvk5_fagci_txm0008.py** prin File → Load Module… și fă o
  citire nouă cu **Quansheng → UV-K5 FAGCI TXM0008**. Salvează imaginea inițială.
- „Extra → TX enabled” și „Duplex = off” rămân disponibile în noul modul.
  O modificare făcută din stație va apărea în CHIRP la următoarea citire.
- Modulul TXP0007 acceptă numai identificarea veche; folosește modulul nou cu TXM0008.

## Numerele meniurilor

Meniurile normale 1–50 păstrează numerele. **TX-CH devine 51**.
Meniurile speciale, accesibile prin PTT + Side Key 1 la pornire, devin:

| Număr | Meniu |
|---|---|
| 52 | 350TX |
| 53 | F-LOCK |
| 54 | 200TX |
| 55 | 500TX |
| 56 | ALL_TX |
| 57 | SCREN |

## Memorie și verificări

- Firmware brut: **60.668 octeți**, împachetat: **60.686 octeți**.
- FLASH rămas din limita de 61.440: **772 octeți**.
- Niciun octet EEPROM nou alocat. Schimbarea folosește marcajul TX existent.
- Se rescrie numai blocul de 8 octeți care conține marcajul, și numai dacă valoarea
  se schimbă. Numele, profilul RX, offsetul și calibrarea rămân păstrate.
- **135 de teste automate**: 70 regresii firmware și 65 CHIRP/ARM/TX/meniu.
  Sunt incluse toate cele 200 de canale, ambele VFO-uri, salvare, anulare, persistență,
  blocare TX globală, protecție în editare și afișarea meniului.

Testele rulează firmware-ul compilat în emulator, cu periferice simulate.
La 15 octombrie 2026, proprietarul a confirmat funcționarea TXM0008 pe stația sa.
Aceasta nu reprezintă verificarea tuturor reviziilor hardware. Poți selecta
un canal, schimba TX-CH, reporni stația și reciti cu noul modul CHIRP.

Blocarea funcționează cu TXP0007/TXM0008. Un firmware mai vechi nu aplică marcajul.
Pentru blocarea simplă pe canal, RX:AUTO/RX:MANUAL sunt independente și nu trebuie schimbate.

## Credite

Firmware FAGCI / DualTachyon, contribuții upstream și dependențe cu licențele
originale păstrate în sursa completă. Adaptare comunitară independentă cu ajutorul
Codex. Firmware: Apache-2.0 plus licențele dependențelor. Modul CHIRP: GPL-3.0-or-later.
Transport CHIRP: Jacek Lipkowski, Dan Smith; adaptarea IJV furnizată îi creditează
și pe Julian Lilov LZ1JDL și Francesco IK8JHL.
