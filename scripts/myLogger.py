import logging


def giveMeLoggingObject():
    format_str = '%(asctime)s:%(message)s'
    file_name  = 'FORENSIC-LOG.log'
    ### creates one Global logger: logging.basicConfig
    logging.basicConfig(format=format_str, filename=file_name, level=logging.INFO)
    loggerObj = logging.getLogger('simple-logger')
    return loggerObj
