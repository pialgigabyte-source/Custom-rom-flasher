# 🚀 ROM Flasher Pro

**MULTI FLASHER / ROM Flasher Pro** is a modern, lightweight, and fully automated GUI tool designed to make flashing Custom ROMs, Recoveries, and Kernels as safe and intuitive as possible. Built with Python and CustomTkinter, it completely eliminates the need to manually type ADB and Fastboot commands in the terminal.

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
1. Launch `flasher.exe`.
2. Connect your device with USB Debugging enabled. The tool will auto-detect it.
3. Click **Reboot to Bootloader** to enter Fastboot mode.
4. Browse and select your Custom Recovery (`.img`) and click **FLASH NOW**.
5. Once in Recovery, wipe your data, enable **ADB Sideload**, and select your ROM (`.zip`) to flash.

### Flashing a Custom Kernel
1. Navigate to the **Kernel Flasher** tab.
2. Ensure your device is connected via ADB.
3. Select your Custom Kernel (`.zip`).
4. Click **FLASH KERNEL**. The tool will automatically reboot your phone to recovery, wait for you to enable sideload, and flash the file.

![Image Alt](https://github.com/pialgigabyte-source/Custom-rom-flasher/blob/fb5a7fd486c476ab5b8683303a9be4fe23bfaa84/Screenshot%202026-04-01%20235823.png)


![Image Alt](https://github.com/pialgigabyte-source/Custom-rom-flasher/blob/8127d754ba879338c9409ee7fed70107ba102971/Screenshot%202026-04-02%20000056.png)




## ⚠️ Disclaimer

**Use at your own risk.** Flashing custom firmware can potentially brick your device. The developer is not responsible for any damage to your device, lost data, or voided warranties. Always ensure you are flashing the correct files for your specific device model.

## 👨‍💻 Author

Developed and built by **Raphael 8s_G4**
