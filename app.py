import streamlit as st
import pandas as pd
import io
from tgd_generator import TGDScriptGenerator
from utils import validate_csv_structure, format_japanese_text

# ページ設定
st.set_page_config(
    page_title="TGDScript自動生成ツール",
    page_icon="📊",
    layout="wide"
)

# メインタイトル
st.title("📊 TGDScript自動生成ツール")
st.markdown("---")

# サイドバー設定
st.sidebar.header("⚙️ 設定")

# セッション状態の初期化
if 'uploaded_data' not in st.session_state:
    st.session_state.uploaded_data = None
if 'generated_data' not in st.session_state:
    st.session_state.generated_data = None
if 'generator' not in st.session_state:
    st.session_state.generator = None

# ファイルアップロード
st.header("1. 📁 トレーニングデータのアップロード")
uploaded_file = st.file_uploader(
    "CSVファイルを選択してください",
    type=['csv'],
    help="TGDScriptのトレーニングデータが含まれるCSVファイルをアップロードしてください"
)

if uploaded_file is not None:
    try:
        # CSVファイルの読み込み
        df = pd.read_csv(uploaded_file, encoding='utf-8')
        
        # データ構造の検証
        is_valid, message = validate_csv_structure(df)
        
        if is_valid:
            st.success("✅ CSVファイルが正常に読み込まれました")
            st.session_state.uploaded_data = df
            st.session_state.generator = TGDScriptGenerator(df)
            
            # データプレビュー
            with st.expander("📋 データプレビュー", expanded=False):
                st.write(f"**総レコード数:** {len(df)}")
                st.write(f"**カラム数:** {len(df.columns)}")
                st.dataframe(df.head(10))
                
        else:
            st.error(f"❌ CSVファイルの構造に問題があります: {message}")
            
    except Exception as e:
        st.error(f"❌ ファイルの読み込みエラー: {str(e)}")

# データ生成セクション
if st.session_state.uploaded_data is not None and st.session_state.generator is not None:
    st.markdown("---")
    st.header("2. 🔧 データ生成設定")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # 生成数の設定
        num_generate = st.number_input(
            "生成するレコード数",
            min_value=1,
            max_value=1000,
            value=50,
            help="生成したいTGDScriptレコードの数を指定してください"
        )
        
        # バリエーション設定
        variation_level = st.selectbox(
            "バリエーションレベル",
            ["低", "中", "高"],
            index=1,
            help="生成されるスクリプトの多様性レベルを選択してください"
        )
    
    with col2:
        # テーブル名の多様化
        diversify_tables = st.checkbox(
            "テーブル名を多様化",
            value=True,
            help="既存のテーブル名を基に新しいテーブル名を生成します"
        )
        
        # カラム名の多様化
        diversify_columns = st.checkbox(
            "カラム名を多様化",
            value=True,
            help="既存のカラム名を基に新しいカラム名を生成します"
        )
        
        # シナリオの多様化
        diversify_scenarios = st.checkbox(
            "分析シナリオを多様化",
            value=True,
            help="既存のシナリオを基に新しい分析シナリオを生成します"
        )
    
    # 生成ボタン
    if st.button("🚀 TGDScriptを生成", type="primary"):
        with st.spinner("TGDScriptを生成中..."):
            try:
                generated_df = st.session_state.generator.generate_scripts(
                    num_scripts=num_generate,
                    variation_level=variation_level.lower(),
                    diversify_tables=diversify_tables,
                    diversify_columns=diversify_columns,
                    diversify_scenarios=diversify_scenarios
                )
                
                st.session_state.generated_data = generated_df
                st.success(f"✅ {len(generated_df)}件のTGDScriptが生成されました！")
                
            except Exception as e:
                st.error(f"❌ 生成エラー: {str(e)}")

