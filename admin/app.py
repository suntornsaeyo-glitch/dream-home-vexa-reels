import sys, json, datetime as dt, io, math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import streamlit as st
import pandas as pd
from admin.catalog import CATEGORIES, normalize, import_table, merge, score
from admin.github_client import Repo
from affiliate import valid_product
from settings import validate_settings

st.set_page_config(page_title='Vexa Viral | Smart Product Manager V2',page_icon='🛒',layout='wide')
repo=Repo()
st.title('Vexa Viral — Smart Product Manager V2')
st.caption('Shopee Thailand • บริหารสินค้าด้วยตนเอง ไม่ใช้ Shopee Open API • Facebook ยังไม่เผยแพร่')
try:
    info=repo.info()
    raw,sha=repo.read('data/affiliate_products.json')
    budget,bsha=repo.read('data/settings.json')
    state,_=repo.read('data/state.json')
    budget=validate_settings(budget)
except Exception as e:
    st.error(str(e));st.stop()
if not repo.token:
    st.warning('อ่านข้อมูลได้อย่างเดียว กรุณาเปิดใน GitHub Codespaces เพื่อบันทึกและสั่งสร้างคลิป')
if not info.get('private'):
    st.warning('Repository เป็นสาธารณะ: ค่าตั้งค่า รายการสินค้า ลิงก์ และประวัติการผลิตที่บันทึกลง GitHub จะเปิดเผยได้ ห้ามใส่ข้อมูลส่วนตัวหรือรหัสลับ')
    public_ok=st.sidebar.checkbox('ยอมรับว่ารายการสินค้าและค่าตั้งค่าที่บันทึกจะเปิดเผยใน Repository สาธารณะ')
else: public_ok=True
can_write=bool(repo.token and public_ok)
if 'catalog' not in st.session_state or 'catalog_sha' not in st.session_state:
    st.session_state.catalog=raw.get('products',[])
    st.session_state.catalog_sha=sha
if st.sidebar.button('โหลดข้อมูลจาก GitHub ใหม่'):
    st.session_state.catalog=raw.get('products',[])
    st.session_state.catalog_sha=sha
    st.rerun()
products=st.session_state.catalog
approved=[p for p in products if valid_product(p)]
month=dt.datetime.now(dt.timezone(dt.timedelta(hours=7))).strftime('%Y-%m')
spent=float(state.get('spent_estimate_by_month',{}).get(month,0))
estimate=budget['images_per_reel']*budget['image_estimate_usd']+budget['voice_estimate_usd']+.01
nav=st.sidebar.radio('เมนู',['ภาพรวม','รายการสินค้า','นำเข้าสินค้า','งบประมาณ','ผลิตคลิป MP4'])
st.sidebar.success('Facebook: ปิดการเผยแพร่จริง')
st.sidebar.caption('ตัวเลขจากไฟล์ที่บันทึกไว้ ไม่ใช่ข้อมูลสดจาก Shopee หรือยอดเรียกเก็บจริง')
def save_catalog():
    if not can_write:
        st.error('ยังไม่ได้อนุญาตบันทึกข้อมูล');return
    if any(p.get('approved') and not valid_product(p) for p in st.session_state.catalog):
        st.error('สินค้าที่เปิดโปรโมตต้องมีชื่อ หมวดหมู่ ลิงก์ Shopee HTTPS และยืนยันสิทธิ์ครบ');return
    try:
        repo.write('data/affiliate_products.json',{'products':st.session_state.catalog},st.session_state.catalog_sha)
        _,newsha=repo.read('data/affiliate_products.json')
        st.session_state.catalog_sha=newsha
        st.success('บันทึกข้อมูลเข้าสู่ GitHub แล้ว')
    except Exception as e:st.error(str(e))
def catalog_table(rows):
    return pd.DataFrame([{'สินค้า':p.get('title'),'หมวดหมู่':CATEGORIES.get(p.get('category'),'อื่นๆ'),'ราคา (บาท)':p.get('price_thb',0),'คอมมิชชัน (%)':p.get('commission_pct',0),'ประมาณการต่อออร์เดอร์ (บาท)':round(score(p),2),'พร้อมโปรโมต':valid_product(p)} for p in rows])
