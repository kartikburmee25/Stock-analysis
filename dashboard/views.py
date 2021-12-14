from django.shortcuts import render
from django.http import HttpResponse
import yfinance as yf
import altair as alt
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from plotly.offline import plot
from plotly.graph_objs import Scatter
from plotly.subplots import make_subplots
import plotly.express as px
from plotly.io import to_html
from json2html import *

# Create your views here.
def main_page(request):
	return HttpResponse("Stock metrics visualizer. Please enter the ticker symbol to see metrics.")

def stock_summary(request,ticker_symbol,period):

	context = generate_stock_summary(ticker_symbol,period)
	return render(request, 'dashboard/stock_summary.html', context)

def generate_stock_summary(ticker_symbol,period):
	
	data = yf.download(ticker_symbol, period=period)
	data = data.rename_axis('Date').reset_index()

	# Closing price
	plot = px.line(data_frame=data, x='Date', y='Close', title=ticker_symbol)
	closing_plot_div = to_html(plot,full_html=False,default_width='100%',default_height='100%')

	# 10 day simple moving average
	data['SMA_10'] = data['Close'].rolling(window=10).mean()
	plot = px.line(data_frame=data, x='Date', y='SMA_10', title=ticker_symbol)
	sma_10_plot_div = to_html(plot,full_html=False,default_width='100%',default_height='100%')

	# 12 day exponential moving average
	data['12dayEWM'] = data['Close'].ewm(span=4, adjust=False).mean()
	plot = px.line(data_frame=data, x='Date', y='12dayEWM', title=ticker_symbol)
	EWM_plot_div = to_html(plot,full_html=False,default_width='100%',default_height='100%')

	# stochastic oscillator
	data['14-high'] = data['High'].rolling(14).max()
	data['14-low'] = data['Low'].rolling(14).min()
	data['%K'] = (data['Close'] - data['14-low'])*100/(data['14-high'] - data['14-low'])
	data['%D'] = data['%K'].rolling(3).mean()
	subfig = make_subplots(specs=[[{"secondary_y": True}]])
	plot1 = px.line(data_frame=data, x='Date', y='%K', render_mode="webgl")
	plot2 = px.line(data_frame=data, x='Date', y='%D', render_mode="webgl")
	plot2.update_traces(yaxis="y2")
	subfig.add_traces(plot1.data + plot2.data)
	subfig.layout.xaxis.title="Date"
	subfig.layout.yaxis.title="%K"
	subfig.layout.yaxis2.title="%D"
	subfig.for_each_trace(lambda t: t.update(line=dict(color=t.marker.color)))
	stochastic_div = to_html(subfig,full_html=False,default_width='100%',default_height='100%')

	company = yf.Ticker(ticker_symbol)
	company_name = company.info['longName']
	company_info = company.sustainability

	ts_data = {'company_name':company_name, 'info_div':company_info,
			   'closing_plot':closing_plot_div, 'sma_10_plot':sma_10_plot_div,
			   'EWM_plot':EWM_plot_div, 'stochastic_plot':stochastic_div}

	return ts_data

	