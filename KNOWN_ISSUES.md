# Known issues — 0.3.0 (beta)

## Requisitos

- 0 A.D. 0.28.0.
- Mod `incas0ad` 0.28.0 instalado y activado. Sin esa dependencia el mod no carga.
- La versión de Incas publicada en mod.io puede ser anterior a 0.28.0; para esta beta usá el release de GitHub: https://github.com/0ADMods/incas-0ad/releases/tag/v0.28.0

## Estado beta

- **Guardado/carga:** la línea de tiempo usa marcadores invisibles y `OnDeserialized`. El test de serialización pasa en las cinco misiones y se probó quicksave/quickload real en la misión 1 (incluido `OnDeserialized`). Conviene repetir la prueba en una partida completa, antes y después de cada oleada.
- **Captura de héroes:** los héroes chancas son capturables para que los objetivos de “elimina o captura” funcionen. Se validó la captura a nivel de componente en el playtest; conviene confirmarla con una orden de captura en partida manual.
- **Balance:** las misiones están pensadas para jugarse, pero los tiempos y tamaños de oleada todavía pueden necesitar ajustes.
- **Voces:** son sintéticas (eSpeak NG), no grabaciones de hablantes nativos. La pronunciación es aproximada y puede sonar robótica.
- **Arte chanca:** las estructuras chancas reutilizan mallas incas con texturas propias. No es una reconstrucción arquitectónica completa.
- **Ropa de trabajadores:** la túnica y la lliclla son una aproximación con recursos existentes; puede haber pequeños clipping o ajustes visuales pendientes.
- **Idioma:** los textos in-game están en español. La ficha de mod.io puede publicarse en inglés/español.
- **Mapas:** el relieve es procedural y las previsualizaciones son simples; no usan un DEM real del Cusco.
- **Nombres chancas:** algunos términos son reconstrucciones o adaptaciones; están documentados como tales en el README.

## Compatibilidad

- Probado en perfil limpio (`0ad + incas0ad + inca-chanca`) y con Delenda Est, Earth Maps y XIII AD.
- El mod sobrescribe plantillas de unidades incas para añadir `<Lang>quechua</Lang>` y corrige dos plantillas incompatibles con esquemas estrictos.
- Si actualizás `incas0ad`, revisá que las plantillas copiadas sigan coincidiendo con la versión nueva.

## Reportar

Al reportar un problema, indicá:
- misión;
- si fue en partida nueva o cargada;
- si usaste otros mods;
- el mensaje del log (`mainlog.html`).
