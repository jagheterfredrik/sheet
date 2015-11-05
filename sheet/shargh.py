import sheet.server
import argh
from argparse import ArgumentParser
from argh.assembling import add_commands

class ShargumentParserExit(Exception):
    def __init__(self, status, message):
        super(ShargumentParserExit, self).__init__(self)
        self.status = status
        self.message = message

class ShargumentParser(ArgumentParser):
    def __init__(self, *args, **kwargs):
        if 'clear_prog' in kwargs and kwargs['clear_prog'] is not False:
            kwargs['prog'] = ''
        if 'output' in kwargs:
            self.output = kwargs['output']
            del kwargs['output']
        super(ShargumentParser, self).__init__(*args, **kwargs)
    def exit(self, status=0, message=None):
        raise ShargumentParserExit(status, message)
    def error(self, message):
        self.output.write(message+'\n')
    def print_help(self):
        self.output.write(self.format_help())

def serve_commands(commands):
    def cb(args, infile, outfile, errfile):
        parser = ShargumentParser(output=outfile, formatter_class=argh.constants.PARSER_FORMATTER)
        argh.assembling.add_commands(parser, commands, func_kwargs={'output': outfile})
        status = 0
        try:
            if args:
                args = args.split(' ')
            else:
                args = []
            argh.dispatch(parser, argv=args, output_file=outfile, errors_file=errfile)
        except ShargumentParserExit, ex:
            status = ex.status
        except Exception, e:
            print e
            status = 1

        return status

    sheet.server.Server(cb).start()
