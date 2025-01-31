#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Fm Tx Fifo
# Author: Naga
# Generated: Mon Feb 25 16:22:57 2013
##################################################

from gnuradio import blks2, audio, digital
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio import uhd
from gnuradio import window
from gnuradio.eng_option import eng_option
from optparse import OptionParser
from multiprocessing import Process,Value
import time, string, os, struct, sys, math
#from gnuradio.gr import firdes
#from gnuradio.wxgui import fftsink2
#from gnuradio.wxgui import forms
#from grc_gnuradio import wxgui as grc_wxgui
#import wx

def transmitter_control(mp,Freq,norestart,sync,Frequency):
    while(1):
	sys.stderr.write('\nIn transmitter_control:\n')
	while (norestart.value==1):
		time.sleep(2)
	norestart.value = 1       
	mp.terminate()
	if (sync.value ==1):
	    Freq.value = 920*10**6
	else:
	    Freq.value = Frequency.value
	mp = Process(target = Start_transmitter,args=(Freq,norestart,sync,Frequency))
	mp.start() 
	
def synchronization(tb):    
	time.sleep(5)
	tb.start() 
	n= 0
	pktno = 150
	print "\nTransmitting in", Freq.value ,"Hz", " containing synchronization packet"
	preamble = 11111
	while n < 100:
	      data = struct.pack('!L', Frequency.value & 0xffffffff)
	      payload = struct.pack('!H', pktno & 0xffff) + struct.pack('!H', preamble & 0xffff) + data # Constructing a packet. Pack a string in to given format. http://docs.python.org/library/struct.html
	      send_pkt(tb,payload)				     # Sending packet
	      n += 1
	      pktno += 1
	      sys.stderr.write('.')				     # error message
	time.sleep(1)
	sync.value = 0
	norestart.value=0
	tb.stop()
	tb.wait()
	return n
        
###################################################################################################################################################################
                                                              #SENSING CODE 
###################################################################################################################################################################

class tune(gr.feval_dd):
      def __init__(self, tb):
	  gr.feval_dd.__init__(self)
	  self.tb = tb
	  
      def eval(self, ignore):
	  try:
	      new_freq = self.tb.set_next_freq()
	      return new_freq
	  except Exception, e:
	      print "tune: Exception: ", e
	    
class parse_msg(object):
      def __init__(self, msg):
	  self.center_freq = msg.arg1()
	  self.vlen = int(msg.arg2())
	  assert(msg.length() == self.vlen * gr.sizeof_float)
	  t = msg.to_string()
	  self.raw_data = t
	  self.data = struct.unpack('%df' % (self.vlen,), t)


