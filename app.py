from flask import Flask, request, render_template_string
import pandas as pd
import plotly.express as px
import os

app = Flask(__name__)

# CSVファイル名（リポジトリ内のファイル）
DEFAULT_CSV = 'suumo_bukken_mod_23_2025-12-06.csv'

# HTMLテンプレート（簡易版）
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>不動産マップ (Flask版)</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>body { padding: 20px; }</style>
</head>
<body>
<div class="container">
    <h2 class="mb-4">🏙️ 不動産坪単価マップ</h2>
    
    <div class="card mb-4">
        <div class="card-body">
            <form method="get" class="row g-3">
                <div class="col-md-3">
                    <label class="form-label">坪単価 (万円) 下限</label>
                    <input type="number" name="min_price" class="form-control" value="{{ min_price }}">
                </div>
                <div class="col-md-3">
                    <label class="form-label">坪単価 (万円) 上限</label>
                    <input type="number" name="max_price" class="form-control" value="{{ max_price }}">
                </div>
                <div class="col-12">
                    <button type="submit" class="btn btn-primary">条件適用</button>
                    <a href="/" class="btn btn-secondary">リセット</a>
                </div>
            </form>
        </div>
    </div>

    <div class="mb-3">
        <strong>表示件数:</strong> {{ count }} 件
    </div>
    
    <div>
        {{ plot_html|safe }}
    </div>
</div>
</body>
</html>
"""

def load_data():
    if os.path.exists(DEFAULT_CSV):
        return pd.read_csv(DEFAULT_CSV)
    return pd.DataFrame()

@app.route('/', methods=['GET'])
def index():
    df = load_data()
    
    if df.empty:
        return "CSVファイルが見つかりません。リポジトリにファイルを配置してください。"

    # フィルタ条件の取得
    min_price = request.args.get('min_price', type=int, default=0)
    max_price = request.args.get('max_price', type=int, default=10000)

    # データのフィルタリング
    # カラム名はCSVに合わせて '不動産単価（万／坪）' を使用
    mask = (df['不動産単価（万／坪）'] >= min_price) & (df['不動産単価（万／坪）'] <= max_price)
    df_filtered = df[mask]

    # マップ作成
    if not df_filtered.empty:
        fig = px.scatter_mapbox(
            df_filtered,
            lat="緯度",
            lon="経度",
            color="不動産単価（万／坪）",
            size="不動産単価（万／坪）",
            hover_name="物件名",
            color_continuous_scale=px.colors.sequential.Jet,
            size_max=15,
            zoom=10,
            mapbox_style="carto-positron",
            height=600
        )
        plot_html = fig.to_html(full_html=False)
    else:
        plot_html = "<p class='alert alert-warning'>条件に一致する物件がありません。</p>"

    return render_template_string(
        HTML_TEMPLATE, 
        plot_html=plot_html, 
        min_price=min_price, 
        max_price=max_price,
        count=len(df_filtered)
    )

if __name__ == '__main__':
    # App Runnerはポート8080で待機
    app.run(host='0.0.0.0', port=8080)