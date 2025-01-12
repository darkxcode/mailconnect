from django.core.management.base import BaseCommand
from django.core.management.commands.runserver import Command as RunserverCommand
import ssl
import os

class Command(RunserverCommand):
    help = 'Runs the server with HTTPS support'

    def handle(self, *args, **options):
        if not os.path.exists('cert.pem') or not os.path.exists('key.pem'):
            # Generate self-signed certificate
            from OpenSSL import crypto
            k = crypto.PKey()
            k.generate_key(crypto.TYPE_RSA, 2048)
            cert = crypto.X509()
            cert.get_subject().CN = "localhost"
            cert.set_serial_number(1000)
            cert.gmtime_adj_notBefore(0)
            cert.gmtime_adj_notAfter(10*365*24*60*60)
            cert.set_issuer(cert.get_subject())
            cert.set_pubkey(k)
            cert.sign(k, 'sha256')
            
            # Save certificate
            with open("cert.pem", "wb") as f:
                f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
            with open("key.pem", "wb") as f:
                f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))

        from django.core.servers.basehttp import WSGIServer
        WSGIServer.ssl_certificate = "cert.pem"
        WSGIServer.ssl_certificate_key = "key.pem"
        super().handle(*args, **options) 