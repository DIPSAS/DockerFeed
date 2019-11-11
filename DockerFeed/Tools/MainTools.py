import warnings


def ParseStackListFiles(stackListFiles: []):
    stacks = []
    for stackListFile in stackListFiles:
        with open(stackListFile, 'r') as f:
            for line in f:
                line = line\
                    .replace('\r', '')\
                    .replace('\n', '')\
                    .replace('\t', '')\
                    .replace(' ', '')
                if not(line == ''):
                    stacks.append(line)
    return stacks


def ParseUsernameAndPassword(usernameAndPassword: str):
    if usernameAndPassword is None:
        return [None, None]
    elif not(':' in usernameAndPassword):
        warnings.warn('Cannot parse username and password {0}. It should be of form <user>:<password>'.format(usernameAndPassword))
        return [None, None]
    return usernameAndPassword.split(':')


def PrettyPrintStacks(stacks: [], source: str):
    info = "<--- Stacks from source {0} --->\r\n".format(source)
    for stack in stacks:
        info += stack + '\r\n'

    print(info)
    return info