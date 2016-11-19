
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


def commandsFromFile(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
    return lines


def commandsToFile(filename, commands):
    with open(filename, 'w+') as file:
        chars = file.write(commands.join('\n'))
    return chars