if nav=='ภาพรวม':
    a,b,c,d=st.columns(4)
    a.metric('สินค้าทั้งหมด',len(products))
    b.metric('พร้อมโปรโมต',len(approved))
    c.metric('สร้างคลิปสำเร็จเดือนนี้',sum(k.startswith(month) for k in state.get('generated',{})))
    d.metric('งบใช้ไปโดยประมาณ',f'${spent:.2f}')
    st.progress(min(1,max(0,spent/budget['monthly_cap_usd'])) if budget['monthly_cap_usd'] else 0,text='สัดส่วนงบประมาณเดือนนี้')
    st.caption('เพดานตามไฟล์ตั้งค่า; repository variables เดิมอาจจำกัดเพิ่ม และยอดจริงจากผู้ให้บริการอาจแตกต่าง')
    st.subheader('จัดอันดับสินค้าตามค่าคอมมิชชันต่อคำสั่งซื้อ')
    st.dataframe(catalog_table(sorted(approved,key=score,reverse=True)),hide_index=True,use_container_width=True)
    st.subheader('ประวัติผลิตคลิป')
    st.dataframe(pd.DataFrame([{'วันที่':k,'เรื่อง':v.get('title'),'รหัสสินค้า':v.get('affiliate_id')} for k,v in sorted(state.get('generated',{}).items(),reverse=True)]),hide_index=True,use_container_width=True)
    st.subheader('ประเมินกำไรจากรายงาน Shopee (ไม่บันทึก)')
    x,y=st.columns(2)
    rev=x.number_input('ค่าคอมมิชชันที่ยืนยันแล้ว (บาท)',min_value=0.0,value=0.0)
    fx=y.number_input('อัตราแลกเปลี่ยนบาทต่อดอลลาร์สำหรับคำนวณ',min_value=0.0,value=35.0)
    st.metric('กำไรประมาณการก่อนภาษีและต้นทุนอื่น',f'{rev-spent*fx:,.2f} บาท')
elif nav=='รายการสินค้า':
    st.subheader('เพิ่มสินค้าใหม่')
    with st.form('new_product'):
        title=st.text_input('ชื่อสินค้าจริง')
        url=st.text_input('ลิงก์ Affiliate จากบัญชี Shopee ของคุณ')
        cat=st.selectbox('หมวดหมู่',list(CATEGORIES),format_func=CATEGORIES.get)
        desc=st.text_input('คำอธิบายประเภทสินค้า')
        a,b=st.columns(2)
        price=a.number_input('ราคา (บาท)',min_value=0.0)
        commission=b.number_input('คอมมิชชัน (%)',min_value=0.0,max_value=100.0)
        add=st.form_submit_button('เพิ่มรายการฉบับร่าง')
    if add:
        item=normalize(dict(title=title,affiliate_url=url,category=cat,visual_description=desc,price_thb=price,commission_pct=commission))
        updated,n,_=merge(products,[item])
        if n:st.session_state.catalog=updated;st.rerun()
        else:st.error('ชื่อ/ลิงก์ไม่ครบหรือรายการซ้ำ')
    st.subheader('แก้ไขและอนุมัติสินค้า')
    if products:
        ids={p['id']:p for p in products}
        chosen=st.selectbox('เลือกรายการ',list(ids),format_func=lambda k:ids[k].get('title',''))
        p=ids[chosen]
        with st.form('edit_'+chosen):
            title=st.text_input('ชื่อสินค้า',p.get('title',''))
            url=st.text_input('ลิงก์ Affiliate',p.get('affiliate_url',''))
            cats=list(CATEGORIES);cat=st.selectbox('หมวดหมู่',cats,index=cats.index(p['category']) if p.get('category') in cats else 0,format_func=CATEGORIES.get)
            desc=st.text_input('ประเภทสินค้าเพื่อเขียนเรื่อง',p.get('visual_description',''))
            price=st.number_input('ราคาที่ตรวจแล้ว (บาท)',min_value=0.0,value=float(p.get('price_thb',0)))
            pct=st.number_input('คอมมิชชันที่ตรวจแล้ว (%)',min_value=0.0,max_value=100.0,value=float(p.get('commission_pct',0)))
            rights=st.checkbox('ยืนยันสิทธิ์ใช้ข้อมูล/สื่อ และตรวจลิงก์แล้ว',bool(p.get('usage_rights_confirmed')))
            enabled=st.checkbox('เปิดโปรโมต',bool(p.get('approved')))
            updated=st.form_submit_button('บันทึกฉบับร่าง')
        if updated:
            new=normalize(dict(id=chosen,title=title,affiliate_url=url,category=cat,visual_description=desc,price_thb=price,commission_pct=pct))
            new['approved']=enabled;new['usage_rights_confirmed']=rights
            if enabled and not valid_product(new):st.error('ข้อมูลหรือสิทธิ์ไม่ครบ กรุณาตรวจสอบก่อนเปิดโปรโมต')
            elif any(q['id']!=chosen and q.get('affiliate_url')==url for q in products):st.error('ลิงก์ซ้ำ')
            else:st.session_state.catalog=[new if q['id']==chosen else q for q in products];st.rerun()
        if st.checkbox('ยืนยันลบรายการที่เลือก',key='delete_'+chosen):
            if st.button('ลบรายการ'):
                st.session_state.catalog=[q for q in products if q['id']!=chosen];st.rerun()
    st.dataframe(catalog_table(sorted(products,key=score,reverse=True)),hide_index=True,use_container_width=True)
    if st.button('บันทึกรายการทั้งหมดเข้า GitHub',disabled=not can_write):save_catalog()
    st.download_button('ดาวน์โหลดรายการ JSON',json.dumps({'products':products},ensure_ascii=False,indent=2),'affiliate_products.json','application/json')
