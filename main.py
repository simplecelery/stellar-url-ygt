import traceback
import StellarPlayer
import os
import sys
import time
import io
import json

plugin_dir = os.path.dirname(__file__)

sys.path.append(plugin_dir)

# monkey patch : don't call TextIOWrapper
sys.stdout.isatty = lambda: False
sys.stdout.buffer = sys.stdout
io.TextIOWrapper = lambda x, **k: x  
from you_get import common, json_output


class MyPlugin(StellarPlayer.IStellarPlayerPlugin):
    def __init__(self, player: StellarPlayer.IStellarPlayer):
        super().__init__(player)

    def start(self):
        super().start()

    def onUrlInput(self, *a):
        dispatchId = None
        if hasattr(self.player, 'dispatchResult'):
            dispatchId, url = a
        else:
            url, = a

        print(f'{dispatchId=}, {url=}')

        # monkey patch: get print content
        old_stdout = sys.stdout
        sys.stdout = buffer = io.StringIO()
        argv = sys.argv[:]
        result = []
        try:
            sys.argv.append('--json')        
            sys.argv.append('--debug')    
            sys.argv.append(url)
            common.main()
            sys.argv=argv
            sys.stdout = old_stdout

            content = buffer.getvalue()
            begin = content.find('{')
            if begin != -1:
                content = content[begin:]
            end = content.rfind('}')
            if end != -1:
                content = content[:end+1]

            print("-----------------")
            print(content)
            print("-----------------")
            j = json.loads(content)
            headers = {}
            extra = j.get('extra', {})
            if 'referer' in extra:
                headers['headers'] = f"Referer: {extra['referer']}"
            if 'ua' in extra:
                headers['user_agent'] = extra['ua']

            title = j.get('title')            
            for k, v in j['streams'].items():
                src = []
                if type(v['src']) == str:
                    src.append(v['src'])
                else:
                    for s in v['src']:
                        if type(s) == str:
                            src.append(s)

                if src:
                    result.append({
                        'src': src,
                        'size': v['size'],
                        'headers': headers,
                        'title': title
                    })

            result.sort(key=lambda x: x['size'], reverse=True)
        except:
            import traceback
            traceback.print_exc()
            sys.argv = ['']
            sys.stdout = old_stdout
            result = []

        if dispatchId is None:
            self.player.urlResult(url, result)
        else:
            self.player.dispatchResult(dispatchId, url=url, result=result)


def newPlugin(player: StellarPlayer.IStellarPlayer, *arg):
    plugin = MyPlugin(player)
    return plugin


def destroyPlugin(plugin: StellarPlayer.IStellarPlayerPlugin):
    plugin.stop()
