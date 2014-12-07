#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Fm Rx Example
# Author: Naga
# Generated: Tue Feb 26 11:16:19 2013
##################################################

from gnuradio import audio
from gnuradio import blks2
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio import uhd
from gnuradio import window
from gnuradio.eng_option import eng_option
from gnuradio.gr import firdes
from gnuradio.wxgui import fftsink2
from gnuradio.wxgui import forms
from grc_gnuradio import wxgui as grc_wxgui
from optparse import OptionParser
import wx

class fm_rx_example(grc_wxgui.top_block_gui):

	def __init__(self):
		grc_wxgui.top_block_gui.__init__(self, title="Fm Rx Example")

		##################################################
		# Variables
		##################################################
		self.usrp_freq = usrp_freq = 96.5e6
		self.samp_rate = samp_rate = 500e3
		self.xlate_tune = xlate_tune = 0
		self.usrp_decim = usrp_decim = 200
		self.rx_freq = rx_freq = usrp_freq
		self.rf_gain = rf_gain = 15
		self.filter_taps = filter_taps = firdes.low_pass(1,samp_rate,200e3,1e3)
		self.af_gain = af_gain = 3

		##################################################
		# Blocks
		##################################################
		_xlate_tune_sizer = wx.BoxSizer(wx.VERTICAL)
		self._xlate_tune_text_box = forms.text_box(
			parent=self.GetWin(),
			sizer=_xlate_tune_sizer,
			value=self.xlate_tune,
			callback=self.set_xlate_tune,
			label='xlate_tune',
			converter=forms.float_converter(),
			proportion=0,
		)
		self._xlate_tune_slider = forms.slider(
			parent=self.GetWin(),
			sizer=_xlate_tune_sizer,
			value=self.xlate_tune,
			callback=self.set_xlate_tune,
			minimum=-250e3,
			maximum=250e3,
			num_steps=100,
			style=wx.SL_HORIZONTAL,
			cast=float,
			proportion=1,
		)
		self.GridAdd(_xlate_tune_sizer, 7, 0, 1, 5)
		_usrp_freq_sizer = wx.BoxSizer(wx.VERTICAL)
		self._usrp_freq_text_box = forms.text_box(
			parent=self.GetWin(),
			sizer=_usrp_freq_sizer,
			value=self.usrp_freq,
			callback=self.set_usrp_freq,
			label='usrp_freq',
			converter=forms.float_converter(),
			proportion=0,
		)
		self._usrp_freq_slider = forms.slider(
			parent=self.GetWin(),
			sizer=_usrp_freq_sizer,
			value=self.usrp_freq,
			callback=self.set_usrp_freq,
			minimum=88e6,
			maximum=108e6,
			num_steps=100,
			style=wx.SL_HORIZONTAL,
			cast=float,
			proportion=1,
		)
		self.GridAdd(_usrp_freq_sizer, 6, 0, 1, 5)
		self.wxgui_fftsink2_0 = fftsink2.fft_sink_c(
			self.GetWin(),
			baseband_freq=0,
			y_per_div=10,
			y_divs=10,
			ref_level=0,
			ref_scale=13.49e3,
			sample_rate=250e3,
			fft_size=1024,
			fft_rate=10,
			average=True,
			avg_alpha=500e-3,
			title="FFT Plot",
			peak_hold=False,
			size=(1120,527),
		)
		self.GridAdd(self.wxgui_fftsink2_0.win, 0, 0, 5, 5)
		self.uhd_usrp_source_0 = uhd.usrp_source(
			device_addr="addr=192.168.20.2",
			stream_args=uhd.stream_args(
				cpu_format="fc32",
				channels=range(1),
			),
		)
		self.uhd_usrp_source_0.set_samp_rate(samp_rate)
		self.uhd_usrp_source_0.set_center_freq(usrp_freq, 0)
		self.uhd_usrp_source_0.set_gain(15, 0)
		self.uhd_usrp_source_0.set_antenna("TX/RX", 0)
		self._rx_freq_static_text = forms.static_text(
			parent=self.GetWin(),
			value=self.rx_freq,
			callback=self.set_rx_freq,
			label='rx_freq',
			converter=forms.float_converter(),
		)
		self.GridAdd(self._rx_freq_static_text, 5, 3, 1, 1)
		_rf_gain_sizer = wx.BoxSizer(wx.VERTICAL)
		self._rf_gain_text_box = forms.text_box(
			parent=self.GetWin(),
			sizer=_rf_gain_sizer,
			value=self.rf_gain,
			callback=self.set_rf_gain,
			label='rf_gain',
			converter=forms.float_converter(),
			proportion=0,
		)
		self._rf_gain_slider = forms.slider(
			parent=self.GetWin(),
			sizer=_rf_gain_sizer,
			value=self.rf_gain,
			callback=self.set_rf_gain,
			minimum=0,
			maximum=50,
			num_steps=100,
			style=wx.SL_HORIZONTAL,
			cast=float,
			proportion=1,
		)
		self.GridAdd(_rf_gain_sizer, 8, 0, 1, 2)
		self.gr_multiply_const_vxx_1 = gr.multiply_const_vff((3, ))
		self.gr_multiply_const_vxx_0 = gr.multiply_const_vff((3, ))
		self.gr_freq_xlating_fir_filter_xxx_0 = gr.freq_xlating_fir_filter_ccc(1, (filter_taps), xlate_tune, samp_rate)
		self.blks2_wfm_rcv_pll_0 = blks2.wfm_rcv_pll(
			demod_rate=500e3,
			audio_decimation=10,
		)
		self.blks2_rational_resampler_xxx_1 = blks2.rational_resampler_fff(
			interpolation=48,
			decimation=50,
			taps=None,
			fractional_bw=None,
		)
		self.blks2_rational_resampler_xxx_0 = blks2.rational_resampler_fff(
			interpolation=48,
			decimation=50,
			taps=None,
			fractional_bw=None,
		)
		self.audio_sink_0 = audio.sink(48000, "", True)
		_af_gain_sizer = wx.BoxSizer(wx.VERTICAL)
		self._af_gain_text_box = forms.text_box(
			parent=self.GetWin(),
			sizer=_af_gain_sizer,
			value=self.af_gain,
			callback=self.set_af_gain,
			label='af_gain',
			converter=forms.float_converter(),
			proportion=0,
		)
		self._af_gain_slider = forms.slider(
			parent=self.GetWin(),
			sizer=_af_gain_sizer,
			value=self.af_gain,
			callback=self.set_af_gain,
			minimum=0,
			maximum=10,
			num_steps=100,
			style=wx.SL_HORIZONTAL,
			cast=float,
			proportion=1,
		)
		self.GridAdd(_af_gain_sizer, 8, 2, 1, 2)

		##################################################
		# Connections
		##################################################
		self.connect((self.uhd_usrp_source_0, 0), (self.gr_freq_xlating_fir_filter_xxx_0, 0))
		self.connect((self.gr_freq_xlating_fir_filter_xxx_0, 0), (self.blks2_wfm_rcv_pll_0, 0))
		self.connect((self.gr_freq_xlating_fir_filter_xxx_0, 0), (self.wxgui_fftsink2_0, 0))
		self.connect((self.gr_multiply_const_vxx_0, 0), (self.audio_sink_0, 0))
		self.connect((self.blks2_rational_resampler_xxx_1, 0), (self.gr_multiply_const_vxx_1, 0))
		self.connect((self.blks2_rational_resampler_xxx_0, 0), (self.gr_multiply_const_vxx_0, 0))
		self.connect((self.gr_multiply_const_vxx_1, 0), (self.audio_sink_0, 1))
		self.connect((self.blks2_wfm_rcv_pll_0, 0), (self.blks2_rational_resampler_xxx_0, 0))
		self.connect((self.blks2_wfm_rcv_pll_0, 1), (self.blks2_rational_resampler_xxx_1, 0))

	def get_usrp_freq(self):
		return self.usrp_freq

	def set_usrp_freq(self, usrp_freq):
		self.usrp_freq = usrp_freq
		self.uhd_usrp_source_0.set_center_freq(self.usrp_freq, 0)
		self.set_rx_freq(self.usrp_freq)
		self._usrp_freq_slider.set_value(self.usrp_freq)
		self._usrp_freq_text_box.set_value(self.usrp_freq)

	def get_samp_rate(self):
		return self.samp_rate

	def set_samp_rate(self, samp_rate):
		self.samp_rate = samp_rate
		self.set_filter_taps(firdes.low_pass(1,self.samp_rate,200e3,1e3))
		self.uhd_usrp_source_0.set_samp_rate(self.samp_rate)

	def get_xlate_tune(self):
		return self.xlate_tune

	def set_xlate_tune(self, xlate_tune):
		self.xlate_tune = xlate_tune
		self._xlate_tune_slider.set_value(self.xlate_tune)
		self._xlate_tune_text_box.set_value(self.xlate_tune)
		self.gr_freq_xlating_fir_filter_xxx_0.set_center_freq(self.xlate_tune)

	def get_usrp_decim(self):
		return self.usrp_decim

	def set_usrp_decim(self, usrp_decim):
		self.usrp_decim = usrp_decim

	def get_rx_freq(self):
		return self.rx_freq

	def set_rx_freq(self, rx_freq):
		self.rx_freq = rx_freq
		self._rx_freq_static_text.set_value(self.rx_freq)

	def get_rf_gain(self):
		return self.rf_gain

	def set_rf_gain(self, rf_gain):
		self.rf_gain = rf_gain
		self._rf_gain_slider.set_value(self.rf_gain)
		self._rf_gain_text_box.set_value(self.rf_gain)

	def get_filter_taps(self):
		return self.filter_taps

	def set_filter_taps(self, filter_taps):
		self.filter_taps = filter_taps
		self.gr_freq_xlating_fir_filter_xxx_0.set_taps((self.filter_taps))

	def get_af_gain(self):
		return self.af_gain

	def set_af_gain(self, af_gain):
		self.af_gain = af_gain
		self._af_gain_slider.set_value(self.af_gain)
		self._af_gain_text_box.set_value(self.af_gain)

if __name__ == '__main__':
	parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
	(options, args) = parser.parse_args()
	tb = fm_rx_example()
	tb.Run(True)

