import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ページ設定
st.set_page_config(layout="wide", page_title="不動産坪単価マップ")

# タイトル
st.title("🏙️ 不動産坪単価可視化マップ")

# データの読み込み関数
@st.cache_data
def load_data(file_path_or_buffer):
    try:
        df = pd.read_csv(file_path_or_buffer)
        return df
    except Exception as e:
        return None

# サイドバー設定
with st.sidebar:
    st.header("データ設定")
    
    # 1. ファイルアップローダー
    uploaded_file = st.file_uploader("CSVファイルをアップロード（任意）", type=["csv"])
    
    # デフォルトファイルのパス（リポジトリに含まれるファイルを想定）
    DEFAULT_FILE = "suumo_bukken_mod_23_2025-12-06.csv"
    
    df = None
    
    # アップロードされたファイルがあればそれを使用、なければデフォルトファイルを探す
    if uploaded_file is not None:
        df = load_data(uploaded_file)
        st.success("アップロードされたファイルを使用中")
    elif os.path.exists(DEFAULT_FILE):
        df = load_data(DEFAULT_FILE)
        st.info(f"デフォルトファイルを使用中: {DEFAULT_FILE}")
    else:
        st.warning("データファイルが見つかりません。CSVをアップロードするか、リポジトリにファイルを配置してください。")

# メイン処理
if df is not None:
    # 必要なカラムの確認 (緯度, 経度, 不動産単価（万／坪）)
    required_columns = ['緯度', '経度', '不動産単価（万／坪）', '物件名']
    
    if all(col in df.columns for col in required_columns):
        # 欠損値の削除
        df_clean = df.dropna(subset=['緯度', '経度', '不動産単価（万／坪）'])
        
        # --- フィルタリング UI ---
        st.sidebar.subheader("検索条件")
        
        # 1. 坪単価スライダー
        min_price = int(df_clean['不動産単価（万／坪）'].min())
        max_price = int(df_clean['不動産単価（万／坪）'].max())
        price_range = st.sidebar.slider(
            "坪単価（万円/坪）",
            min_value=min_price, 
            max_value=max_price, 
            value=(min_price, max_price)
        )
        
        # 2. 面積スライダー（もしカラムがあれば）
        if '面積' in df_clean.columns:
            min_area = int(df_clean['面積'].min())
            max_area = int(df_clean['面積'].max())
            area_range = st.sidebar.slider(
                "面積 (m²)",
                min_value=min_area,
                max_value=max_area,
                value=(min_area, max_area)
            )
            df_clean = df_clean[(df_clean['面積'] >= area_range[0]) & (df_clean['面積'] <= area_range[1])]

        # フィルタ適用
        mask = (
            (df_clean['不動産単価（万／坪）'] >= price_range[0]) & 
            (df_clean['不動産単価（万／坪）'] <= price_range[1])
        )
        df_filtered = df_clean[mask]
        
        # --- メイン画面 ---
        
        # 指標表示
        c1, c2, c3 = st.columns(3)
        c1.metric("表示物件数", f"{len(df_filtered)} 件")
        c2.metric("平均坪単価", f"{df_filtered['不動産単価（万／坪）'].mean():.1f} 万円")
        c3.metric("最高坪単価", f"{df_filtered['不動産単価（万／坪）'].max():.1f} 万円")
        
        # マップ描画
        if not df_filtered.empty:
            fig = px.scatter_mapbox(
                df_filtered,
                lat="緯度",
                lon="経度",
                color="不動産単価（万／坪）",
                size="不動産単価（万／坪）",
                hover_name="物件名",
                hover_data={
                    "緯度": False, "経度": False,
                    "価格(万円)": True,
                    "駅名": True
                },
                color_continuous_scale=px.colors.sequential.Jet,
                size_max=15,
                zoom=10,
                mapbox_style="carto-positron",
                height=700
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # データテーブル
            with st.expander("詳細データを見る"):
                st.dataframe(df_filtered)
        else:
            st.warning("条件に一致する物件がありません。")
            
    else:
        st.error(f"CSVファイルの形式が異なります。必要な列: {required_columns}")
else:
    st.info("👈 サイドバーからCSVファイルをアップロードしてください。")