# SOS0005 - AMH0004 cu semnal SOS pe lanterna LED

Identificator: OSFW-SOS0005. Versiune experimentala, compilata la 14 octombrie 2026. Include configurarea AGC AM din AMH0004, editorul NAME, salvarea Spectrum si salvarea VFO prin Side Key 2 lung.

## Lanterna

Tasta configurata pentru lanterna pastreaza ciclul cu trei apasari scurte:

1. Aprins continuu.
2. SOS repetat: trei impulsuri scurte, trei lungi, trei scurte, apoi pauza.
3. Stins.

O unitate Morse este nominal 160 ms: punct 160 ms, linie 480 ms, pauza intre impulsuri 160 ms, intre litere 480 ms, intre repetari 1120 ms. Ciclul complet este nominal 5,44 secunde. Timpii reali pot varia cu activitatile firmware-ului. La reactivare, SOS incepe din nou de la primul punct.

SOS foloseste temporizarea normala a aplicatiei, fara intarzieri blocante adaugate. Ca si clipirea veche, secventa este suspendata in bucla separata Spectrum si continua dupa iesire. Nu modifica semnalizarea verde/rosie RX/TX.

## Incarcare

- firmware_SOS0005.bin: firmware brut pentru K5Prog compatibil, ca la versiunile anterioare.
- firmware_SOS0005.packed.bin: format impachetat, numai pentru un incarcator compatibil cu acest format.

Pastreaza backupul propriei configuratii si calibrari. Nu este necesar RESET. Dupa incarcare, verifica identificatorul OSFW-SOS0005 si ciclul continuu / SOS / stins pe tasta lanternei. Testeaza in ecranul normal, in afara Spectrum. AGC AM ramane cel din AMH0004; nu a primit o noua reglare in aceasta versiune.

Pentru comparatia AGC cu VFO0003: aceeasi frecventa AERO, antena, pozitie, latime de filtru si volum; AM, SQL 0, DW OFF, SAVE OFF. Rezultatele audio/RF raman de validat pe statie.

## Verificare

ARM GCC 16.1.0. Firmware brut 61404 octeti din 61440 (36 octeti liberi); packed 61422 octeti. Cele 53 de teste ARM au trecut: cele 47 existente plus 6 teste pentru SOS, secventa repetata, repornire, GPIO, temporizarea reala a aplicatiei si rularea AM-fix. Testele folosesc periferice simulate si nu confirma executarea pe hardware.

Firmware-urile AMH0004 si VFO0003 livrate anterior au ramas neschimbate. Aceasta versiune nu a fost publicata pe GitHub.
