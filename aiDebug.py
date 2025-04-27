import aiConfig

def debug_print(*args):
    if aiConfig.DEBUG:
        modified_args = []
        for arg in args:
            if isinstance(arg, str):
                modified_args.append(arg.replace('\n', '*'))
            else:
                modified_args.append(str(arg))
        print(*modified_args)
