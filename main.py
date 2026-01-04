import streamlit as st
from zhdate import ZhDate
from datetime import datetime

# --- 網頁設定 ---
st.set_page_config(page_title="素雅萬年曆", page_icon="📅", layout="centered")

# --- CSS 樣式 ---
st.markdown("""
    <style>
    /* 全域背景 */
    .stApp { background-color: #F7F7F2; }
    
    /* 字體設定 (宋體優先) */
    h1, h2, h3, p, div, label, input, .stMarkdown, span, button {
        font-family: "Songti SC", "SimSun", "PMingLiU", "MingLiU", "Microsoft JhengHei", serif !important;
        color: #333333;
    }

    h1 { 
        color: #8C5042 !important; 
        text-align: center; 
        margin-bottom: 25px; 
        font-weight: bold; 
        letter-spacing: 2px;
    }
    
    /* 輸入框樣式 */
    div[data-baseweb="input"] > div {
        background-color: white; 
        border: 1px solid #ccc;
        color: #333333;
        border-radius: 4px;
    }
    button[kind="secondary"] { border: none; background: transparent; }

    /* 結果顯示區 */
    .result-box {
        background-color: #EBEAD5;
        border: 1px solid #8C5042;
        padding: 30px 10px;
        border-radius: 4px;
        text-align: center;
        margin-top: 20px;
        box-shadow: 3px 3px 10px rgba(0,0,0,0.1);
        line-height: 1.6;
        width: 100%;
    }

    /* 結果大字樣式 */
    .result-big-text {
        color: #8C5042;
        font-weight: bold;
        white-space: nowrap;
        font-size: clamp(1.2rem, 5vw, 2.2rem) !important;
    }

    /* 提示文字 */
    .hint-text {
        font-size: 0.9rem;
        color: #888;
        margin-top: -10px;
        margin-bottom: 10px;
        margin-left: 5px;
        font-style: italic;
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
    
    @media (max-width: 768px) {
        h1 { font-size: 1.8rem !important; margin-bottom: 15px; }
        .result-box { margin-top: 10px; }
    }
    </style>
""", unsafe_allow_html=True)

# --- 輔助資料：天干地支與農曆對照 ---
TIAN_GAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
DI_ZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
L_MONTHS = ["", "正月", "二月", "三月", "四月", "五月", "六月", "七月", "八月", "九月", "十月", "冬月", "臘月"]
L_DAYS = ["", "初一", "初二", "初三", "初四", "初五", "初六", "初七", "初八", "初九", "初十",
          "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八", "十九", "二十",
          "廿一", "廿二", "廿三", "廿四", "廿五", "廿六", "廿七", "廿八", "廿九", "三十"]

