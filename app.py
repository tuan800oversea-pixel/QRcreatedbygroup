import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO
import zipfile

st.set_page_config(page_title="批量二维码生成器", layout="wide")

st.title("📦 批量二维码生成与分堆工具")
st.write("上传 Excel/CSV，选择字段，自动按分组打包下载。")

# 1. 文件上传
uploaded_file = st.file_uploader("选择表格文件 (xlsx 或 csv)", type=['header', 'csv', 'xlsx'])

if uploaded_file:
    # 读取数据
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    
    st.write("### 数据预览", df.head())

    # 2. 参数选择
    col1, col2, col3 = st.columns(3)
    
    with col1:
        group_col = st.selectbox("选择【分堆/文件夹】列", options=df.columns)
    with col2:
        content_col = st.selectbox("选择【二维码内容】列", options=df.columns)
    with col3:
        name_col = st.selectbox("选择【文件命名】列", options=df.columns)

    # 3. 生成逻辑
    if st.button("🚀 开始生成并打包"):
        zip_buffer = BytesIO()
        
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            for index, row in df.iterrows():
                # 获取数据
                group_name = str(row[group_col]).strip()
                content = str(row[content_col])
                file_name = str(row[name_col]).strip()
                
                # 生成二维码
                qr = qrcode.QRCode(version=1, box_size=10, border=5)
                qr.add_data(content)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                
                # 保存到内存
                img_buffer = BytesIO()
                img.save(img_buffer, format="PNG")
                
                # 写入ZIP，按文件夹分堆
                # 路径格式：分组名/文件名.png
                zip_path = f"{group_name}/{file_name}.png"
                zip_file.writestr(zip_path, img_buffer.getvalue())

        st.success("✅ 生成完毕！")
        
        # 4. 下载按钮
        st.download_button(
            label="📥 下载所有二维码 (ZIP)",
            data=zip_buffer.getvalue(),
            file_name="qrcodes_batch.zip",
            mime="application/zip"
        )
