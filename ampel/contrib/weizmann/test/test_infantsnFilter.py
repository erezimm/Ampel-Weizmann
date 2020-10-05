import logging
from os.path import dirname, join

import pytest

from ampel.contrib.weizmann.t0.InfantFilter import InfantFilter
from ampel.log.AmpelLogger import AmpelLogger
from ampel.ztf.dev.DevAlertProcessor import DevAlertProcessor


# Load mixed set of transients for check
@pytest.fixture
def tar_path():
    return join(dirname(__file__), "ztf_public_20180731_cut.tar.gz")


@pytest.fixture
def testrunconfig():
    return {
        "min_ndet": 1,
        "max_ndet": 10,
        "min_tspan": 0,
        "max_tspan": 4.5,
        "max_tul": 2.5,
        "min_rb": 0.3,
        "min_drb": 0,
        "min_fwhm": 0.5,
        "max_fwhm": 5.0,
        "max_elong": 100,
        "max_magdiff": 0.75,
        "max_nbad": 5,
        "min_sso_dist": 20,
        "min_gal_lat": 14,
        "gaia_rs": 0,
        "gaia_pm_signif": 3,
        "gaia_plx_signif": 3,
        "gaia_veto_gmag_min": 9,
        "gaia_veto_gmag_max": 20,
        "gaia_excessnoise_sig_max": 999,
        "ps1_sgveto_rad": 2,
        "ps1_sgveto_th": 0.76,
        "ps1_confusion_rad": 3,
        "ps1_confusion_sg_tol": 0.1,
    }


def test_run_t0_infantSN(tar_path, testrunconfig):
    """
    Test infant filter
    """

    my_filter = InfantFilter(logger=AmpelLogger.get_logger(), **testrunconfig)
    dap = DevAlertProcessor(my_filter)
    dap.process_tar(tar_path, iter_max=100)
    assert len(dap.get_accepted_alerts()) == 1
