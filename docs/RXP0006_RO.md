# RXP0006 - profil RX optional salvat din Spectrum

Versiune experimentala OSFW-RXP0006, bazata pe SOS0005. Include AGC AM din AMH0004, SOS pe lanterna, NAME si salvarile Spectrum/VFO. Nu a fost inca testata pe statie si nu a fost publicata pe GitHub.

## Ce am adaugat

In ascultarea fixa din Spectrum, la salvare poti alege explicit intre:

- RX:AUTO (implicit): salveaza canalul obisnuit. AM foloseste AM-fix automat; celelalte moduri folosesc AGC hardware automat. Reglajele speciale de castig/IF nu se pastreaza.
- RX:MANUAL: salveaza LNAs, LNA, PGA, MIX (REG_13) si IF (REG_3D). La selectarea canalului MR se restaureaza aceste valori si castigul ramane fix. AM-fix nu le suprascrie pe acel canal.

Schimbarea unui reglaj in Spectrum nu selecteaza automat MANUAL. Alegerea se face cu F in ecranul de salvare. Din graficul Spectrum este disponibil numai AUTO: masurarea baleiaza frecvente, deci un castig instantaneu nu trebuie atribuit automat varfului detectat.

## Pasii pentru salvare manuala

1. Intra in Spectrum cu F, apoi 5.
2. Pe semnalul ales, apasa scurt PTT si elibereaza pentru ascultare fixa. In aceasta stare, o alta apasare PTT poate porni emisia.
3. Cu M alegi LNAs/LNA/PGA/MIX/IF, iar cu sagetile reglezi valoarea.
4. Apasa si elibereaza Side Key 2. Ecranul de salvare porneste pe RX:AUTO.
5. Apasa F o data pentru RX:MANUAL. F comuta intre AUTO si MANUAL. Valorile registrelor au fost capturate la deschiderea salvarii.
6. Alege slotul cu sagetile. M cere SAVE? sau REPLACE?, apoi inca o apasare M salveaza. EXIT anuleaza. Schimbarea modului RX sau a slotului cere o noua confirmare.
7. Iesi din Spectrum si selecteaza slotul salvat in modul MR. Profilul se aplica si dupa oprire/pornire. Pentru a redenumi, foloseste 50 NAME.

Pentru a reveni la AUTO pe un canal, salveaza din nou peste acelasi slot cu RX:AUTO. O suprascriere obisnuita MEM-CH dintr-un VFO automat elimina si ea profilul manual vechi. Simplul rename prin NAME pastreaza profilul.

## Limite si compatibilitate

- Prima implementare salveaza numai castigurile LNAs/LNA/PGA/MIX si IF. Nu adauga DEV, CMP, MIC sau squelch/RSSI per canal.
- MANUAL inseamna castig fix. Pe AERO, nivelul avioanelor variaza; AUTO ramane alegerea implicita. Nu este garantata sensibilitate sau inteligibilitate mai buna.
- Profilul foloseste cei sase octeti de dupa numele de zece caractere. Numele, ceilalti parametri de canal si calibrarea sunt pastrate prin caile testate.
- CHIRP/CPS si alte firmware-uri nu au suport verificat pentru acest format; pot sterge sau pastra date speciale fara sa le interpreteze corect. Firmware-ul vechi ignora profilul, iar revenirea la RXP0006 poate reactiva un profil inca prezent.
- Reglajele manuale sunt aplicate la RX. In traseul normal TX sunt folosite valorile de baza; la revenirea RX se reaplica profilul. Testele acestui traseu au fost facute cu registre simulate, fara emisie fizica.
- SAVE_CHANNEL nu selecteaza automat slotul salvat; selecteaza-l ulterior in MR.

## Spatiu si verificare

Firmware brut: 59808 octeti din 61440; raman 1632 octeti liberi. Packed: 59826 octeti. Nicio functie existenta nu a fost dezactivata pentru a face loc. Build-ul foloseste ARM GCC 16.1.0, LTO si eliminarea sectiunilor nefolosite, cu pastrarea explicita a vectorilor de intrerupere si a limitelor de apel folosite in teste.

Toate cele 70 de teste ARM au trecut: cele 53 existente, 15 pentru profilul RX si 2 pentru vectorii de pornire/initializarea memoriei. Profilurile au fost verificate in toate cele 200 de sloturi, cu pastrarea datelor EEPROM din afara destinatiei, restaurare dupa restart, redenumire, AUTO/MANUAL, anulari, schimbare VFO si RX/TX. Tabela si algoritmul FAGCI am_fix.c au ramas identice.

Acestea sunt teste software cu periferice simulate. Pastreaza backupul configuratiei si calibrarii propriei statii. Nu este necesar RESET. Pentru K5Prog compatibil foloseste firmware_RXP0006.bin; formatul packed se foloseste numai cu un incarcator compatibil.

Teste practice propuse: pornire normala, verificarea profilului manual dupa restart, revenirea pe un canal AUTO/FM, NAME, salvarea VFO si SOS. Apoi compara receptia AM pe aceeasi frecventa/antena/filtru, cu SQL 0, DW OFF si SAVE OFF.
