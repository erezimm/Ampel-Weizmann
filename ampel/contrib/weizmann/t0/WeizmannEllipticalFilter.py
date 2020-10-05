#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File              : contrib/Weizmann/t0/WeizmannEllipticalFilter.py
# License           : BSD-3-Clause
# Author            : j. nordin <j.nordin@physik.hu-berlin.de>
# Date              : 28.08.2019
# Last Modified Date: 02.10.2020
# Last Modified By  : Jakob van Santen <jakob.van.santen@desy.de>


from functools import partial
from typing import Callable, Optional

from ampel.abstract.AbsAlertFilter import AbsAlertFilter
from ampel.alert.PhotoAlert import PhotoAlert
from ampel.contrib.hu.base.ExtcatsUnit import ExtcatsUnit


class WeizmannEllipticalFilter(ExtcatsUnit, AbsAlertFilter[PhotoAlert]):
    """
    This filter reject candidates if they have less than a certain number
    of detection or if they are not positive subtractions (reference lower than sci),
    or if they do not match with the position of a cataloged elliptical galaxy.
    """

    min_ndet: int
    elliptical_search_radius: float

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        # feedback
        for k in self.__annotations__:
            self.logger.info(f"Using {k}={getattr(self, k)}")

        self.ido_query: Callable[[float, float], bool] = partial(
            self.get_extcats_query("ido_ellipticals").binaryserach,
            rs_arcsec=self.elliptical_search_radius,
        )

    def apply(self, alert: PhotoAlert) -> bool:

        # cut on the number of previous detections
        if len(alert.pps) < self.min_ndet:
            self.logger.debug("rejected", extra={"ndet": len(alert.pps)})
            return False

        # now consider the last photopoint
        latest = alert.pps[0]["body"]

        # check if it a positive subtraction
        if not (
            latest["isdiffpos"]
            and (latest["isdiffpos"] == "t" or latest["isdiffpos"] == "1")
        ):
            self.logger.debug("rejected: 'isdiffpos' is %s", latest["isdiffpos"])
            return False

        # and match with the catalogs using position of latest photopoint
        return self.ido_query(latest["ra"], latest["dec"])
