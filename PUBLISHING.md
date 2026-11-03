# Publicación beta en mod.io

Repositorio: https://github.com/joseamaya/inca-chanca-campaign

## Estado

- Versión de `mod.json`: `0.3.0`.
- Etiqueta visible: `La Guerra Inca-Chanca (c. 1438) — Beta`.
- Archivo listo: `inca-chanca.pyromod`.
- Para mod.io, subir una copia renombrada como `inca-chanca.zip`.

## Dependencia

`incas0ad` 0.28.0 todavía no está publicado en mod.io. Para esta beta:

1. El jugador debe instalar `incas-0ad-0.28.0.pyromod` desde:
   https://github.com/0ADMods/incas-0ad/releases/tag/v0.28.0
2. Después instala `inca-chanca`.
3. En **Mod Selection** activa `Incas 0 A.D.` y `La Guerra Inca-Chanca`.
4. Reinicia el juego.

La ficha de mod.io debe decirlo de forma visible. Sin `incas0ad` 0.28.0, el mod aparece como incompatible o con dependencias no satisfechas.

## Ficha sugerida

- **Name / name_id:** `inca-chanca`
- **Label:** `La Guerra Inca-Chanca (c. 1438) — Beta`
- **Game:** 0 A.D.
- **Version:** `0.3.0`
- **Tags:** Campaign, Factions, Historical, Spanish
- **Licencia:** código GPL-2.0; arte derivado CC-BY-SA 3.0.

### Resumen en español

Campaña histórica sobre la guerra entre el Curacazgo del Cusco y la confederación chanca (c. 1438), con cuatro misiones, un epílogo y una civilización chanca jugable. Requiere el mod Incas 0 A.D. 0.28.0.

### Resumen en inglés

Historical campaign about the war between the Cusco chiefdom and the Chanca confederation (c. 1438), with four missions, an epilogue and a playable Chanca civilization. Requires the Incas 0 A.D. 0.28.0 mod.

## Pasos de subida

1. Usar el ZIP del release de GitHub o copiar `inca-chanca.pyromod` a `inca-chanca.zip`.
2. En mod.io: **Add Mod** → juego **0 A.D.**
3. Usar `inca-chanca` como nombre/URL.
4. Subir `inca-chanca.zip` como archivo principal.
5. Poner la versión `0.3.0`.
6. Añadir la dependencia de Incas si la ficha lo permite; si no, dejarla escrita en la descripción.
7. Publicar primero como **hidden/unlisted**.
8. Probar la instalación desde mod.io en un perfil limpio.
9. Pasar a público cuando la prueba funcione.

## Pruebas antes de hacer pública

- [x] Activar `incas0ad` y `inca-chanca` sin errores de dependencia.
- [x] Cargar las 5 misiones.
- [x] Guardar/cargar con quicksave/quickload en la misión 1, incluido `OnDeserialized`.
- [x] Revisar el log sin errores.
- [x] Revisar que los héroes chancas se puedan capturar y que la victoria se dispare.
- [x] Revisar que capturar el centro cívico/santuario provoque derrota en las misiones defensivas.
- [x] Verificar la cadena `Requires` y la existencia de los mapas de campaña.
- [ ] Instalación desde mod.io en perfil limpio.
- [ ] Completar una partida completa y verificar el desbloqueo real de la siguiente misión en el menú.

## Resultado del playtest funcional

Se probaron 13 casos con un reloj acelerado sobre una copia temporal:

- victoria de las misiones 1, 2, 3, 4 y epílogo;
- derrota por muerte de Cusi en las misiones 1, 3 y 4;
- derrota por captura del centro cívico en las misiones 1 y 2;
- derrota por captura del santuario en la misión 2;
- victoria alternativa por captura del centro chanca en la misión 2;
- captura de la momia y de los capitanes chancas en la misión 3;
- captura del centro y de Anccu Huallo en la misión 4;
- 0 errores reales en los 13 casos.

## Capturas recomendadas

- Menú de campaña con los cinco niveles.
- Misión 1: Cusco y Cusi Yupanqui.
- Misión 2: asedio y oleada chanca.
- Misión 3: Yahuar Pampa y capitanes chancas.
- Civilización chanca: árbol de unidades o partida skirmish.
- Trabajadores con túnica/lliclla y una unidad con voces quechuas.

## Limitaciones que deben figurar en la ficha

- Voces sintéticas con eSpeak NG, no hablantes nativos.
- Arte chanca derivado/reskin del mod Inca.
- Textos in-game en español.
- Mapas procedurales, sin DEM real.
- Beta: balance y guardado/carga todavía en revisión.
