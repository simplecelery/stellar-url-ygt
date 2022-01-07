import sys
import io

from you_get import common, json_output

sys.argv.append('--debug')
sys.argv.append('--json')
sys.argv.append('https://www.bilibili.com/bangumi/play/ep386583?theme=movie&from_spmid=666.7.recommend.0')
common.main()
