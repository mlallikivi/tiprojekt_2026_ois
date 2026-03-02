# 🛠️ Töökeskkonna seadistamise juhend

Et oma projekte mugavalt läbi viia, seadistame esimese asjana üles keskkonna. Selleks tuleb installeerida ning oma vahel siduda **VS Code**, **Miniconda** ja **Git**.

💡 Ära jäta samme vahele. Kui kaldud juhendist kõrvale, muutub vigade parandamine hiljem  mitu korda raskemaks.

💡 Kui mõni osa jääb segaseks või installeerimisega tekib probleeme, kasuta julgelt suurte keelemudelite abi. Ning alati võid abi küsida ka Moodle’i foorumist. 🙂

Näide, kuidas suurte keelemudelite käest abi küsida:

> 🛑 Said veateate?
> 
> 1. Kopeeri veateade (või osa sellest).
> 2. Kleebi see ChatGPT-sse, Claude'i või Geminisse (vms) koos kirjeldava tekstiga, näiteks midagi sellist:
> 
> *"I am setting up a Conda environment on [Windows/Mac] for a Python Data Science course. I received this error: [PASTE ERROR]. Explain simply what went wrong and give me the command to fix it."*
> 

## Osa 1: Vajalikud tööriistad 🧰

Esimese asjana tuleb paigaldada järgmised tööriistad. Kui need on sul juba olemas, veendu, et need oleksid uuendatud.

### 1. Visual Studio Code (VS Code)

**VS Code** on üks populaarsemaid koodiredaktoreid, mis koondab koodikirjutamise, terminali ja failihalduse mugavalt ühte kohta ning teeb Pythoni ja tehisintellekti rakenduste arendamise lihtsaks, eriti tänu paljudele laiendustele.

