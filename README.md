# Quansheng UV-K5 firmware encoder/decoder

Supports updater v1.1.7 (decrypted only) and 1.1.11 (encrypted only).

## Usage

```
./encdec.py <e|d> filename.bin > raw.bin
```

Example decrypt:

```
./encdec.py d k5_26_encrypted.bin > k5_26_raw.bin
```

Example encrypt:

```
./encdec.py e k5_26_raw.bin > k5_26_encrypted.bin
```

## Links

[Firmware versions](https://drive.google.com/drive/folders/1GXWjiW0geMiAnVxWpm5rf6OUlXT43ZzB?usp=share_link)

[Windows software](https://drive.google.com/drive/folders/1rpQGXZpt3b9hQrC_2rx-hFjnlO8SdsRb?usp=sharing)

[About Quansheng UV-K5 usage](https://mikhail-yudin.ru/notes/quansheng-uv-k5-opyt-raboty/) (Russian)
