from flask import Flask, render_template, request
from pandas_datareader._utils import RemoteDataError
from pandas_datareader import data
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.resources import CDN

# url https://bokehstockplot.herokuapp.com
app = Flask(__name__)


# define url for app and what methods will be used
@app.route('/', methods=['GET', 'POST'])
# our function to run our script and is called when the submit button is pressed in html form
def home():
    # display home page when url is visited; store input data in variables when user submits form data
    if request.method == 'GET':
        return render_template('home.html')

    elif request.method == 'POST':

        start = request.form['start']

        end = request.form['end']

        symbol = request.form['stock'].upper()

        # send input data to pandas data reader; display invalid symbol page if symbol is not found
        try:
            df = data.DataReader(name=symbol, data_source='yahoo', start=start, end=end)
        except RemoteDataError:
            return render_template('invsym.html')

        # determine increase, decrease, or equal when comparing Open and Close values and assign result to variable
        def inc_dec(c, o):
            # set value to 'increase if close is greater than open
            if c > o:
                value = 'Increase'
            elif c < o:
                value: str = 'Decrease'
            else:
                value = 'Equal'
            return value

        # create new column in dataframe based on results of inc_dec function Open/Close data
        df['Status'] = [inc_dec(c, o) for c, o in zip(df.Close, df.Open)]
        # add column for center point of rectangle on y-axis
        df['Middle'] = (df.Open + df.Close) / 2
        # add column to determine full height of rectangle on chart and keep value positive
        df['Height'] = abs(df.Close - df.Open)

        # format display size of chart and location of toolbar
        p = figure(x_axis_type='datetime', width=1000, height=350,
                   sizing_mode='scale_both', toolbar_location='below')
        # Title of chart displayed at top of chart
        p.title.text = f"{symbol} Candlestick Chart"
        # Set x axis label to 'date'
        p.xaxis.axis_label = 'Date'
        # set y axis label to 'price'
        p.yaxis.axis_label = 'Price (USD)'
        # set transparency of grid lines on chart '0-1'
        p.grid.grid_line_alpha = 0.3
        # set 12 hours to milli-seconds to get width of rectangle
        hours_12 = 12 * 60 * 60 * 1000

        # create line segments for chart with segment(x-axis high, y-axis high, x-axis low, y-axis low)
        # set x-axis to date and y-axis to the days high and low
        p.segment(df.index, df.High, df.index, df.Low, color='black')
        # create candlestick rectangles with rect(x-axis center, y-axis center, width, height)
        # set rectangle values where status == increase and color to green,
        p.rect(df.index[df.Status == 'Increase'], df.Middle[df.Status == 'Increase'], hours_12,
               df.Height[df.Status == 'Increase'], fill_color='#228B22', line_color='black')
        # set rectangle values where status == decrease and color to red
        p.rect(df.index[df.Status == 'Decrease'], df.Middle[df.Status == 'Decrease'], hours_12,
               df.Height[df.Status == 'Decrease'], fill_color='#B22222', line_color='black')
        # assign embedded javascript and html link to variables using bokeh components()
        script1, div1 = components(p)
        # store bokeh javascript link in variable for chart
        cdn_js = CDN.js_files[0]
        # return home page with bokeh plot chart
        return render_template('home.html', script1=script1, div1=div1, cdn_js=cdn_js)


if __name__ == '__main__':
    app.run(debug=True)
