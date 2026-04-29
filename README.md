== Instructions to Run the Demo1 Format ==
1. Open Powershell or Visual Studios

2\. Open Projectfolder

3\. Copy Paste this to run:

py -m streamlit run app/main.py

Or double-click:

Run_iTrain.bat

Optional validation commands:

- Run the automated tests:

py -m pytest

- Run the benchmark-focused regression test:

py -m pytest tests\test_benchmark.py

- Print a readable benchmark summary:

py -m app.tools.benchmark

4\. In the app sidebar:

- Upload a handbook (`.txt` or `.pdf`) for real testing, or
- explicitly enable `Use bundled sample handbook (demo mode)` if you want to try the built-in sample content.

Notes\. 
- Docs: the docs section includes documents that were used to help build the program and were used as test manuals. The program does not reference these directly. These were placed so I can keep track what was used and tested on at satisfactory level.

- .exe: The launcher.py, dist/iTrain/iTrain.exe and .spec files are leftover from attempting to get an .exe to work. This proved to be way more labor intensive than needed so for now I decided to use a .bat file as what is currently being used.