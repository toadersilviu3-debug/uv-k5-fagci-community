# VFO0003 - salvare VFO cu Side Key 2 lung

Versiune de test OSFW-VFO0003, bazata pe SPC0002. Nu a fost publicata pe GitHub si nu a fost inca testata pe statie.

## Utilizare

1. Intra in VFO (F, apoi 3 daca esti in modul canal MR).
2. Introdu frecventa si apasa M pentru acceptare. Verifica frecventa efectiv acordata; firmware-ul o aliniaza la pasul VFO existent.
3. Tine apasat Side Key 2, butonul lateral inferior, pana apare direct meniul 13 MEM-CH in editarea slotului (aproximativ 1,3 secunde).
4. Elibereaza Side Key 2. Este propus primul slot liber, sau CH-001 daca toate sunt ocupate.
5. Alege slotul cu sagetile sau introdu trei cifre, de exemplu 025 pentru CH-025.
6. Apasa M: apare SURE?. Verifica slotul; un canal ocupat va fi suprascris.
7. Apasa M din nou pentru salvare. EXIT anuleaza editarea slotului; inca un EXIT revine la ecranul principal.

Schimbarea slotului anuleaza confirmarea precedenta. M tinut apasat nu confirma automat salvarea. In timpul alegerii slotului in MEM-CH, PTT si tastele laterale sunt ignorate. Dupa salvare ramane meniul MEM-CH; EXIT revine la ecranul principal. Slotul salvat poate fi selectat in MR si redenumit din 50 NAME.

Apasarea scurta Side Key 2 isi pastreaza functia configurata. In VFO, apasarea lunga este rezervata salvarii si inlocuieste functia lunga configurata anterior. In MR si in celelalte ecrane, functia lunga configurata ramane disponibila. Spectrum pastreaza salvarea lui prin Side Key 2.

Daca frecventa este inca in curs de introducere, scurtatura nu salveaza frecventa veche: accepta mai intai cu M, apoi foloseste Side Key 2 lung. Scurtatura este blocata cand tastatura este blocata sau cand scanarea este activa.

## Ce se salveaza

Se foloseste calea existenta MEM-CH: frecventa RX, offsetul si directia sa, codurile/tonurile RX si TX, modulatia, pasul, latimea de banda, puterea, BCL, reverse, DTMF, scrambling si apartenenta la listele de scanare din VFO-ul activ. Numele existent al slotului este pastrat, la fel ca in MEM-CH. Reglajele speciale de registre si squelch-ul global nu sunt adaugate in memoria canalului.

## Fisiere si verificare

- firmware_VFO0003.bin: firmware brut, pentru utilitarul K5Prog compatibil folosit anterior.
- firmware_VFO0003.packed.bin: format impachetat, pentru un incarcator compatibil cu acest format.
- sursa_FAGCI_VFO0003.zip: sursa completa cu dependente, teste si licente.
- modificare_SPC0002_VFO0003.patch: modificarile de cod fata de copia locala SPC0002.
- TESTE_VFO0003.txt si SHA256_VFO0003.txt: rezultate si sume de control.

Compilat cu ARM GCC 16.1.0. Firmware brut: 61264 octeti din 61440; raman 176 octeti. Cele 38 de teste executa instructiuni ARM cu periferice simulate: 13 NAME, 14 Spectrum si 11 VFO. Testul VFO verifica toate cele 200 de sloturi si pastrarea restului EEPROM-ului, iar suita Spectrum verifica 180 de combinatii de modulatie/filtru/pas. Testele nu reprezinta validare RF sau confirmare pe hardware.

Pastreaza backupul configuratiei si calibrarii propriei statii. Nu este necesar RESET. AGC-ul AM nu a fost modificat. Sursa si firmware-ul SPC0002 publicate anterior nu au fost inlocuite.
