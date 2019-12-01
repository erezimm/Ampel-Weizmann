#!/usr/bin/env python
# coding: utf-8

import sys

# # Testing Idos elliptical filter

# In[1]:

datestring = '20191117'
subset = sys.argv[1]

import logging, os
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logpath = '/home/jnordin/tmp/'
handler = logging.FileHandler(os.path.join(logpath, 'test_idoelliptical.log'))
logger.addHandler(handler)


# First step is to load the filter, using the path specified in the `setup.py` file in the repository. 
# 

# In[2]:


from ampel.contrib.weizmann.t0.WeizmannEllipticalFilter import WeizmannEllipticalFilter


# The full behaviour of a T0 unit is controlled by a set of parameters provided as `run_config`. We here directly specify these as a dictionary. When implemented for a live channel these constitue one entry to the `channel.json` main configuration file.

# In[3]:


runConfig = {
                    "MinNdet": 2,
                    "EllipticalSearchRadius": 30,
                    }


# In[ ]:





# In[4]:


baseModel_runConfig = WeizmannEllipticalFilter.RunConfig(**runConfig)


# In[5]:


import os
import urllib.request

# Small test
#tar_url = 'https://ztf.uw.edu/alerts/public/ztf_public_20181129.tar.gz'
#tar_path = '/home/jnordin/data/ztfalerts/ztf_public_20181129.tar.gz'
# No stars
#tar_url = None # Does not exist online
#tar_path = '/home/jnordin/data/ztfalerts/ztf_public_20180731_nostars.tar.gz'
# Test patch
tar_url = None # Does not exist online
tar_path = '/home/jnordin/data/ztfalerts/subset%s.tar.gz'%(subset)

if not os.path.isfile(tar_path):
    print('Downloading tar')
    urllib.request.urlretrieve(tar_url, tar_path)


# The Decent does assume the catSHTM server to pe present. Have to write a nice workaraound for test cases when it is not.

# In[6]:


on_match_t2_units = []
baseConfig = {'extcats.reader': "mongodb://localhost:27017"}




from ampel.pipeline.t0.DevAlertProcessor import DevAlertProcessor

my_filter = WeizmannEllipticalFilter(on_match_t2_units, base_config=baseConfig, run_config=baseModel_runConfig, logger=logger)
dap = DevAlertProcessor(my_filter, use_dev_alerts=True)


# In[8]:


iter_batch = 1000000
iter_runs = 1
skip_runs = 0

for k in range(iter_runs):

	import time

	print ("processing alert batch %s from %s" %(k, tar_path) )
	start = time.time()
	nproc = dap.process_tar(tar_path, iter_max=iter_batch, iter_skip=k*iter_batch+skip_runs*iter_batch)
	end = time.time()
	print ("processed %d alerts in %.2e sec"%(nproc, end-start))


# In[9]:


n_good, n_bad = len(dap.get_accepted_alerts()), len(dap.get_rejected_alerts())
print ("%d alerts accepted by the filter (%.2f perc)"%(n_good, 100*n_good/nproc))
print ("%d alerts rejected by the filter (%.2f perc)"%(n_bad, 100*n_bad/nproc))


# In[ ]:





# In[10]:


accepted = dap.get_accepted_alerts()
outf = open('/home/jnordin/tmp/ellipticals_%s.txt'%(datestring),'a')

for a in accepted:
    print(a.get_id())
    outf.write(a.get_id()+'\n')

outf.close()


# In[ ]:





# In[ ]:




