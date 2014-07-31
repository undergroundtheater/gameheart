class PluginBase(object):

    '''
    Required Fields:
       plugin_label
       plugin_name
       plugin_author string or None
       plugin_version string or None
       plugin_hooks (iterable of string-like objects)
    '''
    plugin_label = 'generic'
    plugin_name = 'Generic Plugin'
    plugin_author = 'Underground Theater, Inc.'
    plugin_version = '0.1'
    plugin_hooks = []
    plugin_config = {}

    def __init__(self):
        self.__aliases = {}

    def add_alias(self, alias_dict):
        self.__aliases.update({
            alias_dict['name']: getattr(self, alias_dict['method_name'], self.hook_unknown),
            })

    def hook_unknown(self, *args, **kwargs):
        raise NotImplementedError("hook or alias not found in plugin %s" % (hook_name, self.__class__.plugin_label))

    def __getattr__(self, name):
        if name in self.__aliases.keys():
            return self.__aliases.get(name)
            
        return self.hook_unknown
