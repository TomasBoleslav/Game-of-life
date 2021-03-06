# Game of Life
Implementace [Conwayovy Hry života](https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life) v okenní aplikaci. Vývoj generací je zobrazován za sebou ve snímcích jako animace. Program umožňuje:
- Nakreslit počáteční rozložení buněk.
- Nastavit počty sousedů buněk pro přežití a narození nových.
- Změnit rychlost animace na některou z přednastavených hodnot.
- Přiblížit a oddálit herní plochu.
- Uložit a načíst sestavu buněk.

## Obsah
* [Instalace](#instalace)
* [Použití](#použití)
* [Dokumentace](#dokumentace)
* [Návrhy na zlepšení](#návrhy-na-zlepšení)

## Instalace
Před spuštěním programu si musíte nainstalovat [Python](https://www.python.org/downloads/).

Spolu s Pythonem se stáhne program pip, pomocí něj nainstalujte knihovnu [Pillow](https://pillow.readthedocs.io/en/stable/installation.html):
1. Otevřete příkazový řádek jako správce.
2. Stáhněte knihovnu příkazem:  
``Path\pip install Pillow``,  
kde `Path` je cesta k programu pip na vašem počítači.

## Použití
Na operačním systému Windows spusťtě soubor [main.pyw](game-of-life/main.pyw). Pokud máte jiný operační systém, spusťte [main.py](game-of-life/main.py) (zobrazí se s konzolí, tu ignorujte).

Otevře se okno programu. V horním panelu jsou k dispozici tlačítka pro minimalizaci, maximalizaci a zavření okna.

<img src="images/window.png" height="444" width="675" />

### Tvorba mřížky
1. Prázdnou mřížku vytvoříte kliknutím na **New Board**.
2. Držením levého tlačítka myši můžete kreslit buňky. Úpravy lze provádět jen před spuštěním animace nebo po jejím resetování. V pravém menu jsou k dispozici 3 módy:
    - **Add** - přidat buňku.
    - **Remove** - odebrat buňku.
    - **Toggle** - změnit současný stav buňky. Po celou dobu jednoho tahu je nastaven jako *Add* nebo *Remove* podle stavu 1. buňky, na kterou bylo kliknuto.
3. Plochu přibližujte a oddalujte pomocí posuvníku **Zoom** nebo klávesami "**+**" a "**-**".
4. Obrazem pohybujte pomocí šipek.
5. Pro uložení použijte tlačítko **Save**. Zobrazí se dialog, v něm vyberte název souboru a cestu, potvrzením soubor uložte.
6. Načtení provedete kliknutím na **Open**. V dialogu nalezněte příslušný soubor a potvrďte.

Ve složce [examples](examples) najdete některé hotové mřížky pro načtení.

Všechny mřížky mají šířku a výšku 1000 - dohromady 1 milion buněk.

### Animace
1. Animaci spustíte tlačítkem **Play**. Text tlačítka se změní na **Stop** a opětovným kliknutím animaci pozastavíte.
2. Při pozastavené animaci můžete přejít k další generaci tlačítkem **Step**.
2. Rychlost animace lze upravit posuvníkem **Speed**.
3. Číslo současné generace je označeno nápisem **Gen**.
4. Animaci resetujte pomocí tlačítka **Reset**.

### Změna pravidla
Pravidlo hry se zapisuje ve formátu "B*x*/R*y*", kde *x* jsou počty sousedů pro narození buňky a *y* počty sousedů pro přežití. Čísla se v těchto částech nesmí opakovat a nula je zakázána.

Současné pravidlo je označeno nápisem **Rule** nad herní plochou. Změníte jej následovně:
1. Text kolonky v pravém menu nahraďte novým pravidlem.
2. Nastavení potvrďte tlačítkem **Set Rule**.

## Dokumentace
Detaily najdete v kódu, zde jsou uvedeny pouze nejdůležitější metody a datové struktury.

### Použité knihovny
Zejména pro vzhled aplikace byly použity některé knihovny:
- **Tkinter** - okno programu a jeho komponenty, zpracování událostí od uživatele.
- **Pillow** - kreslení na obrázek v paměti.
- **Time** - měření času mezi snímky animace.
- **Os** - nalezení cesty k adresáři hlavního programu, která se použije jako výchozí při načítání hry ze souboru.
- **Sys** - předčasné ukončení programu.
- **Typing** - označení proměnných datovými typy, které nepatří mezi standardní.

### Moduly
- **gol.py:**  
Třídy určené pro výpočet, kreslení a animaci: `Board`, `Rule`, `Painter`, `Animator`.
- **main.py / main.pyw:**  
Hlavní program se třídami: `FileManager`, `TkState`, `Application`.

### Třída `Board`
Obsahuje informace o herní ploše (seznam buněk) a stará se o výpočet dalších generací. Umožňuje přidávat a odebírat buňky.

#### Proměnné:
- **current: list**  
Mřížka současné generace buněk jako 2D seznam proměnných bool (`True` = živá buňka, `False` = mrtvá buňka).
- **living: list**  
Seznam souřadnic (dvojice celých čísel) živých buněk v seznamu `current`.

#### Metody:
- **next_gen() → None:**  
Spočítá další generaci buněk podle počtu jejich sousedů. Prochází pouze živé buňky a jejich sousedy, protože ostatní buňky zůstanou nezměněné.

### Třída `Rule`
Slouží pro snadnější nastavování pravidel hry (počtů sousedů) pomocí textového řetězce. Uloží si množiny čísel, které se pak mohou předat objektu `Board` a ten podle nich přizpůsobí výpočet dalších generací.

#### Proměnné:
- **birth_rule: set**  
Počty sousedů pro narození nové buňky.
- **remain_rule: set**  
Počty sousedů pro přežití buňky.

#### Metody:
- **try_set_rule(value: str) → bool:**  
Pokusí se nastavit textový řetězec `value` jako nové pravidlo. Vrací `True`, pokud je pravidlo správné, jinak `False`.

### Třída `Painter`
Kreslí herní plochu `Board` na plátno `Canvas`.

#### Proměnné:
- **grids: list**  
Obrázky s mřížkou (svislými a vodorovnými čárami) pro různé velikosti buněk. Slouží jako pozadí, na které se budou buňky kreslit. Vytváří se v metodě `reset`, kterou je proto nutné zavolat před jakýmkoliv kreslením. Lze mezi nimi přepínat a tím mřížku „přibližovat / oddalovat“.
- **m_cell: Tuple[int, int]**  
Souřadnice buňky, která je kreslena doprostřed mřížky. Se změnou těchto souřadnic se bude zobrazovat jiná část herní plochy. Obraz se tak může posouvat nahoru, dolů, anebo do stran.
- **canvas_image: int**  
Obrázek na plátně `Canvas` knihovny `tkinter` (ve skutečnosti jen jeho index). Je natažen na celou velikost plátna, pokud nepřekračuje velikost mřížek. Nakreslení herní plochy je provedeno změnou jeho parametru `image`.

#### Metody:
- **reset(...,cell_sizes: list,...) → None:**  
Vytváří obrázky mřížek pro zadané velikosti buněk.
- **draw_board() → None:**  
Nakreslí herní plochu v těchto krocích:
  - Ořízne prostřední část mřížky z `grids` na velikost plátna.
  - Podle souřadnic buňky kreslené doprostřed (`m_cell`) nakreslí všechny viditelné buňky na oříznutou mřížku.
  - Výsledný obrázek nastaví jako parametr `image` obrázku `canvas_image`.

### Třída `Animator`
S využitím objektu typu `Painter` kreslí generace buněk za sebou jako animaci.

#### Proměnné:
- **time_per_gen: int**  
Čas mezi kreslením generací v milisekundách.

#### Metody:
- **play() → None:**  
Spustí animaci.
- **stop() → None:**  
Pozastaví animaci.

### Třída `FileManager`
Statická třída, která načítá a ukládá `Board` do souboru. Výsledek zobrazuje v okně se zprávou - `messagebox`.

### Třída `TkState`
Statická třída, která aktivuje a deaktivuje komponenty `tkinter` (především tlačítka).

### Třída `Application`
Propojuje výpočet a grafické rozhraní programu. Obsahuje komponenty okna a objekty modulu `gol.py`, se kterými manipuluje podle událostí.

## Návrhy na zlepšení

### Rychlost
U většího počtu buněk nebo některých pravidel (např. *B1/R23*) je vidět, že počítání generací je velmi pomalé.

V současné verzi program prochází všechny živé buňky a spočte jejich stav. Výpočet by se dal potenciálně zlepšit:
- Knihovna `numpy` nabízí datovou strukturu pole, kterým se mohou nahradit seznamy standardního Pythonu.
- Použití bitových operací umožní pracovat s celými řádky najednou. Problém by nastal při kreslení, kdy se v řádcích musí najít živé buňky - bity 1 nebo 0. V nejhorším případě se tak znovu projde celá mřížka.

### Paměť
Objekt `Painter` vytváří obrázek pro každou velikost buňky zvlášť. To je zejména kvůli tomu, aby se mřížky nemusely kreslit v každém snímku. Pro rychlejší kreslení tento problém nenastane a v jednu chvíli by tak mohl existovat pouze 1 obrázek.

S využitím bitových operací (viz [Rychlost](#rychlost)) se značně ušetří na paměti. Každá buňka se uloží jako 1 bit a seznam živých buněk se vůbec nepoužije.

### Ostatní
- Přesunutí na konrétní pozici v mřížce pomocí kolonky a tlačítka.
- Kreslení buněk i po spuštění animace.
- Změna barvy pozadí, buněk, atd.