# --- 核心函式：自訂農曆格式 ---
def format_custom_lunar(lunar_obj):
    """
    將 zhdate 物件轉換為格式：乙巳年（2025）五月初二
    """
    # 1. 計算天干地支
    # 西元 4 年是甲子年，以此類推
    year = lunar_obj.lunar_year
    gan_index = (year - 4) % 10
    zhi_index = (year - 4) % 12
    gan_zhi = f"{TIAN_GAN[gan_index]}{DI_ZHI[zhi_index]}"
    
    # 2. 處理月份 (含閏月判斷)
    # zhdate 的 leap_month 屬性若為非0，代表該年有閏月；
    # 但我們要判斷「當前月份」是否為閏月，zhdate 0.4.0+ 通常會直接處理，
    # 這裡我們用更保險的方式：直接讀取數值轉換
    month_text = L_MONTHS[lunar_obj.lunar_month]
    
    # 檢查 zhdate 物件內部屬性來判斷是否顯示「閏」字
    # 註：不同版本的 zhdate 對閏月的處理字串不同，這裡我們手動組裝最保險
    # 如果 zhdate 內建的 chinese() 輸出包含 "闰" 或 "閏"，且月份對得上，則加上閏字
    # 但更簡單的是直接信賴 zhdate 的計算，我們只負責組字串
    is_leap = getattr(lunar_obj, "leap_month", 0) == lunar_obj.lunar_month
    # 注意：zhdate 的 leap_month 屬性是指出「哪個月是閏月」，不是「現在是不是閏月」
    # 嚴謹判斷：zhdate 物件通常是 ZhDate(year, month, day, leap_month=True/False)
    # 不過為了簡化，我們直接看月份和日期文字
    
    # 這裡採用最簡單暴力的字串重組法，確保文字正確
    leap_prefix = "閏" if (getattr(lunar_obj, "leap_month", 0) == lunar_obj.lunar_month and getattr(lunar_obj, "is_leap", False)) else ""
    # 修正：zhdate 庫比較單純，我們直接用 chinese() 取得基本資訊會比較亂，
    # 改用我們自己的 L_MONTHS 對照表最漂亮。
    
    # 關於閏月：如果使用者輸入時勾選閏月，或者從國曆轉過來剛好是閏月
    # 從國曆轉過來的 lunar_obj，我們無法直接簡單得知「現在是不是閏月」(is_leap 屬性不一定公開)
    # 變通：從 lunar_obj.chinese() 偷看有沒有「閏」字
    raw_str = lunar_obj.chinese()
    if "闰" in raw_str or "閏" in raw_str:
        # 如果 raw_str 裡有閏，且月份跟我們算的一樣，那就加上閏
        # 這裡做個簡單判斷，如果 chinese() 輸出的月份字串包含 "閏"，我們就加
        if f"闰{L_MONTHS[lunar_obj.lunar_month]}" in raw_str.replace("閏", "闰") or \
           f"閏{L_MONTHS[lunar_obj.lunar_month]}" in raw_str:
            leap_prefix = "閏"
    
    # 3. 處理日期
    day_text = L_DAYS[lunar_obj.lunar_day]
    
    # 4. 組裝最終字串：乙巳年（2025）五月初二
    return f"{gan_zhi}年（{year}）{leap_prefix}{month_text}{day_text}"

def to_traditional_chinese(simplified_str):
    mapping = {'龙': '龍', '马': '馬', '鸡': '雞', '猪': '豬', '闰': '閏', '腊': '臘', '颜': '顏'}
    result = simplified_str
    for s, t in mapping.items():
        result = result.replace(s, t)
    return result

# --- 主程式 ---
st.title("萬年曆轉換系統")

mode = st.radio("轉換模式：", ["國曆 轉 農曆", "農曆 轉 國曆"], horizontal=True)
st.write("") 
    
c1, c2, c3 = st.columns(3)

with c1:
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

is_leap = False
if mode == "農曆 轉 國曆":
    is_leap = st.checkbox("輸入的是閏月")

# --- 轉換邏輯 ---
if y is not None and m is not None and d is not None:
    try:
        if y < 1900:
            calc_year = y + 1911
            display_year_str = f"西元 {calc_year} (民國 {y})"
        else:
            calc_year = y
            display_year_str = f"西元 {y}"

        if mode == "國曆 轉 農曆":
            solar = datetime(calc_year, m, d)
            lunar = ZhDate.from_datetime(solar)
            
            # 【關鍵修改】使用自訂格式化函式
            formatted_lunar = format_custom_lunar(lunar)
            trad_lunar = to_traditional_chinese(formatted_lunar)
            
            st.markdown(f"""
            <div class="result-box">
                <span style="font-size: 0.8em; color: #666;">【輸入國曆】</span><br>
                <b>{display_year_str} 年 {m} 月 {d} 日</b><br><br>
                <span style="font-size: 0.8em; color: #666;">【轉換農曆】</span><br>
                <span class="result-big-text">{trad_lunar}</span>
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
                <span class="result-big-text">西元 {solar_dt.year} 年 {solar_dt.month} 月 {solar_dt.day} 日</span><br>
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
