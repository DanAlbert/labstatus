from pysnmp.entity.rfc3413.oneliner import cmdgen
import re


def host_for_name(name):
    subdomain = 'engr'
    if 'kec1130' in name:
        subdomain = 'eecs'
    elif 'gl02' in name or 'mfd107' in name:
        subdomain = 'cbee'
    elif 'bat041' in name:
        subdomain = 'mime'
    elif 'kear302' in name or 'owen' in name:
        subdomain = 'cce'

    return '%s.%s.oregonstate.edu' % (name, subdomain)


class Printer(object):
    OIDS = {
            'name': '1.3.6.1.2.1.1.5.0',
            'status': '.1.3.6.1.2.1.43.16.5.1.2.1.1',
            'pages-remaining': '1.3.6.1.2.1.43.11.1.1.9.1.1',
            'tray1-capacity': '1.3.6.1.2.1.43.8.2.1.9.1.1',
            'tray2-capacity': '1.3.6.1.2.1.43.8.2.1.9.1.2',
            'tray3-capacity': '1.3.6.1.2.1.43.8.2.1.9.1.3',
            'tray4-capacity': '1.3.6.1.2.1.43.8.2.1.9.1.5',
            'tray1-contents': '1.3.6.1.2.1.43.8.2.1.10.1.1',
            'tray2-contents': '1.3.6.1.2.1.43.8.2.1.10.1.2',
            'tray3-contents': '1.3.6.1.2.1.43.8.2.1.10.1.3',
            'tray4-contents': '1.3.6.1.2.1.43.8.2.1.10.1.5',
    }
    
    def __init__(self, address, port=161, community='public'):
        self.address = address
        self.port = port
        self.community = community

    @classmethod
    def all(cls):
        printer_names = [
            'bat041-prn1',
            'bat041-prn2',
            'dear115-prn1',
            'dear115-prn2',
            'dear119-prn1',
            'dear119-prn2',
            'gl02-prn1',
            'gl02-prn2',
            'graf202-prn1',
            'graf202-prn2',
            'kear302-prn',
            'kec1130-prn1',
            'kec1130-prn2',
            'kec1130-prn3',
            'mfd107-prn1',
            'mfd107-prn2',
            'owen237-prn1',
            'owen237-prn2',
            'owen241-prn1',
            'owen241-prn2',
            'rog338-prn1',
            'rog338-prn2',
        ]

        return [Printer(host_for_name(name)) for name in printer_names]

    @property
    def name(self):
        return self.get(self.OIDS['name'])
    
    @property
    def status(self):
        return self.get(self.OIDS['status'])

    @property
    def has_error(self):
        status = self.status
        if status.lower() == 'replace black':
            return True
        elif re.match(r'^ERROR:', status):
            return True
        elif self.pages_remaining < 0:
            return True
        else:
            return False

    @property
    def pages_remaining(self):
        return int(self.get(self.OIDS['pages-remaining']))
    
    def tray_contents(self, index):
        return self.get(self.OIDS['tray%d-contents' % index])
    
    def tray_capacity(self, index):
        return self.get(self.OIDS['tray%d-capacity' % index])

    def get(self, oid):
        cmd = cmdgen.CommandGenerator()

        err_indicator, err_status, err_index, var_binds = cmd.getCmd(
                cmdgen.CommunityData(self.community),
                cmdgen.UdpTransportTarget((self.address, self.port)),
                oid)
        
        if err_indicator:
            return err_indicator
        else:
            if err_status:
                return '%s at %s' % (err_status.prettyPrint(), err_index and
                        var_binds[int(err_index) - 1] or '?')
            else:
                return var_binds[0][1].prettyPrint()
