from pysnmp.error import PySnmpError
from flask import Flask
import multiprocessing
import json

from printer import Printer, host_for_name

app = Flask(__name__)
app.config.from_pyfile('settings.py')


def make_printer_status(printer):
    return {
        'name': printer.name,
        'has_error': printer.has_error,
    }


@app.route('/printers')
def printer_list():
    names = []
    for printer in Printer.all():
        names.append(printer.name)
    return json.dumps(names)


@app.route('/printers/status')
def printer_status_threaded():
    pool = multiprocessing.Pool(len(Printer.all()))
    status = pool.map(make_printer_status, Printer.all())
    return json.dumps(status)


@app.route('/printer/<printer_id>')
def printer_info(printer_id):
    try:
        printer = Printer(host_for_name(printer_id))
        info = {
                'name': printer.name,
                'status': printer.status,
                'pages_remaining': printer.pages_remaining,
                'toner_max': 30000,  # TODO: actually calculate this
                'trays': []
        }
        
        for index in range(1, 4):
            capacity = printer.tray_capacity(index)
            current = printer.tray_contents(index)
            tray = {
                    'index': index,
                    'capacity': capacity,
                    'current': current,
            }

            info['trays'].append(tray)
        
        return json.dumps(info)
    except PySnmpError, ex:
        return str(ex)


if __name__ == '__main__':
    app.run()
