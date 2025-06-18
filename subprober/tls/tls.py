from datetime import datetime
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, ec, dsa 
from cryptography.x509.extensions import AuthorityKeyIdentifier, SubjectKeyIdentifier, SignedCertificateTimestamps
from subprober.logger.logger import Logger


class TlsCert:
    def __init__(self):
        self.logger = Logger()

    async def tlsinfo(self,network_stream=None) -> dict:
        tlsinfo = {}
        if network_stream:
            try:
                ssl_object = network_stream.get_extra_info("ssl_object")
                if not ssl_object:
                    return tlsinfo 

                ssl_bin = ssl_object.getpeercert(True)
                cert = x509.load_der_x509_certificate(ssl_bin, default_backend())

                tlsinfo["Serial Number"] = cert.serial_number
                tlsinfo["Version"] = cert.version.name
                tlsinfo["Signature Algorithm"] = cert.signature_algorithm_oid._name
                tlsinfo["Issuer"] = {attr.oid._name: attr.value for attr in cert.issuer}
                tlsinfo["Subject"] = {attr.oid._name: attr.value for attr in cert.subject}
                tlsinfo["Validity"] = {
                    "Not Before (UTC)": cert.not_valid_before_utc.strftime("%Y-%m-%dT%H:%M:%S"),
                    "Not After (UTC)": cert.not_valid_after_utc.strftime("%Y-%m-%dT%H:%M:%S"),
                }
                tlsinfo["Public Key Algorithm"] = cert.public_key().__class__.__name__
                tlsinfo["Pub Key Size"] = cert.public_key().key_size
                tlsinfo["SHA-1 Fingerprint"] = cert.fingerprint(hashes.SHA1()).hex()
                tlsinfo["SHA-256 Fingerprint"] = cert.fingerprint(hashes.SHA256()).hex()
                tlsinfo["MD5 Fingerprint"] = cert.fingerprint(hashes.MD5()).hex()
                tlsinfo["Is Self-Signed"] = (cert.issuer == cert.subject)
                tlsinfo["Subject Alternative Names (SANs)"] = []
                tlsinfo["Key Usage"] = {}
                tlsinfo["Extended Key Usage"] = []
                tlsinfo["Certificate Policies"] = []
                tlsinfo["Basic Constraints"] = {}
                tlsinfo["Authority Information Access"] = []
                tlsinfo["CRL Distribution Points"] = []
                tlsinfo["OCSP URLs"] = []
                tlsinfo["Signed Certificate Timestamps"] = [] 
                tlsinfo["Authority Key Identifier"] = None    
                tlsinfo["Subject Key Identifier"] = None      
                tlsinfo["Critical Extensions"] = []           
                tlsinfo["Public Key Details"] = {}            

                try:
                    san_extension = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
                    tlsinfo["Subject Alternative Names (SANs)"] = san_extension.value.get_values_for_type(x509.DNSName)
                except x509.ExtensionNotFound:
                    pass

                try:
                    key_usage = cert.extensions.get_extension_for_class(x509.KeyUsage)
                    tlsinfo["Key Usage"] = {
                        "Digital Signature": key_usage.value.digital_signature,
                        "Content Commitment": key_usage.value.content_commitment,
                        "Key Encipherment": key_usage.value.key_encipherment,
                        "Data Encipherment": key_usage.value.data_encipherment,
                        "Key Agreement": key_usage.value.key_agreement,
                        "Key Cert Sign": key_usage.value.key_cert_sign,
                        "CRL Sign": key_usage.value.crl_sign,
                    }
                except x509.ExtensionNotFound:
                    pass

                try:
                    ext_key_usage = cert.extensions.get_extension_for_class(x509.ExtendedKeyUsage)
                    tlsinfo["Extended Key Usage"] = [eku.dotted_string for eku in ext_key_usage.value]
                except x509.ExtensionNotFound:
                    pass

                try:
                    cert_policies = cert.extensions.get_extension_for_oid(x509.ExtensionOID.CERTIFICATE_POLICIES).value
                    tlsinfo["Certificate Policies"] = [{"Policy": policy.policy_identifier.dotted_string} for policy in cert_policies]
                except x509.ExtensionNotFound:
                    pass

                try:
                    authority_info = cert.extensions.get_extension_for_oid(x509.ExtensionOID.AUTHORITY_INFORMATION_ACCESS).value
                    tlsinfo["Authority Information Access"] = [f"{desc.access_method.dotted_string}: {desc.access_location.value}" for desc in authority_info]
                except x509.ExtensionNotFound:
                    pass

                try:
                    crl_distribution_points = cert.extensions.get_extension_for_oid(x509.ExtensionOID.CRL_DISTRIBUTION_POINTS).value
                    tlsinfo["CRL Distribution Points"] = [dp.full_name[0].value for dp in crl_distribution_points if dp.full_name]
                except x509.ExtensionNotFound:
                    pass

                try:
                    ocsp_ext = cert.extensions.get_extension_for_oid(x509.ExtensionOID.AUTHORITY_INFORMATION_ACCESS).value
                    tlsinfo["OCSP URLs"] = [ desc.access_location.value for desc in ocsp_ext if desc.access_method == x509.AuthorityInformationAccessOID.OCSP ]
                except x509.ExtensionNotFound:
                    pass

                try:
                    basic_constraints = cert.extensions.get_extension_for_class(x509.BasicConstraints)
                    tlsinfo["Basic Constraints"] = {"CA": basic_constraints.value.ca, "Path Length": basic_constraints.value.path_length}
                except x509.ExtensionNotFound:
                    pass

                try:
                    scts_extension = cert.extensions.get_extension_for_class(SignedCertificateTimestamps)
                    for sct in scts_extension.value:
                        tlsinfo["Signed Certificate Timestamps"].append({
                            "Log ID": sct.log_id.hex(),
                            "Timestamp (UTC)": sct.timestamp.strftime("%Y-%m-%dT%H:%M:%S"),
                            "Signature (hex)": sct.signature.hex(),
                            "Version": sct.version.name
                        })
                except x509.ExtensionNotFound:
                    pass
                except Exception as e:
                    self.logger.warn(f"Error parsing SCTs for {cert.subject.rfc4514_string()}: {e}")
                    tlsinfo["Signed Certificate Timestamps"] = "Error parsing SCTs"


                try:
                    aki_extension = cert.extensions.get_extension_for_class(AuthorityKeyIdentifier)
                    aki_data = {}
                    if aki_extension.value.key_identifier:
                        aki_data["Key Identifier"] = aki_extension.value.key_identifier.hex()
                    if aki_extension.value.authority_cert_issuer:
                        aki_data["Authority Cert Issuer"] = [
                            {attr.oid._name: attr.value for attr in name}
                            for name in aki_extension.value.authority_cert_issuer
                        ]
                    if aki_extension.value.authority_cert_serial_number:
                        aki_data["Authority Cert Serial Number"] = aki_extension.value.authority_cert_serial_number
                    tlsinfo["Authority Key Identifier"] = aki_data if aki_data else None
                except x509.ExtensionNotFound:
                    pass

                try:
                    ski_extension = cert.extensions.get_extension_for_class(SubjectKeyIdentifier)
                    tlsinfo["Subject Key Identifier"] = ski_extension.value.digest.hex()
                except x509.ExtensionNotFound:
                    pass

                for ext in cert.extensions:
                    if ext.critical:
                        tlsinfo["Critical Extensions"].append(ext.oid._name) 

                public_key = cert.public_key()
                if isinstance(public_key, rsa.RSAPublicKey):
                    tlsinfo["Public Key Details"]["Algorithm"] = "RSA"
                    tlsinfo["Public Key Details"]["Modulus (hex)"] = hex(public_key.public_numbers().n)
                    tlsinfo["Public Key Details"]["Public Exponent"] = public_key.public_numbers().e
                elif isinstance(public_key, ec.EllipticCurvePublicKey):
                    tlsinfo["Public Key Details"]["Algorithm"] = "EC"
                    tlsinfo["Public Key Details"]["Curve"] = public_key.curve.name
                elif isinstance(public_key, dsa.DSAPublicKey):
                    tlsinfo["Public Key Details"]["Algorithm"] = "DSA"
            except Exception as e:
                self.logger.warn(f"Exception occurred in TlsCert.get_tls_info during processing: {e}")
                return {} 
        
        return tlsinfo