import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. アプリ設定 ---
st.set_page_config(page_title="破滅回避カウンター", layout="centered")
st.title("💸 破滅回避カウンター v1.0")

# --- 2. マスター設定（過去のクソな自分） ---
with st.sidebar.expander("⚙️ 過去のクソな自分設定", expanded=False):
    st.write("何もしなければ毎日使っていた金額を入力するでち")
    old_smoke = st.number_input("タバコ代/日", value=620)
    old_coffee = st.number_input("コーヒー・飲料/日", value=800)
    old_food = st.number_input("平均食費/日", value=1500)
    old_extra = st.number_input("その他無駄（月平均÷30）", value=1000)
    
    daily_old_total = old_smoke + old_coffee + old_food + old_extra
    st.error(f"過去の自分は毎日【{daily_old_total:,}円】ドブに捨てていたでち。")

# --- 3. データ保持（セッション状態） ---
if 'today_logs' not in st.session_state:
    st.session_state.today_logs = []
if 'history_total' not in st.session_state:
    st.session_state.history_total = 0

# --- 4. メイン画面：入力 ---
st.subheader("📊 今日の断罪入力")
cols = st.columns(3)

# 各ボタンの定義
inputs = {
    "🚬 タバコ": 620,
    "☕ コーヒー": 160,
    "🍱 食費": 500,
    "🍻 趣味・飲み": 1000,
    "💀 その他無駄": 100
}

# 2列でボタンを配置
for i, (name, price) in enumerate(inputs.items()):
    col_idx = i % 3
    if cols[col_idx].button(f"{name}\n{price}円"):
        st.session_state.today_logs.append({"item": name, "price": price})
        st.session_state.history_total += price
        st.toast(f"{name}を計上。地獄へ一歩近づいたでち...", icon="🚨")

# 自由入力（高額な趣味代など）
extra_price = st.number_input("自由入力（上記以外の金額）", min_value=0, step=100)
if st.button("自由入力を追加"):
    st.session_state.today_logs.append({"item": "自由入力", "price": extra_price})
    st.session_state.history_total += extra_price

# --- 5. 集計表示 ---
st.divider()
today_sum = sum(item['price'] for item in st.session_state.today_logs)

c1, c2 = st.columns(2)
c1.metric("本日の総支出", f"{today_sum:,} 円")
c2.metric("アプリ開始からの累計", f"{st.session_state.history_total:,} 円")

# --- 6. 未来予測（絶望のコーナー） ---
st.subheader("🔮 未来の損失予測")
tab1, tab2, tab3 = st.tabs(["1ヶ月", "1年", "5年"])

with tab1:
    st.write(f"1ヶ月の損失: **{(today_sum * 30):,} 円**")
with tab2:
    st.write(f"1年の損失: **{(today_sum * 365):,} 円**")
with tab3:
    st.error(f"5年の損失: **{(today_sum * 365 * 5):,} 円**")
    st.write("※これだけあれば社保なんて余裕で払えたでちね。")

# 過去の自分との比較
diff = daily_old_total - today_sum
if diff > 0:
    st.success(f"✨ 過去のクソな自分より **{diff:,}円** 節約できてるでち！この調子でち！")
else:
    st.warning(f"👹 過去の自分より **{abs(diff):,}円** 多く使ってるでち。破滅に向かってるでち。")

# リセットボタン
if st.sidebar.button("今日のデータをリセット"):
    st.session_state.today_logs = []
    st.rerun()
