import multiprocessing, logging, yaml, os ,click
from multiprocessing import Manager
from .process import WebProcess, MeasurementProcess
from .util import health_check
from threading import Thread, Event
import signal

logger = multiprocessing.log_to_stderr(logging.INFO)


def get_config(config_file):
    with open(config_file) as f:
        config = yaml.load(f)

    return config


def create_manager(config):

    dataManager = Manager()
    config = get_config(config)
    sharedData = dataManager.dict(config)

    return sharedData


@click.group()
def cli():
    pass


@cli.command('run')
@click.option("-c", default=os.path.join(os.getcwd(),"config.yml"))
def main(c):
    handler = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGTERM, handler)

    sharedData = create_manager(c)

    processes = [
        # WebProcess(sharedData),
        MeasurementProcess(sharedData)
    ]

    logger.info("Starting heartbeat")
    heartbeat_event = Event()
    heartbeat_event.set()

    heartbeat = Thread(target=health_check, args=(heartbeat_event,))
    heartbeat.start()

    try:
        for process in processes:
            logger.info('Starting process {}'.format(process))
            process.start()

        for process in processes:
            logger.info('Joining process {}'.format(process))
            process.join()
            logger.info("process {} finished joining".format(process))

    except (KeyboardInterrupt, SystemExit):
        logger.warning('Process interrupted')
        heartbeat_event.clear()

    logger.debug("waiting for heartbeat!")
    heartbeat.join()


@cli.command('setup')
@click.option("-c", default=os.path.join(os.getcwd(),"config.yml"))
def network(c):
    config = get_config(c)

    with open('/etc/wpa_supplicant/wpa_supplicant.conf', 'a') as f:
        f.write(
            "network={{\n    ssid=\"{}\"\n    psk=\"{}\"\n}}".format(
                config['wifi']['ssid'],
                config['wifi']['password']
            )
        )
