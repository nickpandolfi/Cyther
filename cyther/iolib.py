
RESPONSES_ERROR = "Argument 'acceptableResponses' cannot be of type: '{}'"


def getResponse(message, acceptableResponses):
    if isinstance(acceptableResponses, str):
        acceptableResponses = (acceptableResponses,)
    else:
        if not isinstance(acceptableResponses, tuple):
            raise ValueError(RESPONSES_ERROR.format(type(acceptableResponses)))

    response = input(message)
    while response not in acceptableResponses:
        response = input(message)
    return response


class CompilingCommands:
    def __init__(self, commands=None):
        self.__commands = commands

    def toFile(self, filename=None):
        if not filename:
            filename = 'cytherize'
        with open(filename, 'w+') as file:
            chars = file.write(self.__commands.join('\n'))
        return chars

    def fromFile(self, filename=None):
        if not filename:
            filename = 'cytherize'
        with open(filename, 'r') as file:
            lines = file.readlines()
        if self.__commands is not None:
            raise ValueError("The commands '{}' already exist, you cannot"
                             "overwrite them".format(self.__commands))
        self.__commands = eval(lines)

    def sortCommands(self):
        """ Intended to put the -l commands at the end """
        pass

    def getCommands(self):
        self.sortCommands()
        return self.__commands


