# Vexa Viral — AI Entertainment Reels Automation

ระบบนี้รีแบรนด์จาก **Dream Home Vexa** เป็น **Vexa Viral** (ชื่อเสนอสำหรับเพจ; การเปลี่ยนชื่อ Facebook จริงต้องทำใน Page Settings) ใช้ GitHub Actions สร้างวิดีโอความบันเทิงภาษาอังกฤษวันละหนึ่งคลิป

## 1. แนวคอนเทนต์
หมุนเวียน 30 หัวข้อที่เขียนขึ้นเองใน `scripts/main.py` ระหว่าง Funny Animals, Absurd Comedy, AI Memes และ Comedy Stories: มี setup / plot twist / punchline พร้อมภาพสามฉากและเสียงพากย์ AI

**ข้อจำกัด:** ภาพเป็น AI stills + FFmpeg zoom/pan ไม่ใช่วิดีโอที่ตัวละครขยับหรือ lip-sync จริง การสร้าง true video animation ต้องเพิ่ม Video API ที่คิดค่าใช้จ่ายแยกต่างหาก

## 2. โหมดปลอดภัย
- Facebook Auto Publish ถูก **บังคับปิด** ในไฟล์ `.github/workflows/daily.yml` ด้วย `ENABLE_PUBLISH: 'false'` และ `FB_LIVE_APPROVED: 'false'`
- ระบบมี `GEMINI_API_KEY` และ `OPENAI_API_KEY` ซึ่งต้องเก็บเป็น **GitHub Actions Secrets** เท่านั้น ห้าม commit หรือโพสต์ key
- `MONTHLY_SPEND_CAP_USD` ค่าเริ่มต้น **5.00** เป็นการรวมประมาณการในไฟล์ state ไม่ใช่วงเงินจริงจาก OpenAI และไม่ได้รับประกันจำนวนคลิปทุกวันเมื่อโควตาหมด
- โปรดตั้ง Usage/Budget alerts ใน OpenAI Platform และตรวจบิลจริงเสมอ
- Daily schedule เป็น 10:17 UTC = 17:17 ไทย (GitHub อาจเริ่มช้า)

## 3. ทดสอบโดยไม่ใช้เงิน
1. เปิด GitHub > Actions > **Vexa Viral AI Entertainment Reels**
2. คลิก Run workflow เลือก `main`
3. เลือก **dry_run = true** (ค่าเริ่มต้น) แล้ว Run workflow
4. งานควรมี artifact `preview_plan.json`, `narration.txt`, `caption.txt`; **ไม่มี MP4** เพราะไม่เรียก Image/TTS API
5. ตรวจว่าแคปชันและ hashtag เป็นแนว comedy และ log ไม่มีคำสั่งเผยแพร่ Facebook

## 4. ทดลองสร้าง MP4 จริง
หลังตรวจเครดิตและงบแล้ว ให้ Run workflow โดยตั้ง `dry_run = false` เพียงครั้งเดียว ระบบจะใช้ Image API และ TTS ซึ่งมีค่าใช้จ่าย ตรวจ artifact `reel.mp4`, ภาพ และเสียงก่อนใช้จริง

## 5. เปลี่ยนชื่อ Facebook Page
ไปที่ Facebook Page > Settings > Page setup หรือ Page information > Name (เมนูอาจต่างกันตามเวอร์ชัน)
เสนอชื่อ **Vexa Viral** ตรวจสอบชื่อซ้ำและ @username ก่อนยืนยัน และเปลี่ยนหมวดหมู่เป็น Digital Creator หรือ Entertainment ตามรายการที่มี
Bio: "Funny AI stories, absurd memes, talking animals and surprising comedy twists. Original English entertainment, every day."
การเปลี่ยนชื่อเพจต้องใช้สิทธิ์ผู้ดูแล Facebook และอาจต้องรอ Meta อนุมัติ ไม่ได้เกิดขึ้นโดยการเปลี่ยนชื่อใน GitHub

## 6. Facebook Reels API
ยังไม่เชื่อม/ยืนยัน Page Token และสิทธิ์ Meta: ห้ามเปิด auto-publish ก่อนตรวจสิทธิ์ Page, ทดสอบ upload, ตรวจสถานะ processed/published และจัดการ duplicate/retries
ตัวแปร `FB_PAGE_ID` และ `FB_PAGE_ACCESS_TOKEN` หากสร้างต้องอยู่ใน Secrets เท่านั้น
โค้ดมีการเรียก start/upload/finish แต่ไม่ได้ยืนยันว่า Meta เผยแพร่สำเร็จจนกว่าจะตรวจหน้าเพจจริง

## 7. ต้นทุนที่ต้องทราบ
ค่า `IMAGE_ESTIMATE_USD` และ `VOICE_ESTIMATE_USD` เป็นตัวเลขสมมติอาจต่ำกว่าหรือสูงกว่าค่าจริง โดย default 3 ภาพ x $0.12 + voice $0.05 = $0.41/คลิป $5 เดือนหนึ่งจึงรองรับการประมาณค่าเพียง ~12 คลิป ไม่รับประกันวันละคลิปครบเดือน; ต้องเปลี่ยนงบ/จำนวนภาพตามค่าใช้งานจริงหรือใช้โมเดลราคาต่ำกว่า

Repo: https://github.com/suntornsaeyo-glitch/dream-home-vexa-reels
