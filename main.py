#!/usr/bin/python
import requests
import getpass
import math
import time

STATS_URL = '/cgi-bin/sysconf.cgi?page=ajax.asp&action=status_wanInfo'

def toFloat( v, fallback = None ):
	try:
		return float( v )
	except:
		return fallback

def toInt( v, fallback = None ):
	try:
		return int( v )
	except:
		return fallback

class LinkStatus:
	def __init__( self, data ):
		self.state = 'unknown'
		self.operator = None
		self.connectionType = None
		self.scanMode = None
		self.connectionTime = 0
		self.lteMode = None
		self.wanStatus = None
		self.dlFreq = None
		self.ulFreq = None
		self.bandwidth = None
		self.rsrp0 = None
		self.rsrp1 = None
		self.rsrq = None
		self.cinr0 = None
		self.cinr1 = None
		self.sinr0 = None
		self.sinr1 = None
		self.txPower = None
		self.pci = None
		self.wimaxCellID = None
		self.eNodeBID = None
		self.upDataRate = None
		self.upBytes = None
		self.upPackets = None
		self.downDataRate = None
		self.downBytes = None
		self.downPackets = None

		self.load( data )

	def load( self, data ):
		if not data:
			return

		parts = data.split( ';' ) # general, wanInfo, updownLink, secondCellInfo
		if len( parts ) < 3:
			return
		general = parts[0].split( '\t' )

		if general[0].lower( ) != 'successfully':
			return

		self.state = 'connected' if toInt( general[1] ) == 5 else 'connecting'
		self.operator = str( general[2] )
		self.connectionType = str( general[3] )
		self.scanMode = toInt( general[4] )
		self.connectionTime = toFloat( general[5] ) # seconds

		if parts[1].lower( ) != 'not value':
			wanInfo = parts[1].split( '\t' )
			if self.scanMode == 1:
				self.lteMode = wanInfo[0].lower( )
				if self.lteMode == 'sequans':
					if len( parts ) > 3:
						cell2 = parts[3].split( '\t' )
						# cell2InfoCount = toInt( cell2[0] )
						# cell2Info = cell2[1:]
						# todo [addRowToTable(cell2InfoCount, cell2Info)]
					self.wanStatus = [
						'Device Init',
						'SIM Detecting',
						'Device Ready',
						'Search',
						'Network Entry',
						'Attached',
						'Idle',
						'No Signal',
						'Unknown'
					][toInt(wanInfo[1],8)]
					self.dlFreq = toFloat( wanInfo[2] )    # kHz
					self.ulFreq = toFloat( wanInfo[3] )    # kHz
					self.bandwidth = toFloat( wanInfo[4] ) # kHz
					self.rsrp0 = toFloat( wanInfo[5] )     # dBm
					self.rsrp1 = toFloat( wanInfo[6] )     # dBm
					self.rsrq = toFloat( wanInfo[7] )      # dB
					self.cinr0 = toFloat( wanInfo[8] )     # dBm [Carier to Interference + noise ratio]
					self.cinr1 = toFloat( wanInfo[9] )     # dBm
					self.sinr0 = toFloat( wanInfo[20] )    # dBm [Signal to Interference + noise ratio]
					self.sinr1 = toFloat( wanInfo[21] )    # dBm
					self.txPower = toFloat( wanInfo[10] )  # dBm
					self.pci = toFloat( wanInfo[11] )
					self.wimaxCellID = str( wanInfo[12] )
					self.eNodeBID = str( wanInfo[17] )
				elif self.lteMode.lower( ) == 'qualcom':
					pass # todo
			elif self.scanMode == 2: # 3G
				pass # todo
			elif self.scanMode == 3: # 2G
				pass # todo
			elif self.scanMode == 6: # WiMAX
				pass # todo

			updownLink = parts[2].split( '\t' )
			self.upDataRate = toFloat( updownLink[0] )   # kb/s
			self.upBytes = toInt( updownLink[1] )
			self.upPackets = toInt( updownLink[2] )
			self.downDataRate = toFloat( updownLink[3] ) # kb/s
			self.downBytes = toInt( updownLink[4] )
			self.downPackets = toInt( updownLink[5] )

class RouterUI:
	def __init__( self, ip, secure = False ):
		self.protocol = 'https' if secure else 'http'
		self.ip = ip
		self.baseURL = self.protocol + '://' + self.ip

	def get_status( self ):
		try:
			r = requests.get( self.baseURL + STATS_URL )
		except:
			# connection is down - maybe the router has been switched off for a moment
			return None
		return LinkStatus( r.text )

def euclidDB( a, b ):
	return math.log10( math.pow( 10, a * 2 ) + math.pow( 10, b * 2 ) ) / 2

class rolling_window:
	def __init__( self, window ):
		self.store = []
		self.window = window

	def add( self, value ):
		self.store.append( value )
		self.store = self.store[-self.window:]
		return self.get( )

	def get( self ):
		return sum( self.store ) / len( self.store )

def main( ):
	ui = RouterUI( '192.168.15.1' )

	window = 10
	c0l = rolling_window( window )
	c1l = rolling_window( window )
	tDBl = rolling_window( window )

	print( '{:>8} {:>8} {:>8}      Window Averages'.format( 'CINR0', 'CINR1', 'Comb' ) )

	while True:
		time0 = time.clock( )
		status = ui.get_status( )
		if status is None:
			print( '[no connection to router]' )
		elif status.cinr0 is None or status.cinr1 is None:
			print( '[no signal data]' )
		else:
			c0 = status.cinr0
			c1 = status.cinr1
			tDB = euclidDB( c0, c1 )
			c0a = c0l.add( c0 )
			c1a = c1l.add( c1 )
			tDBa = tDBl.add( tDB )
			print( '{:>8.1f} {:>8.1f} {:>8.1f}      {:>8.1f} {:>8.1f} {:>8.1f}'.format(
				c0, c1, tDB,
				c0a, c1a, tDBa
			) )
		delay = time0 + 0.5 - time.clock( )
		if delay > 0:
			time.sleep( delay )

if __name__ == '__main__':
	main( )
