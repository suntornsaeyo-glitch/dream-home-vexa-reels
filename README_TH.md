# Dream Home Vexa — Free-first Facebook Reels Automation

ชุดตั้งต้นที่ทำงานบน GitHub Actions โดยไม่ต้องเปิดคอมพิวเตอร์ สามารถสร้างวิดีโอ 9:16 30 วินาทีภาษาอังกฤษทุกวันจากภาพบ้าน **กราฟิกที่วาดด้วยโค้ด** และเสียงสังเคราะห์แบบออฟไลน์ ไม่ใช่วิดีโอ photorealistic AI.

## 1. ทำงานฟรีอะไรได้บ้าง
- GitHub Actions runner ฟรีตามเงื่อนไข GitHub โดยเฉพาะ public repository; private repo ต้องตรวจโควตา Actions ของบัญชี
- สร้างภาพสถาปัตยกรรมต้นฉบับ 5 เฟรมด้วย Pillow ฟรี
- สร้างเสียงภาษาอังกฤษด้วย espeak-ng ฟรี (เสียงหุ่นยนต์ ไม่ใช่เสียงพรีเมียม)
- ประกอบ MP4 ด้วย FFmpeg ฟรี
- เลือกเปิด Gemini API สำหรับร่างสคริปต์ใหม่ได้ หากบัญชี/ภูมิภาคมีโควตาฟรี รุ่น gemini-2.5-flash-lite; ถ้าไม่มีจะใช้สคริปต์สำรอง
- การโพสต์ Facebook จะไม่ทำงานจนกว่าจะได้ Page token/permissions และตั้ง ENABLE_PUBLISH=true

## 2. ติดตั้ง
1. สร้าง GitHub repository เช่น `dream-home-vexa-reels` ตั้ง Private ถ้าไม่ต้องการเผยโค้ด (ตรวจโควตา Actions)
2. อัปโหลดทุกไฟล์และโฟลเดอร์นี้ไปที่ root ของ repository; ต้องรวม `.github/workflows/daily.yml`
3. GitHub > Settings > Secrets and variables > Actions > Secrets เพิ่ม `GEMINI_API_KEY` (ถ้ามี), `FB_PAGE_ID`, `FB_PAGE_ACCESS_TOKEN` (หลังได้รับสิทธิ์)
4. GitHub > Settings > Secrets and variables > Actions > Variables สร้าง `ENABLE_PUBLISH=false`
5. GitHub > Actions > Dream Home Vexa Daily Reel > Run workflow
6. ดาวน์โหลดไฟล์ reel.mp4 จาก Artifacts ด้านล่างของงาน เพื่อดูคุณภาพ
7. เมื่อได้รับสิทธิ์เผยแพร่ของ Meta และทดสอบด้วยเพจจริงแล้ว เปลี่ยน `ENABLE_PUBLISH=true`

## 3. ตั้งเวลา
Workflow เริ่มเวลา 10:17 UTC = 17:17 ในไทยทุกวัน เพื่อพยายามสร้างคลิปก่อน 18:00 แต่ GitHub Actions **ไม่รับประกันเริ่มตรงเวลา** และโพสต์ทัน 18:00 เสมอ ถ้าต้องตรงเวลาให้เพิ่มการตั้งเวลาโพสต์ด้วย Meta หลังทดสอบ API.

## 4. การตั้ง Meta
- ใช้ Facebook Page ไม่ใช่โปรไฟล์ส่วนตัว
- สร้าง Meta Developer App และตั้งค่า Facebook Login / Page permissions ตามข้อกำหนดปัจจุบัน
- ขอสิทธิ์ที่เกี่ยวข้อง เช่น pages_show_list, pages_manage_posts, pages_read_engagement และการอนุมัติที่จำเป็นตามสถานะแอป
- รับ Page ID และ Page Access Token จากขั้นตอน Facebook Login และตรวจสิทธิ์กับ Graph API Explorer
- ใช้ secrets เท่านั้น ห้ามใส่ token ใน repo, screenshot หรือใน ChatGPT
- ทดลอง API 3 ช่วง START -> upload binary -> FINISH / PUBLISHED ตามเอกสาร Meta
- เช็กสถานะ processing และ URL คลิปบนเพจจริง เพราะการตอบกลับจาก FINISH ไม่รับประกันว่าคลิปมองเห็นแล้ว

## 5. งบและความเสี่ยง
- **ห้ามเปิด Billing ใน AI provider ถ้าอยากจำกัดที่ 0 บาท**
- ติดตาม Google AI Studio API quotas และ GitHub Billing / Usage ก่อนและหลังทดสอบ
- Gemini อาจตอบ 429/403; ระบบจะใช้บทสำรอง โดยไม่พยายามซื้อโควตา
- หากโพสต์สำเร็จแต่ `git push` state ไม่สำเร็จ อาจโพสต์ซ้ำได้ในการรันใหม่ ควรตรวจเพจก่อน retry; ระบบนี้เป็น starter ไม่ใช่ production-grade idempotency
- ภาพสไตล์กราฟิก; หากต้องการ AI photorealistic 100% ต้องมีบริการ image-generation API และงบ/เครดิตเพียงพอ
- ไม่รับประกันผ่าน Facebook Monetization; ตรวจความเป็นต้นฉบับ คุณภาพ และเนื้อหาก่อนเปิดโพสต์อัตโนมัติ
- รหัสนี้ทำให้โพสต์ทันทีหลังสร้างในงาน schedule ไม่ใช่รอให้ถึงเวลา 18:00 แน่นอน

## 6. ปรับแต่ง
- แก้ 30 หัวข้อใน `TOPICS` ใน `scripts/main.py`
- แก้ข้อความ/ภาพโดยปรับ `scene()`, เสียง `espeak-ng -s`, และความละเอียด FFmpeg
- ต้องการเสียงดีขึ้น เชื่อม TTS provider ที่มี license สำหรับ commercial use และคิดค่าใช้จ่ายตามจริง
