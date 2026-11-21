# Vexa Viral — AI Reels + Facebook Affiliate

**สถานะ:** โค้ดบน GitHub อัปเดตแล้ว แต่ Facebook Auto Publish ยังถูกล็อกเป็น `false` ใน GitHub Actions และยังไม่ได้ยืนยันการโพสต์จริง

## เป้าหมาย
- ภาษาอังกฤษ วันละ 1 MP4 แนวตั้ง 1080x1920 เมื่อ API สำเร็จและมีงบประมาณพอ
- ภาพ AI 3 ฉาก + เสียงบรรยาย AI + Caption + Hashtags
- 70% Affiliate entertainment / 30% viral comedy เมื่อมีสินค้าที่อนุมัติแล้ว
- ถ้า `data/affiliate_products.json` ยังไม่มีสินค้าที่ตรวจสอบผ่าน จะสร้าง **คลิปตลกปกติ** โดยไม่มีลิงก์ Affiliate หรือตัวเลขคอมมิชชันที่แต่งขึ้น
- ภาพเคลื่อนไหวแบบซูมและแพนจากภาพนิ่ง AI ไม่ใช่ตัวละครพูดขยับปากหรือ full AI-video

## 1. เพิ่มสินค้า Affiliate ที่ได้รับอนุมัติ
เปิด `data/affiliate_products.json` แล้วเพิ่มรายการที่ **มีลิงก์จากบัญชี Affiliate ของคุณเอง** ตัวอย่างโครงสร้าง (เป็นตัวอย่างช่องข้อมูล ไม่ใช่ลิงก์ใช้งานจริง):

```json
{
  "products": [
    {
      "id": "your-unique-product-id",
      "title": "Actual Product Listing Title",
      "category": "pet_gadgets",
      "affiliate_url": "https://YOUR-REAL-AFFILIATE-LINK",
      "program": "Your Affiliate Program",
      "visual_description": "generic pet feeding gadget as a fictional prop",
      "usage_rights_confirmed": true,
      "approved": true
    }
  ]
}
```

หมวดหมู่ที่อนุญาต: `home_gadgets`, `pet_gadgets`, `kitchen_gadgets`, `desk_gadgets`, `funny_gifts`, `tech_accessories`

ห้ามใช้ตัวอย่างลิงก์ด้านบนจริง, ห้ามใส่ลิงก์ที่ไม่ได้รับจากโปรแกรม Affiliate หรือสินค้าที่ไม่ได้ตรวจสอบเงื่อนไขโปรโมต
ค่า `usage_rights_confirmed` หมายถึงคุณยืนยันว่ามีสิทธิ์ใช้ข้อมูล/สื่อประกอบตามที่โปรแกรมอนุญาต ไม่ใช่การซื้อสิทธิ์จากโค้ดนี้
**เมื่อไม่มีสินค้า approved ที่มี URL HTTPS ถูกต้อง ระบบจะไม่แต่งลิงก์ให้เอง**

## 2. ขั้นตอนสร้างคลิป
1. GitHub Actions เริ่มราว 17:17 เวลาไทย (อาจล่าช้าหรือรันไม่ตรงเวลา)
2. เลือกหัวข้อ 30 ตอนหมุนเวียน; หากเป็นวัน Affiliate และมีสินค้าที่ผ่าน validation เลือกรายการสินค้า
3. Gemini เขียนบทภาษาอังกฤษให้เป็นมุกตลก หากไม่ตอบจะใช้บทสำรอง
4. OpenAI Image API สร้าง 3 ภาพ AI, TTS สร้างเสียงตลกอังกฤษ, FFmpeg ทำคลิป `reel.mp4` (ไม่ใช่ generative moving video)
5. บันทึก `caption.txt`, `narration.txt`, `metadata.json` และ MP4 ใน Artifacts 7 วัน
6. **ไม่โพสต์ Facebook:** ทั้ง `ENABLE_PUBLISH` และ `FB_LIVE_APPROVED` ถูกบังคับ `false` ใน Workflow

