#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Fm Tx Fifo
# Author: Naga
# Generated: Mon Apr 22 12:06:39 2013
##################################################

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

class FM_tx_FIFO(grc_wxgui.top_block_gui):

	def __init__(self):
		grc_wxgui.top_block_gui.__init__(self, title="Fm Tx Fifo")

		##################################################
		# Variables
		##################################################
		self.samp_rate = samp_rate = 195.312e3
		self.FM_freq = FM_freq = 96.5e6

		##################################################
		# Blocks
		##################################################
		self.notebook_0 = self.notebook_0 = wx.Notebook(self.GetWin(), style=wx.NB_TOP)
		self.notebook_0.AddPage(grc_wxgui.Panel(self.notebook_0), "Audio")
		self.notebook_0.AddPage(grc_wxgui.Panel(self.notebook_0), "FM")
		self.Add(self.notebook_0)
		_FM_freq_sizer = wx.BoxSizer(wx.VERTICAL)
		self._FM_freq_text_box = forms.text_box(
			parent=self.GetWin(),
			sizer=_FM_freq_sizer,
			value=self.FM_freq,
			callback=self.set_FM_freq,
			label="FM Frequency",
			converter=forms.float_converter(),
			proportion=0,
		)
		self._FM_freq_slider = forms.slider(
			parent=self.GetWin(),
			sizer=_FM_freq_sizer,
			value=self.FM_freq,
			callback=self.set_FM_freq,
			minimum=87.5e6,
			maximum=108e6,
			num_steps=100,
			style=wx.SL_HORIZONTAL,
			cast=float,
			proportion=1,
		)
		self.Add(_FM_freq_sizer)
		self.wxgui_fftsink2_1 = fftsink2.fft_sink_f(
			self.notebook_0.GetPage(0).GetWin(),
			baseband_freq=0,
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
			win=window.hamming,
		)
		self.notebook_0.GetPage(0).Add(self.wxgui_fftsink2_1.win)
		self.wxgui_fftsink2_0 = fftsink2.fft_sink_c(
			self.notebook_0.GetPage(1).GetWin(),
			baseband_freq=FM_freq,
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
		self.notebook_0.GetPage(1).Add(self.wxgui_fftsink2_0.win)
		self.uhd_usrp_sink_0 = uhd.usrp_sink(
			device_addr="addr=192.168.10.2",
			stream_args=uhd.stream_args(
				cpu_format="fc32",
				channels=range(1),
			),
		)
		self.uhd_usrp_sink_0.set_samp_rate(samp_rate)
		self.uhd_usrp_sink_0.set_center_freq(FM_freq, 0)
		self.uhd_usrp_sink_0.set_gain(60, 0)
		self.uhd_usrp_sink_0.set_antenna("TX/RX", 0)
		self.gr_short_to_float_0 = gr.short_to_float(1, 1)
		self.gr_multiply_const_vxx_0 = gr.multiply_const_vff((400e-6, ))
		self.gr_file_source_0 = gr.file_source(gr.sizeof_short*1, "/home/kranthi/documents/project/FM Transceiver Original/test.raw", True)
		self.blks2_wfm_tx_0 = blks2.wfm_tx(
			audio_rate=32000,
			quad_rate=800000,
			tau=75e-6,
			max_dev=75e3,
		)
		self.blks2_rational_resampler_xxx_0 = blks2.rational_resampler_ccc(
			interpolation=1,
			decimation=2,
			taps=None,
			fractional_bw=None,
		)

		##################################################
		# Connections
		##################################################
		self.connect((self.blks2_rational_resampler_xxx_0, 0), (self.uhd_usrp_sink_0, 0))
		self.connect((self.blks2_rational_resampler_xxx_0, 0), (self.wxgui_fftsink2_0, 0))
		self.connect((self.blks2_wfm_tx_0, 0), (self.blks2_rational_resampler_xxx_0, 0))
		self.connect((self.gr_file_source_0, 0), (self.gr_short_to_float_0, 0))
		self.connect((self.gr_multiply_const_vxx_0, 0), (self.blks2_wfm_tx_0, 0))
		self.connect((self.gr_multiply_const_vxx_0, 0), (self.wxgui_fftsink2_1, 0))
		self.connect((self.gr_short_to_float_0, 0), (self.gr_multiply_const_vxx_0, 0))

	def get_samp_rate(self):
		return self.samp_rate

	def set_samp_rate(self, samp_rate):
		self.samp_rate = samp_rate
		self.wxgui_fftsink2_1.set_sample_rate(self.samp_rate)
		self.wxgui_fftsink2_0.set_sample_rate(self.samp_rate)
		self.uhd_usrp_sink_0.set_samp_rate(self.samp_rate)

	def get_FM_freq(self):
		return self.FM_freq

	def set_FM_freq(self, FM_freq):
		self.FM_freq = FM_freq
		self.wxgui_fftsink2_0.set_baseband_freq(self.FM_freq)
		self._FM_freq_slider.set_value(self.FM_freq)
		self._FM_freq_text_box.set_value(self.FM_freq)
		self.uhd_usrp_sink_0.set_center_freq(self.FM_freq, 0)

if __name__ == '__main__':
	parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
	(options, args) = parser.parse_args()
	tb = FM_tx_FIFO()
	tb.Run(True)

