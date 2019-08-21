import pytest
from os.path import dirname, join
import logging
from ampel.ztf.pipeline.t0.DevAlertProcessor import DevAlertProcessor
from ampel.contrib.weizmann.t0.InfantFilter import InfantFilter


# Load mixed set of transients for check
@pytest.fixture
def tar_path():
    return join(dirname(__file__),'ztf_public_20180731_cut.tar.gz')

@pytest.fixture
def testrunconfig():
    return InfantFilter.RunConfig(
                    MIN_NDET = 1,
                    MIN_TSPAN = 0,
                    MAX_TSPAN = 4.5,
                    MAX_TUL = 2.5,
                    MIN_RB = 0.3,
                    MIN_DRB = 0,
                    MIN_FWHM = 0.5,
                    MAX_FWHM = 5.0,
                    MAX_ELONG = 100,
                    MAX_MAGDIFF = 0.75,
                    MAX_NBAD = 5,
                    MIN_DIST_TO_SSO = 20,
                    MIN_GAL_LAT = 14,
                    GAIA_RS = 0,
                    GAIA_PM_SIGNIF = 3,
                    GAIA_PLX_SIGNIF = 3,
                    GAIA_VETO_GMAG_MIN = 9,
                    GAIA_VETO_GMAG_MAX = 20,
                    GAIA_EXCESSNOISE_SIG_MAX = 999,
                    PS1_SGVETO_RAD = 2,
                    PS1_SGVETO_SGTH = 0.76,
                    PS1_CONFUSION_RAD = 3,
                    PS1_CONFUSION_SG_TOL = 0.1
                    )




def test_run_t0_infantSN(tar_path, testrunconfig):
    '''
    Test infant filter
    '''

    my_filter = InfantFilter([], base_config={'catsHTM.default':None}, run_config=testrunconfig, logger=logging.getLogger())
    dap = DevAlertProcessor(my_filter, use_dev_alerts=True)
    dap.process_tar(tar_path, iter_max=100)
    assert len(dap.get_accepted_alerts()) == 1
 

