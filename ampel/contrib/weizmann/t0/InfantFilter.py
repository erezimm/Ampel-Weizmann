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
from pydantic import BaseModel

from ampel.contrib.hu.t0.DecentFilter import DecentFilter


class InfantFilter(DecentFilter):
	"""
		Filter derived from the DecentFilter. Additional cuts are applied to look
		for infant transients.
	"""

	# Static version info
	version = 1.0
	resources = ('catsHTM.default',)


	class RunConfig(BaseModel):
		"""
 		Necessary class to validate configuration.
		"""
		
		MIN_NDET					: int	# min number of previous detections
		MAX_NDET					: int	# max number of previous detections (allows to set separate configurations for these)
		MIN_TSPAN 					: float	# minimum duration of alert detection history [days]
		MAX_TSPAN 					: float # maximum duration of alert detection history [days]
		MAX_TUL						: float # # maximum time between the first detection and the first non-detection prior to that [days]
		MIN_FWHM					: float # sexctrator FWHM (assume Gaussian) [pix]
		MIN_RB						: float # real bogus score
		MIN_DRB						: float = 0.  # deep learning real bogus score
		MAX_FWHM					: float # sexctrator FWHM (assume Gaussian) [pix]
		MAX_ELONG					: float	# Axis ratio of image: aimage / bimage 
		MAX_MAGDIFF					: float	# Difference: magap - magpsf [mag]
		MAX_NBAD					: int	# number of bad pixels in a 5 x 5 pixel stamp
		MIN_DIST_TO_SSO				: float	#distance to nearest solar system object [arcsec]
		MIN_GAL_LAT 				: float	#minium distance from galactic plane. Set to negative to disable cut.
		GAIA_RS						: float	#search radius for GAIA DR2 matching [arcsec]
		GAIA_PM_SIGNIF				: float	# significance of proper motion detection of GAIA counterpart [sigma]
		GAIA_PLX_SIGNIF				: float	# significance of parallax detection of GAIA counterpart [sigma]
		GAIA_VETO_GMAG_MIN			: float	# min gmag for normalized distance cut of GAIA counterparts [mag]
		GAIA_VETO_GMAG_MAX			: float	# max gmag for normalized distance cut of GAIA counterparts [mag]
		GAIA_EXCESSNOISE_SIG_MAX	: float	# maximum allowed noise (expressed as significance) for Gaia match to be trusted.
		PS1_SGVETO_RAD				: float	# maximum distance to closest PS1 source for SG score veto [arcsec]
		PS1_SGVETO_SGTH				: float	# maximum allowed SG score for PS1 source within PS1_SGVETO_RAD
		PS1_CONFUSION_RAD			: float	# reject alerts if the three PS1 sources are all within this radius [arcsec]
		PS1_CONFUSION_SG_TOL		: float	# and if the SG score of all of these 3 sources is within this tolerance to 0.5

	
	def __init__(self, on_match_t2_units, base_config=None, run_config=None, logger=None):
		"""
		"""
		if run_config is None:
			raise ValueError("Please check you run configuration")

		self.on_match_t2_units = on_match_t2_units
		self.logger = logger if logger is not None else logging.getLogger()
		
		# init the parent DecentFilter
		DecentFilter.__init__(self, self.on_match_t2_units, base_config, run_config, logger=self.logger)
		
		
		# remember the pars
		rcdict = run_config.dict()
		self.max_tul					= rcdict['MAX_TUL']
		self.min_fwhm					= rcdict['MIN_FWHM']
		self.max_ndet					= rcdict['MAX_NDET']




	def apply(self, alert):
		"""
		run the decent filter on the alert
		"""
		
		# --------------------------------------------------------------------- #
		#					CUT ON THE HISTORY OF THE ALERT						#
		# --------------------------------------------------------------------- #

		npp = len(alert.pps)
		if not (self.min_ndet <= npp <= self.max_ndet):
			self.logger.info(None, extra={'nDet': npp})
			return None

		# cut on length of detection history
		detections_jds = array(sorted(alert.get_values('jd', upper_limits=False)))
		det_tspan = detections_jds[-1] - detections_jds[0]
		if not (self.min_tspan <= det_tspan <= self.max_tspan):
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

		latest = alert.pps[0]    # Not guranteed to be latest!?
		if not self._alert_has_keys(latest):
			return None

		if not (self.min_fwhm <= latest['fwhm'] <= self.max_fwhm):
			self.logger.debug("rejected: fwhm %.2f not within the range %.2f - %.2f"%
				(latest['fwhm'], self.min_fwhm, self.max_fwhm))
			return None

		# now apply the DecentFilter
		return DecentFilter.apply(self, alert)
