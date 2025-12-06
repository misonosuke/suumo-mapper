from flask import Flask, request, render_template_string
import pandas as pd
import plotly.express as px
import os

app = Flask(__name__)

# CSVファイル設定
CSV_FILE = 'suumo_bukken_mod_23_2025-12-06.csv'

# HTMLテンプレート（簡易デザイン）
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>不動産坪単価マップ</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #f8f9fa; padding: 20px; }
        .map-container { background: white; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    </style>
</head>
<body>
    <div class="container">
        <h2 class="mb-4">🏙️ 不動産坪単価マップ (Flask版)</h2>
        
        <div class="card mb-4">
            <div class="card-body">
                <form method="get" class="row g-3 align-items-end">
                    <div class="col-md-3">
                        <label class="form-label">坪単価 (万円/坪) 下限</label>
                        <input type="number" name="min_price" class="form-control" value="{{ min_price }}">
                    </div>
                    <div class="col-md-3">
                        <label class="form-label">坪単価 (万円/坪) 上限</label>
                        <input type="number" name="max_price" class="form-control" value="{{ max_price }}">
                    </div>
                    <div class="col-md-3">
                        <button type="submit" class="btn btn-primary w-100">検索</button>
                    </div>
                    <div class="col-md-3">
                        <a href="/" class="btn btn-outline-secondary w-100">リセット</a>
                    </div>
                </form>
            </div>
        </div>

        {% if error %}
            <div class="alert alert-danger">{{ error }}</div>
        {% else %}
            <div class="mb-2 text-end text-muted">
                該当件数: <strong>{{ count }}</strong> 件
            </div>
            <div class="map-container">
                {{ plot_html|safe }}
            </div>
        {% endif %}
    </div>
</body>
</html>
"""

def load_data():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)
    return pd.DataFrame()

@app.route('/', methods=['GET'])
def index():
    df = load_data()
    
    if df.empty:
        return render_template_string(HTML_TEMPLATE, error="CSVファイルが読み込めませんでした。", min_price=0, max_price=10000, count=0, plot_html="")

    # フィルタパラメータ取得
    try:
        min_price = int(request.args.get('min_price', 0))
        max_price = int(request.args.get('max_price', 10000))
    except ValueError:
        min_price = 0
        max_price = 10000

    # フィルタリング
    # データフレームの列名は実際のCSVに合わせています
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
            hover_data=["価格(万円)", "駅名", "築年数"],
            color_continuous_scale=px.colors.sequential.Jet,
            size_max=15,
            zoom=10,
            mapbox_style="carto-positron",
            height=600
        )
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        plot_html = fig.to_html(full_html=False, include_plotlyjs='cdn')
    else:
        plot_html = "<p class='text-center py-5'>条件に一致する物件がありません。</p>"

    return render_template_string(
        HTML_TEMPLATE, 
        plot_html=plot_html, 
        min_price=min_price, 
        max_price=max_price,
        count=len(df_filtered),
        error=None
    )

if __name__ == '__main__':
    # App Runner用のポート設定
    app.run(host='0.0.0.0', port=8080)