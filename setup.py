
from distutils.core import setup

setup(name='ampel-contrib-weizmann',
      version='0.3.0',
      packages=['ampel.contrib.weizmann',
                'ampel.contrib.weizmann.t0'],
      package_data = {'': ['*.json']},
      entry_points = {
          'ampel.channels' : [
              'weizmann = ampel.contrib.weizmann.channels:load_channels',
          ],
          'ampel.target_sources' : [
              'TargetSourceListener = ampel.contrib.weizmann.TargetSourceListener:TargetSourceListener',
          ],
          'ampel.pipeline.t0' : [
              'InfantFilter = ampel.contrib.weizmann.t0.InfantFilter:InfantFilter',
          ],
      }
)
