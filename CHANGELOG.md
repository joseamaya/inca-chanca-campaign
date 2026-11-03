# Changelog

## 0.3.0 (beta)

- Campaña y civ chanca publicables como beta.
- Línea de tiempo de misiones reescrita con marcadores invisibles y un único `OnInterval`, para reducir duplicados al guardar/cargar.
- Añadido `OnDeserialized` en las cinco misiones para reanudar objetivos y tick.
- Restricciones históricas para el jugador inca: se deshabilitan ariete, campeones imperiales, héroes de otras épocas, barcos, puerto, maravilla, colonia militar y mercenarios anacrónicos.
- Ropa de trabajadores incas y chancas: túnica corta para hombres y lliclla para mujeres.
- Voces quechuas sintéticas con eSpeak NG; voz femenina con variante `qu+f3` para distinguirla de la masculina.
- Añadidos `thumbnail.png`, `CHANGELOG.md`, `KNOWN_ISSUES.md` y resumen en inglés.
- Corregida la plantilla `infantry_chaski` para validar también en perfil limpio (sin Delenda Est).
- Las misiones defensivas ahora pierden también si el centro cívico o el santuario son capturados, no solo destruidos.
- Los héroes chancas ahora son capturables, para que los objetivos de Yahuar Pampa y Andahuaylas sean coherentes.
- Versión numérica `0.3.0` para que 0 A.D. valide el mod; “Beta” queda en la etiqueta y la documentación.
- Documentación actualizada con rutas genéricas e instrucciones de dependencia.
- Playtest funcional de 13 casos: victorias, derrotas, capturas de edificios/héroes, momia, centro chanca y epílogo, sin errores reales.

## 0.2.1

- Voces masculinas y femeninas diferenciadas por tono y formantes.
- Reempaquetado del mod.

## 0.2.0

- Paquete de voces quechuas sintéticas.
- `<Lang>quechua</Lang>` en unidades incas y chancas.
- Correcciones de ropa de trabajadores.
- Notificaciones con escapes Unicode para tildes y ñ.

## 0.1.0

- Versión inicial: campaña de 5 niveles, civ chanca, mapas, triggers y arte derivado.
