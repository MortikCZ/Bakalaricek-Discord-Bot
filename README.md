# Bakalaricek Discord Bot
Discord Bot pro zobrazování suplování, aktuálního rozvrhu a jeho změn z Bakalářů v jazyce Python.

Tento bot umožňuje skrze [bakapi-v2](https://github.com/MortikCZ/bakapi-v2), komunikovat s Bakaláři API a získavat informace o suplování, dokáže v předem určeném kanálu zobrazovat suplování pro aktuální týden a posílat upozornění na změny v rozvrhu.

## Požadavky
- Prostor pro hostování bota (např. VPS, Raspberry Pi, atd.) s nainstalovaným Pythonem.
- Příhlašovací údaje k Bakalářům (uživatelské jméno a heslo).
- URL adresa příhlašovací stránky Bakalářů.
- Discord Bot Token.

## Instalace
1. Stáhněte si repozitář
```
    git clone https://github.com/MortikCZ/Bakalaricek-Discord-BOT.git
    cd Bakalaricek-Discord-BOT
```
2. Nainstalujte závislosti
```
    pip install -r requirements.txt
```
3. Konfigurace
    - Vytvořte soubor `config.json` podle této šablony
```json
    {
    "bot": {
        "token": "token bota"
    },
    "bakalari": {
        "username": "přihlašovací jméno do bakalářů",
        "password": "heslo do bakalářů",
        "url": "URL přihlašovací stránky bakalářů"
    },
    "discord": {
        "substitutions_channel_id": kanál pro zobrazení suplování,
        "timetable_channel_id": kanál pro zobrazení rozvrhu,
        "subst_change_channel_id": kanál pro oznámení změn v rozvrhu,
        "subst_change_role_id": role pro oznámení změn v rozvrhu
    }
```
5. Spusťte bota
```
    py main.py
```
## Changelog
### 0.3
- Status se nově ukládá do souboru `config.json` a při restartu bota se načte poslední status.
### 0.2
- Přídán embed pro zobrazení rozvrhu pro aktuální den.
- Přídána možnost nastavení statusu bota pomocí příkazu /status <status>
### 0.1
- První release 