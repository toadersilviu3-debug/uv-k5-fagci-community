# Ghidul tastei M pentru FAGCI SPC0002

Versiunea descrisă este **OSFW-SPC0002**, ultima versiune generată în acest proiect. Ghidul a fost verificat în sursa firmware-ului la 13 octombrie 2026. Această versiune include editorul NAME și salvarea din Spectrum prin Side Key 2; comparația AM cu Egzumer nu a schimbat firmware-ul.

## Folosirea meniului principal

1. Din ecranul principal, apasă scurt **M / MENU**.
2. Alege opțiunea cu **▲/▼** sau tastează numărul ei. De exemplu, **5 apoi 0** selectează NAME.
3. Apasă **M** pentru a intra în setare.
4. Modifică valoarea cu săgețile sau, unde este permis, cu cifrele.
5. Apasă **M** pentru acceptare. **EXIT** abandonează editarea; încă un EXIT închide meniul.

MEM-CH, DEL-CH și RESET cer o confirmare suplimentară: după alegerea valorii, M afișează **SURE?**, iar următorul M execută operația.

## Meniul normal cu opțiunile 01–50

Numerele și etichetele de mai jos sunt cele afișate de SPC0002. Opțiunile 01–49 își păstrează numerotarea originală; NAME este opțiunea nouă 50.

| Nr. | Afișaj | Funcție | Valori sau utilizare |
|---:|---|---|---|
| 01 | **SQL** | Pragul squelch; 0 lasă recepția deschisă. | 0–9 |
| 02 | **STEP** | Pasul de acord. Schimbarea prin acest meniu este acceptată numai în VFO. | 0,01 / 0,1 / 0,5 / 1 / 2,5 / 5 / 6,25 / 8,33 / 10 / 12,5 / 25 / 100 kHz |
| 03 | **TXP** | Puterea de emisie a VFO-ului/canalului activ. | LOW / MID / HIGH |
| 04 | **R_DCS** | Cod DCS pentru recepție. | OFF sau cod DCS normal/inversat |
| 05 | **R_CTCS** | Ton CTCSS pentru recepție. | OFF sau unul dintre cele 50 de tonuri |
| 06 | **T_DCS** | Cod DCS pentru emisie. | OFF sau cod DCS normal/inversat |
| 07 | **T_CTCS** | Ton CTCSS pentru emisie. | OFF sau unul dintre cele 50 de tonuri |
| 08 | **SFT-D** | Direcția decalajului frecvenței de emisie. | OFF / + / − |
| 09 | **OFFSET** | Valoarea decalajului RX–TX, afișată în MHz. | Introducere numerică sau săgeți |
| 10 | **W/N** | Lățimea filtrului de canal. | WIDE / NARROW |
| 11 | **SCR** | Scrambling pentru canal; funcție prevăzută pentru FM. | OFF / 1–10; depinde și de SCREN |
| 12 | **BCL** | Blocarea emisiei când canalul este ocupat. | OFF / ON |
| 13 | **MEM-CH** | Memorarea parametrilor curenți în slotul ales. Cere confirmare SURE?. | CH-001–CH-200 |
| 14 | **SAVE** | Economisirea bateriei. SAVE de aici nu memorează un canal. | OFF / 1:1 / 1:2 / 1:3 / 1:4 |
| 15 | **VOX** | Emisie activată de voce și nivelul de declanșare. | OFF / 1–10 |
| 16 | **BACKLI** | Durata iluminării ecranului. | OFF / 5 sec / 10 sec / 20 sec / 1 min / 2 min / ON |
| 17 | **DW** | Dual Watch: supravegherea celor două VFO-uri și selecția asociată A/B. | OFF / CHAN_A / CHAN_B |
| 18 | **WX** | Rutarea recepției și emisiei între VFO-urile A/B. În această sursă este setarea cross-band, deși afișajul spune WX. | OFF / CHAN_A / CHAN_B |
| 19 | **BEEP** | Sunetele tastelor. | OFF / ON |
| 20 | **TOT** | Limitarea duratei unei emisii. | OFF / 1–10 min |
| 21 | **VOICE** | Selectorul moștenit pentru limba anunțurilor vocale. În această sursă nu există redarea vocală legată de această setare. | OFF / CHI / ENG |
| 22 | **SC-REV** | Comportamentul scanării la detectarea unui semnal: temporizat, după dispariția purtătoarei sau oprire. | TO / CO / SE |
| 23 | **MDF** | Felul în care este afișat un canal memorat. | FREQ / CHAN / NAME / NAME+F |
| 24 | **AUTOLK** | Blocarea automată a tastaturii. | OFF / ON |
| 25 | **S-ADD1** | Includerea canalului în lista de scanare 1. | OFF / ON |
| 26 | **S-ADD2** | Includerea canalului în lista de scanare 2. | OFF / ON |
| 27 | **STE** | Eliminarea zgomotului de final al transmisiei, unde este aplicabilă. | OFF / ON |
| 28 | **RP-STE** | Întârzierea pentru eliminarea cozii de repetor. | OFF / 1–10 × 100 ms |
| 29 | **MIC** | Sensibilitatea microfonului pentru emisie. | 0–4 |
| 30 | **1-CALL** | Canalul de apel rapid, accesibil ulterior cu F → 9. | CH-001–CH-200 |
| 31 | **S-LIST** | Lista implicită pentru scanarea canalelor. | LIST1 / LIST2 |
| 32 | **SLIST1** | Consultarea listei 1 și a canalelor prioritare. Nu este editor de priorități. | Canale din listă / NULL |
| 33 | **SLIST2** | Consultarea listei 2 și a canalelor prioritare. Nu este editor de priorități. | Canale din listă / NULL |
| 34 | **ANI-ID** | Afișarea identificatorului DTMF propriu. Nu se editează aici. | Consultare |
| 35 | **UPCODE** | Afișarea codului DTMF de început de emisie. Nu se editează aici. | Consultare |
| 36 | **DWCODE** | Afișarea codului DTMF de sfârșit de emisie. Nu se editează aici. | Consultare |
| 37 | **D-ST** | Ascultarea locală a tonurilor DTMF. | OFF / ON |
| 38 | **D-RSP** | Reacția la decodarea unui apel DTMF. | NULL / RING / REPLY / BOTH |
| 39 | **D-HOLD** | Timpul de menținere/resetare automată a apelului DTMF. | 5–60 sec |
| 40 | **D-PRE** | Preîntârzierea pentru transmiterea codului DTMF. | 3–99 × 10 ms |
| 41 | **PTT-ID** | Momentul trimiterii identificatorului DTMF la PTT. | OFF / BOT la început / EOT la sfârșit / BOTH |
| 42 | **D-DCD** | Activarea decodării DTMF pe canal. | OFF / ON |
| 43 | **D-LIST** | Selectarea unui contact DTMF. Confirmarea unui contact valid îl pregătește pentru apel. | 1–16 / NULL dacă intrarea nu este validă |
| 44 | **PONMSG** | Ecranul de pornire: ecran plin, mesaj sau tensiunea bateriei. | FULL / MSG / VOL |
| 45 | **ROGER** | Semnalul de sfârșit de emisie. | OFF / ROGER / MDC |
| 46 | **VOL** | Afișarea tensiunii bateriei. VOL în acest meniu nu înseamnă reglarea volumului. | Consultare, în volți |
| 47 | **MODUL** | Selectorul simplu de modulație din meniul principal. | OFF = FM / ON = AM; vezi nota despre modulații |
| 48 | **DEL-CH** | Ștergerea canalului ales din memoria utilizabilă. Cere SURE?. | CH-001–CH-200 |
| 49 | **RESET** | Resetarea setărilor sau resetarea completă. Cere SURE? și repornește stația. | VFO / ALL |
| 50 | **NAME** | Vizualizarea și editarea numelui canalului memorat activ. | Maximum 10 caractere ASCII; vezi pașii de mai jos |

