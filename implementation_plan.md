# Haqiqiy Email (Gmail SMTP) tizimini ulash va Sozlash

Hozirgi vaqtda barcha xabarlar faqat terminalda ko'rinmoqda. Uni haqiqiy email manzilingizga yuboradigan qilish uchun loyihani Gmail SMTP serveriga bog'laymiz.

## ⚠️ User Review Required

Ushbu jarayon uchun sizdan:
1. **Gmail manzilingiz** (masalan: `example@gmail.com`).
2. **Google App Password** (16 xonali maxsus kod).

> [!IMPORTANT]
> Oddiy Gmail parolingiz bu erda ishlamaydi. Siz Google hisobingizdan maxsus "App Password" olishingiz kerak. Uni qanday olish bo'yicha yo'riqnomani quyida keltiraman.

---

## Taklif qilinayotgan o'zgarishlar

### 1. Xavfsizlikni ta'minlash (`.env` fayli)
Parollarni kod ichida yozish xavfli bo'lgani uchun, loyihaning ildiz papkasida `.env` faylini yaratamiz va `django-environ` yordamida sozlaymiz.

### 2. `settings.py` tahriri
- `EMAIL_BACKEND`ni terminaldan **SMTP**ga o'zgartiramiz.
- Gmail uchun kerakli port va xavfsizlik sozlamalarini (`EMAIL_USE_TLS`, `EMAIL_HOST`, va h.k.) kiritamiz.

---

## 🛠 Google App Password olish tartibi (Yo'riqnoma):
1. Google hisobingizga kiring -> **Security** (Xavfsizlik) bo'limiga o'ting.
2. **2-Step Verification** (2 bosqichli tekshiruv) yoqilganligiga ishonch hosil qiling.
3. Sahifaning eng pastiga tushib **App Passwords** bo'limini qidiring (yoki qidiruvga yozing).
4. "App name" degan joyga `Vantage Tests` deb yozing va **Create** tugmasini bosing.
5. Chiqqan **16 xonali kodni** (masalan: `abcd efgh ijkl mnop`) nusxalab oling.

---

## Ochiq Savollar
- Gmail manzilingiz va o'sha 16 xonali kodni menga yubora olasizmi? (Bunda xavfsizlikni o'zingiz ta'minlashingiz uchun men sizga `.env` fayliga qayerga yozishni ko'rsatib ham bera olaman).

Ushbu reja ma'qul bo'lsa, sozlashni boshlayman!