## 3. การทดสอบ
เปิด GitHub Actions → `Vexa Viral AI Reels + Affiliate` → Run workflow
- `dry_run = true`: ไม่เสียค่า Image/TTS API สร้าง `preview_plan.json`, caption, narration แต่ยังไม่มี MP4
- `dry_run = false`: ทดสอบ MP4 จริง (มีค่าใช้จ่าย) และยัง **ไม่โพสต์ Facebook**
- Workflow ตรวจ `python -m py_compile` และรัน `tests/test_affiliate.py` ก่อนใช้ API
- หากมีข้อผิดพลาด ดู Logs และตรวจงบก่อนรันซ้ำ เพราะอาจคิดค่า API ไปแล้วบางส่วน

## 4. งบประมาณ
ค่าเริ่มต้น `MONTHLY_SPEND_CAP_USD=5.00`, `IMAGE_ESTIMATE_USD=0.12`, `VOICE_ESTIMATE_USD=0.05`, `IMAGES_PER_REEL=3`
ตาม **การประมาณในโค้ด** = `3×0.12+0.05 = $0.41` ต่อคลิป, 30 คลิป = `$12.30` ต่อเดือน โดยไม่รวมต้นทุนอื่นและ **ไม่ใช่ราคาปัจจุบันที่รับประกัน**.
ดังนั้น $5 ไม่พอทำ 30 คลิปจริงตามประมาณการ; ระบบจะหยุดแทนที่จะเพิ่มงบเอง และค่าใช้จ่ายจริงจาก API อาจต่างจากประมาณมาก โปรดตั้ง Provider Budget/Alerts แยกต่างหาก
`data/state.json` เก็บประวัติประมาณการเดือนปัจจุบัน; การรันซ้ำและข้อผิดพลาดของ `git push` อาจทำให้ยอดประมาณการไม่ครบถ้วน ไม่ใช่ hard spending limit ของ OpenAI

## 5. ข้อกำหนด Affiliate / Meta
- เนื้อหา Affiliate ต้องเปิดเผยว่าได้ค่าคอมมิชชัน และใช้ Paid partnership / branded content labeling ของ Meta เมื่อกฎและเครื่องมือบังคับ
- โค้ดใส่ disclosure ใน Caption แต่ **การใส่ Caption อย่างเดียวไม่ได้แทนระบบติดป้าย Paid partnership บน Facebook** จำเป็นต้องตรวจสิทธิ์/วิธีติดป้ายก่อนโพสต์จริง
- หลีกเลี่ยงการแสดงภาพ AI เป็นผลทดสอบของสินค้าจริง การรับรองสินค้า หรือคุณสมบัติที่ยังไม่ตรวจสอบ
- การทำ Facebook Native Affiliate tagging อาจต้องผูก Affiliate catalog/Brand ให้ Meta อนุญาต ระบบนี้เตรียมลิงก์ใน caption เท่านั้น ยังไม่ได้ทำ native commerce tagging
- ห้ามเผยแพร่ Facebook อัตโนมัติก่อนตรวจ Meta Permissions, Product/Link Compliance, video processing, page and URL, duplicate guard และแสดง label ถูกต้อง

## 6. ขั้นตอนต่อไป
1. เพิ่มสินค้า Affiliate จริง 3–5 รายการที่คุณได้รับสิทธิ์โปรโมต
2. ทดสอบ `dry_run=true` และตรวจ Caption
3. ทดสอบ `dry_run=false` 1 ครั้งเพื่อดูภาพและเสียง MP4
4. ส่งผลลัพธ์มาปรับแนวสคริปต์และความต่อเนื่องของฉาก
5. เชื่อม Meta App/Page Token เมื่อคุณพร้อม แล้วตรวจ disclosure/paid partnership ก่อนเปิด live publish

Repository: https://github.com/suntornsaeyo-glitch/dream-home-vexa-reels
