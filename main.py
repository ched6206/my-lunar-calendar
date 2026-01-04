import streamlit as st
from zhdate import ZhDate
from datetime import datetime

# --- 網頁設定 ---
st.set_page_config(page_title="素雅萬年曆", page_icon="📅")

# --- CSS 樣式 (宋體版) ---
st.markdown("""
    <style>
    /* 全域背景 */
    .stApp { background-color: #F7F7F2; }
    
    /* 【字體設定關鍵修改】 
       優先順序：Mac宋體 -> Windows中易宋體 -> Windows新細明體 -> 系統預設襯線體
    */
    h1, h2, h3, p, div, label, input, .stMarkdown, span, button {
        font-family: "Songti SC", "SimSun", "PMingLiU", "MingLiU", "Microsoft JhengHei", serif !important;
        color: #333333;
    }

    /* 標題加強一點粗體，宋體如果太細標題會沒氣勢 */
    h1 { 
        color: #8C5042 !important; 
        text-align: center; 
        margin-bottom: 25px; 
        font-weight: bold; 
        letter-spacing: 2px; /* 增加字距，更有古風 */
    }
    
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
        border-radius: 4px; /* 宋體適合方一點的角 */
        text-align: center;
        margin-top: 20px;
        font-size: 1.6rem;
        box-shadow: 3px 3px 10px rgba(0,0,0,0.1);
        max-width: 600px;
        margin-left: auto;
        margin-right: auto;
        line-height: 1.8; /* 增加行高，像古書排版 */
    }
    
    /* 提示文字 */
    .hint-text {
        font-size: 0.9rem;
        color: #888;
        margin-top: -10px;
        margin-bottom: 10px;
        margin-left: 5px;
        font-style: italic; /* 宋體斜體很有味道 */
    }
    
    /* 等待輸入的提示區塊 */
    .waiting-box {
        text-align: center;
        color: #aaa;
        padding: 40px;
        border: 1px dashed #ccc;
        border-radius: 4px;
        margin-top: 20px;
        letter-spacing: 1px;
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

# 版面配置
col_spacer1, col_content, col_spacer2 = st.columns([1, 8, 1])

with col_content:
    # 模式選擇
    mode = st.radio("轉換模式：", ["國曆 轉 農曆", "農曆 轉 國曆"], horizontal=True)
    st.write("") 
    
    # 輸入區
    c1, c2, c3 = st.columns(3)
    
    with c1:
        # 預設空白 (value=None)
        y = st.number_input("年", min_value=1, max_value=2100, value=None, step=1, format="%d", placeholder="如 114")
        
        if y is not None:
            if y < 1900:
                st.markdown(f"<div class='hint-text'>民國 {y} 年</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='hint-text'>西元 {y} 年</div>", unsafe_allow_html=True)
        else:
             st.markdown(f"<div class='hint-text'>&nbsp;</div>", unsafe_allow_html=True)
            
    with c2:
        m = st.number_input("月", min_value=1, max_value=12, value=None, step=1, format="%d", placeholder="1~12")
    with c3:
        d = st.number_input("日", min_value=1, max_value=31, value=None, step=1, format="%d", placeholder="1~31")

    # 閏月勾選
    is_leap = False
    if mode == "農曆 轉 國曆":
        is_leap = st.checkbox("輸入的是閏月")

    # --- 轉換邏輯 ---
    if y is not None and m is not None and d is not None:
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
                    <b style="color: #8C5042; font-size: 2.2rem; font-weight: bold;">{trad_lunar}</b>
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
                    <b style="color: #8C5042; font-size: 2.2rem; font-weight: bold;">西元 {solar_dt.year} 年 {solar_dt.month} 月 {solar_dt.day} 日</b><br>
                    (民國 {minguo_y} 年) {w_day}
                </div>
                """, unsafe_allow_html=True)

        except Exception:
            st.warning("⚠️ 日期無效，請檢查輸入")
    else:
        st.markdown("""
        <div class="waiting-box">
            請輸入完整 年、月、日 以進行轉換
        </div>
        """, unsafe_allow_html=True)
