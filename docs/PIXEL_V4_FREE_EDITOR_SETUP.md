# Optional desktop editors — real installation evidence

The installer now recognizes the actual upstream filenames for Linux Pixelorama, LDtk and Godot.

On supported Linux systems, run:
  npm run art:install:free
  npm run art:check

For an individual editor:
  python3 scripts/install_studio_v2.py --pixelorama
  python3 scripts/install_studio_v2.py --godot
  python3 scripts/install_studio_v2.py --ldtk
  python3 scripts/install_studio_v2.py --krita

The included optional CI workflow downloads the official editors and checks executables. It does NOT verify that a movie artist actually edited sprites in these programs.

Real-art evidence must include editable files (.pxo, .kra, .ldtk and Godot project scenes), the export, and proof that the editor produced that export. Installing a GUI does not create art. PixelLab remains a separate authenticated remote MCP service. PixelOver paid export is not included. Sprite Fusion web is not a local CLI.

The downloaded executables live in gitignored .tools. They are not embedded in the repository.
