import streamlit as st
import pandas as pd
import io
from tgd_generator import TGDScriptGenerator
from utils import validate_csv_structure, format_japanese_text

# Cấu hình trang
st.set_page_config(
    page_title="Công cụ tự động tạo TGDScript",
    page_icon="📊",
    layout="wide"
)

# Tiêu đề chính
st.title("📊 Công cụ tự động tạo TGDScript")
st.markdown("---")

# Cài đặt thanh bên
st.sidebar.header("⚙️ Cài đặt")

# セッション状態の初期化
if 'uploaded_data' not in st.session_state:
    st.session_state.uploaded_data = None
if 'generated_data' not in st.session_state:
    st.session_state.generated_data = None
if 'generator' not in st.session_state:
    st.session_state.generator = None

# Tải file lên
st.header("1. 📁 Tải lên dữ liệu huấn luyện")
uploaded_file = st.file_uploader(
    "Chọn file CSV",
    type=['csv'],
    help="Tải lên file CSV chứa dữ liệu huấn luyện TGDScript"
)

if uploaded_file is not None:
    try:
        # CSVファイルの読み込み
        df = pd.read_csv(uploaded_file, encoding='utf-8')
        
        # データ構造の検証
        is_valid, message = validate_csv_structure(df)
        
        if is_valid:
            st.success("✅ File CSV đã được tải lên thành công")
            st.session_state.uploaded_data = df
            st.session_state.generator = TGDScriptGenerator(df)
            
            # Xem trước dữ liệu
            with st.expander("📋 Xem trước dữ liệu", expanded=False):
                st.write(f"**Tổng số dòng:** {len(df)}")
                st.write(f"**Số cột:** {len(df.columns)}")
                st.dataframe(df.head(10))
                
        else:
            st.error(f"❌ Có lỗi trong cấu trúc file CSV: {message}")
            
    except Exception as e:
        st.error(f"❌ Lỗi đọc file: {str(e)}")

# Phần tạo dữ liệu
if st.session_state.uploaded_data is not None and st.session_state.generator is not None:
    st.markdown("---")
    st.header("2. 🔧 Cài đặt tạo dữ liệu")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Cài đặt số lượng tạo
        num_generate = st.number_input(
            "Số lượng bản ghi cần tạo",
            min_value=1,
            max_value=1000,
            value=50,
            help="Chỉ định số lượng bản ghi TGDScript muốn tạo"
        )
        
        # Cài đặt mức độ đa dạng
        variation_level = st.selectbox(
            "Mức độ đa dạng",
            ["Thấp", "Trung bình", "Cao"],
            index=1,
            help="Chọn mức độ đa dạng của các script được tạo"
        )
    
    with col2:
        # Đa dạng hóa tên bảng
        diversify_tables = st.checkbox(
            "Đa dạng hóa tên bảng",
            value=True,
            help="Tạo tên bảng mới dựa trên các tên bảng hiện có"
        )
        
        # Đa dạng hóa tên cột
        diversify_columns = st.checkbox(
            "Đa dạng hóa tên cột",
            value=True,
            help="Tạo tên cột mới dựa trên các tên cột hiện có"
        )
        
        # Đa dạng hóa kịch bản
        diversify_scenarios = st.checkbox(
            "Đa dạng hóa kịch bản phân tích",
            value=True,
            help="Tạo kịch bản phân tích mới dựa trên các kịch bản hiện có"
        )
    
    # Nút tạo
    if st.button("🚀 Tạo TGDScript", type="primary"):
        with st.spinner("Đang tạo TGDScript..."):
            try:
                # Mapping level từ tiếng Việt sang tiếng Anh
                level_mapping = {"Thấp": "low", "Trung bình": "medium", "Cao": "high"}
                level_en = level_mapping.get(variation_level, "medium")
                
                generated_df = st.session_state.generator.generate_scripts(
                    num_scripts=num_generate,
                    variation_level=level_en,
                    diversify_tables=diversify_tables,
                    diversify_columns=diversify_columns,
                    diversify_scenarios=diversify_scenarios
                )
                
                st.session_state.generated_data = generated_df
                st.success(f"✅ Đã tạo {len(generated_df)} TGDScript thành công!")
                
            except Exception as e:
                st.error(f"❌ Lỗi tạo dữ liệu: {str(e)}")

