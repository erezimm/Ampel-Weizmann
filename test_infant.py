from ampel.pipeline.t0.DevAlertProcessor import DevAlertProcessor
#from ampel.contrib.hu.t0.DecentFilter import DecentFilter
from ampel.contrib.weizmann.t0.InfantFilter import InfantFilter
from ampel.view.AmpelAlertPlotter import AmpelAlertPlotter

import glob
import json
import logging
import numpy as np
import sys
import time

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# initialize your filter
base_config = {
	'catsHTM.default': "/Volumes/3TB/catsHTM/"
	}

with open('ampel/contrib/weizmann/channels.json', 'r') as f:
	channel_param 	= json.load(f)

run_config	= channel_param['Weizmann_InfantSN']['sources']['ZTFIPAC']['t0Filter']['runConfig']
print(run_config)

# run_config = {
# 	"MIN_NDET": 1,
# 	"MIN_TSPAN": 0.02,
# 	"MAX_TSPAN": 4.5,
# 	"MAX_TUL": 2.5,
# 	"MIN_RB": 0.3,
# 	"MIN_FWHM": 0.5,
# 	"MAX_FWHM": 5.0,
# 	"MAX_ELONG": 100,
# 	"MAX_MAGDIFF": 0.75,
# 	"MAX_NBAD": 5,
# 	"MIN_DIST_TO_SSO": 20,
# 	"MIN_GAL_LAT": 14,
# 	"GAIA_RS": 40,
# 	"GAIA_PM_SIGNIF": 3,
# 	"GAIA_PLX_SIGNIF": 3,
# 	"GAIA_VETO_GMAG_MIN": 9,
# 	"GAIA_VETO_GMAG_MAX": 20,
# 	"PS1_SGVETO_RAD": 2,
# 	"PS1_SGVETO_SGTH": 0.76,
# 	"PS1_CONFUSION_RAD": 3,
# 	"PS1_CONFUSION_SG_TOL": 0.1
# }

# print (run_config)

on_match_t2_units = ["SNCOSMO"]
my_filter = InfantFilter( 
    base_config = base_config,
    run_config = run_config,
    on_match_t2_units=on_match_t2_units,
    logger = logger
    )
# process the stuff

# tar = '/Volumes/Samsung_T3/AMPEL/Partnership_alerts/ztf_partnership_20180608.tar.gz'

# dap = DevAlertProcessor(my_filter, use_dev_alerts=True)
# dap._logger=logger
# print ("processing alerts from %s"%tar)
# start = time.time()
# nproc = dap.process_tar(tar, iter_max=2000)#1e666)
# end = time.time()
# print ("processed %d alerts in %.2e sec"%(nproc, end-start))

# n_good, n_bad = len(dap.get_accepted_alerts()), len(dap.get_rejected_alerts())
# print ("%d alerts accepted by the filter (%.2f perc)"%(n_good, 100*n_good/nproc))
# print ("%d alerts rejected by the filter (%.2f perc)"%(n_bad, 100*n_bad/nproc))

# # plot the stuff
# accepted_plot = AmpelAlertPlotter(interactive = False, plot_dir = "./accepted", plot_name_tmpl="{objectId}.pdf")
# rejected_plot = AmpelAlertPlotter(interactive = False, plot_dir = "./rejected", plot_name_tmpl="{objectId}.pdf")

# accepted = dap.get_accepted_alerts()
# rejected = dap.get_rejected_alerts()

# np.random.seed(42)

# for accepted_alert in accepted:
# 	accepted_plot.summary_plot(accepted_alert)
# for rejected_alert in np.random.choice(rejected, 1, replace=False):
# 	rejected_plot.summary_plot(rejected_alert)

# Check multiple archives

dap = DevAlertProcessor(my_filter, use_dev_alerts=True)
dap._logger=logger

for tar in glob.glob('/Volumes/Samsung_T3/AMPEL/Partnership_alerts/ztf_partnership_*gz'):

	print ("processing alerts from %s"%tar)
	start = time.time()
	nproc = dap.process_tar(tar, iter_max=2000)#1e666)
	end = time.time()
	print ("processed %d alerts in %.2e sec"%(nproc, end-start))

	n_good, n_bad = len(dap.get_accepted_alerts()), len(dap.get_rejected_alerts())
	print ("%d alerts accepted by the filter (%.2f perc)"%(n_good, 100*n_good/nproc))
	print ("%d alerts rejected by the filter (%.2f perc)"%(n_bad, 100*n_bad/nproc))

	# plot the stuff
	accepted_plot = AmpelAlertPlotter(interactive = False, plot_dir = "./accepted", plot_name_tmpl="{objectId}.pdf")
	rejected_plot = AmpelAlertPlotter(interactive = False, plot_dir = "./rejected", plot_name_tmpl="{objectId}.pdf")

	accepted = dap.get_accepted_alerts()
	rejected = dap.get_rejected_alerts()

	np.random.seed(42)

	for accepted_alert in accepted:
		accepted_plot.summary_plot(accepted_alert)
	for rejected_alert in np.random.choice(rejected, 1, replace=False):
		rejected_plot.summary_plot(rejected_alert)
