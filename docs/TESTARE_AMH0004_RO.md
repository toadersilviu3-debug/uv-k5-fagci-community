# AMH0004 - primul test AGC AM / AERO

Versiune experimentala OSFW-AMH0004, bazata pe VFO0003, care pastreaza NAME, salvarea Spectrum si salvarea VFO cu Side Key 2 lung. Nu a fost inca testata pe statie si nu a fost publicata pe GitHub.

## Schimbarea testata

La configurarea receptiei normale in AM, BK4819 REG_7E este trecut in modul fix (bit 15 = 1), cu indexul 3 (REG_13). AM-fix din FAGCI controleaza astfel castigul fara selectia automata concurenta a etajelor hardware. Bitii 11:0 sunt pastrati. In FM/USB/BYP/RAW se reactiveaza selectia automata AGC.

Tabela de castig, tinta RSSI, histerezisul, temporizarea si algoritmul din am_fix.c sunt identice cu VFO0003/FAGCI. Nu am portat tabela Egzumer si nu am modificat squelch-ul sau calibrarea. Principiul blocarii AGC hardware a fost identificat in codul Egzumer 0.22; atribuirile originale sunt pastrate.

La intrarea in Spectrum se foloseste AGC hardware automat, deoarece Spectrum FAGCI nu executa AM-fix. La iesire se restaureaza registrul salvat. AM-fix automat in Spectrum nu a fost implementat in aceasta versiune.

## Test pe statie

1. Pastreaza backupurile propriei statii. Incarca firmware_AMH0004.bin cu utilitarul K5Prog compatibil folosit anterior. Formatul packed este numai pentru un incarcator compatibil cu el. Nu incarca o calibrare straina. Nu este necesar RESET.
2. Verifica identificatorul OSFW-AMH0004 la pornire.
3. Alege o frecventa AERO cunoscuta si selecteaza AM. Testul urmareste receptia normala in canal/VFO.
4. Pentru comparatie, foloseste aceeasi antena, pozitie, latime de filtru si volum ca in VFO0003 (sau SPC0002, care are acelasi AGC de baza). Dezactiveaza Dual Watch: 17 DW = OFF. Dezactiveaza economisirea bateriei: 14 SAVE = OFF. Pune temporar 01 SQL = 0 pentru a separa efectul AGC de taierea squelch-ului.
5. Asculta mai multe transmisii slabe, apoi unele puternice. Noteaza inteligibilitatea cuvintelor, distorsiunea, variatiile de volum, pierderea primelor silabe si revenirea dupa un semnal puternic.
6. Verifica si revenirea la un canal FM, apoi inapoi in AM, precum si iesirea din Spectrum. Nu este nevoie de emisie pentru testul AERO.
7. Daca receptia se inrautateste, revino la firmware_VFO0003.bin cu aceeasi configuratie. Noteaza simptomele si frecventa folosita.

Un semnal mai tare in difuzor sau o indicatie RSSI diferita nu demonstreaza singure sensibilitate RF mai buna. Avioanele si propagarea variaza; compara mai multe transmisii inainte de concluzie.

## Ce sa raportezi

- Frecventa, AM, latimea filtrului, antena si daca SQL a fost 0.
- Semnal slab: cuvintele sunt mai clare, la fel sau mai greu de inteles?
- Semnal puternic: mai exista distorsiune sau pompare de volum?
- Dupa un semnal puternic, revine repede receptia celui slab?
- FM si Spectrum se comporta normal dupa schimbare?

## Verificare software

ARM GCC 16.1.0. Firmware brut: 61324 octeti din 61440; raman 116 octeti. Format packed: 61342 octeti. Toate cele 47 de teste ARM au trecut: 38 pentru NAME/Spectrum/VFO si 9 pentru integrarea AGC (ambele VFO-uri, pastrarea bitilor inferiori, modurile non-AM, trecerea RX/TX, controlul software REG_13, Spectrum si controllerul nemodificat).

Registre simulate: de la REG_7E = 0x302E, configurarea AM produce 0xB02E. FM si Spectrum folosesc 0x302E; revenirea din Spectrum in AM restaureaza 0xB02E. Aceste rezultate confirma traseele software, nu performanta RF sau audio pe statia reala.

Nu este necesara o reglare noua in meniu pentru activarea modificarii. Firmware-urile anterioare raman disponibile ca reper.
