from app.dns.load_records import load_records, Records, Zone
from app.dns.record import Record


def test_load_records(zones_file):
    records = load_records(zones_file)

    assert records == Records(
        zones=[
            Zone(host='example.com', type='A', answer='1.2.3.4'),
            Zone(host='example.com', type='A', answer='1.2.3.4'),
            Zone(host='example.com', type='CNAME', answer='whatever.com'),
            Zone(host='example.com', type='MX', answer=['whatever.com.', 5]),
            Zone(host='example.com', type='MX', answer=['mx2.whatever.com.', 10]),
            Zone(host='example.com', type='MX', answer=['mx3.whatever.com.', 20]),
            Zone(host='example.com', type='NS', answer='ns1.whatever.com.'),
            Zone(host='example.com', type='NS', answer='ns2.whatever.com.'),
            Zone(host='example.com', type='TXT', answer='hello this is some text'),
            Zone(host='example.com', type='SOA', answer=['ns1.example.com', 'dns.example.com']),
            Zone(
                host='testing.com',
                type='TXT',
                answer=(
                    'one long value: IICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgFWZUed1qcBziAsqZ/LzT2ASxJYuJ5sko1CzWFhFu'
                    'xiluNnwKjSknSjanyYnm0vro4dhAtyiQ7OPVROOaNy9Iyklvu91KuhbYi6l80Rrdnuq1yjM//xjaB6DGx8+m1ENML8PEdSFbK'
                    'Qbh9akm2bkNw5DC5a8Slp7j+eEVHkgV3k3oRhkPcrKyoPVvniDNH+Ln7DnSGC+Aw5Sp+fhu5aZmoODhhX5/1mANBgkqhkiG9w'
                    '0BAQEFAAOCAg8AMIICCgKCAgEA26JaFWZUed1qcBziAsqZ/LzTF2ASxJYuJ5sk'
                ),
            ),
            Zone(host='_caldavs._tcp.example.com', type='SRV', answer=[0, 1, 80, 'caldav']),
            Zone(host='e56.com', type='A', answer='2.3.4.5'),
        ],
    )


def test_create_server(zones_file):
    records = load_records(zones_file)
    [Record(zone) for zone in records.zones]
