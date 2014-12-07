#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Ettus Fm
# Author: Naga
# Generated: Tue Apr 23 16:08:03 2013
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

class ettus_fm(grc_wxgui.top_block_gui):

	def __init__(self):
		grc_wxgui.top_block_gui.__init__(self, title="Ettus Fm")

		##################################################
		# Variables
		##################################################
		self.samp_rate = samp_rate = 5e6
		self.freq = freq = 96.5e6

		##################################################
		# Blocks
		##################################################
		self.notebook_0 = self.notebook_0 = wx.Notebook(self.GetWin(), style=wx.NB_TOP)
		self.notebook_0.AddPage(grc_wxgui.Panel(self.notebook_0), "RF Spectrum")
		self.notebook_0.AddPage(grc_wxgui.Panel(self.notebook_0), "Demod Spectrum")
		self.notebook_0.AddPage(grc_wxgui.Panel(self.notebook_0), "Audio")
		self.Add(self.notebook_0)
		self._freq_text_box = forms.text_box(
			parent=self.GetWin(),
			value=self.freq,
			callback=self.set_freq,
			label='freq',
			converter=forms.float_converter(),
		)
		self.Add(self._freq_text_box)
		self.wxgui_fftsink2_2 = fftsink2.fft_sink_f(
			self.notebook_0.GetPage(2).GetWin(),
			baseband_freq=0,
			y_per_div=10,
			y_divs=10,
			ref_level=0,
			ref_scale=2.0,
			sample_rate=48e3,
			fft_size=1024,
			fft_rate=15,
			average=False,
			avg_alpha=None,
			title="FFT Plot",
			peak_hold=False,
		)
		self.notebook_0.GetPage(2).Add(self.wxgui_fftsink2_2.win)
		self.wxgui_fftsink2_1 = fftsink2.fft_sink_f(
			self.notebook_0.GetPage(1).GetWin(),
			baseband_freq=0,
			y_per_div=10,
			y_divs=10,
			ref_level=0,
			ref_scale=2.0,
			sample_rate=250e3,
			fft_size=1024,
			fft_rate=15,
			average=False,
			avg_alpha=None,
			title="FFT Plot",
			peak_hold=False,
		)
		self.notebook_0.GetPage(1).Add(self.wxgui_fftsink2_1.win)
		self.wxgui_fftsink2_0 = fftsink2.fft_sink_c(
			self.notebook_0.GetPage(0).GetWin(),
			baseband_freq=freq,
			y_per_div=10,
			y_divs=10,
			ref_level=0,
			ref_scale=2.0,
			sample_rate=samp_rate,
			fft_size=1024,
			fft_rate=15,
			average=False,
			avg_alpha=None,
			title="FFT Plot",
			peak_hold=False,
		)
		self.notebook_0.GetPage(0).Add(self.wxgui_fftsink2_0.win)
		self.uhd_usrp_source_0 = uhd.usrp_source(
			device_addr="addr=192.168.20.2",
			stream_args=uhd.stream_args(
				cpu_format="fc32",
				channels=range(1),
			),
		)
		self.uhd_usrp_source_0.set_samp_rate(samp_rate)
		self.uhd_usrp_source_0.set_center_freq(freq, 0)
		self.uhd_usrp_source_0.set_gain(25, 0)
		self.uhd_usrp_source_0.set_antenna("TX/RX", 0)
		self.uhd_usrp_source_0.set_bandwidth(200e3, 0)
		self.low_pass_filter_0 = gr.fir_filter_ccf(20, firdes.low_pass(
			1, samp_rate, 100e3, 10e3, firdes.WIN_HAMMING, 6.76))
		self.gr_multiply_const_vxx_0 = gr.multiply_const_vff((5, ))
		self.blks2_wfm_rcv_0 = blks2.wfm_rcv(
			quad_rate=250e3,
			audio_decimation=1,
		)
		self.blks2_rational_resampler_xxx_0 = blks2.rational_resampler_fff(
			interpolation=48,
			decimation=250,
			taps=None,
			fractional_bw=None,
		)
		self.audio_sink_0 = audio.sink(48000, "", True)

		##################################################
		# Connections
		##################################################
		self.connect((self.uhd_usrp_source_0, 0), (self.low_pass_filter_0, 0))
		self.connect((self.uhd_usrp_source_0, 0), (self.wxgui_fftsink2_0, 0))
		self.connect((self.low_pass_filter_0, 0), (self.blks2_wfm_rcv_0, 0))
		self.connect((self.blks2_wfm_rcv_0, 0), (self.blks2_rational_resampler_xxx_0, 0))
		self.connect((self.blks2_wfm_rcv_0, 0), (self.wxgui_fftsink2_1, 0))
		self.connect((self.blks2_rational_resampler_xxx_0, 0), (self.gr_multiply_const_vxx_0, 0))
		self.connect((self.gr_multiply_const_vxx_0, 0), (self.audio_sink_0, 0))
		self.connect((self.blks2_rational_resampler_xxx_0, 0), (self.wxgui_fftsink2_2, 0))

	def get_samp_rate(self):
		return self.samp_rate

	def set_samp_rate(self, samp_rate):
		self.samp_rate = samp_rate
		self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.samp_rate, 100e3, 10e3, firdes.WIN_HAMMING, 6.76))
		self.wxgui_fftsink2_0.set_sample_rate(self.samp_rate)
		self.uhd_usrp_source_0.set_samp_rate(self.samp_rate)

	def get_freq(self):
		return self.freq

	def set_freq(self, freq):
		self.freq = freq
		self.wxgui_fftsink2_0.set_baseband_freq(self.freq)
		self.uhd_usrp_source_0.set_center_freq(self.freq, 0)
		self._freq_text_box.set_value(self.freq)

if __name__ == '__main__':
	parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
	(options, args) = parser.parse_args()
	tb = ettus_fm()
	tb.Run(True)