class sensor(gr.top_block):
      def __init__(self,options):
	  gr.top_block.__init__(self)
	  if options.input_file == "":
	      self.IS_USRP2 = True
	  else:
	      self.IS_USRP2 = False
	  #self.min_freq = options.start
	  #self.max_freq = options.stop
	  self.min_freq = 905*10**6-(10*10**6) # same as that of the transmitter bandwidth ie 6MHZ approx for a given value of decimation line option any more
	  self.max_freq = 905*10**6+(10*10**6)
	  if self.min_freq > self.max_freq:
	      self.min_freq, self.max_freq = self.max_freq, self.min_freq # swap them
	      print "Start and stop frequencies order swapped!"
	  self.fft_size = options.fft_size
	  self.ofdm_bins = options.sense_bins
	  # build graph
	  s2v = gr.stream_to_vector(gr.sizeof_gr_complex, self.fft_size)
	  mywindow = window.blackmanharris(self.fft_size)
	  fft = gr.fft_vcc(self.fft_size, True, mywindow)
	  power = 0
	  for tap in mywindow:
	      power += tap*tap
	  c2mag = gr.complex_to_mag_squared(self.fft_size)
	  #log = gr.nlog10_ff(10, self.fft_size, -20*math.log10(self.fft_size)-10*math.log10(power/self.fft_size))
	  # modifications for USRP2 
	  self.u= uhd.usrp_source(device_addr="addr=192.168.10.2",stream_args=uhd.stream_args(cpu_format="fc32",channels=range(1),),)
	  if self.IS_USRP2:	
	      # self.u.set_decim(options.decim)
	      # samp_rate = self.u.adc_rate()/self.u.decim()
	      samp_rate = 100e6/options.decim		# modified sampling rate
	      self.u.set_samp_rate(samp_rate)
	  else:
	      self.u = gr.file_source(gr.sizeof_gr_complex,options.input_file, True)
	      samp_rate = 100e6 /options.decim		# modified sampling rate

	  self.freq_step =0 #0.75* samp_rate
	  self.min_center_freq = (self.min_freq + self.max_freq)/2
	  
	  global BW
	  BW = self.max_freq - self.min_freq
	  global size
	  size=self.fft_size
	  global ofdm_bins
	  ofdm_bins = self.ofdm_bins
	  global usr
	  #global thrshold_inorder
	  usr=samp_rate
	  nsteps = 10 
	  self.max_center_freq = self.min_center_freq + (nsteps * self.freq_step)
	  self.next_freq = self.min_center_freq
	  tune_delay = max(0, int(round(options.tune_delay * samp_rate / self.fft_size))) # in fft_frames
	  dwell_delay = max(1, int(round(options.dwell_delay * samp_rate / self.fft_size))) # in fft_frames
	  self.msgq = gr.msg_queue(16)					# thread-safe message queue
	  self._tune_callback = tune(self) 				# hang on to this to keep it from being GC'd
	  stats = gr.bin_statistics_f(self.fft_size, self.msgq, self._tune_callback, tune_delay,
					dwell_delay)			# control scanning and record frequency domain statistics
	  self.connect(self.u, s2v, fft,c2mag,stats)
	  if options.gain is None:
	      g = self.u.get_gain_range()
	      options.gain = float(g.start()+g.stop())/2			# if no gain was specified, use the mid-point in dB
	      
      def set_next_freq(self):
	  target_freq = self.next_freq	#tx_success=0
	  self.next_freq = self.next_freq + self.freq_step
	  if self.next_freq >= self.max_center_freq:
	      self.next_freq = self.min_center_freq
	  if self.IS_USRP2:
	      if not self.set_freq(target_freq):
		  print "Failed to set frequency to ", target_freq, "Hz"
	  return target_freq
	  
      def set_freq(self, target_freq):
	  #return self.u.set_center_freq(target_freq)
	  return self.u.set_center_freq(target_freq,0)
      def set_gain(self, gain):
	  #self.u.set_gain(gain)
	  self.u.set_gain(gain,0)
	
def sensor_init(options):
      tb1=sensor(options)
      return tb1
    
def sense_loop(tb,Frequency):
    print "\n\nSensing the spectrum"
    time.sleep(2)
    tb.start()						# Added Line
    moving_avg_data = [0]*(size)
    count = 11
    avg_iterations = avg_iter_count = 10
    while count>0:
	count=count-1
	#hexa_thr=""
	m = parse_msg(tb.msgq.delete_head())
	if avg_iter_count > 0:
		for i in range(0,size):
		      moving_avg_data[i] = moving_avg_data[i] + m.data[i]
		avg_iter_count = avg_iter_count - 1
	else: 
		for i in range(0,len(moving_avg_data)):
			moving_avg_data[i] = moving_avg_data[i]/float(avg_iterations)
		thrshold = map(lambda x: 0 if x>0.001 else 1, moving_avg_data)		# Modified threshold	
		thrshold_inorder= [0]*size
		sensed_freq = [0]*size
		avg_data = [0]*(size)
		ofdm_center_freq = m.center_freq # For now we are keeping the center freq of the ofdm same as that of sensing, will have to modify this later
		freq_resolution = usr/size
		p = m.center_freq - freq_resolution*((size/2)-1)
		for i in range(0,size/2):
			sensed_freq[i]= p	
			print p,  moving_avg_data[i+size/2], thrshold[i+size/2]
			p=p+freq_resolution
			thrshold_inorder[i] = thrshold[i+size/2]
			avg_data[i] = moving_avg_data[i+(size/2)]
		
		for i in range(0,size/2):
			sensed_freq[i+size/2] = p
			print p,  moving_avg_data[i], thrshold[i]
			p=p+freq_resolution
			thrshold_inorder[i+size/2]= thrshold[i]
			avg_data[i+(size/2)] = moving_avg_data[i]		
		hexa_thr = hex_conv(thrshold_inorder)
		
		print hexa_thr
	
		required_index = int(math.ceil((Frequency.value - 8925*10**5)*size/(usr)))
		carrier_map = thrshold_inorder[required_index-16:required_index+16]		
		print "\n\nCarrier map = ", carrier_map
		
		test = 0
		for i in range(0,len(carrier_map)):
		    if carrier_map[i]==0:
			test+=1
		print test
		if test >= 10:
		    sys.stderr.write('\nPrimary Transmission detected')
		    #---------------------------
		    # Finding best 200KHz spectrum band
		    #---------------------------
		    n = 0
		    power_temp = 50
		    for i in range(200,size-217):
			power = 0
			for j in range(0,17):
			    power = power + avg_data[i+j]
			#print sensed_freq[i+16],'\t', power
			if power < power_temp:
			    power_temp = power
			    index = i+8
		    Frequency.value = int(1e5*math.ceil(sensed_freq[index]/1e5))
		    print 'Frequency',Frequency.value
		    norestart.value=0
		    sync.value = 1
		    time.sleep(2)
		moving_avg_data = [0]*(size)
		avg_iter_count = avg_iterations
    tb.stop()
    tb.wait()
    return hexa_thr
        
