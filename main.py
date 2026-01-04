import streamlit as st
from zhdate import ZhDate
from datetime import datetime
import calendar

# --- 網頁設定 ---
st.set_page_config(page_title="素雅萬年曆", page_icon="📅", layout="wide")

# --- CSS 樣式 (素雅中國風) ---
st.markdown("""
    <style>
    /* 全域設定 */
    .stApp { background-color: #F7F7F2; }
    
    /* 強制設定所有字體 */
    h1, h2, h3, p, div, label, input, .stMarkdown, span, th, td {
        font-family: "KaiTi", "BiauKai", "Microsoft JhengHei", serif !important;
        color: #333333;
    }

    h1 { color: #8C5042 !important; text-align: center; margin-bottom: 20px; }
    
    /* 輸入框樣式 */
    div[data-baseweb="input"] > div {
        background-color: white; 
        border: 1px solid #ccc;
        color: #333333;
        border-radius: 4px;
    }
    /* 隱藏輸入框的加減按鈕 */
    button[kind="secondary"] { border: none; background: transparent; }

    /* 左側結果區 */
    .result-box {
        background-color: #EBEAD5;
        border: 1px solid #8C5042;
        padding: 20px;
        border-radius: 5px;
        text-align: center;
        margin-top: 15px;
        font-size: 1.3rem;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    
    /* --- 右側日曆容器樣式 --- */
    .calendar-container {
        background-color: white;
        border: 2px solid #8C5042;
        border-radius: 8px;
        padding: 10px;
        box-shadow: 3px 3px 8px rgba(0,0,0,0.1);
        width: 100%;
        margin: 0 auto;
    }
    .cal-header {
        text-align: center;
        font-size: 1.4rem;
        font-weight: bold;
        color: #8C5042;
        margin-bottom: 8px;
        border-bottom: 1px dashed #8C5042;
        padding-bottom: 5px;
    }
    table.cal-table {
        width: 100%;
        text-align: center;
        border-collapse: collapse;
    }
    th { color: #888; font-weight: normal; padding: 5px; font-size: 1rem; border-bottom: 1px solid #eee;}
    
    td { 
        padding: 2px; 
        vertical-align: top; 
        height: 60px; 
        width: 14.28%; 
        border: 1px solid #f9f9f9;
    }
    
    /* 日期格子內容 */
    .day-cell {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100%;
        width: 100%;
        border-radius: 5px;
        cursor: default;
    }
    
    .solar-num { font-size: 1.1rem; font-weight: bold; line-height: 1.2; }
    .lunar-num { font-size: 0.7rem; color: #999; line-height: 1; margin-top: 2px; }

    /* 選中日期樣式 (紅底金字) */
    .selected-day-bg {
        background-color: #8C5042;
        border-radius: 4px;
    }
    .selected-day-bg .solar-num { color: white !important; }
    .selected-day-bg .lunar-num { color: #FFD700 !important; }
    
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
L_MONTHS = ["", "正月", "二月", "三月", "四月", "五月", "六月", "七月", "八月", "九月", "十月", "冬月", "臘月"]
L_DAYS = ["", "初一", "初二", "初三", "初四", "初五", "初六", "初七", "初八", "初九", "初十",
          "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八", "十九", "二十",
          "廿一", "廿二", "廿三", "廿四", "廿五", "廿六", "廿七", "廿八", "廿九", "三十"]

def get_lunar_text(solar_date):
    try:
        ld = ZhDate.from_datetime(solar_date)
        if ld.lunar_day == 1:
            leap_str = "閏" if ld.leap_month else ""
            return f"{leap_str}{L_MONTHS[ld.lunar_month]}"
        else:
            return L_DAYS[ld.lunar_day]
    except:
        return ""

def to_traditional_chinese(simplified_str):
    mapping = {'龙': '龍', '马': '馬', '鸡': '雞', '猪': '豬', '闰': '閏', '腊': '臘', '颜': '顏'}
    result = simplified_str
    for s, t in mapping.items():
        result = result.replace(s, t)
    return result

def generate_calendar_html(year, month, highlight_day):
    cal = calendar.Calendar(firstweekday=6)
    month_days = cal.monthdayscalendar(year, month)
    
    html = f"""
    <div class="calendar-container">
        <div class="cal-header">{year}年 {month}月</div>
        <table class="cal-table">
            <thead>
                <tr>
                    <th style="color:#D2222D">日</th>
                    <th>一</th><th>二</th><th>三</th><th>四</th><th>五</th>
                    <th style="color:#228B22">六</th>
                </tr>
            </thead>
            <tbody>
    """
    for week in month_days:
        html += "<tr>"
        for day in week:
            if day == 0:
                html += "<td></td>"
            else:
                curr_date = datetime(year, month, day)
                lunar_txt = get_lunar_text(curr_date)
                cell_class = "day-cell"
                if day == highlight_day:
                    cell_class += " selected-day-bg"
                
                html += f"""
                <td>
                    <div class="{cell_class}">
                        <div class="solar-num">{day}</div>
                        <div class="lunar-num">{lunar_txt}</div>
                    </div>
                </td>
                """
        html += "</tr>"
    html += "</tbody></table></div>"
    return html

# --- 主程式 ---
st.title("萬年曆轉換系統")

col_main, col_side = st.columns([1.8, 1.2])

# 左側：輸入與結果
with col_main:
    mode = st.radio("轉換模式：", ["國曆 轉 農曆", "農曆 轉 國曆"], horizontal=True)
    st.write("") 
    
    c1, c2, c3 = st.columns(3)
    
    with c1:
        # 輸入框：輸入完按 Enter 即可
        y = st.number_input("年", min_value=1, max_value=2100, value=2024, step=1, format="%d")
        if y < 1900:
            st.markdown(f"<div class='hint-text'>民國 {y} 年</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='hint-text'>西元 {y} 年</div>", unsafe_allow_html=True)
            
    with c2:
        m = st.number_input("月", min_value=1, max_value=12, value=1, step=1, format="%d")
    with c3:
        d = st.number_input("日", min_value=1, max_value=31, value=1, step=1, format="%d")

    is_leap = False
    if mode == "農曆 轉 國曆":
        is_leap = st.checkbox("輸入的是閏月")

    try:
        # 自動判斷
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
                <span style="font-size: 0.9em; color: #666;">【輸入國曆】</span><br>
                <b>{display_year_str} 年 {m} 月 {d} 日</b><br><br>
                <span style="font-size: 0.9em; color: #666;">【轉換農曆】</span><br>
                <b style="color: #8C5042; font-size: 1.6rem;">{trad_lunar}</b>
            </div>
            """, unsafe_allow_html=True)
            
            cal_year, cal_month, cal_day = calc_year, m, d

        else: # 農曆 轉 國曆
            lunar = ZhDate(calc_year, m, d, leap_month=is_leap)
            solar_dt = lunar.to_datetime()
            minguo_y = solar_dt.year - 1911
            week_days = ["週一", "週二", "週三", "週四", "週五", "週六", "週日"]
            w_day = week_days[solar_dt.weekday()]
            leap_txt = "(閏)" if is_leap else ""
            
            st.markdown(f"""
            <div class="result-box">
                <span style="font-size: 0.9em; color: #666;">【輸入農曆】</span><br>
                <b>{display_year_str} 年 {m} 月 {d} 日 {leap_txt}</b><br><br>
                <span style="font-size: 0.9em; color: #666;">【轉換國曆】</span><br>
                <b style="color: #8C5042; font-size: 1.6rem;">西元 {solar_dt.year} 年 {solar_dt.month} 月 {solar_dt.day} 日</b><br>
                (民國 {minguo_y} 年) {w_day}
            </div>
            """, unsafe_allow_html=True)
            
            cal_year, cal_month, cal_day = solar_dt.year, solar_dt.month, solar_dt.day

    except Exception:
        cal_year, cal_month, cal_day = calc_year, m, 0

# 右側：日曆顯示區
with col_side:
    st.markdown("<div style='margin-top: 60px;'></div>", unsafe_allow_html=True)
    
    if 'cal_year' in locals():
        cal_html = generate_calendar_html(cal_year, cal_month, cal_day)
        
        # 【關鍵修復】
        # 這裡的 unsafe_allow_html=True 絕對不能少！
        st.markdown(cal_html, unsafe_allow_html=True)