1. [**Lae VS Code alla siit**](https://code.visualstudio.com/).
2. **Tegevus:** Pärast paigaldamist ava VS Code, klõpsa vasakul asuvale "Extensions" ikoonile (klotsid) ja paigalda Microsofti **"Python"** laiendus (extension).

### 2. Miniconda

**Teegid** (ingl k *libraries*) on olemasolevad koodikomplektid, mis annavad meile vajalikud tööriistad (nt andmetöötlus või tehisintellekti-mudelitega suhtlemine), et me ei peaks kogu koodi nullist kirjutama. **Miniconda** aitab meil neid sadu teeke hallata ja paigaldada nii, et need töötaksid koos tõrgeteta ega läheks sinu arvuti teiste programmidega konflikti. 

**💡 Ilmselt paljud teist teavad Anacondat. Mis vahe on Minicondal ja Anacondal?**
Miniconda on **Anaconda** kompaktsem versioon. Kui tavaline Anaconda laeb alla gigabaitide viisi teeke, mida sa tõenäoliselt kunagi ei kasuta, siis Miniconda on puhas ja kerge tööriist, kuhu lisame ainult kursuseks vajalikud osad.

**💡 Kui sul on Anaconda juba olemas?**
Kui sul on arvutis Anaconda juba paigaldatud, siis sa ei pea Minicondat lisaks paigaldama. Nad kasutavad täpselt samu käske ja töötavad identselt. Jätka lihtsalt olemasoleva Anacondaga.

1. [**Lae Miniconda alla siit**](https://docs.conda.io/en/latest/miniconda.html).
2. Conda kasutamine terminalis:
    - **Windows:** Ära lisa conda’t PATH’i (kui seda paigaldamise ajal küsitakse). Välja arvatud juhul, kui sa tead täpselt, mida teed. Hiljem hakkame conda’t kasutama **"Anaconda Prompt"** terminali abil (otsi rakendust Anaconda Prompt ja näed, et avaneb terminal). Iga kord kui meie juhend palub avada terminali, siis just see Anaconda Prompt on see, mida Windows’i kasutaja avama peaks.
    - **Mac ja Linux:** Võid julgelt kasutada tavalist terminali.

### 3. Git

Git on vajalik koodi allalaadimiseks ja versioonihalduseks.

- [**Lae Git alla siit**](https://git-scm.com/downloads).

## Osa 2: Koodirepositoorium☁️

Koodi haldamiseks hoiustatakse seda tavaliselt repositooriumis. Esiteks tagab see, et sinu koodist on olemas sinu arvutist väljaspool koopia. Teiseks, niimoodi saavad mitu inimest sama koodi muuta ning muudatused on ühes kohas hoiul. Kolmandaks, see võimaldab meil koodi väga lihtsalt alla laadida erinevatese kohtadesse (näiteks serverisse). Neljandaks, see aitab silma peal hoida arendustööl ning muudatustel. Meie loome GitHubi repositooriumi ning hakkame oma koodi seal hoiustama.

### Samm 1: Loo GitHubi repositoorium

1. Logi sisse [GitHubi](https://github.com/) (kui sul kontot pole, siis loo uus konto).
2. Vajuta üleval paremal nurgas **+** märki ja vali **"New repository"**.
3. Täida väljad järgmiselt:
    - **Repository name:** `tehisintellekti-rakendamise-projekt`
    - **Public**
    - **Initialize this repository with:** Pane linnuke kasti **"Add a README file"**. (See on oluline, et me saaksime repositooriumi kohe kloonida - ehk endale koopia alla laadida).
4. Vajuta rohelist nuppu **Create repository**.

### Samm 2: Klooni repositoorium arvutisse

Nüüd kopeerime selle repositooriumi sinu arvutisse.

1. Sinu uue repositooriumi lehel vajuta rohelist nuppu **<> Code**.
2. Veendu, et valitud on vaheleht **HTTPS** ja kopeeri seal olev link (vajuta kopeerimise ikooni).
3. Ava VS Code’i uus aken ja vali sealt variant **Clone Git Repository**.
4. Sisesta oma repositooriumi link.
5. Salvesta see sobivasse kausta.
6. Avaneb VS Code sinu repositooriumiga.
7. **Kontroll:** Vaata VS Code'i vasakut äärt. Seal peaks olema ikoon, mis näeb välja nagu harunev joon (Source Control).
    - Kui klõpsad sellel, peaks seal olema kiri "Source Control" ja tõenäoliselt tühi nimekiri (sest me pole veel muudatusi teinud).
    - See tähendab, et VS Code tunneb Giti automaatselt ära – eraldi laiendust (extensioni) pole vaja paigaldada.

## Osa 3: Conda keskkond ja vajalikud teegid📦

Nüüd seame üles conda keskkonna ja installime sinna vajalikud teegid. Conda keskkond on justkui eraldatud “mull”, kuhu saad installeerida konkreetseid variante python’ist ning teekidest - sellega saad tagada, et konkreetse projekti jaoks on sul just õige komplekt teeke, mille peal sinu kood korrektselt jookseb. Tüüpiliselt ongi eraldi projektide jaoks eraldi teegid, kus igaühes on just sellele vajalik seadistus. Meie loome keskkonna viisil, kus me juba selle loomise käigus laseme ka vajalikud teegid installeerida.

### Samm 1: Loo environment.yml fail

Selleks, et kõigil tudengitel oleksid täpselt samad versioonid teekidest, kasutame keskkonna initsialiseerimiseks `environment.yml` faili, mis paneb paika nii keskkonna nime, kanalid (channels), kust teeke installida, python’i versiooni ning teegid. Nii tehes ei pea me iga teeki ise käsitsi installima - see oleks aeganõudvam ning niimoodi korraga installeerides tekib oluliselt vähem võimalusi konfliktideks (mõnikord teeke käsitsi installeerides toimuvad versioonide vahelised konfliktid, mida on tüütu lahendada).

1. Veendu, et oled VS Code'is oma projektikaustas (`thisintellekti-rakendamise-kursus`).
2. Loo vasakul failide paneelis uus fail nimega **`environment.yml`**.
3. Kopeeri ja kleebi sinna see sisu:

```yaml
name: oisi_projekt
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.10
  - pip
  - numpy
  - pandas
  - requests
  - scikit-learn
  - pip:
      - streamlit
      - openai
      - ollama
      - groq
      - sentence-transformers
      - langchain
      - langchain-community
      - python-dotenv
      - watchdog
```

1. Salvesta fail.

### **Samm 2: VS Code’i terminali seadistamine**

Mugavuse huvides ei pea sa akende vahel hüppama. **VS Code'il on sisseehitatud terminal**, kus saad käivitada Anaconda käske otse koodi kõrval.

1. Vali ülevalt menüüst **Terminal > New Terminal.**
2. All avaneb paneel, kuhu saad kirjutada käske.  Kirjuta: `conda --version`.
    - **Kui näed versiooninumbrit:** Kõik korras, mine Samm 3 juurde.
    - **Windowsi kasutajad näevad suure tõenäosusega punast viga:** Sellisel juhul tee läbi järgnev **ühekordne parandus.**

**🔧 Windowsi Ühekordne Parandus (One-time fix):**

1. Ava Start menüüst programm **Anaconda Prompt** (parem klõps -> *Run as Administrator*).
2. Kirjuta sinna käsk:
    
    ```bash
    conda init powershell
    ```
    
3. Sulge Anaconda Prompt.
4. **TÄHTIS:** Sulge VS Code täielikult ja ava uuesti.
5. Ava VS Code'is uus terminal. Nüüd peaks `conda --version` töötama!
****

### **Samm 3: Keskkonna loomine ja aktiveerimine**

Nüüd, kus terminal töötab, loome oma keskkonna.

1. Kirjuta VS Code'i terminali:
    
    ```bash
    conda env create -f environment.yml
    ```
    
    See loob keskkonna ja installib vajalikud teegid.
    
2. Kui keskkond on loodud, saame selle aktiveerida. Kui oleme keskkonna aktiveerinud, toimuvad kõik meie tehtud pythoni jooksutamised selle keskkonna sees. Keskkonna aktiveerimiseks kirjuta terminali:
    
    ```bash
    conda activate oisi_projekt
    ```
    
3. **Kontroll:** Kui terminali rea alguses on sulgudes **`(oisi_projekt)`**, siis on kõik korras! 🎉

****

## Osa 4: Töökeskkonna testimine 🚀

Nüüd on kõik paigaldatud. Teeme läbi reaalse töövoo: kirjutame lihtsa rakenduse, testime seda oma arvutis ja saadame koodi GitHubi pilve.

### Samm 1: Loo esimene rakendus

1. Veendu, et oled VS Code'is oma projektikaustas.
2. Loo uus fail nimega **`hello_ai.py`**.
3. Kopeeri sinna see kood:

```python
import streamlit as st

st.set_page_config(page_title="Minu Esimene Äpp", page_icon="🤖")

st.title("Tere, tehisintellekti rakendaja! 👋")
st.write("Kui sa näed seda teksti, siis sinu töökeskkond on 100% korras.")

# Lihtne interaktiivsus
name = st.text_input("Kirjuta siia oma nimi:")
if name:
    st.success(f"Väga meeldiv, {name}! Sinu arvuti on kursuseks valmis.")
```

1. Salvesta fail.

### Samm 2: Käivita rakendus

Nüüd paneme Streamliti serveri tööle.

1. Ava VS Code'i terminal.
2. Veendu, et näed rea alguses **`(ti_rakendamise_kursus)`**.
3. Kirjuta käsk:

```bash
streamlit run hello_ai.py
```

1. Sinu veebibrauser peaks automaatselt avanema ja kuvama sinu rakendust. Proovi sinna oma nimi kirjutada!
2. Kui oled testimise lõpetanud, mine tagasi VS Code'i terminali ja vajuta klaviatuuril **`Ctrl + C`**. See paneb serveri seisma ja laseb sul jälle käske kirjutada.

**PS!** Samamoodi terminalist on võimalik jooksutada ka “tavalisi” pythoni faile (python failinimi.py).
****

### Samm 3. Ühendus repositooriumiga

Järgmiseks pushime oma rakenduse koodi ka repositooriumisse. Seda saab teha käsurealt, aga VS Code’il on ka väga mugav graafiline liides selle tegemiseks.

1. **Ava Source Control:**
Klõpsa vasakul menüüs ikoonile, mis näeb välja nagu harunev joon (või vajuta `Ctrl+Shift+G`).
2. **Stage Changes (+):**
Näed nimekirja "Changes". Hõlju hiirega faili `hello_ai.py` kohal ja vajuta ilmnevat **`+`** märki (Stage Changes). See tõstab faili valmispaneku alasse ("Staged Changes").
3. **Commit (Salvesta ajalugu):**
Ülal on tekstikast kirjaga *"Message"*.
    - Kirjuta sinna lühike kirjeldus, nt: `Esimene testrakendus`.
    - Vajuta sinist nuppu **Commit** (või linnukest ✔️).
4. **Push (Sünkroniseeri pilvega):**
Nüüd ilmub sinine nupp kirjaga **Sync Changes** (või "Publish Branch"). Vajuta seda.
    - *Kui VS Code küsib kinnitust, vajuta OK.*

### Samm 4: Lõplik kontroll ✅

1. Mine oma GitHubi repositooriumi lehele (veebis).
2. Värskenda lehte.
3. Kui näed seal faili **`hello_ai.py`**, oled ametlikult valmis! 🎓