elif nav=='นำเข้าสินค้า':
    st.subheader('นำเข้า Excel หรือ CSV')
    st.caption('รองรับ .xlsx และ .csv ภาษาไทย/อังกฤษ ข้อมูลนำเข้าเป็นฉบับร่างปิดโปรโมตทั้งหมด ไม่รับรองลิงก์จริงแทนเจ้าของบัญชี')
    template=pd.DataFrame(columns=['ชื่อสินค้า','ลิงก์','ราคา (บาท)','ค่าคอมมิชชัน (%)','หมวดหมู่','คำอธิบาย'])
    st.download_button('ดาวน์โหลดแม่แบบ CSV',template.to_csv(index=False).encode('utf-8-sig'),'shopee-template.csv','text/csv')
    xlsx=io.BytesIO();template.to_excel(xlsx,index=False,engine='openpyxl')
    st.download_button('ดาวน์โหลดแม่แบบ Excel',xlsx.getvalue(),'shopee-template.xlsx','application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    up=st.file_uploader('เลือกไฟล์',type=['csv','xlsx'])
    if up:
        try:
            incoming=import_table(up.getvalue(),up.name)
            st.dataframe(catalog_table(incoming),hide_index=True,use_container_width=True)
            if st.button('นำเข้าฉบับร่าง'):
                rows,n,skip=merge(products,incoming)
                st.session_state.catalog=rows
                st.success(f'เพิ่ม {n} รายการ ข้าม {skip} รายการ กรุณาอนุมัติในเมนูรายการสินค้า')
        except Exception as e:st.error(str(e))
    if st.button('บันทึกรายการเข้า GitHub',disabled=not can_write):save_catalog()
elif nav=='งบประมาณ':
    st.subheader('ตั้งเพดานงบประมาณ')
    with st.form('budget'):
        monthly=st.number_input('งบต่อเดือน (USD)',min_value=0.0,value=budget['monthly_cap_usd'])
        daily=st.number_input('งบต่อคลิป/วัน (USD)',min_value=0.0,value=budget['daily_cap_usd'])
        images=st.selectbox('ภาพต่อคลิป',[1,2,3],index=budget['images_per_reel']-1)
        img=st.number_input('ประมาณการต่อภาพ (USD)',min_value=.001,value=budget['image_estimate_usd'],format='%.3f')
        voice=st.number_input('ประมาณการเสียง (USD)',min_value=.001,value=budget['voice_estimate_usd'],format='%.3f')
        confirm=st.checkbox('ยืนยันการตั้งงบใหม่ รวมถึงค่าใช้จ่าย API ที่อาจเกิดขึ้น')
        go=st.form_submit_button('บันทึกงบ',disabled=not can_write)
    st.metric('ประมาณการต่อคลิป (รวม Gemini .01)',f'${images*img+voice+.01:.2f}')
    st.caption('ค่าประมาณเท่านั้น ระบบจะใช้ข้อจำกัดเดิมใน GitHub Variables ร่วมด้วยถ้ามี')
    if go:
        if not confirm:st.error('กรุณายืนยัน')
        else:
            try:repo.write('data/settings.json',validate_settings(dict(monthly_cap_usd=monthly,daily_cap_usd=daily,images_per_reel=images,image_estimate_usd=img,voice_estimate_usd=voice)),bsha);st.success('บันทึกแล้ว')
            except Exception as e:st.error(str(e))
elif nav=='ผลิตคลิป MP4':
    st.subheader('สั่งงาน GitHub Actions')
    st.info('ไม่เผยแพร่ Facebook • ผลิตจากสินค้าที่บันทึกใน GitHub แล้วเท่านั้น • MP4 เป็นภาพนิ่ง AI ซูม/แพนและเสียงไทย')
    st.link_button('เปิด GitHub Actions','https://github.com/'+repo.name+'/actions/workflows/daily.yml')
    if st.button('ทดสอบบทและแคปชันฟรี',disabled=not repo.token):
        try:repo.dispatch(True,False);st.success('ส่งคำขอทดสอบแล้ว ตรวจสถานะใน Actions')
        except Exception as e:st.error(str(e))
    again=st.checkbox('อนุญาตสร้างซ้ำในวันเดียวกัน (มีค่าใช้จ่าย)')
    paid=st.checkbox('ยืนยันเรียก API แบบมีค่าใช้จ่ายและตรวจสอบงบแล้ว')
    if st.button('สร้าง MP4 ฉบับจริง',disabled=not (repo.token and paid)):
        try:repo.dispatch(False,again);st.success('ส่งคำขอผลิตคลิปแล้ว ตรวจสถานะใน Actions')
        except Exception as e:st.error(str(e))
    try:
        for run in repo.runs():
            with st.expander(f'{run["created_at"][:16]} | {run["status"]} | {run.get("conclusion") or ""}'):
                st.link_button('ดู Log / ดาวน์โหลด MP4 จาก Artifacts',run['html_url'])
                if run.get('status')=='completed':
                    for a in repo.artifacts(run['id']):
                        if not a.get('expired'):st.caption('Artifact: '+a['name'])
    except Exception as e:st.warning(str(e))
