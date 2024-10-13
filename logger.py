import logging

# Create a logger object
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# Create a file handler that logs all messages
file_handler = logging.FileHandler('app.log')
file_handler.setLevel(logging.DEBUG)

# Create a console handler that logs only errors and above
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)

# Create a formatter for the log messages
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add the handlers to the logger
log.addHandler(file_handler)
log.addHandler(console_handler)