#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File              : ampel/contrib/weizmann/t0/InfantFilter.py
# License           : BSD-3-Clause
# Author            : m. giomi <matteo.giomi@desy.de>
# Date              : 28.08.2018
# Last Modified Date: 13.08.2019
# Last Modified By  : s. schulze <steve.schulze@weizmann.ac.il>


import logging
from numpy import array, logical_and, where
from urllib.parse import urlparse
from astropy.time import Time

from ampel.contrib.hu.t0.DecentFilter import DecentFilter


class InfantFilter(DecentFilter):
	"""
		Filter derived from the DecentFilter. Additional cuts are applied to look
		for infant transients.
	"""

	# Static version info
	version = 1.0
	resources = ('catsHTM.default',)
	
	
	def __init__(self, on_match_t2_units, base_config=None, run_config=None, logger=None):
		"""
		"""
		if run_config is None:
			raise ValueError("Please check you run configuration")

		self.on_match_t2_units = on_match_t2_units
		self.logger = logger if logger is not None else logging.getLogger()
		
		# init the parent DecentFilter
		DecentFilter.__init__(self, self.on_match_t2_units, base_config, run_config, logger=self.logger)
		
		# now add the parameters which are relevant for this
		# new filter. All the others are passed to the DecentFilter
		config_params = (
			'MAX_TUL',					# maximum time between the first detection and the first non-detection prior to that [days]
			'MIN_FWHM',					# sexctrator FWHM (assume Gaussian) [pix]
			)
		for el in config_params:
			if el not in run_config:
				raise ValueError("Parameter %s missing, please check your channel config" % el)
			if run_config[el] is None:
				raise ValueError("Parameter %s is None, please check your channel config" % el)
			self.logger.info("Using %s=%s" % (el, run_config[el]))
		
		# remember the pars
		self.max_tul					= run_config['MAX_TUL']
		self.min_fwhm					= run_config['MIN_FWHM']




	def apply(self, alert):
		"""
		run the decent filter on the alert
		"""
		
		# --------------------------------------------------------------------- #
		#					CUT ON THE HISTORY OF THE ALERT						#
		# --------------------------------------------------------------------- #

		# cut on length of detection history
		detections_jds = array(sorted(alert.get_values('jd', upper_limits=False)))
		det_tspan = detections_jds[-1] - detections_jds[0]
		if not (self.min_tspan < det_tspan < self.max_tspan):
			self.logger.debug("rejected: detection history is %.3f d long, requested between %.3f and %.3f d"%
				(det_tspan, self.min_tspan, self.max_tspan))
			return None

		# cut on the distance between the first detection and the closest non-detection prior to the first detection
		ulim_jds = alert.get_values('jd', upper_limits=True)
		upperlimits_jds = array(sorted(ulim_jds)) if not ulim_jds is None else []
		if len(upperlimits_jds) > 0:

			mask			= where((detections_jds[0] - upperlimits_jds > 0) & (detections_jds[0] - upperlimits_jds < self.max_tul) )[0]

			if len(mask) == 0:
				self.logger.debug(
					"rejected: no upper limit within %.2f" %
					(self.max_tul)
				)
				return None

		else:
			self.logger.debug(
				"rejected: no upper limits in the alert package"
				)
			return None

		# --------------------------------------------------------------------- #
		#							IMAGE QUALITY CUTS							#
		# --------------------------------------------------------------------- #

		latest = alert.pps[0]
		if not self._alert_has_keys(latest):
			return None

		if not (self.min_fwhm <= latest['fwhm'] <= self.max_fwhm):
			self.logger.debug("rejected: fwhm %.2f not within the range %.2f - %.2f"%
				(latest['fwhm'], self.min_fwhm, self.max_fwhm))
			return None

		# now apply the DecentFilter
		return DecentFilter.apply(self, alert)
