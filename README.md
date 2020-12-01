# dominion-game

## Windows

### First Time Setup

1. Install Windows Terminal from the Microsoft Store: https://www.microsoft.com/store/productId/9N0DX20HK701.

2. Download and install the latest stable Python 3 release from here: https://www.python.org/downloads/.

   * Use the default settings unless you know what you're doing, except for:
     * **Add Python to PATH**: Check this box.

3. Download and install the latest stable Git for Windows release from here: https://gitforwindows.org/

   * Use the default settings except for:
     * **Default Editor**: Whatever you're comfortable using.
     * **PATH Environment**: Choose "Git from the command line and also from 3rd-party software."

4. Open Windows Terminal and launch a Command Prompt tab (or type `cmd` from PowerShell).

5. Clone the dominion-game GitHub repository and navigate into the newly cloned directory:

   ```
   git clone https://github.com/eshapiro42/dominion-game
   cd dominion-game
   ```

6. Create (and activate) a new Python virtual environment:

   ```bash
   python3 -m venv venv
   venv\Scripts\activate.bat
   ```

7. Install all necessary Python modules:

   ```bash
   pip install -r requirements.txt
   ```

### Every Time

1. Open Windows Terminal and launch a Command Prompt tab

2. Pull the latest code from the dominion-game GitHub repository:

   ```bash
   cd dominion-game
   git pull
   ```

3. Source your Python virtual environment:

   ```bash
   venv\Scripts\activate.bat
   ```

4. Run the game client (resize/zoom your Terminal window before you do this):

   ```bash
   python client.py
   ```

5. If you need to kill the client, use  <kbd>CTRL</kbd>+<kbd>Break</kbd> (or <kbd>CTRL</kbd>+<kbd>Pause</kbd>).



