import streamlit as st
from zhdate import ZhDate
from datetime import datetime

# --- 網頁設定 ---
st.set_page_config(page_title="素雅萬年曆", page_icon="📅")

# --- CSS 樣式 (素雅中國風) ---
st.markdown("""
    <style>
    /* 全域設定 */
    .stApp { background-color: #F7F7F2; }
    
    /* 字體設定 */
    h1, h2, h3, p, div, label, input, .stMarkdown, span {
        font-family: "KaiTi", "BiauKai", "Microsoft JhengHei", serif !important;
        color: #333333;
    }

    h1 { color: #8C5042 !important; text-align: center; margin-bottom: 25px; }
    
    /* 輸入框樣式 */
    div[data-baseweb="input"] > div {
        background-color: white; 
        border: 1px solid #ccc;
        color: #333333;
        border-radius: 4px;
    }
    /* 隱藏加減按鈕 */
    button[kind="secondary"] { border: none; background: transparent; }

    /* 結果顯示區 */
    .result-box {
        background-color: #EBEAD5;
        border: 1px solid #8C5042;
        padding: 30px;
        border-radius: 8px;
        text-align: center;
        margin-top: 20px;
        font-size: 1.5rem;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
        max-width: 600px; /* 限制寬度讓它在電腦版置中比較好看 */
        margin-left: auto;
        margin-right: auto;
    }
    
    .hint-text {
        font-size: 0.9rem;
        color: #888;
        margin-top: -10px;
        margin-bottom: 10px;
        margin-left: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 輔助函式 ---
def to_traditional_chinese(simplified_str):
    mapping = {'龙': '龍', '马': '馬', '鸡': '雞', '猪': '豬', '闰': '閏', '腊': '臘', '颜': '顏'}
    result = simplified_str
    for s, t in mapping.items():
        result = result.replace(s, t)
    return result

# --- 主程式 ---
st.title("萬年曆轉換系統")

# 版面配置：置中顯示
col_spacer1, col_content, col_spacer2 = st.columns([1, 8, 1])

with col_content:
    # 模式選擇
    mode = st.radio("轉換模式：", ["國曆 轉 農曆", "農曆 轉 國曆"], horizontal=True)
    st.write("") # 空行
    
    # 輸入區
    c1, c2, c3 = st.columns(3)
    
    with c1:
        # 年 (輸入完按 Enter 即生效)
        y = st.number_input("年", min_value=1, max_value=2100, value=2024, step=1, format="%d")
        # 智慧提示文字
        if y < 1900:
            st.markdown(f"<div class='hint-text'>民國 {y} 年</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='hint-text'>西元 {y} 年</div>", unsafe_allow_html=True)
            
    with c2:
        m = st.number_input("月", min_value=1, max_value=12, value=1, step=1, format="%d")
    with c3:
        d = st.number_input("日", min_value=1, max_value=31, value=1, step=1, format="%d")

    # 閏月勾選
    is_leap = False
    if mode == "農曆 轉 國曆":
        is_leap = st.checkbox("輸入的是閏月")

    # --- 轉換邏輯 ---
    try:
        # 自動判斷西元/民國
        if y < 1900:
            calc_year = y + 1911
            display_year_str = f"西元 {calc_year} (民國 {y})"
        else:
            calc_year = y
            display_year_str = f"西元 {y}"

        if mode == "國曆 轉 農曆":
            solar = datetime(calc_year, m, d)
            lunar = ZhDate.from_datetime(solar)
            trad_lunar = to_traditional_chinese(lunar.chinese())
            
            st.markdown(f"""
            <div class="result-box">
                <span style="font-size: 0.8em; color: #666;">【輸入國曆】</span><br>
                <b>{display_year_str} 年 {m} 月 {d} 日</b><br><br>
                <span style="font-size: 0.8em; color: #666;">【轉換農曆】</span><br>
                <b style="color: #8C5042; font-size: 2rem;">{trad_lunar}</b>
            </div>
            """, unsafe_allow_html=True)
            
        else: # 農曆 轉 國曆
            lunar = ZhDate(calc_year, m, d, leap_month=is_leap)
            solar_dt = lunar.to_datetime()
            minguo_y = solar_dt.year - 1911
            week_days = ["週一", "週二", "週三", "週四", "週五", "週六", "週日"]
            w_day = week_days[solar_dt.weekday()]
            leap_txt = "(閏)" if is_leap else ""
            
            st.markdown(f"""
            <div class="result-box">
                <span style="font-size: 0.8em; color: #666;">【輸入農曆】</span><br>
                <b>{display_year_str} 年 {m} 月 {d} 日 {leap_txt}</b><br><br>
                <span style="font-size: 0.8em; color: #666;">【轉換國曆】</span><br>
                <b style="color: #8C5042; font-size: 2rem;">西元 {solar_dt.year} 年 {solar_dt.month} 月 {solar_dt.day} 日</b><br>
                (民國 {minguo_y} 年) {w_day}
            </div>
            """, unsafe_allow_html=True)

    except Exception:
        # 靜默處理錯誤 (日期未打完不顯示紅字)
        pass