# This function converts the vector of 1s and 0s into hexadecimal string for transmission   
def hex_conv(thrshold_inorder):
      dec_thr=0
      i=0
      hexa_thr=''
      abc = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']
      length=len(thrshold_inorder)
      while ((i<length) & ((length-i)>=4)):
	  j=4
	  while(j>0):
	    if thrshold_inorder[i]==1:
	      dec_thr+= (2)**(4-j)
	    #print "dec_thr=",dec_thr
	    i=i+1
	    j=j-1
	  mul=dec_thr
	  #print "mul=",mul
	  dec_thr=0
	  hexa_thr_part = ''
	  while mul >15:
	    c = abc[mul%16]
	    hexa_thr_part = c+hexa_thr_part
	    mul = mul/16  
	  hexa_thr_part= abc[mul]+hexa_thr_part 
	  hexa_thr=hexa_thr+hexa_thr_part	   
      # print "hexa_thr=",hexa_thr
      return hexa_thr
	    
###################################################################################################################################################################        
	                                                 # Transmitter code
###################################################################################################################################################################        

class transmitter(gr.top_block):
      def __init__(self,Freq):
	      gr.top_block.__init__(self)

	      ##################################################
	      # Variables
	      ##################################################
	      self.samp_rate = samp_rate = 195.312e3
	      self.FM_freq = FM_freq = Freq.value

	      self.uhd_usrp_sink_0 = uhd.usrp_sink(
		      device_addr="addr=192.168.10.2",
		      stream_args=uhd.stream_args(
			      cpu_format="fc32",
			      channels=range(1),
		      ),
	      )
	      self.uhd_usrp_sink_0.set_samp_rate(samp_rate)
	      self.uhd_usrp_sink_0.set_center_freq(FM_freq, 0)
	      self.uhd_usrp_sink_0.set_gain(0, 0)
	      self.uhd_usrp_sink_0.set_antenna("TX/RX", 0)
	      self.gr_short_to_float_0 = gr.short_to_float(1, 1)
	      self.gr_multiply_const_vxx_0 = gr.multiply_const_vff((30e-6, ))
	      self.gr_file_source_0 = gr.file_source(gr.sizeof_short*1, "/home/kranthi/documents/sound_cognition/test.raw", True)
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
#	      print "#####Start of transmitter########"

	      ##################################################
	      # Connections
	      ##################################################
	      self.connect((self.blks2_rational_resampler_xxx_0, 0), (self.uhd_usrp_sink_0, 0))
	      self.connect((self.blks2_wfm_tx_0, 0), (self.blks2_rational_resampler_xxx_0, 0))
	      self.connect((self.gr_file_source_0, 0), (self.gr_short_to_float_0, 0))
	      self.connect((self.gr_short_to_float_0, 0), (self.gr_multiply_const_vxx_0, 0))
	      self.connect((self.gr_multiply_const_vxx_0, 0), (self.blks2_wfm_tx_0, 0))


