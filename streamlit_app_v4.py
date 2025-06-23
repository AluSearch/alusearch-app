import streamlit as st # type: ignore
import pandas as pd # type: ignore
import altair as alt # type: ignore
import os

def load_alloy_data(csv_file_path="aluminum_data_v2.csv"):
    """
    CSVファイルからアルミ合金データを読み込み、DataFrameとして返す。
    """
    try:
        # スクリプトのディレクトリを基準にファイルパスを解決
        base_path = os.path.dirname(__file__)
        full_path = os.path.join(base_path, csv_file_path)
        df = pd.read_csv(full_path)
        # 化学成分の欠損値を0で埋める
        cols_to_fill = [
            'Si_percent', 'Fe_percent', 'Cu_percent', 'Mn_percent', 'Mg_percent', 'Cr_percent', 'Zn_percent', 'Ti_percent',
            'density_g_cm3', 'thermal_expansion_e-6_k', 'thermal_conductivity_w_mk', 'electrical_conductivity_iacs'
        ]
        # Al_percent は 'Rem.' のような文字列が入る可能性があるため除外
        df[cols_to_fill] = df[cols_to_fill].fillna(0)
        # 耐食性の欠損値を'-'で埋める
        if 'corrosion_resistance' in df.columns:
            df['corrosion_resistance'] = df['corrosion_resistance'].fillna('-')
        return df
    except FileNotFoundError:
        st.error(f"エラー: データファイル '{csv_file_path}' が見つかりません。")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"データの読み込み中にエラーが発生しました: {e}")
        return pd.DataFrame()

# --- 訪問者カウンター機能 ---
COUNT_FILE = "visitor_count.txt"

def get_visitor_count():
    """ファイルから現在の訪問者数を読み込む"""
    try:
        base_path = os.path.dirname(__file__)
        full_path = os.path.join(base_path, COUNT_FILE)
        with open(full_path, "r") as f:
            return int(f.read())
    except (FileNotFoundError, ValueError):
        return 0 # ファイルがない、または中身が不正な場合は0から開始

def increment_visitor_count():
    """訪問者数を1増やしてファイルに保存する"""
    count = get_visitor_count() + 1
    try:
        base_path = os.path.dirname(__file__)
        full_path = os.path.join(base_path, COUNT_FILE)
        with open(full_path, "w") as f:
            f.write(str(count))
    except Exception as e:
        st.error(f"カウンターの更新中にエラーが発生しました: {e}")

