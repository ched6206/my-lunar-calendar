import streamlit as st
from zhdate import ZhDate
from datetime import datetime
import calendar # 新增日曆模組

# --- 網頁設定 ---
st.set_page_config(page_title="素雅萬年曆", page_icon="📅", layout="wide") # layout="wide" 讓畫面寬一點，才放得下並排

# --- CSS 樣式 (素雅中國風 + 日曆樣式) ---
st.markdown("""
    <style>
    /* 全域背景 */
    .stApp { background-color: #F7F7F2; }
    
    /* 字體設定 */
    h1, h2, h3, p, div, label, .stSelectbox, .stMarkdown {
        font-family: "KaiTi", "BiauKai", "Microsoft JhengHei", serif !important;
        color: #333333 !important;
    }

    h1 { color: #8C5042 !important; text-align: center; margin-bottom: 10px; }
    
    /* 調整選單顏色 */
    div[data-baseweb="select"] > div {
        background-color: white;
        border: 1px solid #ccc;
        color: #333333;
    }
    
    /* 結果顯示區 (左側) */
    .result-box {
        background-color: #EBEAD5;
        border: 1px solid #8C5042;
        padding: 20px;
        border-radius: 5px;
        text-align: center;
        margin-top: 20px;
        font-size: 1.3rem;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    
    /* --- 右側日曆專用樣式 --- */
    .calendar-container {
        background-color: white;
        border: 2px solid #8C5042;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 3px 3px 8px rgba(0,0,0,0.1);
        width: 100%;
        max-width: 350px; /* 限制日曆最大寬度 */
        margin: 0 auto;
    }
    .cal-header {
        text-align: center;
        font-size: 1.5rem;
        font-weight: bold;
        color: #8C5042;
        margin-bottom: 10px;
        border-bottom: 1px dashed #8C5042;
        padding-bottom: 5px;
    }
    table.cal-table {
        width: 100%;
        text-align: center;
        border-collapse: collapse;
        font-size: 1.1rem;
    }
    th { color: #666; font-weight: normal; padding: 5px; }
    td { padding: 8px 2px; }
    
    /* 被選中的日期 (紅圈圈) */
    .selected-day {
        background-color: #8C5042;
        color: white !important;
        border-radius: 50%;
        width: 30px;
        height: 30px;
        display: inline-block;
        line-height: 30px; /* 垂直置中 */
        font-weight: bold;
    }
    .today-marker {
        border: 1px solid #8C5042;
        border-radius: 50%;
        width: 30px;
        height: 30px;
        display: inline-block;
        line-height: 30px;
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

# --- 產生 HTML 日曆的函式 ---
def generate_calendar_html(year, month, highlight_day):
    # 設定週日為第一天
    cal = calendar.Calendar(firstweekday=6)
    month_days = cal.monthdayscalendar(year, month)
    
    # 標題 (例如：2024年 2月)
    html = f"""
    <div class="calendar-container">
        <div class="cal-header">{year}年 {month}月</div>
        <table class="cal-table">
            <thead>
                <tr>
                    <th style="color:#D2222D">日</th> <th>一</th><th>二</th><th>三</th><th>四</th><th>五</th>
                    <th style="color:#228B22">六</th> </tr>
            </thead>
            <tbody>
    """
    
    for week in month_days:
        html += "<tr>"
        for day in week:
            if day == 0:
                html += "<td></td>" # 空白日期
            else:
                # 判斷是否為選中的日期
                if day == highlight_day:
                    cell_content = f'<span class="selected-day">{day}</span>'
                else:
                    cell_content = str(day)
                html += f"<td>{cell_content}</td>"
        html += "</tr>"
    
    html += """
            </tbody>
        </table>
    </div>
    """
    return html

# --- 標題區 ---
st.title("萬年曆轉換系統")
st.markdown("<div style='text-align: center; color: #888; margin-bottom: 25px;'>⎯⎯ 素雅．查詢 ⎯⎯</div>", unsafe_allow_html=True)

# --- 版面配置 (左 2 : 右 1) ---
col_main, col_side = st.columns([1.8, 1])

# ================= 左側：輸入與結果區 =================
with col_main:
    mode = st.radio("轉換模式：", ["國曆 轉 農曆", "農曆 轉 國曆"], horizontal=True)
    
    st.write("") # 空行微調
    
    # 輸入區 (使用 columns 並排)
    c1, c2, c3 = st.columns(3)
    
    # 資料準備
    year_list = list(range(1900, 2101))
    default_year_idx = year_list.index(2024)
    
    def format_year(y):
        if y > 1911: return f"{y} (民國{y-1911})"
        elif y == 1911: return f"{y} (民國元年)"
        else: return f"{y} (西元)"

    with c1:
        # 使用 selectbox 即可直接打字搜尋
        y = st.selectbox("年", options=year_list, index=default_year_idx, format_func=format_year)
    with c2:
        m = st.selectbox("月", options=range(1, 13), format_func=lambda x: f"{x}月")
    with c3:
        d = st.selectbox("日", options=range(1, 32), format_func=lambda x: f"{x}日")

    is_leap = False
    if mode == "農曆 轉 國曆":
        is_leap = st.checkbox("輸入的是閏月")

    # --- 轉換邏輯 (即時執行) ---
    try:
        # 顯示用的年份字串
        if y >= 1912: display_year_str = f"西元 {y} (民國 {y-1911})"
        else: display_year_str = f"西元 {y}"

        if mode == "國曆 轉 農曆":
            # 嘗試建立日期 (檢查日期是否存在)
            solar = datetime(y, m, d)
            lunar = ZhDate.from_datetime(solar)
            trad_lunar = to_traditional_chinese(lunar.chinese())
            
            # 顯示結果
            st.markdown(f"""
            <div class="result-box">
                <span style="font-size: 0.9em; color: #666;">【輸入國曆】</span><br>
                <b>{display_year_str} 年 {m} 月 {d} 日</b><br><br>
                <span style="font-size: 0.9em; color: #666;">【轉換農曆】</span><br>
                <b style="color: #8C5042; font-size: 1.6rem;">{trad_lunar}</b>
            </div>
            """, unsafe_allow_html=True)
            
            # 設定日曆要顯示的日期 (就是輸入的日期)
            cal_year, cal_month, cal_day = y, m, d

        else: # 農曆 轉 國曆
            lunar = ZhDate(y, m, d, leap_month=is_leap)
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

            # 農曆轉國曆時，日曆應該顯示「轉換出來的國曆」
            cal_year, cal_month, cal_day = solar_dt.year, solar_dt.month, solar_dt.day

    except ValueError:
        st.error(f"❌ 無效日期！請檢查 {m}月 是否有 {d}日。")
        cal_year, cal_month, cal_day = y, m, 0 # 出錯時日曆不圈選
    except Exception as e:
        st.error(f"錯誤：{e}")
        cal_year, cal_month, cal_day = y, m, 0

# ================= 右側：日曆顯示區 =================
with col_side:
    st.write("") # 排版微調，讓日曆跟輸入框對齊
    st.write("") 
    # 呼叫產生 HTML 的函式
    if 'cal_year' in locals():
        cal_html = generate_calendar_html(cal_year, cal_month, cal_day)
        st.markdown(cal_html, unsafe_allow_html=True)
