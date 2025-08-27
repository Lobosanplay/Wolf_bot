# Wolf_bot

## funcionalidades del bot de discord
### 1. pokedex
- Poked <pokemon>: lo que hace es devolverte una img del pokemon q le pases, si no encientra el pokemon te dira q no existe.
- poked-info <pokemon>: te muestra la info del pokemon q le pases.
### 2. comants randon
- clear: limpiara el canal donde sea usado.
- repit <str>: repite lo q le pases.
### 3. Adivine Pokemon
- pokeguess <dificulti>: comienza un juego de adivinanza de pokemons al azar.
    - dificulta facil: solo primera generacion,
    - dificulta media: de primera a tercera generacion,
    - dificulta alta: de primera a ultima generacion,
- answer <respuesta>: respuesta a la adivinanza,
- pokedexhint: primera letra del pokemon.
- typehint: typo del pokemon.
- giveup: Para rendirse.

## Configuración
1. Clona el repositorio:
```cmd
git clone <url-del-repo>
cd wolf_bot
```
2. crear e inizializar entorno virtual:
```py
python -m venv <nombre de tu entorno virtual>
<nombre_entornovirtual>/Scripts/activate
```
3. instalar dependencias:
```py
pip install -r requirements.txt
```
4. Configura las variables de entorno:
Copia el archivo .env.example a .env y completa los valores de el bot de discord:
```cmd
cp .env.example .env
# Edita .env con tu token del bot de discord
```
5. Inicia el bot:
```py
python main.py
```