class trans_init():
      def __init__(self,Freq): 
	  global parser
	  parser = OptionParser(option_class=eng_option, conflict_handler="resolve")
	  expert_grp = parser.add_option_group("Expert")
	  parser.add_option("", "--tune-delay", type="eng_float", default=20e-3, metavar="SECS", help="time to delay (in seconds) after changing frequency[default=%default]")
	  parser.add_option("", "--dwell-delay", type="eng_float",default=1e-3, metavar="SECS", help="time to dwell (in seconds) at a given frequncy[default=%default]")
	  parser.add_option("-G", "--gain", type="eng_float", default=None,help="set gain in dB (default is midpoint)")
	  parser.add_option("-s", "--fft-size", type="int", default=2048, help="specify number of FFT bins [default=%default]")# changed default value(256)
	  parser.add_option("-d", "--decim", type="intx", default=4, help="set decimation to DECIM [default=%default]")	# changed default value(16) to 128
	  parser.add_option("-i", "--input_file", default="", help="radio input file",metavar="FILE")
	  parser.add_option("-S", "--sense-bins", type="int", default=128, help="set number of bins in the OFDM block [default=%default]")
#	  parser.add_option("-s", "--size", type="eng_float", default=1024, help="set packet size [default=%default]")
#	  parser.add_option("-M", "--megabytes", type="eng_float", default=10.0, help="set megabytes to transmit [default=%default]")
#	  parser.add_option("","--discontinuous", action="store_true", default=False, help="enable discontinuous mode")
#	  parser.add_option("","--from-file", default=None, help="use file for packet contents")
#	  parser.add_option("-e", "--interface", type="string", default="eth0", help="Select ethernet interface. Default is eth0")
#	  parser.add_option("-m", "--MAC_addr", type="string", default="", help="Select USRP2 by its MAC address.Default is auto-select")
#	  parser.add_option("-j", "--start", type="eng_float", default=1e7, help="Start ferquency [default = %default]")
#	  parser.add_option("-k", "--stop", type="eng_float", default=1e8,help="Stop ferquency [default = %default]")
#	  parser.add_option("-f", "--freq", type="eng_float", action="callback", callback=freq_callback, help="set Tx and/or Rx frequency to FREQ [default=%default]",metavar="FREQ")
	  
	  (self.options, self.args) = parser.parse_args ()
	  if len(self.args) != 0:
		  parser.print_help()
		  sys.exit(1)
	  self.tb = transmitter(Freq)
	  r = gr.enable_realtime_scheduling()
	  if r != gr.RT_OK:
		  print "Warning: failed to enable realtime scheduling"
	      
      def return_obj(self):
	    return self.tb 
	    
      def return_options(self):
	    return self.options
           
def run_transmitter(tb,norestart):  
      if (norestart.value==1):
	  time.sleep(2)
	  tb.start()
	  #print "Carrier map = ",carrier_map
	  #if string.count(carrier_map,'0') >= 10:
		  #sys.stderr.write('Primary Transmission detected\n')
		  #norestart.value=0
	  print "\n\nTransmitting in", Freq.value ,"Hz"
	  tb.stop()
	  tb.wait()
	  return norestart.value
      
def Start_transmitter(Freq,norestart,sync,Frequency):
	trans = trans_init(Freq)
	tb = trans.return_obj()
	
	if Freq.value == 920*10**6:
	      n = synchronization(tb)
	else:
	    options=trans.return_options()
	    tb1=sensor_init(options)
	    n=0
	    while 1:  
		  carrier_map=sense_loop(tb1,Frequency)       
		  n=run_transmitter(tb,norestart)


if __name__ == '__main__':
      try:
	    parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
	    (options, args) = parser.parse_args()
	    Frequency = Value('i',905*10**6)
	    sync = Value('i',1)
	    norestart=Value('i',1)
	    Freq=Value('i',905*10**6)
	    mp=Process(target=Start_transmitter,args=(Freq,norestart,sync,Frequency))
	    mp.start()
	    p=Process(target=transmitter_control,args=(mp,Freq,norestart,sync,Frequency))
	    p.start()
	    
      except KeyboardInterrupt:
	    pass