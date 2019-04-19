handler_classes = {}
event_classes = {}


def register_handler(command):
    def register_class(handler_class):
        assert command not in handler_classes
        handler_classes[command] = handler_class
        return handler_class

    return register_class


def register_event(name):
    def register_class(event_class):
        assert name not in event_classes
        event_classes[name] = event_class
        return event_class

    return register_class
