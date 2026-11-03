# The Inca–Chanca War (c. 1438)

Repository: https://github.com/joseamaya/inca-chanca-campaign

**Beta** campaign for **0 A.D. Empires Ascendant 0.28.0** about the conflict between the Cusco chiefdom and the Chanca confederation. Includes a playable Chanca civilization, four missions and an epilogue.

## Requirements

- 0 A.D. **0.28.0**.
- The **Incas 0 A.D.** mod (`incas0ad`) 0.28.0:
  - Repository: https://github.com/0ADMods/incas-0ad
  - Required release: https://github.com/0ADMods/incas-0ad/releases/tag/v0.28.0
  - The version published on mod.io may be older than 0.28.0. For this beta, install the `.pyromod` from the GitHub release.

This mod declares:

```json
"dependencies": ["0ad=0.28.0", "incas0ad=0.28.0"]
```

## Installation

1. Copy this folder to your 0 A.D. mods directory:
   - Linux: `~/.local/share/0ad/mods/inca-chanca`
   - Windows: `%USERPROFILE%\Documents\My Games\0ad\mods\inca-chanca`
   - macOS: `~/Library/Application Support/0ad/mods/inca-chanca`
2. Install `incas-0ad-0.28.0.pyromod` from the GitHub release into the same mods directory.
3. In game: **Settings → Mod Selection**, enable both `Incas 0 A.D.` and `The Inca–Chanca War`.
4. Restart, then open **Single-player → New Campaign**.

Do not use **Load Campaign** to find a new campaign; that menu only lists saved campaign runs.

## Campaign

1. The Chanca threat
2. The siege of Cusco
3. Yahuar Pampa
4. The Chanca campaign
5. Epilogue: Pachacútec

## Beta limitations

- Synthetic Quechua voices generated with eSpeak NG. They are not native-speaker recordings.
- Chanca buildings reuse Inca meshes with new textures; this is not a full architectural reconstruction.
- Worker clothing and the lliclla are approximations and may need visual polish.
- Save/load uses marker entities and `OnDeserialized`; please test it in your own playthrough.
- In-game text is Spanish; this English file is for the mod.io listing.
- The Inca player has late imperial units, ships, wonder, extra heroes and siege rams disabled for historical accuracy.

## Historical note

The Inca–Chanca war is a mytho-historical event known mainly from colonial chronicles and oral tradition. Dates, numbers and details differ between sources. The campaign follows a historiographically reasonable interpretation, not a literal transcription of the chronicles. The pururauca episode is presented explicitly as a legend.

## License

Code: GPL-2.0. Derived art: CC-BY-SA 3.0, with attribution to the original Incas 0 A.D. authors. See `CREDITS.md`, `LICENSE` and `art/LICENSE.txt`.
