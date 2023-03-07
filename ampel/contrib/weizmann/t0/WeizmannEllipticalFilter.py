#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File              : contrib/Weizmann/t0/WeizmannEllipticalFilter.py
# License           : BSD-3-Clause
# Author            : j. nordin <j.nordin@physik.hu-berlin.de>
# Date              : 28.08.2019
# Last Modified Date: 02.10.2020
# Last Modified By  : Jakob van Santen <jakob.van.santen@desy.de>


from ampel.ztf.base.CatalogMatchFilter import CatalogMatchFilter

class WeizmannEllipticalFilter(CatalogMatchFilter):
    """
    This filter reject candidates if they have less than a certain number
    of detection or if they are not positive subtractions (reference lower than sci),
    or if they do not match with the position of a cataloged elliptical galaxy.
    """

    elliptical_search_radius: float

    def __init__(self, **kwargs) -> None:
        kwargs["accept"] = {
            "name": "ido_ellipticals",
            "use": "extcats",
            "rs_arcsec": kwargs.get("elliptical_search_radius"),
        }
        super().__init__(**kwargs)
