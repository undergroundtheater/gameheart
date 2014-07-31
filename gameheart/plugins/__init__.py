from gameheart.plugins.generic import GenericPlugin

class GHPluginManager(object):
    __active_plugins = {}
    __plugin_config = {}

    def __init__(self):
        pass

    def activate_plugin(self, p_class):
        plabel = self.get_plugin_label(p_class)
        pname = self.get_plugin_name(p_class)
        self.__active_plugins.update({
                plabel: p_class()
            })

        self.__plugin_config.update({
                plabel: {'name': pname}.update(p_class.plugin_config),
            })

    def get_plugin_name(self, p_class):
        return p_class.plugin_name

    def get_plugin_label(self, p_class):
        return p_class.plugin_label

    def get_plugin_config(self, p_class):
        return self.__plugin_config.get(self.get_plugin_label(p_class), {})

    def get_hooks(self, p_class):
        return p_class.plugin_hooks

    def get_hook_methods(self, hook):
        hook_methods = {}
        for plugin_name, plugin in self.active_plugins().items():
            p_class = plugin.__class__
            if hook in self.get_hooks(p_class):
                if callable(getattr(plugin, hook)):
                    hook_methods.update({
                        self.get_plugin_label(p_class): getattr(plugin, hook),
                        })

        return hook_methods

    def call_hooks(self, hook, *args, **kwargs):
        hooks = self.get_hook_methods(hook)
        hook_return = {}
        new_args = args
        new_kwargs = kwargs
        for plugin_label, hook in hooks.items():
            try:
                new_args, new_kwargs = hook(*new_args, **new_kwargs)
            except NotImplementedError:
                # Don't even add it to the chain
                pass 
            # We want all hooks to continue as if this one
            # were not broken, so let's continue and handle it
            # somewhat gracefully
            except Exception as ex:

                hook_return.update({
                        plugin_label: ex
                    })

                return [hook_return], {'error': hook_return}

        return new_args, new_kwargs

    def active_plugins(self):
        return self.__active_plugins

manager = GHPluginManager()

#manager.activate_plugin(GenericPlugin)
