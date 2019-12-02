# Game of life

## Specifikace

Implementace Conwayovy Hry života v okenní aplikaci.

Vývoj generací buněk se zobrazuje za sebou ve snímcích jako animace.
Program umožňuje:
- Nakreslit počáteční rozložení buněk v dostatečně velké mřížce.
- Nastavit počty sousedů buněk pro přežití a narození nových.
- Změnit rychlost animace na některou z přednastavených hodnot.
- Přiblížit / oddálit herní plochu.
- Uložit / načíst sestavu buněk z textového souboru.

## Dokumentace
V popisu tříd jsou uvedeny pouze nejdůležitější datové struktury a metody.

### Použité knihovny
Program využívá některé knihovny zejména pro vzhled aplikace.

#### tkinter:
Okno aplikace a jeho komponenty, zpracování událostí od uživatele.

#### pillow:
Vytvoření obrázku v paměti a kreslení.

#### time:
Měření času při animaci.

#### os:
Nalezení cesty k adresáři hlavního programu, která je použita jako výchozí cesta v dialogu pro načítání herní plochy.

#### typing:
Doplnění některých datových typů pro našeptávač, které nepatří mezi standardní.

### Modul gol.py
Obsahuje třídy potřebné pro výpočet, kreslení a animaci hry, které se využijí v hlavním programu.

#### Board
Obsahuje informace o herní ploše (seznam živých buněk).
Dovoluje přidávat a odebírat buňky, počítá další generaci buněk.

##### Datové struktury:
current:
2D seznam proměnných bool reprezentující mřížku buněk (True = živá buňka, False = mrtvá buňka).

living:
Seznam souřadnic živých buněk v current.

##### Metody:
next_gen():
Spočítá další generaci buněk podle počtu jejich sousedů.
Prochází pouze živé buňky a jejich sousedy, protože ostatní buňky zůstanou nezměněné.

#### Rule
Slouží pro snadnější nastavování pravidel hry (počtů sousedů) pomocí textového řetězce.

##### Datové struktury:
birth_rule:
Množina pro počty sousedů, které způsobují narození buňky.

remain_rule:
Množina pro počty sousedů se kterými zůstane buňka naživu.

##### Metody:
try_set_rule(value: str) → bool:
Pokusí se nastavit textový řetězec value jako nové pravidlo.
Vrací True, pokud je pravidlo správné, jinak False.

#### Painter
Kreslí herní plochu (Board) na plátno (Canvas).

##### Datové struktury:
grids:
Obrázky s mřížkou pro různé velikosti buněk. Slouží jako pozadí, na které se budou buňky kreslit. 
Vytváří se v metodě reset, kterou je nutné zavolat před jakýmkoliv kreslením.
Lze mezi nimi přepínat a tím mřížku „přibližovat / oddalovat“.

m_cell:
Souřadnice buňky, která je zobrazena uprostřed mřížky.
Se změnou této souřadnice se bude zobrazovat jiná část herní plochy. Obraz se tak může posouvat nahoru, dolů, anebo do stran.

canvas_image:
Objekt obrázku na plátně z knihovny tkinter. Je natažen na celou velikost plátna, pokud nepřekračuje velikost mřížek. Vykreslení mřížek je provedeno změnou parametru image tohoto objektu.

##### Metody:
reset():
Vytváří obrázky mřížek pro zadané velikosti.

draw_board():
Vykreslí herní plochu.
Ořízne prostřední část mřížky z grids na velikost plátna. 
Podle souřadnic buňky kreslené doprostřed (m_cell) nakreslí všechny viditelné buňky na vyříznutou mřížku.
Výsledný obrázek nastaví jako parametr image objektu canvas_image.

#### Animator
S využitím objektu Painter kreslí generace buněk za sebou jako animaci.

##### Proměnné instance:
time_per_gen: Čas mezi kreslením generací.

##### Metody:
play():
Spustí animaci.

stop():
Pozastaví animaci.

### Hlavní program main.py
Tento soubor je určen pouze jako hlavní program.
Z důvodu přehlednosti jsou proto proměnné tříd psány jako veřejné (bez podtržítka).

#### FileManager
Statická třída, která načítá a ukládá plochu Board do souboru.
Výsledek zobrazuje v okně se zprávou (messagebox).

#### TkState
Statická třída, která aktivuje a deaktivuje komponenty tkinter.

#### Application
Obsahuje všechny komponenty okenní aplikace, zpracovává události spuštěné uživatelem.
Manipuluje s objekty modulu gol.py, nastavuje jejich hodnoty a spouští jejich metody.

