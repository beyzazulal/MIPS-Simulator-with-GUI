
![Uploading 16-bit pipelined mips CPU tasarımııı.png…]()



# 16-bit RISC Pipelined Processor Design

[cite_start]Bu proje, **MIPS mimarisinden** esinlenerek tasarlanmış, 16-bit veri yoluna sahip ve 5 aşamalı pipeline (bor hattı) yapısını kullanan bir RISC işlemci tasarımıdır[cite: 1, 5, 11]. [cite_start]Bilgisayar Mimarisi dersi kapsamında geliştirilen bu işlemci, veri ve kontrol hazard'larını (çakışmalarını) yönetebilen gelişmiş bir mimariye sahiptir[cite: 2, 33, 34].

## 🚀 Temel Özellikler

  * [cite_start]**Mimari:** 16-bit RISC[cite: 1, 5].
  * [cite_start]**Veri Yolu (Data Path):** 16-bit[cite: 11].
  * [cite_start]**Pipeline Yapısı:** 5 Aşamalı (IF, ID, EX, MEM, WB)[cite: 10, 26].
  * [cite_start]**Kaydediciler:** 8 adet genel amaçlı register (R0-R7)[cite: 9].
  * [cite_start]**Bellek:** \* 512 Byte Instruction Memory (Komut Belleği)[cite: 12, 38].
      * [cite_start]512 Byte Data Memory (Veri Belleği)[cite: 13, 39].
  * [cite_start]**Hazard Yönetimi:** Forwarding Unit (İleri Besleme Birimi) ve Stall/Flush mekanizmaları ile veri ve kontrol hazard çözümü[cite: 33, 34, 35].

-----

## 🛠 Mimari Diyagramı

İşlemcinin veri yolu ve kontrol ünitelerinin yerleşimini gösteren blok diyagram aşağıdadır:

*(Not: Dosya adını GitHub'daki görsel adıyla eşleştirdiğinden emin ol.)*

-----

## 📜 Desteklenen Komut Seti (ISA)

[cite_start]İşlemci, temel aritmetik, mantıksal, bellek erişim ve kontrol akışı komutlarını destekler[cite: 19]:

| Tip | Komutlar | Açıklama |
| :--- | :--- | :--- |
| **Aritmetik/Mantık** | `add`, `sub`, `and`, `or`, `slt` | [cite_start]Kaydedici işlemleri[cite: 19]. |
| **Kaydırma** | `sll`, `srl` | [cite_start]Mantıksal sola/sağa kaydırma[cite: 19]. |
| **Immediate** | `addi` | [cite_start]Sabit değer ile toplama[cite: 19]. |
| **Bellek** | `lw`, `sw` | [cite_start]Kelime yükleme ve saklama[cite: 19]. |
| **Dallanma** | `beq`, `bne` | [cite_start]Eşitlik durumuna göre dallanma[cite: 19]. |
| **Atlama** | `j`, `jal`, `jr` | [cite_start]Doğrudan, bağlantılı ve kaydedici tabanlı atlama[cite: 19]. |

-----

## 🏗 Pipeline Aşamaları

[cite_start]İşlemci her komutu 5 ana aşamada işler[cite: 26]:

1.  [cite_start]**IF (Instruction Fetch):** Komutun bellekten getirilmesi[cite: 27].
2.  [cite_start]**ID (Instruction Decode):** Komutun çözülmesi ve register okuma[cite: 28].
3.  [cite_start]**EX (Execute):** ALU üzerinde aritmetik işlemlerin yapılması[cite: 29].
4.  [cite_start]**MEM (Memory Access):** Veri belleğine erişim[cite: 30].
5.  [cite_start]**WB (Write Back):** Sonucun register dosyasına yazılması[cite: 31].

-----

## 💻 Örnek Assembly Kodu

[cite_start]Aşağıdaki kod bloğu, işlemcinin komutları nasıl işlediğine dair bir örnek sunmaktadır[cite: 85]:

```assembly
addi R0, R0, 5    # R0 = 5
addi R1, R1, 8    # R1 = 8
jal func          # func etiketine atla ve geri dönüş adresini sakla
nop               # Boş işlem (delay slot)

func: 
    addi R3, R3, 20
    sw R0, 0(R1)   # R0 değerini R1'deki adrese sakla
    lw R1, 0(R0)   # R0'daki adresten R1'e değer yükle
```

-----

## 📂 Proje Aşamaları

Proje toplam üç ana fazdan oluşmaktadır:

  * [cite_start]**Phase 1:** İşlemci Tasarımı ve ISA planlaması[cite: 43].
  * [cite_start]**Phase 2:** Yüksek seviyeli dilde (C++, Python vb.) işlemci simülatörü geliştirme[cite: 52].
  * [cite_start]**Phase 3:** Verilog HDL ile donanım implementasyonu ve test bench doğrulaması[cite: 61, 63].
  * [cite_start]**Bonus:** FPGA üzerinde fiziksel uygulama[cite: 69, 71].

-----

### Proje Bilgileri

  * [cite_start]**Dönem:** 2024-2025 Güz Dönemi[cite: 3].
  * [cite_start]**Ders:** Bilgisayar Mimarisi (Computer Architecture)[cite: 2].


