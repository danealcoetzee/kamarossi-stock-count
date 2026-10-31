# Kamarossi Stock Count

A web app for counting cable drums on the Honeywell EDA52 handhelds. Install it from Chrome
(menu > Add to Home screen / Install app); it then works without signal.

- Scan the drum label (or type the batch), enter the metres on the keypad, save.
- Each scan is checked against the K8 stock check list on the spot: not on the list, label and K8
  product don't match, batch on several K8 lines, already counted on this device.
- Counts and photos stay on the device until they are sent (Send counts > the phone's share menu),
  or saved as a ZIP backup.

## Data

This repository holds only the program. The K8 lists in `lists/` are encrypted (AES-GCM, key from a
count code with PBKDF2-SHA256); the app asks for the count code once per count and decrypts the list
on the device. Count codes are never stored here. `tools/make_list.py` encrypts a new list.

Fonts: Barlow and IBM Plex Mono, SIL Open Font License (see `fonts/`).
