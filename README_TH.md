# Vexa Viral Thailand — Shopee Affiliate

ระบบสร้างคลิปตลกและคอนเทนต์ Affiliate ภาษาไทย วันละหนึ่งคลิปบน GitHub Actions (ประมาณ 17:17 เวลาไทย อาจล่าช้า) โดยใช้ภาพ AI แบบซูม/แพน เสียงพากย์ TTS ภาษาไทย และ MP4 1080×1920 ไม่ใช่วิดีโอ AI ที่ตัวละครเคลื่อนไหวจริงหรือระบบซับไตเติลตามเสียงแบบอัตโนมัติ

## การเพิ่มสินค้า
บัญชี Shopee Affiliate ของเจ้าของได้รับอนุมัติแล้ว แต่ระบบยังไม่ได้รับสิทธิ์ Shopee Open API และยังไม่มีลิงก์สินค้าจริง

แก้ data/affiliate_products.json โดยเพิ่มรายการที่ได้รับอนุญาตใน products:
- id: รหัสสินค้าภายในที่ไม่ซ้ำ
- title: ชื่อสินค้าจริงภาษาไทย
- category: home_gadgets, pet_gadgets, kitchen_gadgets, desk_gadgets, funny_gifts หรือ tech_accessories
- program: Shopee Thailand
- affiliate_url: ลิงก์ HTTPS จากแดชบอร์ด Affiliate ของเจ้าของเท่านั้น
- visual_description: คำอธิบายประเภทอุปกรณ์ทั่วไปภาษาไทย
- usage_rights_confirmed: true เมื่อตรวจสิทธิ์ใช้ข้อมูลและสื่อแล้ว
- approved: true เมื่อเจ้าของตรวจสอบสินค้าและลิงก์แล้ว

ระบบตรวจรูปแบบและโดเมน Shopee ไม่ได้ตรวจปลายทางสต็อก ราคา การติดตามค่าคอมมิชชัน หรือสิทธิ์บัญชีแบบสด ต้องยืนยันด้วยแดชบอร์ด Shopee จริง ห้ามใส่ API key หรือ token ในไฟล์สาธารณะ
หากไม่มีสินค้าที่อนุมัติ จะสร้างคลิปตลกทั่วไปโดยไม่มีลิงก์ปลอม เมื่อมีสินค้า จะหมุนเวียนวัน Affiliate 70% และตลกทั่วไป 30%

## การทดสอบ
Actions > Vexa Viral Thailand - Shopee Affiliate > Run workflow
- dry_run=true: ทดสอบบทไทย แคปชันและแผน ไม่เรียก API เสียเงิน ไม่สร้าง MP4
- dry_run=false (ค่าเริ่มต้น): สร้าง MP4 ด้วย API จริง มีค่าใช้จ่าย
- allow_regenerate=false (ค่าเริ่มต้น): ไม่สร้างซ้ำหลังบันทึกความสำเร็จในวันที่เดียวกัน ใช้ true เฉพาะต้องการสร้างซ้ำและยอมรับค่าใช้จ่าย
- Workflow ตรวจ syntax และ unit tests ก่อนเรียก API
- Artifacts: reel.mp4, voice.mp3, caption.txt, narration.txt, metadata.json
- เสียงไทยใช้ OpenAI TTS พร้อมคำสั่งออกเสียงธรรมชาติ ไม่ย้อนกลับไปใช้เสียงอังกฤษเมื่อผิดพลาด

## งบ
เก็บประมาณการเดิมใน data/state.json; default $5/เดือน, 3 ภาพ x $0.12 + เสียง $0.05 + Gemini $0.01 เมื่อมี key = $0.42 ต่อคลิปตามสมมติฐาน (30 คลิป $12.60)
ตรวจงบก่อนเรียก API และบันทึกก่อนแต่ละ call ตัวเลขนี้ไม่ใช่ใบแจ้งหนี้หรือ hard limit ของผู้ให้บริการ และหาก GitHub commit ล้มเหลวอาจบันทึกไม่ครบ ต้องตรวจ billing จริง
ไม่เพิ่มเพดานงบโดยอัตโนมัติ

## Facebook
ENABLE_PUBLISH และ FB_LIVE_APPROVED ถูกบังคับ false ใน workflow แม้ตั้ง variables ไว้แล้ว
ยังไม่เชื่อมเพจและยังไม่ทดสอบเผยแพร่จริง เตรียม FB_PAGE_ID และ FB_PAGE_ACCESS_TOKEN ผ่าน GitHub Secrets เท่านั้น
ก่อนเปิดเผยแพร่ต้องตรวจสิทธิ์ Meta, การติดป้ายความสัมพันธ์เชิงพาณิชย์ตามกฎที่ใช้, ลิงก์ Affiliate และระบบติดแท็กสินค้า Shopee (ยังไม่ได้เชื่อม native product tags)
คลิปและ caption ระบุเรื่องสมมติจาก AI ไม่ใช่รีวิวหรือการทดสอบสินค้าจริง ไม่แต่งราคา สรรพคุณ หรือผลทดลอง
