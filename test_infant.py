from ampel.pipeline.t0.DevAlertProcessor import DevAlertProcessor
#from ampel.contrib.hu.t0.DecentFilter import DecentFilter
from ampel.contrib.weizmann.t0.InfantFilter import InfantFilter
from ampel.view.AmpelAlertPlotter import AmpelAlertPlotter

import glob
import json
import logging
import numpy as np
import os
import sys
import time

logger				= logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# initialize your filter
base_config 		= {'catsHTM.default': "/raid/eran/catsHTM/"}

with open('ampel/contrib/weizmann/channels.json', 'r') as f:
	channel_param 	= json.load(f)

run_config	= channel_param['WEIZMANN_INFANTSN']['sources']['ZTFIPAC']['t0Filter']['runConfig']
print(run_config)

on_match_t2_units 	= ["SNCOSMO"]
my_filter 			= InfantFilter( 
									base_config 		= base_config,
									run_config 			= run_config,
									on_match_t2_units	= on_match_t2_units,
									logger 				= logger
									)

# process the stuff

tar 				= sys.argv[1]
dir					= tar.split('/')[-1].replace('.tar.gz', '')

try:
	os.system("rm -r ./accepted_{name} ./rejected_{name}".format(name=dir))
except:
	pass

try:
	os.system("mkdir accepted_{name} rejected_{name}".format(name=dir))
except:
	pass


dap 				= DevAlertProcessor(my_filter, use_dev_alerts=True)
dap._logger			= logger

print ("processing alerts from %s"%tar)

start 				= time.time()
nproc 				= dap.process_tar(tar, iter_max=1e5)#1e666)

print ("processed %d alerts in %.2e sec"%(nproc, time.time() - start))

n_good, n_bad 		= len(dap.get_accepted_alerts()), len(dap.get_rejected_alerts())

print ("%d alerts accepted by the filter (%.2f perc)"%(n_good, 100*n_good/nproc))
print ("%d alerts rejected by the filter (%.2f perc)"%(n_bad, 100*n_bad/nproc))

# plot the stuff
accepted_plot 		= AmpelAlertPlotter(interactive = False, plot_dir = "./accepted_{name}".format(name=dir), plot_name_tmpl="{objectId}.pdf")
rejected_plot 		= AmpelAlertPlotter(interactive = False, plot_dir = "./rejected_{name}".format(name=dir), plot_name_tmpl="{objectId}.pdf")

accepted			= dap.get_accepted_alerts()
rejected 			= dap.get_rejected_alerts()

np.random.seed(42)

for accepted_alert in accepted:
	accepted_plot.summary_plot(accepted_alert)
for rejected_alert in np.random.choice(rejected, 1, replace=False):
	rejected_plot.summary_plot(rejected_alert)

output				= open('results.log', 'a')
output.write('{archive}\t{alerts}\t{accepted}\t{rejected}\n'.format(archive=dir, alerts=nproc, accepted=n_good, rejected=n_bad))
output.close