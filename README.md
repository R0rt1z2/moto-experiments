# Experiments for MTK based Motorolas
This repository contains various tools and scripts to experiment with MTK based Motorola devices. The primary goal of this project is to reverse engineer methods used by paid tools to unlock the bootloader, root the device, and flash any partition.

## Supported Devices
- Motorola G13 / G23 codenamed `penangf` (MT6768)
- Motorola G24 / G24 power codenamed `fogorow` (MT6768)

## Background
On high-end MediaTek devices, Motorola provides an official bootloader unlock method, allowing users to unlock their devices legitimately. However, on low-end Motorola devices, this functionality is not officially supported. Open-source tools like **mtkclient** offer alternative methods for unlocking bootloaders by exploiting bootROM vulnerabilities but Motorola has patched these vulnerabilities on our devices, making such methods ineffective.

After months of unsuccessful attempts, reports emerged that AMT (Android Multi Tool) could unlock bootloaders, flash firmware, and perform various operations on Motorola devices, even those previously thought to be secure.

In our specific case, we found that using **mtkclient** allows uploading stock Download Agents (DAs) to perform a limited range of operations, such as reading certain partitions. However, more critical actions like writing to partitions remain restricted.

Given the limitations of free tools, paid solutions seemed to offer broader access. We suspected these tools might be using leaked DAs to perform all these operations. To investigate this, I used a USB Beagle physical sniffer to monitor USB traffic and act as a man-in-the-middle. By doing so, I managed to filter the traffic and successfully extract the custom DA used by these paid tools.

## Tools
- `preloader-relay`: Allows you to relay the traffic from these paid tools to upload the extracted DA.
- `parse_da`: Script that parses a DA file and dumps the information (supported SOCs, version, identifier, etc).
- `parse_sniff`: Script that can be used to parse DataSource CSV exports from the Beagle USB sniffer to extract the DA.

The `bin` folder contains a collection of DAs for each device. This collection includes stock DAs and the leaked DA extracted from the paid tools.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. All Download Agents (DAs) are property of MediaTek Inc. and are used for educational purposes only.