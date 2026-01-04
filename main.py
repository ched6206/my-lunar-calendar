import streamlit as st
from zhdate import ZhDate
from datetime import datetime

# --- 網頁設定 ---
st.set_page_config(page_title="素雅萬年曆", page_icon="📅")

# --- CSS 樣式 (移植您的素雅中國風) ---
st.markdown("""
    <style>
    /* 1. 設定背景色 (宣紙白) */
    .stApp {
        background-color: #F7F7F2;
    }
    
    /* 2. 設定標題顏色 (豆沙紅) */
    h1 {
        color: #8C5042 !important;
        font-family: "KaiTi", "BiauKai", "Microsoft JhengHei", serif;
        text-align: center;
    }
    
    /* 3. 設定文字顏色 (墨灰) */
    .stMarkdown, .stRadio, label {
        color: #333333 !important;
        font-family: "KaiTi", "BiauKai", "Microsoft JhengHei", serif;
        font-size: 1.2rem !important;
    }
    
    /* 4. 修改按鈕樣式 (豆沙紅底白字) */
    div.stButton > button {
        background-color: #8C5042;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 0.5rem 1rem;
        font-size: 1.2rem;
        width: 100%;
    }
    div.stButton > button:hover {
        background-color: #A52A2A;
        color: #FFD700;
        border: 1px solid #FFD700;
    }
    
    /* 5. 結果顯示區塊 (絹布色) */
    .result-box {
        background-color: #EBEAD5;
        border: 1px solid #8C5042;
        padding: 20px;
        border-radius: 5px;
        text-align: center;
        margin-top: 20px;
        color: #2B2B2B;
        font-size: 1.5rem;
        font-family: "KaiTi", "BiauKai", "Microsoft JhengHei", serif;
    }
    </style>
""", unsafe_allow_html=True)

# --- 標題 ---
st.title("萬年曆轉換系統")
st.markdown("---") # 分隔線代替墨痕

# --- 輔助函式：繁體轉換 ---
def to_traditional_chinese(simplified_str):
    mapping = {'龙': '龍', '马': '馬', '鸡': '雞', '猪': '豬', '闰': '閏', '腊': '臘', '颜': '顏'}
    result = simplified_str
    for s, t in mapping.items():
        result = result.replace(s, t)
    return result

# --- 介面佈局 ---
# 使用 col1, col2 置中排列
col1, col2, col3 = st.columns([1, 6, 1])

with col2:
    # 模式選擇
    mode = st.radio("請選擇轉換模式：", ["國曆 轉 農曆", "農曆 轉 國曆"], horizontal=True)

    # 輸入區 (分成三欄)
    c1, c2, c3 = st.columns(3)
    with c1:
        y = st.number_input("年", min_value=1900, max_value=2100, value=2024, step=1)
    with c2:
        m = st.number_input("月", min_value=1, max_value=12, value=1, step=1)
    with c3:
        d = st.number_input("日", min_value=1, max_value=31, value=1, step=1)

    # 閏月勾選 (只有農曆轉國曆才顯示)
    is_leap = False
    if mode == "農曆 轉 國曆":
        is_leap = st.checkbox("輸入的是閏月 (如閏二月)")

    st.write("") # 空行
    
    # 按鈕與邏輯
    if st.button("開始轉換"):
        try:
            # 判斷民國年 (網頁版輸入框我們限制 1900-2100，通常使用者會輸入西元，這裡做個相容)
            # 如果使用者想輸入民國 113，我們自動幫他加
            calc_year = y
            if y < 1900:
                calc_year = y + 1911
                display_year = f"民國 {y}"
            else:
                display_year = f"西元 {y}"

            # --- 邏輯處理 ---
            if mode == "國曆 轉 農曆":
                solar = datetime(calc_year, m, d)
                lunar = ZhDate.from_datetime(solar)
                trad_lunar = to_traditional_chinese(lunar.chinese())
                
                result_html = f"""
                <div class="result-box">
                    <b>【輸入國曆】</b><br>{display_year} 年 {m} 月 {d} 日<br><br>
                    <b>【轉換農曆】</b><br>{trad_lunar}
                </div>
                """
                st.markdown(result_html, unsafe_allow_html=True)
                
            else: # 農曆 轉 國曆
                lunar = ZhDate(calc_year, m, d, leap_month=is_leap)
                solar_dt = lunar.to_datetime()
                minguo_y = solar_dt.year - 1911
                week_days = ["週一", "週二", "週三", "週四", "週五", "週六", "週日"]
                w_day = week_days[solar_dt.weekday()]
                leap_txt = "(閏)" if is_leap else ""
                
                result_html = f"""
                <div class="result-box">
                    <b>【輸入農曆】</b><br>{display_year} 年 {m} 月 {d} 日 {leap_txt}<br><br>
                    <b>【轉換國曆】</b><br>西元 {solar_dt.year} 年 {solar_dt.month} 月 {solar_dt.day} 日<br>
                    (民國 {minguo_y} 年) {w_day}
                </div>
                """
                st.markdown(result_html, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"轉換失敗：日期無效或不存在！")
