
from setuptools import setup

setup(name='ampel-contrib-weizmann',
      version='0.5.0',
      packages=['ampel.contrib.weizmann',
                'ampel.contrib.weizmann.t0'],
      package_data = {'': ['*.json']},
      entry_points = {
          'ampel.channels' : [
              'weizmann = ampel.contrib.weizmann.channels:load_channels',
          ],
          'ampel.pipeline.t0.units' : [
              'InfantFilter = ampel.contrib.weizmann.t0.InfantFilter:InfantFilter',
              'CoreCollapseEllipticalFilter = ampel.contrib.weizmann.t0.CoreCollapseEllipticalFilter:CoreCollapseEllipticalFilter',
          ],
          'ampel.pipeline.t3.jobs' : [
              'weizmann = ampel.contrib.weizmann.channels:load_t3_jobs',
          ]
      }
)