## Editarea numelui canalului

Selectează întâi un canal memorat, apoi folosește **M → 50 NAME → M**. Pe ecran apar numărul canalului și numele complet, indiferent de setarea MDF.

| Tastă în editorul NAME | Acțiune |
|---|---|
| ▲ / ▼ | Schimbă caracterul de sub cursor; menținerea tastei repetă schimbarea. |
| F | Mută cursorul la dreapta. |
| * | Mută cursorul la stânga. |
| 0–9 | Introduce cifra direct și avansează cursorul. |
| M | Salvează numele și încheie editarea. |
| EXIT | Anulează modificările. |

Sunt disponibile maximum **10 caractere**, fără diacritice. Pozițiile cursorului sunt circulare. Pentru scurtare, înlocuiește caracterele finale cu spații; zece spații șterg numele. NAME nu creează canale și afișează **MR ONLY** dacă nu este selectat un canal memorat valid.

## Memorarea obișnuită a unui canal

Configurează frecvența și parametrii, apoi urmează:

**M → 13 MEM-CH → M → alegi CH-xxx → M → SURE? → M**

Verifică numărul slotului înainte de ultima confirmare. Un slot ocupat este suprascris. Funcția **14 SAVE** este economisirea bateriei și nu înlocuiește MEM-CH.

În codul SPC0002, modificările obișnuite de parametri, cum ar fi TXP, tonurile sau MODUL, folosesc o cale care salvează automat VFO-ul, dar nu rescrie parametrii unui canal MR existent. Pentru a le păstra într-un canal memorat, folosește explicit **MEM-CH** după modificare. Editorul NAME și participarea S-ADD1/S-ADD2 au căi proprii de salvare.

## Modulațiile disponibile

Opțiunea **47 MODUL** oferă numai **OFF = FM** și **ON = AM**, chiar dacă titlul sugerează un selector general. Dacă accepți această opțiune peste un canal USB/BYP/RAW, selectezi FM sau AM.

Cele cinci modulații **FM, AM, USB/SSB, BYP, RAW** se parcurg cu **F → 7** din ecranul principal sau cu **0** în Spectrum. Pentru persistența schimbării pe un canal MR, folosește MEM-CH sau salvarea din Spectrum.

## Rolul tastei M în Spectrum

Intrarea în Spectrum se face din ecranul principal: **F**, eliberezi, apoi **5**. M are roluri diferite în funcție de ecran:

| Ecran | Ce face M |
|---|---|
| Graficul Spectrum | Nu deschide meniul principal și nu deschide un help. În SPC0002, meniul extins de registre din acest ecran este dezactivat. |
| Introducerea unei frecvențe, după tasta 5 | Acceptă frecvența introdusă și revine în starea Spectrum/ascultare anterioară. |
| Ascultarea fixă Spectrum | Selectează succesiv reglajele LNAs, LNA, PGA, MIX, IF, DEV, CMP, MIC. Săgețile modifică reglajul selectat. |
| Alegerea slotului după Side Key 2 | Prima apăsare cere confirmarea, a doua salvează. |

Pentru a trece de la grafic la ascultarea fixă pe vârful detectat, apasă scurt PTT și eliberează. **În ascultarea fixă, o nouă apăsare PTT poate porni emisia**; PTT nu este butonul de salvare.

În ascultarea fixă, EXIT închide întâi selecția reglajelor, dacă este activă; următorul EXIT revine la grafic. Din grafic, EXIT închide Spectrum.

Reglajele speciale se aplică temporar. În SPC0002, Side Key 2 **nu memorează** LNAs/LNA/PGA/MIX/IF/DEV/CMP/MIC sau pragul squelch/RSSI.

## Salvarea din Spectrum prin Side Key 2

1. Apasă și eliberează **Side Key 2**, butonul lateral inferior. În Spectrum acesta înlocuiește comutarea iluminării.
2. Verifică frecvența afișată. Este capturată frecvența vârfului de pe grafic sau frecvența acordată în ascultarea fixă.
3. Este propus primul slot liber. Alege alt slot cu **▲/▼** dacă dorești.
4. Apasă și eliberează **M**: apare **SAVE?** pentru un slot liber sau **REPLACE?** pentru unul ocupat.
5. Apasă din nou **M** pentru salvare. Apare **SAVED CH-xxx** și revii în Spectrum.

EXIT anulează din oricare etapă. Schimbarea slotului anulează confirmarea precedentă. Menținerea lui M nu poate confirma automat suprascrierea. PTT este ignorat în acest ecran.

Se păstrează frecvența, modulația, pasul și Wide/Narrow. Filtrul Spectrum de 6,25 kHz se memorează ca Narrow. Canalul este creat fără offset sau tonuri, cu puterea din VFO-ul activ și cu participare la ambele liste de scanare. La suprascriere se păstrează numele existent; la un slot nou numele este gol și poate fi editat ulterior prin NAME.

Salvarea nu selectează automat noul canal în ecranul principal. După ieșirea din Spectrum, selectează slotul salvat pentru a-l folosi sau redenumi.

## Opțiunile speciale 51–56

Aceste opțiuni apar în modul special accesat pornind stația cu **PTT + Side Key 1** ținute apăsate simultan. Side Key 1 este butonul mic imediat sub PTT. Eliberează ambele butoane când apare meniul **51 - 350TX**. Ele configurează permisiunile de emisie și funcția globală scrambling; nu sunt reglaje de sensibilitate AERO sau AGC AM.

| Nr. | Afișaj | Funcție | Valori |
|---:|---|---|---|
| 51 | **350TX** | Permisiunea configurată pentru emisie în zona 350 MHz. | OFF / ON |
| 52 | **F-LOCK** | Profilul limitelor de emisie. | OFF / FCC / CE / GB / LPD PMR |
| 53 | **200TX** | Permisiunea configurată pentru emisie în zona 200 MHz. | OFF / ON |
| 54 | **500TX** | Permisiunea configurată pentru emisie în zona 500 MHz. | OFF / ON |
| 55 | **ALL_TX** | Modul general de permitere a emisiei. | DEFAULT / ENABLE / DISABLE |
| 56 | **SCREN** | Activarea globală a funcției scrambling. | OFF / ON |

## Repere rapide

- **13 MEM-CH:** memorează un canal.
- **14 SAVE:** economisirea bateriei.
- **23 MDF:** afișarea numelui sau frecvenței.
- **46 VOL:** tensiunea bateriei.
- **47 MODUL:** numai FM/AM în meniul principal.
- **48 DEL-CH:** ștergerea canalului.
- **49 RESET:** resetare; nu este necesară pentru activarea funcțiilor noi.
- **50 NAME:** editarea numelui.
- **F → 5:** Spectrum.
- **Side Key 2 în Spectrum:** alegerea slotului pentru salvare.

Acesta este un ghid extern pentru versiunea existentă. Nu a fost adăugat un ecran HELP în firmware și nu s-a schimbat comportamentul tastei M prin generarea documentului.

