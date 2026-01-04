import streamlit as st
from zhdate import ZhDate
from datetime import datetime

# --- 網頁設定 ---
st.set_page_config(page_title="素雅萬年曆", page_icon="📅")

# --- CSS 樣式 (素雅中國風) ---
st.markdown("""
    <style>
    /* 背景色 */
    .stApp {
        background-color: #F7F7F2;
    }
    
    /* 標題樣式 */
    h1 {
        color: #8C5042 !important;
        font-family: "KaiTi", "BiauKai", "Microsoft JhengHei", serif;
        text-align: center;
        margin-bottom: 0px;
    }
    
    /* 輸入框標籤顏色 */
    .stMarkdown, .stRadio, label, .stCheckbox {
        color: #333333 !important;
        font-family: "KaiTi", "BiauKai", "Microsoft JhengHei", serif;
        font-size: 1.1rem !important;
    }
    
    /* 調整 Number Input 輸入框本體 */
    div[data-baseweb="input"] > div {
        background-color: white; 
        border: 1px solid #ccc;
        color: #333333;
    }

    /* 按鈕樣式 (豆沙紅) */
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
    
    /* 結果顯示區塊 */
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
st.markdown("<div style='text-align: center; color: #aaa; margin-bottom: 20px;'>⎯⎯⎯  輸入日期後按 Enter 即可  ⎯⎯⎯</div>", unsafe_allow_html=True)

# --- 輔助函式 ---
def to_traditional_chinese(simplified_str):
    mapping = {'龙': '龍', '马': '馬', '鸡': '雞', '猪': '豬', '闰': '閏', '腊': '臘', '颜': '顏'}
    result = simplified_str
    for s, t in mapping.items():
        result = result.replace(s, t)
    return result

# --- 主介面 ---

# 1. 模式選擇 (放在最上面，不用包進表單，隨點隨切換)
mode = st.radio("請選擇模式：", ["國曆 轉 農曆", "農曆 轉 國曆"], horizontal=True)

# 2. 【關鍵！】建立一個表單 (Form)
# 表單內的輸入不會立刻重整頁面，直到按 Enter 或 Submit
with st.form(key='date_form'):
    
    # 使用 columns 讓輸入框並排
    c1, c2, c3 = st.columns(3)
    
    with c1:
        # format="%d" 非常重要！這樣輸入 2024 才不會變成 2,024 (有逗號)
        # value=0 預設留給使用者輸入，或者設為今年
        y = st.number_input("年 (西元/民國)", min_value=1, max_value=2100, value=2024, step=1, format="%d")
    with c2:
        m = st.number_input("月", min_value=1, max_value=12, value=1, step=1, format="%d")
    with c3:
        d = st.number_input("日", min_value=1, max_value=31, value=1, step=1, format="%d")

    # 閏月勾選 (只有轉國曆時才需要，但為了版面整齊，我們讓它一直存在，用程式碼控制是否生效)
    is_leap = False
    if mode == "農曆 轉 國曆":
        is_leap = st.checkbox("輸入的是閏月")
    
    # 這就是「提交按鈕」，在表單內，按下 Enter 鍵等同於點擊這個按鈕
    submit_btn = st.form_submit_button(label="開始轉換")

# --- 3. 邏輯處理 (當按下按鈕或 Enter 後執行) ---
if submit_btn:
    try:
        # 自動判斷民國年 (輸入小於1900自動加1911)
        calc_year = y
        if y < 1900:
            calc_year = y + 1911
            display_year = f"民國 {y}"
        else:
            display_year = f"西元 {y}"

        # 轉換邏輯
        if mode == "國曆 轉 農曆":
            solar = datetime(calc_year, m, d)
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
            lunar = ZhDate(calc_year, m, d, leap_month=is_leap)
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
        st.error("❌ 日期不存在！(例如：2月30日 或 該年沒有閏月)")
    except Exception as e:
        st.error(f"❌ 發生錯誤：{e}")