def main():
    st.set_page_config(
        page_title="AluSearch - アルミ合金特性検索データベース",
        page_icon="🔬",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # --- SEO と デザイン調整 ---
    st.markdown("""
        <meta name="description" content="AluSearchは、アルミ合金の特性と成分を検索・比較できる無料のデータベースです。引張強度、降伏強度、熱伝導性、導電率などの詳細なデータをスライダーで絞り込み、散布図で視覚的に分析できます。">
        <meta name="keywords" content="アルミ, アルミニウム, 合金, データベース, 検索, データ, 強度, 熱伝導性, 導電率, 耐食性, 成分, A5052, A6061, A7075, 特性比較">
        <style>
               .block-container {
                    padding-top: 1.5rem;
                    padding-left: 2rem;
                    padding-right: 2rem;
                    padding-bottom: 2rem;
                }
        </style>
        """, unsafe_allow_html=True)
    st.markdown('<h1>AluSearch <span style="font-size: 0.6em;">- アルミ合金 特性・成分データベース -</span></h1>', unsafe_allow_html=True)
    df = load_alloy_data()
    if df.empty:
        return

    # --- 訪問者カウンターの処理 ---
    # セッション内でまだカウントされていない場合のみ、カウントを増やす
    if 'counted' not in st.session_state:
        increment_visitor_count()
        st.session_state.counted = True

    visitor_count = get_visitor_count()

    # --- サイドバー ---
    st.sidebar.header("⚙️ 合金・質別 選択")

    # 選択ウィジェットを後から配置するためのプレースホルダー
    selection_placeholder = st.sidebar.empty()

    # --- 絞り込み検索フィルター (エキスパンダー内) ---
    with st.sidebar.expander("絞り込み検索 (フィルタ)", expanded=False):
        # 耐食性フィルター
        corrosion_options = sorted(df['corrosion_resistance'].unique().tolist())
        selected_corrosion = st.multiselect(
            "耐食性:",
            options=corrosion_options,
            default=corrosion_options
        )

        # 数値特性フィルター (スライダー)
        tensile_min, tensile_max = int(df['tensile_strength_mpa'].min()), int(df['tensile_strength_mpa'].max())
        if tensile_min == tensile_max: tensile_max += 1
        tensile_range = st.slider("引張強度 (MPa)", tensile_min, tensile_max, (tensile_min, tensile_max))

        yield_min, yield_max = int(df['yield_strength_mpa'].min()), int(df['yield_strength_mpa'].max())
        if yield_min == yield_max: yield_max += 1
        yield_range = st.slider("降伏強度 (MPa)", yield_min, yield_max, (yield_min, yield_max))

        elongation_min, elongation_max = int(df['elongation_percent'].min()), int(df['elongation_percent'].max())
        if elongation_min == elongation_max: elongation_max += 1
        elongation_range = st.slider("伸び (%)", elongation_min, elongation_max, (elongation_min, elongation_max))

        thermal_cond_min, thermal_cond_max = int(df['thermal_conductivity_w_mk'].min()), int(df['thermal_conductivity_w_mk'].max())
        if thermal_cond_min == thermal_cond_max: thermal_cond_max += 1
        thermal_cond_range = st.slider("熱伝導性 (W/m·K)", thermal_cond_min, thermal_cond_max, (thermal_cond_min, thermal_cond_max))

        elec_cond_min, elec_cond_max = int(df['electrical_conductivity_iacs'].min()), int(df['electrical_conductivity_iacs'].max())
        if elec_cond_min == elec_cond_max: elec_cond_max += 1
        elec_cond_range = st.slider("導電率 (% IACS)", elec_cond_min, elec_cond_max, (elec_cond_min, elec_cond_max))

    # --- フィルターを適用 ---
    filtered_df = df[
        (df['corrosion_resistance'].isin(selected_corrosion)) &
        (df['tensile_strength_mpa'].between(tensile_range[0], tensile_range[1])) &
        (df['yield_strength_mpa'].between(yield_range[0], yield_range[1])) &
        (df['elongation_percent'].between(elongation_range[0], elongation_range[1])) &
        (df['thermal_conductivity_w_mk'].between(thermal_cond_range[0], thermal_cond_range[1])) &
        (df['electrical_conductivity_iacs'].between(elec_cond_range[0], elec_cond_range[1]))
    ].copy()

    # --- プレースホルダーに選択ウィジェットを配置 ---
    alloy_list = sorted(filtered_df['alloy'].unique().tolist())
    with selection_placeholder.container():
        if not alloy_list:
            selected_alloy = None
            selected_temper = None
        else:
            selected_alloy = st.selectbox(
                "合金:", alloy_list,
                index=(alloy_list.index('A5052') if 'A5052' in alloy_list else 0)
            )
            available_tempers = sorted(filtered_df[filtered_df['alloy'] == selected_alloy]['temper'].unique().tolist()) if selected_alloy else []
            selected_temper = st.selectbox(
                "質別:", available_tempers,
                index=(available_tempers.index('H32') if 'H32' in available_tempers else 0)
            )

    st.sidebar.divider()
    st.sidebar.caption(
        "注意: このデータベースに記載されているアルミ合金の特性（強度、熱伝導性、導電率など）や化学成分は、"
        "生成AIによりWEB上から自動収集した一般的な参考情報であり、この特性を保証するものではありません。"
        "また、製造メーカー、ロット、具体的な規格（JIS、ASTMなど）、分析方法、試験条件によって数値や成分比は変動します。 "
        "特に化学成分は、規格で定められた含有量の上限・下限の範囲内で変動するため、ここに記載されているのはその代表的な、あるいは平均的な値です。 "
        "安全性が求められる設計や用途に使用する際は、必ずメーカーの公式データシートや該当する規格（JISハンドブック、ASTM標準など）をご確認ください。 "
        "記載されている数値はあくまで参考データとしてお使いください。"
    )
    with st.sidebar.expander("管理者用データ", expanded=False):
        st.metric("累計訪問者数", f"{visitor_count} 人")

    # --- メインコンテンツ ---
    if selected_alloy and selected_temper:
        alloy_data = filtered_df[(filtered_df['alloy'] == selected_alloy) & (filtered_df['temper'] == selected_temper)].iloc[0]

        # --- 合金-調質名と説明を詰めて横並び ---
        st.markdown(f"<h3>{selected_alloy}-{selected_temper} <span style='font-size: 0.7em; font-weight: normal; color: #555;'>{alloy_data['description']}</span></h3>", unsafe_allow_html=True)

        st.divider()

        # --- 詳細情報とグラフを2カラムで表示 ---
        detail_col, graph_col = st.columns([1.35, 1], gap="medium") # 左カラムをさらに5%狭く調整

        with detail_col:
            # --- 機械的特性テーブル ---
            with st.expander("📊 機械的特性", expanded=True):
                mechanical_properties = {
                    "特性": ["引張強度 (MPa)", "降伏強度 (MPa)", "伸び (%)", "ブリネル硬さ"],
                    "値": [
                        alloy_data['tensile_strength_mpa'],
                        alloy_data['yield_strength_mpa'],
                        alloy_data['elongation_percent'],
                        alloy_data['hardness_brinell']
                    ]
                }
                mech_df = pd.DataFrame(mechanical_properties).set_index("特性").T
                mech_html = mech_df.style.format(precision=0).hide(axis="index").to_html()
                st.markdown(mech_html, unsafe_allow_html=True)
            
            # --- その他の物理特性テーブル ---
            with st.expander("🌡️ 物理特性", expanded=True):
                physical_properties = {
                    "特性": ["耐食性", "比重 (g/cm³)", "熱膨張率 (10⁻⁶/K)", "熱伝導性 (W/m·K)", "導電率 (% IACS)"],
                    "値": [
                        alloy_data['corrosion_resistance'],
                        alloy_data['density_g_cm3'],
                        alloy_data['thermal_expansion_e-6_k'],
                        alloy_data['thermal_conductivity_w_mk'],
                        alloy_data['electrical_conductivity_iacs']
                    ]
                }
                phys_df = pd.DataFrame(physical_properties).set_index("特性").T
                phys_html = phys_df.style.format(precision=2).hide(axis="index").to_html()
                st.markdown(phys_html, unsafe_allow_html=True)

            # --- 化学成分テーブル ---
            with st.expander("🧪 化学成分", expanded=True):
                chem_cols = [
                    'Si_percent', 'Fe_percent', 'Cu_percent', 'Mn_percent',
                    'Mg_percent', 'Cr_percent', 'Zn_percent', 'Ti_percent', 'Al_percent' # Al_percentを再追加
                ]
                chem_data = alloy_data[chem_cols].rename(lambda x: x.replace('_percent', '').upper())
                formatted_chem_data = chem_data.apply(lambda x: f"{x:.2f}" if isinstance(x, (int, float)) else x)
                chem_df_horizontal = formatted_chem_data.to_frame().T
                chem_df_horizontal.columns.name = "元素"
                chem_html = chem_df_horizontal.style.hide(axis="index").to_html() # 2段表示のロジックを削除し、単一テーブルに戻す
                st.markdown(chem_html, unsafe_allow_html=True)

        with graph_col:
            st.subheader("📈 特性比較用 散布図") # 散布図のタイトルを追加
            # --- 軸選択のプルダウン ---
            axis_options = {
                "引張強度 (MPa)": "tensile_strength_mpa", "降伏強度 (MPa)": "yield_strength_mpa",
                "伸び (%)": "elongation_percent", "ブリネル硬さ": "hardness_brinell",
                "比重 (g/cm³)": "density_g_cm3", "熱膨張率 (10⁻⁶/K)": "thermal_expansion_e-6_k",
                "熱伝導性 (W/m·K)": "thermal_conductivity_w_mk", "導電率 (% IACS)": "electrical_conductivity_iacs",
                "Si (%)": "Si_percent", "Fe (%)": "Fe_percent", "Cu (%)": "Cu_percent",
                "Mn (%)": "Mn_percent", "Mg (%)": "Mg_percent", "Cr (%)": "Cr_percent",
                "Zn (%)": "Zn_percent", "Ti (%)": "Ti_percent",
            }
            axis_labels = list(axis_options.keys())

            default_x_index = axis_labels.index('伸び (%)')
            default_y_index = axis_labels.index('引張強度 (MPa)')

             # ラベルとプルダウンを横に並べるためのカラム設定
            col1, col2, col3, col4 = st.columns([0.5, 2, 0.5, 2])
            col1.markdown("<div style='padding-top: 0.5rem; text-align: right;'>X軸:</div>", unsafe_allow_html=True)
            x_axis_label = col2.selectbox("X軸", axis_labels, index=default_x_index, label_visibility="collapsed")
            col3.markdown("<div style='padding-top: 0.5rem; text-align: right;'>Y軸:</div>", unsafe_allow_html=True)
            y_axis_label = col4.selectbox("Y軸", axis_labels, index=default_y_index, label_visibility="collapsed")

            x_axis_col = axis_options[x_axis_label]
            y_axis_col = axis_options[y_axis_label]

            # --- 散布図グラフの描画 ---
            tooltip_cols = ['alloy', 'temper'] # ツールチップに表示する情報を限定

            base = alt.Chart(filtered_df).mark_circle(opacity=0.5, size=60).encode(
                x=alt.X(x_axis_col, title=x_axis_label, scale=alt.Scale(zero=False)), # x軸のスケールを0から開始しない
                y=alt.Y(y_axis_col, title=y_axis_label, scale=alt.Scale(zero=False)), # y軸のスケールを0から開始しない
                tooltip=tooltip_cols
            ).properties(
                height=350 # グラフの高さを固定
            ).interactive()

            highlight = alt.Chart(
                filtered_df[(filtered_df['alloy'] == selected_alloy) & (filtered_df['temper'] == selected_temper)]
            ).mark_circle(size=150, color='red', stroke='black', strokeWidth=1).encode(
                x=alt.X(x_axis_col, title=x_axis_label),
                y=alt.Y(y_axis_col, title=y_axis_label),
            ).properties(
                height=350 # 強調レイヤーも同じ高さに
            )

            st.altair_chart(base + highlight, use_container_width=True)

            # --- 凡例 ---
            st.markdown("""
                <div style="display: flex; align-items: center; gap: 15px; margin-top: 10px; font-size: 0.9em;">
                    <span style="display: inline-block; width: 15px; height: 15px; border-radius: 50%; background-color: gray; border: 1px solid #ccc;"></span>
                    <span>その他の合金</span>
                    <span style="display: inline-block; width: 15px; height: 15px; border-radius: 50%; background-color: red; border: 1px solid black;"></span>
                    <span>選択中の合金</span>
                </div>
            """, unsafe_allow_html=True)
    elif not alloy_list:
        st.warning("指定された条件に合う合金が見つかりませんでした。フィルター条件を緩和してください。")
    else:
        st.info("サイドバーから合金と質別を選択してください。")

if __name__ == '__main__':
    main()
