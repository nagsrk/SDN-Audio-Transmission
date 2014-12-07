#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: UHD WBFM Receive
# Author: Naga
# Description: WBFM Receive
# Generated: Tue Apr 23 16:11:41 2013
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

class uhd_wbfm_receive(grc_wxgui.top_block_gui):

	def __init__(self, gain=0, audio_output="", samp_rate=400e3, address="addr=192.168.20.2", freq=96.5e6):
		grc_wxgui.top_block_gui.__init__(self, title="UHD WBFM Receive")

		##################################################
		# Parameters
		##################################################
		self.gain = gain
		self.audio_output = audio_output
		self.samp_rate = samp_rate
		self.address = address
		self.freq = freq

		##################################################
		# Variables
		##################################################
		self.volume = volume = 1
		self.tun_gain = tun_gain = gain
		self.tun_freq = tun_freq = freq
		self.fine = fine = 0
		self.audio_decim = audio_decim = 10

		##################################################
		# Blocks
		##################################################
		_volume_sizer = wx.BoxSizer(wx.VERTICAL)
		self._volume_text_box = forms.text_box(
			parent=self.GetWin(),
			sizer=_volume_sizer,
			value=self.volume,
			callback=self.set_volume,
			label="Volume",
			converter=forms.float_converter(),
			proportion=0,
		)
		self._volume_slider = forms.slider(
			parent=self.GetWin(),
			sizer=_volume_sizer,
			value=self.volume,
			callback=self.set_volume,
			minimum=0,
			maximum=10,
			num_steps=100,
			style=wx.SL_HORIZONTAL,
			cast=float,
			proportion=1,
		)
		self.GridAdd(_volume_sizer, 1, 0, 1, 4)
		_tun_gain_sizer = wx.BoxSizer(wx.VERTICAL)
		self._tun_gain_text_box = forms.text_box(
			parent=self.GetWin(),
			sizer=_tun_gain_sizer,
			value=self.tun_gain,
			callback=self.set_tun_gain,
			label="UHD Gain",
			converter=forms.float_converter(),
			proportion=0,
		)
		self._tun_gain_slider = forms.slider(
			parent=self.GetWin(),
			sizer=_tun_gain_sizer,
			value=self.tun_gain,
			callback=self.set_tun_gain,
			minimum=0,
			maximum=20,
			num_steps=100,
			style=wx.SL_HORIZONTAL,
			cast=float,
			proportion=1,
		)
		self.Add(_tun_gain_sizer)
		_tun_freq_sizer = wx.BoxSizer(wx.VERTICAL)
		self._tun_freq_text_box = forms.text_box(
			parent=self.GetWin(),
			sizer=_tun_freq_sizer,
			value=self.tun_freq,
			callback=self.set_tun_freq,
			label="Freq (Hz)",
			converter=forms.float_converter(),
			proportion=0,
		)
		self._tun_freq_slider = forms.slider(
			parent=self.GetWin(),
			sizer=_tun_freq_sizer,
			value=self.tun_freq,
			callback=self.set_tun_freq,
			minimum=87.9e6,
			maximum=108.1e6,
			num_steps=100,
			style=wx.SL_HORIZONTAL,
			cast=float,
			proportion=1,
		)
		self.Add(_tun_freq_sizer)
		_fine_sizer = wx.BoxSizer(wx.VERTICAL)
		self._fine_text_box = forms.text_box(
			parent=self.GetWin(),
			sizer=_fine_sizer,
			value=self.fine,
			callback=self.set_fine,
			label="Fine Freq (MHz)",
			converter=forms.float_converter(),
			proportion=0,
		)
		self._fine_slider = forms.slider(
			parent=self.GetWin(),
			sizer=_fine_sizer,
			value=self.fine,
			callback=self.set_fine,
			minimum=-.1,
			maximum=.1,
			num_steps=100,
			style=wx.SL_HORIZONTAL,
			cast=float,
			proportion=1,
		)
		self.GridAdd(_fine_sizer, 0, 2, 1, 2)
		self.wxgui_fftsink2 = fftsink2.fft_sink_c(
			self.GetWin(),
			baseband_freq=(freq+fine),
			y_per_div=10,
			y_divs=10,
			ref_level=0,
			ref_scale=2.0,
			sample_rate=samp_rate,
			fft_size=512,
			fft_rate=15,
			average=False,
			avg_alpha=None,
			title="FFT Plot",
			peak_hold=False,
		)
		self.GridAdd(self.wxgui_fftsink2.win, 2, 0, 2, 4)
		self.uhd_usrp_source_0 = uhd.usrp_source(
			device_addr=address,
			stream_args=uhd.stream_args(
				cpu_format="fc32",
				channels=range(1),
			),
		)
		self.uhd_usrp_source_0.set_samp_rate(samp_rate)
		self.uhd_usrp_source_0.set_center_freq(tun_freq+fine, 0)
		self.uhd_usrp_source_0.set_gain(tun_gain, 0)
		self.uhd_usrp_source_0.set_antenna("TX/RX", 0)
		self.low_pass_filter_0 = gr.fir_filter_ccf(1, firdes.low_pass(
			1, samp_rate, 115e3, 30e3, firdes.WIN_HANN, 6.76))
		self.gr_multiply_const_vxx = gr.multiply_const_vff((volume, ))
		self.blks2_wfm_rcv = blks2.wfm_rcv(
			quad_rate=samp_rate,
			audio_decimation=audio_decim,
		)
		self.blks2_rational_resampler_xxx_0 = blks2.rational_resampler_fff(
			interpolation=48,
			decimation=40,
			taps=None,
			fractional_bw=None,
		)
		self.audio_sink = audio.sink(48000, audio_output, True)

		##################################################
		# Connections
		##################################################
		self.connect((self.gr_multiply_const_vxx, 0), (self.audio_sink, 0))
		self.connect((self.low_pass_filter_0, 0), (self.blks2_wfm_rcv, 0))
		self.connect((self.uhd_usrp_source_0, 0), (self.low_pass_filter_0, 0))
		self.connect((self.low_pass_filter_0, 0), (self.wxgui_fftsink2, 0))
		self.connect((self.blks2_wfm_rcv, 0), (self.blks2_rational_resampler_xxx_0, 0))
		self.connect((self.blks2_rational_resampler_xxx_0, 0), (self.gr_multiply_const_vxx, 0))

	def get_gain(self):
		return self.gain

	def set_gain(self, gain):
		self.gain = gain
		self.set_tun_gain(self.gain)

	def get_audio_output(self):
		return self.audio_output

	def set_audio_output(self, audio_output):
		self.audio_output = audio_output

	def get_samp_rate(self):
		return self.samp_rate

	def set_samp_rate(self, samp_rate):
		self.samp_rate = samp_rate
		self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.samp_rate, 115e3, 30e3, firdes.WIN_HANN, 6.76))
		self.wxgui_fftsink2.set_sample_rate(self.samp_rate)
		self.uhd_usrp_source_0.set_samp_rate(self.samp_rate)

	def get_address(self):
		return self.address

	def set_address(self, address):
		self.address = address

	def get_freq(self):
		return self.freq

	def set_freq(self, freq):
		self.freq = freq
		self.wxgui_fftsink2.set_baseband_freq((self.freq+self.fine))
		self.set_tun_freq(self.freq)

	def get_volume(self):
		return self.volume

	def set_volume(self, volume):
		self.volume = volume
		self._volume_slider.set_value(self.volume)
		self._volume_text_box.set_value(self.volume)
		self.gr_multiply_const_vxx.set_k((self.volume, ))

	def get_tun_gain(self):
		return self.tun_gain

	def set_tun_gain(self, tun_gain):
		self.tun_gain = tun_gain
		self._tun_gain_slider.set_value(self.tun_gain)
		self._tun_gain_text_box.set_value(self.tun_gain)
		self.uhd_usrp_source_0.set_gain(self.tun_gain, 0)

	def get_tun_freq(self):
		return self.tun_freq

	def set_tun_freq(self, tun_freq):
		self.tun_freq = tun_freq
		self.uhd_usrp_source_0.set_center_freq(self.tun_freq+self.fine, 0)
		self._tun_freq_slider.set_value(self.tun_freq)
		self._tun_freq_text_box.set_value(self.tun_freq)

	def get_fine(self):
		return self.fine

	def set_fine(self, fine):
		self.fine = fine
		self._fine_slider.set_value(self.fine)
		self._fine_text_box.set_value(self.fine)
		self.wxgui_fftsink2.set_baseband_freq((self.freq+self.fine))
		self.uhd_usrp_source_0.set_center_freq(self.tun_freq+self.fine, 0)

	def get_audio_decim(self):
		return self.audio_decim

	def set_audio_decim(self, audio_decim):
		self.audio_decim = audio_decim

if __name__ == '__main__':
	parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
	parser.add_option("-g", "--gain", dest="gain", type="eng_float", default=eng_notation.num_to_str(0),
		help="Set Default Gain [default=%default]")
	parser.add_option("-O", "--audio-output", dest="audio_output", type="string", default="",
		help="Set Audio Output Device [default=%default]")
	parser.add_option("-s", "--samp-rate", dest="samp_rate", type="eng_float", default=eng_notation.num_to_str(400e3),
		help="Set Sample Rate [default=%default]")
	parser.add_option("-a", "--address", dest="address", type="string", default="addr=192.168.10.2",
		help="Set IP Address [default=%default]")
	parser.add_option("-f", "--freq", dest="freq", type="eng_float", default=eng_notation.num_to_str(96e6),
		help="Set Default Frequency [default=%default]")
	(options, args) = parser.parse_args()
	tb = uhd_wbfm_receive(gain=options.gain, audio_output=options.audio_output, samp_rate=options.samp_rate, address=options.address, freq=options.freq)
	tb.Run(True)

