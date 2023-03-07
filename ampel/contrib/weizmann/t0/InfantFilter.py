#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File              : ampel/contrib/weizmann/t0/InfantFilter.py
# License           : BSD-3-Clause
# Author            : m. giomi <matteo.giomi@desy.de>
# Date              : 28.08.2018
# Last Modified Date: 03.03.2023
# Last Modified By  : J Nordin <jnordin@physik.hu-berlin.de>


import numpy as np

from ampel.protocol.AmpelAlertProtocol import AmpelAlertProtocol
from ampel.ztf.t0.DecentFilter import DecentFilter


class InfantFilter(DecentFilter):
    """
    Filter derived from the DecentFilter. Additional cuts are applied to look
    for infant transients.
    """

    max_ndet: int  #: max number of previous detections (to select young transients only)
    max_tul: float  #: maximum time between the first detection and the first non-detection prior to that [days]
    min_fwhm: float  #: sexctrator fwhm (assume gaussian) [pix]

    def process(self, alert: AmpelAlertProtocol) -> None | bool | int:

        # -------------------------------------------------------------------- #
        #                   CUT ON THE HISTORY OF THE ALERT                    #
        # -------------------------------------------------------------------- #

        pps = [el for el in alert.datapoints if el.get("candid") is not None]
        npp = len(pps)
        # Add max_ndet to decent filter, to skip this.
        if not (self.min_ndet <= npp <= self.max_ndet):
            self.logger.info(None, extra={"nDet": npp})
            return None


        # cut on the distance between the first detection and the closest
        # non-detection prior to the first detection
        detections_jds = sorted( [pp['jd'] for pp in pps] )
        ulim_jds = [el['jd'] for el in alert.datapoints if el.get("candid") is None]
        upperlimits_jds = np.array(sorted(ulim_jds)) if not ulim_jds is None else []
        
        if len(upperlimits_jds) > 0:

            mask = np.where(
                (detections_jds[0] - upperlimits_jds > 0)
                & (detections_jds[0] - upperlimits_jds < self.max_tul)
            )[0]

            if len(mask) == 0:
                self.logger.debug(
                    "rejected: no upper limit within %.2f" % (self.max_tul)
                )
                return None

        else:
            self.logger.debug("rejected: no upper limits in the alert package")
            return None

        # -------------------------------------------------------------------- #
        #                           IMAGE QUALITY CUTS                         #
        # -------------------------------------------------------------------- #

        latest = alert.datapoints[0]
        if not self._alert_has_keys(latest):
            return None

        # Add min_fhwm to decent filter, to skip this.
        if not (self.min_fwhm <= latest["fwhm"] <= self.max_fwhm):
            self.logger.debug(
                "rejected: fwhm %.2f not within the range %.2f - %.2f"
                % (latest["fwhm"], self.min_fwhm, self.max_fwhm)
            )
            return None

        # now apply the DecentFilter
        return DecentFilter.process(self, alert)
