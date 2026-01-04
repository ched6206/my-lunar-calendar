import streamlit as st
from zhdate import ZhDate
from datetime import datetime

# --- 網頁設定 ---
st.set_page_config(page_title="素雅萬年曆", page_icon="📅")

# --- CSS 樣式 (素雅中國風) ---
st.markdown("""
    <style>
    .stApp { background-color: #F7F7F2; }
    
    h1 {
        color: #8C5042 !important;
        font-family: "KaiTi", "BiauKai", "Microsoft JhengHei", serif;
        text-align: center;
        margin-bottom: 0px;
    }
    
    /* 調整所有標籤文字顏色 */
    .stSelectbox label, .stRadio label, .stCheckbox label {
        color: #333333 !important;
        font-family: "KaiTi", "BiauKai", "Microsoft JhengHei", serif;
        font-size: 1.1rem !important;
    }
    
    /* 調整選單本體顏色 (白底黑字) */
    div[data-baseweb="select"] > div {
        background-color: white;
        border: 1px solid #ccc;
        color: #333333;
    }
    
    /* 按鈕樣式 */
    div.stButton > button {
        background-color: #8C5042;
        color: white;
        border: none;
        width: 100%;
        margin-top: 10px;
    }
    div.stButton > button:hover {
        background-color: #A52A2A;
        border: 1px solid #FFD700;
        color: #FFD700;
    }
    
    /* 結果顯示區 */
    .result-box {
        background-color: #EBEAD5;
        border: 1px solid #8C5042;
        padding: 20px;
        border-radius: 5px;
        text-align: center;
        margin-top: 20px;
        color: #2B2B2B;
        font-size: 1.4rem;
        font-family: "KaiTi", "BiauKai", "Microsoft JhengHei", serif;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# --- 標題 ---
st.title("萬年曆轉換系統")
st.markdown("<div style='text-align: center; color: #aaa; margin-bottom: 20px;'>⎯⎯  請選擇或輸入日期  ⎯⎯</div>", unsafe_allow_html=True)

# --- 輔助函式 ---
def to_traditional_chinese(simplified_str):
    mapping = {'龙': '龍', '马': '馬', '鸡': '雞', '猪': '豬', '闰': '閏', '腊': '臘', '颜': '顏'}
    result = simplified_str
    for s, t in mapping.items():
        result = result.replace(s, t)
    return result

# --- 準備下拉選單的資料 ---

# 1. 年份清單 (1900 ~ 2100)
# 我們產生一個數字列表，ZhDate 支援範圍通常是 1900-2100
year_list = list(range(1900, 2101))
# 設定預設年份索引 (例如預設選 2024，需找出 2024 在清單中的位置)
default_year_index = year_list.index(2024)

# 2. 顯示年份的格式函式 (讓選單同時顯示西元和民國)
def format_year_func(y):
    # 顯示格式： "2024 (民國113年)"
    # 這樣使用者打 "2024" 或打 "113" 都可以搜到
    if y > 1911:
        return f"{y} (民國{y-1911}年)"
    elif y == 1911:
        return f"{y} (民國元年)"
    else:
        return f"{y} (民前{1912-y}年)"

# --- 主介面 ---

mode = st.radio("請選擇模式：", ["國曆 轉 農曆", "農曆 轉 國曆"], horizontal=True)

with st.form(key='date_form'):
    
    c1, c2, c3 = st.columns(3)
    
    with c1:
        # 年：使用 selectbox
        # key point: format_func 讓它顯示民國，使用者可以打字搜尋
        y = st.selectbox(
            "年 (可打字搜尋)", 
            options=year_list, 
            index=default_year_index, 
            format_func=format_year_func
        )
        
    with c2:
        # 月：1~12
        m = st.selectbox(
            "月", 
            options=range(1, 13), 
            format_func=lambda x: f"{x}月"
        )
        
    with c3:
        # 日：1~31
        d = st.selectbox(
            "日", 
            options=range(1, 32), 
            format_func=lambda x: f"{x}日"
        )

    # 閏月勾選
    is_leap = False
    if mode == "農曆 轉 國曆":
        is_leap = st.checkbox("輸入的是閏月")
    
    submit_btn = st.form_submit_button(label="開始轉換")

# --- 邏輯處理 ---
if submit_btn:
    try:
        # y 這裡取回來的是西元數字 (因為 options 是 year_list 數字列表)
        # 顯示用的字串 (西元/民國)
        if y >= 1912:
            display_year = f"西元 {y} (民國 {y-1911})"
        else:
            display_year = f"西元 {y}"

        # 轉換邏輯
        if mode == "國曆 轉 農曆":
            solar = datetime(y, m, d)
            lunar = ZhDate.from_datetime(solar)
            trad_lunar = to_traditional_chinese(lunar.chinese())
            
            result_html = f"""
            <div class="result-box">
                <span style="font-size: 0.9em; color: #666;">【輸入國曆】</span><br>
                <b>{display_year} 年 {m} 月 {d} 日</b><br><br>
                <span style="font-size: 0.9em; color: #666;">【轉換農曆】</span><br>
                <b style="color: #8C5042;">{trad_lunar}</b>
            </div>
            """
            st.markdown(result_html, unsafe_allow_html=True)
            
        else: # 農曆 轉 國曆
            lunar = ZhDate(y, m, d, leap_month=is_leap)
            solar_dt = lunar.to_datetime()
            minguo_y = solar_dt.year - 1911
            week_days = ["週一", "週二", "週三", "週四", "週五", "週六", "週日"]
            w_day = week_days[solar_dt.weekday()]
            leap_txt = "(閏)" if is_leap else ""
            
            result_html = f"""
            <div class="result-box">
                <span style="font-size: 0.9em; color: #666;">【輸入農曆】</span><br>
                <b>{display_year} 年 {m} 月 {d} 日 {leap_txt}</b><br><br>
                <span style="font-size: 0.9em; color: #666;">【轉換國曆】</span><br>
                <b style="color: #8C5042;">西元 {solar_dt.year} 年 {solar_dt.month} 月 {solar_dt.day} 日</b><br>
                (民國 {minguo_y} 年) {w_day}
            </div>
            """
            st.markdown(result_html, unsafe_allow_html=True)

    except ValueError:
        st.error(f"❌ 日期無效！請檢查 {y}年{m}月 是否有 {d}日。")
    except Exception as e:
        st.error(f"❌ 發生錯誤：{e}")
