import streamlit as st
import pandas as pd
from datetime import datetime
import os
from github import Github
import io

# --- 1. アプリ設定 ---
st.set_page_config(page_title="破滅回避カウンター", layout="centered")
st.title("💸 破滅回避カウンター v2.0")

# --- 2. GitHub 認証 ---
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN")
REPO_NAME = "chimabird-glitch/cihma"
SHEET_URL = "https://docs.google.com/spreadsheets/d/1mKbibR5Ua-6_s-mP8xq1BLAWdK9Gbmg1OQcEBflOWQ8/edit?gid=0#gid=0"

if not GITHUB_TOKEN:
    st.error("❌ GITHUB_TOKEN が設定されていません")
    st.stop()

# GitHub リポジトリ接続
try:
    g = Github(GITHUB_TOKEN)
    repo = g.get_repo(REPO_NAME)
except Exception as e:
    st.error(f"❌ GitHub 接続エラー: {e}")
    st.stop()

# --- 3. ユーザー選択 ---
st.sidebar.title("👤 ユーザー選択")
user = st.sidebar.radio("誰ですか？", ["なおと", "あいり"], key="user_select")

# --- 4. CSV ファイル名 ---
csv_filename = f"{user}.csv"

# --- 5. GitHub から CSV を読み込む ---
@st.cache_data(ttl=60)
def load_csv_from_github(filename):
    try:
        contents = repo.get_contents(filename)
        df = pd.read_csv(io.StringIO(contents.decoded_content.decode()))
        return df
    except:
        # ファイルが存在しない場合は空の DataFrame を作成
        return pd.DataFrame(columns=["日付", "ユーザー", "項目", "金額"])

# --- 6. GitHub に CSV を保存 ---
def save_csv_to_github(df, filename, message):
    csv_content = df.to_csv(index=False)
    try:
        contents = repo.get_contents(filename)
        repo.update_file(contents.path, message, csv_content, contents.sha)
    except:
        repo.create_file(filename, message, csv_content)

# --- 7. データ読み込み ---
df = load_csv_from_github(csv_filename)

# --- 8. マスター設定（過去のクソな自分） ---
with st.sidebar.expander("⚙️ 過去のクソな自分設定", expanded=False):
    st.write("何もしなければ毎日使っていた金額を入力するでち")
    old_smoke = st.number_input("タバコ代/日", value=620)
    old_coffee = st.number_input("コーヒー・飲料/日", value=800)
    old_food = st.number_input("平均食費/日", value=1500)
    old_extra = st.number_input("その他無駄（月平均÷30）", value=1000)
    
    daily_old_total = old_smoke + old_coffee + old_food + old_extra
    st.error(f"過去の自分は毎日【{daily_old_total:,}円】ドブに捨てていたでち。")

# --- 9. セッション状態初期化 ---
if 'today_logs' not in st.session_state:
    st.session_state.today_logs = []

# --- 10. メイン画面：入力 ---
st.subheader(f"📊 {user} - 今日の断罪入力")
cols = st.columns(3)

# 各ボタンの定義
inputs = {
    "🚬 タバコ": 620,
    "☕ コーヒー": 160,
    "🍱 食費": 500,
    "🍻 趣味・飲み": 1000,
    "💀 その他無駄": 100
}

# 3列でボタンを配置
for i, (name, price) in enumerate(inputs.items()):
    col_idx = i % 3
    if cols[col_idx].button(f"{name}\n{price}円"):
        st.session_state.today_logs.append({"item": name, "price": price})
        st.toast(f"{name}を計上。地獄へ一歩近づいたでち...", icon="🚨")

# 自由入力（高額な趣味代など）
extra_price = st.number_input("自由入力（上記以外の金額）", min_value=0, step=100)
if st.button("自由入力を追加"):
    st.session_state.today_logs.append({"item": "自由入力", "price": extra_price})

# --- 11. 集計表示 ---
st.divider()
today_sum = sum(item['price'] for item in st.session_state.today_logs)

c1, c2 = st.columns(2)
c1.metric("本日の総支出", f"{today_sum:,} 円")
c2.metric(f"{user}の累計", f"{df['金額'].sum():,.0f} 円" if len(df) > 0 else "0 円")

# --- 12. 未来予測（絶望のコーナー） ---
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

# --- 13. 保存ボタン ---
st.divider()
if st.button("💾 今日のデータを保存"):
    if len(st.session_state.today_logs) > 0:
        # 新しい行を作成
        today_date = datetime.now().strftime("%Y-%m-%d")
        new_rows = []
        for log in st.session_state.today_logs:
            new_rows.append({
                "日付": today_date,
                "ユーザー": user,
                "項目": log["item"],
                "金額": log["price"]
            })
        
        new_df = pd.DataFrame(new_rows)
        updated_df = pd.concat([df, new_df], ignore_index=True)
        
        # GitHub に保存
        save_csv_to_github(updated_df, csv_filename, f"Add {user}'s expenses for {today_date}")
        
        st.success(f"✅ {len(st.session_state.today_logs)} 件のデータを保存しました！")
        st.balloons()
        
        # キャッシュをリセット
        st.cache_data.clear()
        
        # データをリセット
        st.session_state.today_logs = []
        st.rerun()
    else:
        st.warning("⚠️ 今日のデータがありません")

# --- 14. 履歴表示 ---
st.divider()
st.subheader(f"📋 {user} の履歴")
if len(df) > 0:
    st.dataframe(df, use_container_width=True)
    st.info(f"📌 合計: **{df['金額'].sum():,.0f} 円** ({len(df)} 件)")
    st.write(f"📊 Google Sheet で確認: [クリック]({SHEET_URL})")
else:
    st.info("まだデータがありません")

# リセットボタン
if st.sidebar.button("🔄 今日のセッションをリセット"):
    st.session_state.today_logs = []
    st.rerun()