# Hiển thị kết quả tạo
if st.session_state.generated_data is not None:
    st.markdown("---")
    st.header("3. 📊 Kết quả tạo")
    
    generated_df = st.session_state.generated_data
    
    # Thông tin thống kê
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Số bản ghi đã tạo", len(generated_df))
    with col2:
        if 'テーブル名（日本語）' in generated_df.columns:
            unique_tables = int(generated_df['テーブル名（日本語）'].nunique())
            st.metric("Số bảng duy nhất", unique_tables)
        else:
            st.metric("Số bảng duy nhất", 0)
    with col3:
        if '分析シナリオ' in generated_df.columns:
            unique_scenarios = int(generated_df['分析シナリオ'].nunique())
            st.metric("Số kịch bản duy nhất", unique_scenarios)
        else:
            st.metric("Số kịch bản duy nhất", 0)
    with col4:
        if 'TGDScript' in generated_df.columns:
            avg_script_length = float(generated_df['TGDScript'].str.len().mean())
            st.metric("Độ dài script trung bình", f"{avg_script_length:.0f} ký tự")
        else:
            st.metric("Độ dài script trung bình", "0 ký tự")
    
    # Xem trước dữ liệu
    st.subheader("📋 Xem trước dữ liệu đã tạo")
    
    # Tùy chọn lọc
    with st.expander("🔍 Tùy chọn lọc", expanded=False):
        filter_col1, filter_col2 = st.columns(2)
        
        with filter_col1:
            if 'テーブル名（日本語）' in generated_df.columns:
                table_options = ["Tất cả"] + list(generated_df['テーブル名（日本語）'].unique())
            else:
                table_options = ["Tất cả"]
            selected_table = st.selectbox(
                "Lọc theo bảng",
                table_options,
                index=0
            )
        
        with filter_col2:
            show_columns = st.multiselect(
                "Chọn cột hiển thị",
                generated_df.columns.tolist(),
                default=['テーブル名（日本語）', '分析シナリオ', 'TGDScript'] if all(col in generated_df.columns for col in ['テーブル名（日本語）', '分析シナリオ', 'TGDScript']) else generated_df.columns.tolist()[:3]
            )
    
    # Lọc dữ liệu
    display_df = generated_df.copy()
    if selected_table != "Tất cả" and 'テーブル名（日本語）' in display_df.columns:
        display_df = display_df[display_df['テーブル名（日本語）'] == selected_table]
    
    if show_columns:
        display_df = display_df[show_columns]
    
    # Hiển thị bảng dữ liệu
    st.dataframe(
        display_df,
        use_container_width=True,
        height=400
    )
    
    # Hiển thị chi tiết TGDScript
    st.subheader("🔍 Hiển thị chi tiết TGDScript")
    if len(display_df) > 0:
        selected_row = st.selectbox(
            "Chọn bản ghi để hiển thị",
            range(len(display_df)),
            format_func=lambda x: f"Bản ghi {x+1}: {display_df.iloc[x]['テーブル名（日本語）'] if 'テーブル名（日本語）' in display_df.columns else f'Dòng {x+1}'}"
        )
        
        if selected_row is not None:
            selected_record = display_df.iloc[selected_row]
        
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Thông tin cơ bản:**")
                for col in ['テーブル名（日本語）', 'テーブル名（英語）', 'カラム名（日）', 'カラム名（英）']:
                    if col in selected_record:
                        col_vn = {
                            'テーブル名（日本語）': 'Tên bảng (Tiếng Nhật)',
                            'テーブル名（英語）': 'Tên bảng (Tiếng Anh)', 
                            'カラム名（日）': 'Tên cột (Tiếng Nhật)',
                            'カラム名（英）': 'Tên cột (Tiếng Anh)'
                        }
                        st.write(f"**{col_vn.get(col, col)}:** {selected_record[col]}")
            
            with col2:
                st.write("**Thông tin phân tích:**")
                for col in ['仮説', '分析シナリオ', '説明文', '具体的手続']:
                    if col in selected_record:
                        col_vn = {
                            '仮説': 'Giả thuyết',
                            '分析シナリオ': 'Kịch bản phân tích',
                            '説明文': 'Mô tả',
                            '具体的手続': 'Thủ tục cụ thể'
                        }
                        st.write(f"**{col_vn.get(col, col)}:** {selected_record[col]}")
            
            st.write("**TGDScript đã tạo:**")
            if 'TGDScript' in selected_record:
                st.code(selected_record['TGDScript'], language='text')
    else:
        st.info("Không có dữ liệu để hiển thị")
    
    # Chức năng tải xuống
    st.subheader("⬇️ Tải xuống")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Tải xuống định dạng CSV
        csv_buffer = io.StringIO()
        generated_df.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
        csv_data = csv_buffer.getvalue()
        
        st.download_button(
            label="📁 Tải xuống file CSV",
            data=csv_data,
            file_name=f"tgd_scripts_generated_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            help="Tải xuống TGDScript đã tạo dưới định dạng CSV"
        )
    
    with col2:
        # Chỉ tải xuống TGDScript
        if 'TGDScript' in generated_df.columns:
            scripts_only = generated_df[['テーブル名（日本語）', 'TGDScript']]
            scripts_buffer = io.StringIO()
            scripts_only.to_csv(scripts_buffer, index=False, encoding='utf-8-sig')
            scripts_data = scripts_buffer.getvalue()
            
            st.download_button(
                label="📋 Chỉ tải TGDScript",
                data=scripts_data,
                file_name=f"tgd_scripts_only_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                help="Chỉ tải xuống cột TGDScript"
            )

# Chân trang
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666666;'>
        <p>Công cụ tự động tạo TGDScript | Tạo dữ liệu huấn luyện để cải thiện chất lượng dữ liệu</p>
    </div>
    """,
    unsafe_allow_html=True
)
