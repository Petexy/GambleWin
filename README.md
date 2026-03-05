# Gamba - Slot Machine

**Gamba** is a high-stakes slot machine simulation that uses your actual files as currency. This application is designed to demonstrate the extreme risks of gambling by tying game outcomes to the encryption and decryption of your personal data.

## ⚠️ DISCLAIMER & WARNING ⚠️
**I AM NOT RESPONSIBLE FOR ANY LOST, ENCRYPTED, OR CORRUPTED FILES.**

This software is provided "as is", without warranty of any kind. It is intended for educational and demonstrative purposes only. By running this program, you acknowledge and accept that:

1. **Real Data is at Risk:** The program interacts with your file system (including mounting Windows partitions) and uses real encryption on your files.
2. **Loss is Permanent:** If files are encrypted and the program is closed or crashes before decrypting them, your data may be permanently unrecoverable.
3. **No Liability:** The creator and maintainers of this repository take absolutely zero responsibility for any damage, data loss, or emotional distress caused by this software, whether initiated by the user intentionally or by an unaware user. Use it strictly at your own risk. Do not run this on a machine with important files.

## Features
- **High-Stakes Gameplay:** Bet your files on a fully animated slot machine interface.
- **Real-Time Encryption/Decryption:** Files are encrypted when you lose and decrypted when you win.
- **Windows Partition Mounting:** Automatically detects and mounts Windows partitions (`ntfs-3g`) to use as collateral.
- **Debug Mode:** A safe mode (`--debug`) is available to bypass the mounting and encryption process for testing purposes.
- **Multi-language Support:** Includes localization support (e.g., Polish language fallback).

## Requirements
- Python 3
- GTK 4 and libadwaita
- GStreamer (for audio playback)
- `ntfs-3g` (for mounting Windows partitions)
- `cryptography` Python library (`crypto.py` uses Fernet for encryption)

## Usage
Run the application using Python:
```bash
python3 gamba.py
```

### Safe Mode (Testing)
To run the application safely without mounting partitions or encrypting files, use the `--debug` flag:
```bash
python3 gamba.py --debug
```

### Forcing a Language
You can force a specific language (if available in the `locales/` directory):
```bash
python3 gamba.py --force-language pl
```

## How It Works
1. **Collateral:** The application identifies a Windows partition and counts the files to use as your "starting coins".
2. **Betting:** You choose how many files to bet per spin.
3. **Spinning:** The slot machine spins. If you lose, a corresponding number of your files are encrypted. If you win, encrypted files are decrypted.
4. **House Edge:** Like all casinos, the game is rigged to ensure you cannot win more "coins" than your starting amount.
5. **Decryption:** You can choose to decrypt all files and end the session, but only after accepting a harsh reality check about gambling addiction in the "Terms of Decryption".

**Again: DO NOT USE THIS ON A SYSTEM WITH DATA YOU CANNOT AFFORD TO LOSE.**
