# 🚀 ROM Flasher Pro

**MULTI FLASHER / ROM Flasher Pro** is a modern, lightweight, and fully automated GUI tool designed to make flashing Custom ROMs, Recoveries, and Kernels as safe and intuitive as possible. Built with Python and CustomTkinter, it completely eliminates the need to manually type ADB and Fastboot commands in the terminal.


✨ What's New
Faster Extraction: Switched to payload-dumper-go for lightning-fast native ROM extraction.

Sleek UI Overhaul: Upgraded to a deep space dark theme with 100fps fluid tab animations and perfectly symmetrical layouts.

Smart ADB Cleanup: Automatically kills background ADB processes when the app is closed to free up system memory.

Safe Abort Button: Added a red "STOP FLASHING" button to safely cancel operations before entering Sideload mode.

Anti-Brick Protection: Reboot and Stop actions are strictly locked out during adb sideload to prevent soft-bricks.

Dynamic UI: The Kernel tab is now safely disabled until the device is actively detected in Sideload mode.

## ✨ Features

* **Smart Device Detection:** Automatically detects whether your device is in ADB, Fastboot, or Sideload mode and updates the UI in real-time.
* **Multi-Flasher Interface:** Dedicated tabs for **ROM Flashing** and **Kernel Flashing** to keep the workflow organized.
* **Automated Workflows:** * *ROMs & Recoveries:* One-click Fastboot flashing for `.img` files and ADB Sideloading for `.zip` files.
    * *Kernels:* Automatically reboots the device to recovery, waits for sideload mode, flashes the kernel, and safely remains in recovery.
* **Live Progress Tracking:** Beautiful, dynamic animated progress rings and real-time step-by-step checklists.
* **Built-in Console:** A dedicated **Logs** tab outputs live ADB/Fastboot terminal data so you always know exactly what is happening under the hood.
* **Modern UI:** Sleek, dark-mode Material UI design with dynamic icons and responsive elements.
* **Portable:** Compiled as a single standalone `.exe` file—no installation required.

## 🛠️ Prerequisites

Before using this tool, ensure you have the following:
1.  **Unlocked Bootloader:** Your device's bootloader must be unlocked.
2.  **USB Debugging Enabled:** Turn on USB Debugging in your Android Developer Options.
3.  **Proper Drivers:** Ensure standard Google/OEM USB and Fastboot drivers are installed on your Windows machine.

## 🚀 How to Use

### Flashing a Custom ROM / Recovery
1. Launch `Multi Flasher Tool By Raphael.exe`.
2. Connect your device with USB Debugging enabled. The tool will auto-detect it.
3. Click **Reboot to Bootloader** to enter Fastboot mode.
4. Browse and select your Custom Recovery (`.img`) and click **FLASH NOW**.
5. Once in Recovery, wipe your data, enable **ADB Sideload**, and select your ROM (`.zip`) to flash.

## ROM Flasher Pro V4
![Image Alt](https://github.com/pialgigabyte-source/Custom-rom-flasher/blob/d6d40c47f4690e0a6566fadf412591be9d2c34d5/image.png)
## ROM Flasher Pro V3
![Image Alt](https://github.com/pialgigabyte-source/Custom-rom-flasher/blob/d1fe8c8d70eb5b8c002e160c8b1af28ff8938423/Screenshot%202026-04-14%20212314.png)
![Image Alt](https://github.com/pialgigabyte-source/Custom-rom-flasher/blob/d1fe8c8d70eb5b8c002e160c8b1af28ff8938423/Screenshot%202026-04-14%20213454.png)
## ROM Flasher Pro V2
![Image Alt](https://github.com/pialgigabyte-source/Custom-rom-flasher/blob/fb5a7fd486c476ab5b8683303a9be4fe23bfaa84/Screenshot%202026-04-01%20235823.png)
![Image Alt](https://github.com/pialgigabyte-source/Custom-rom-flasher/blob/8127d754ba879338c9409ee7fed70107ba102971/Screenshot%202026-04-02%20000056.png)
![Image Alt](https://github.com/pialgigabyte-source/Custom-rom-flasher/blob/c34fb6433a3075a28bc25c8fed39ad4fb19bd244/Screenshot%202026-04-02%20000609.png)

### Flashing a Custom Kernel
1. Navigate to the **Kernel Flasher** tab.
2. Ensure your device is connected via ADB.
3. Select your Custom Kernel (`.zip`).
4. Click **FLASH KERNEL**. The tool will automatically reboot your phone to recovery, wait for you to enable sideload, and flash the file.


![Image Alt](https://github.com/pialgigabyte-source/Custom-rom-flasher/blob/d1fe8c8d70eb5b8c002e160c8b1af28ff8938423/Screenshot%202026-04-14%20212338.png)

![Image Alt](https://github.com/pialgigabyte-source/Custom-rom-flasher/blob/c34fb6433a3075a28bc25c8fed39ad4fb19bd244/Screenshot%202026-04-02%20000840.png)

![Image Alt](https://github.com/pialgigabyte-source/Custom-rom-flasher/blob/c34fb6433a3075a28bc25c8fed39ad4fb19bd244/Screenshot%202026-04-02%20001548.png)


## ⚠️ Disclaimer

**Use at your own risk.** Flashing custom firmware can potentially brick your device. The developer is not responsible for any damage to your device, lost data, or voided warranties. Always ensure you are flashing the correct files for your specific device model.

⚠️ Windows Defender / Antivirus Warning
Because this tool is a compiled Python executable that runs background terminal commands (ADB/Fastboot), Windows Defender may flag it as a virus (e.g., Program:Win32/Contebrew.A!ml).

This is a false positive. To use the tool, click "More info" -> "Run anyway" if SmartScreen blocks it, or allow it in Windows Security. All source code is provided in this repository for full transparency.

## 👨‍💻 Author

Developed and built by **Raphael 8s_G4**
