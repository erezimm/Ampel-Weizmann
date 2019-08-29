#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File              : contrib/hu/t0/LensedTransientFilter.py
# License           : BSD-3-Clause
# Author            : j. nordin <j.nordin@physik.hu-berlin.de>
# Date              : 28.08.2019
# Last Modified Date: 28.08.2019
# Last Modified By  : j. nordin <j.nordin@physik.hu-berlin.de>

import numpy as np
from pydantic import BaseModel
from extcats import CatalogQuery
from pymongo import MongoClient

from ampel.pipeline.logging.AmpelLogger import AmpelLogger
from ampel.base.abstract.AbsAlertFilter import AbsAlertFilter

class CoreCollapseEllipticalFilter(AbsAlertFilter):
	"""
	"""

	# Static version info
	version = 0.1
	resources = ('extcats.reader',)
	
	class RunConfig(BaseModel):
		"""
 		Necessary class to validate configuration.
		"""
		
		MinNdet			: int
		EllipticalSearchRadius	: float




	def __init__(self, on_match_t2_units, base_config=None, run_config=None, logger=None):
		"""
			This filter reject candidates if they have less than a certain number
			of detection or if they are not positive subtractions (reference lower than sci),
			or if they do not match with the position of a cataloged elliptical galaxy.
		"""
		
		if run_config is None:
			raise ValueError("Please check you run configurtion")
		
		self.logger = AmpelLogger.get_logger() if logger is None else logger
		
		self.on_match_t2_units = on_match_t2_units
		self.min_ndet = run_config.MinNdet
		self.search_radiuses = {
			'ellip': run_config.EllipticalSearchRadius
		}
		
		# init the catalog query objects for the different lens catalogs
		catq_kwargs = {
			'logger': logger, 
			'dbclient': MongoClient(base_config['extcats.reader'])
		}
		self.elliptical_query = CatalogQuery.CatalogQuery(
			"ellip", ra_key = 'ra_deg', dec_key = 'dec_deg', **catq_kwargs
		)
		


		# Feedback
		self.logger.info("Catalog: Elliptical --> Search radius: %.2e arcsec"%( run_config.EllipticalSearchRadius))
		

	def apply(self, alert):
		"""
		Mandatory implementation.
		To exclude the alert, return *None*
		To accept it, either 
			* return self.on_match_default_flags
			* return a custom combination of T2 unit names
		"""

		# cut on the number of previous detections
		if len(alert.pps) < self.min_ndet:
			return None
		
		# now consider the last photopoint
		latest = alert.pps[0]
		
		# check if it a positive subtraction
		if not (
				latest['isdiffpos'] and 
				(latest['isdiffpos'] == 't' or latest['isdiffpos'] == '1')
			):
			self.logger.debug("rejected: 'isdiffpos' is %s", latest['isdiffpos'])
			return None
		
		# and match with the catalogs using position of latest photopoint
		rs = self.search_radiuses["ellip"]
		if self.elliptical_query.binaryserach(latest["ra"], latest["dec"], rs):
				self.logger.debug("searching matches in %s within %.2f arcsec"%(cat, rs))
				return self.on_match_t2_units 
		self.logger.debug("rejected: alert position did not match any lens in the catalogs.")
		return None



