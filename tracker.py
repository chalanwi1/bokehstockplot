from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def home():
    from pandas_datareader._utils import RemoteDataError
    from pandas_datareader import data
    from datetime import datetime
    from bokeh.plotting import figure
    from bokeh.embed import components
    from bokeh.resources import CDN

    if request.method == 'GET':
        return render_template('home.html')

    elif request.method == 'POST':

        start = datetime.strptime(request.form['start'], '%Y-%m-%d')

        end = datetime.strptime(request.form['end'], '%Y-%m-%d')

        symbol = request.form['stock'].upper()

        try:
            df = data.DataReader(name=symbol, data_source='yahoo', start=start, end=end)
        except RemoteDataError:
            return render_template('invsym.html')

        def inc_dec(c, o):
            if c > o:
                value = 'Increase'
            elif c < o:
                value = 'Decrease'
            else:
                value = 'Equal'
            return value

        df['Status'] = [inc_dec(c, o) for c, o in zip(df.Close, df.Open)]
        df['Middle'] = (df.Open + df.Close) / 2
        df['Height'] = abs(df.Close - df.Open)

        p = figure(x_axis_type='datetime', width=1000, height=600,
                   sizing_mode='scale_both', toolbar_location='below')
        p.title.text = symbol + ' ' + 'Candlestick Chart'
        p.grid.grid_line_alpha = 0.3

        hours_12 = 12 * 60 * 60 * 1000

        p.segment(df.index, df.High, df.index, df.Low, color='black')

        p.rect(df.index[df.Status == 'Increase'], df.Middle[df.Status == 'Increase'], hours_12,
               df.Height[df.Status == 'Increase'], fill_color='#228B22', line_color='black')

        p.rect(df.index[df.Close < df.Open], df.Middle[df.Status == 'Decrease'], hours_12,
               df.Height[df.Status == 'Decrease'], fill_color='#B22222', line_color='black')

        script1, div1 = components(p)
        cdn_js = CDN.js_files[0]
        return render_template('home.html', script1=script1, div1=div1, cdn_js=cdn_js)


if __name__ == '__main__':
    app.run(debug=True)
