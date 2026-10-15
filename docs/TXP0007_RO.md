# TXP0007 — activare/dezactivare TX pe canal din CHIRP

Versiune experimentală, 14 octombrie 2026. Continuă RXP0006 și păstrează editarea
numelor, salvarea din Spectrum/VFO, controlul AM, SOS și profilurile RX.

## Ce face opțiunea

În proprietățile fiecărui canal CHIRP, la **Extra**, apare:

**TX enabled (subject to global limits)**

- **Bifat:** canalul poate transmite dacă și regulile generale ale firmware-ului permit.
- **Debifat:** canalul rămâne numai pentru recepție. Permisiunea globală TX nu anulează această blocare.

Blocarea se salvează în EEPROM și rămâne după repornire. Frecvența RX, deplasarea
pentru repetor, numele și profilul RX sunt păstrate. În tabel, canalul blocat apare
cu **Duplex = off**. Poți folosi și această valoare pentru a activa blocarea.
Rebifarea TX enabled restabilește deplasarea TX care exista înaintea blocării.

Opțiunea se aplică **fiecărui canal memorat**, nu unei liste globale de frecvențe.
Aceeași frecvență introdusă separat în VFO sau salvată într-un alt canal nu este
blocată automat. În Cross-band, contează canalul folosit efectiv pentru TX.

Firmware-ul blochează pornirea TX în modul normal și în Spectrum atunci când
canalul curent pentru TX este blocat. Căile de alarmă și 1750 Hz respectă marcajul.
Recepția rămâne disponibilă.

## Ordinea instalării

1. Păstrează copia ta de configurație/calibrare. Nu este necesară resetarea EEPROM.
2. Instalează **firmware_TXP0007.bin** cu utilitarul folosit pentru imaginile brute
   anterioare. Dacă utilitarul tău cere formatul împachetat, folosește
   **firmware_TXP0007.packed.bin**. Fișierele nu se redenumesc unul în locul celuilalt.
3. În CHIRP, salvează lucrul deschis și alege **File → Load Module…** pentru
   **uvk5_fagci_txp0007.py**. Dacă meniul lipsește, activează
   **Help → Developer Mode**, repornește CHIRP și încarcă modulul.
4. Alege **Radio → Download From Radio**, portul cablului tău (anterior COM5),
   vendor **Quansheng**, model **UV-K5 FAGCI TXP0007**. Stația trebuie să fie în
   modul normal, în afara Spectrum.
5. Salvează o copie nouă `.img`, de exemplu `Quansheng_TXP0007_initial.img`.
6. Deschide proprietățile canalului prin dublu clic pe rând. În **Extra**, debifează
   **TX enabled** pentru canalele pe care le dorești numai pentru recepție.
7. Salvează modificările și folosește **Radio → Upload To Radio**, cu același model.

Instalarea firmware-ului singură nu dezactivează automat canalele existente.
Modificările CHIRP devin active în stație după upload. Driverul acceptă numai
**OSFW-TXP0007** și cere o imagine citită cu acest model; vechea filă IJV/RXP0006
nu este convertită prin simpla încărcare a modulului.

## Păstrarea blocării

- Editarea numelui, filtrului, gain-ului, IF-ului și a celorlalți parametri păstrează blocarea.
- Resalvarea din Spectrum sau VFO peste un canal ocupat și blocat păstrează blocarea.
- Pentru reactivare explicită, bifează TX enabled în CHIRP și trimite modificarea.
- Ștergerea canalului și crearea unui canal nou elimină proprietățile vechi, inclusiv blocarea.
- Dacă revii la RXP0006 sau la alt firmware vechi, acesta nu aplică această blocare.

În RX:AUTO, controlul AM rămâne cel din RXP0006. TX enabled și profilul RX MANUAL
sunt opțiuni independente. Parametrii RX suplimentari sunt descriși în ghidul
modulului RXP0006, cu modelul nou folosit în locul celui vechi.

## Verificări efectuate

Au trecut **123 de teste automate**: 70 pentru funcțiile existente ale firmware-ului
și 53 pentru CHIRP/interoperabilitate/TX. S-a executat firmware-ul ARM compilat
în emulator, cu periferice simulate. Testele includ toate cele 200 de canale,
ambele VFO-uri, TX global activat/dezactivat, offset, reverse, alarmă, Spectrum,
resalvare și păstrarea profilului RX.

Imagine brută: **60.248 octeți**; împachetată: **60.266 octeți**;
spațiu FLASH rămas din limita de 61.440: **1.192 octeți**.

Nu am conectat, programat sau testat fizic stația. Verificarea pe stația ta și
în interfața CHIRP instalată la tine rămâne următoarea etapă.

## Corecție pentru modulul RXP0006 anterior

Am eliminat din modulul RXP0006 opțiunea Duplex off, deoarece implementarea
prin deplasare negativă egală cu frecvența nu garanta blocarea emisiei în acel
firmware. Pentru opțiunea descrisă aici sunt necesare **ambele**: TXP0007 și modulul
CHIRP TXP0007. Modulul RXP0006 corectat rămâne destinat firmware-ului RXP0006.

## Credite și licențe

Firmware bazat pe FAGCI v1.2.1 / DualTachyon, cu contribuțiile upstream și licențele
originale păstrate în sursa completă. Adaptare comunitară independentă cu ajutorul
Codex. Firmware: Apache-2.0 și licențele dependențelor; vezi sursa, NOTICE și
THIRD_PARTY_NOTICES.txt. Modul CHIRP: GPL-3.0-or-later, vezi COPYING_GPL3.txt.
Transport CHIRP: Jacek Lipkowski, Dan Smith; adaptarea IJV furnizată îi creditează
și pe Julian Lilov LZ1JDL și Francesco IK8JHL.
