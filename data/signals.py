from blinker import signal

data_generator_init = signal('data_generator_init')
data_generator_finalized = signal('data_generator_finalized')
data_writer_finalized = signal('data_writer_finalized')

data_generator_preread = signal('data_generator_preread')
data_generator_context = signal('data_generator_context')