# 生成結果の表示
if st.session_state.generated_data is not None:
    st.markdown("---")
    st.header("3. 📊 生成結果")
    
    generated_df = st.session_state.generated_data
    
    # 統計情報
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("生成レコード数", len(generated_df))
    with col2:
        unique_tables = generated_df['テーブル名（日本語）'].nunique()
        st.metric("ユニークテーブル数", unique_tables)
    with col3:
        unique_scenarios = generated_df['分析シナリオ'].nunique()
        st.metric("ユニークシナリオ数", unique_scenarios)
    with col4:
        avg_script_length = generated_df['TGDScript'].str.len().mean()
        st.metric("平均スクリプト長", f"{avg_script_length:.0f}文字")
    
    # データプレビュー
    st.subheader("📋 生成データプレビュー")
    
    # フィルタリングオプション
    with st.expander("🔍 フィルタリングオプション", expanded=False):
        filter_col1, filter_col2 = st.columns(2)
        
        with filter_col1:
            selected_table = st.selectbox(
                "テーブルでフィルタ",
                ["すべて"] + list(generated_df['テーブル名（日本語）'].unique()),
                index=0
            )
        
        with filter_col2:
            show_columns = st.multiselect(
                "表示カラムを選択",
                generated_df.columns.tolist(),
                default=['テーブル名（日本語）', '分析シナリオ', 'TGDScript']
            )
    
    # データのフィルタリング
    display_df = generated_df.copy()
    if selected_table != "すべて":
        display_df = display_df[display_df['テーブル名（日本語）'] == selected_table]
    
    if show_columns:
        display_df = display_df[show_columns]
    
    # データテーブル表示
    st.dataframe(
        display_df,
        use_container_width=True,
        height=400
    )
    
    # TGDScriptの詳細表示
    st.subheader("🔍 TGDScript詳細表示")
    selected_row = st.selectbox(
        "表示するレコードを選択",
        range(len(display_df)),
        format_func=lambda x: f"レコード {x+1}: {display_df.iloc[x]['テーブル名（日本語）'] if 'テーブル名（日本語）' in display_df.columns else f'行{x+1}'}"
    )
    
    if selected_row is not None:
        selected_record = display_df.iloc[selected_row]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**基本情報:**")
            for col in ['テーブル名（日本語）', 'テーブル名（英語）', 'カラム名（日）', 'カラム名（英）']:
                if col in selected_record:
                    st.write(f"**{col}:** {selected_record[col]}")
        
        with col2:
            st.write("**分析情報:**")
            for col in ['仮説', '分析シナリオ', '説明文', '具体的手続']:
                if col in selected_record:
                    st.write(f"**{col}:** {selected_record[col]}")
        
        st.write("**生成されたTGDScript:**")
        if 'TGDScript' in selected_record:
            st.code(selected_record['TGDScript'], language='text')
    
    # ダウンロード機能
    st.subheader("⬇️ ダウンロード")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # CSV形式でダウンロード
        csv_buffer = io.StringIO()
        generated_df.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
        csv_data = csv_buffer.getvalue()
        
        st.download_button(
            label="📁 CSVファイルをダウンロード",
            data=csv_data,
            file_name=f"generated_tgd_scripts_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            help="生成されたTGDScriptをCSVファイルとしてダウンロードします"
        )
    
    with col2:
        # TGDScriptのみを抜き出してダウンロード
        if 'TGDScript' in generated_df.columns:
            scripts_only = generated_df[['テーブル名（日本語）', 'TGDScript']]
            scripts_buffer = io.StringIO()
            scripts_only.to_csv(scripts_buffer, index=False, encoding='utf-8-sig')
            scripts_data = scripts_buffer.getvalue()
            
            st.download_button(
                label="📋 TGDScriptのみダウンロード",
                data=scripts_data,
                file_name=f"tgd_scripts_only_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                help="TGDScriptのみを抽出してダウンロードします"
            )

# フッター
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666666;'>
        <p>TGDScript自動生成ツール | データ品質向上のためのトレーニングデータ生成</p>
    </div>
    """,
    unsafe_allow_html=True
)
