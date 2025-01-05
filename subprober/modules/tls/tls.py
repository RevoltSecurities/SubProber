from datetime import datetime
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from subprober.modules.logger.logger import logger


async def tlsinfo(args, network_stream=None) -> dict:
    tlsinfo ={}
    if network_stream:
        try:
            ssl_bin = network_stream.get_extra_info("ssl_object").getpeercert(True)
        except Exception as e:
            return tlsinfo
        cert = x509.load_der_x509_certificate(ssl_bin, default_backend())    
        tlsinfo["Serial Number"] = cert.serial_number
        tlsinfo["Version"] = cert.version.name
        tlsinfo["Signature Algorithm"] = cert.signature_algorithm_oid._name,
        tlsinfo["Issuer"] = {attr.oid._name: attr.value for attr in cert.issuer}
        tlsinfo["Subject"] = {attr.oid._name: attr.value for attr in cert.subject}
        tlsinfo["Validity"] = {"Not Before (UTC)": cert.not_valid_before_utc.strftime("%Y-%m-%dT%H:%M:%S"), "Not After (UTC)": cert.not_valid_after_utc.strftime("%Y-%m-%dT%H:%M:%S"),}
        tlsinfo["Public Key Algorithm"] = cert.public_key().__class__.__name__
        tlsinfo["Pub Key Size"] = cert.public_key().key_size
        tlsinfo["SHA-1 Fingerprint"] = cert.fingerprint(hashes.SHA1()).hex()
        tlsinfo["SHA-256 Fingerprint"] = cert.fingerprint(hashes.SHA256()).hex()
        tlsinfo["MD5 Fingerprint"] = cert.fingerprint(hashes.MD5()).hex()
        tlsinfo["Subject Alternative Names (SANs)"] = []
        tlsinfo["Key Usage"] = {}
        tlsinfo["Extended Key Usage"] = []
        tlsinfo["Certificate Policies"] = []
        tlsinfo["Basic Constraints"] = {}
        tlsinfo["Authority Information Access"] = []
        tlsinfo["CRL Distribution Points"] = []
        tlsinfo["OCSP URLs"]=[]
        
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
            ocsp = cert.extensions.get_extension_for_oid(x509.ExtensionOID.AUTHORITY_INFORMATION_ACCESS).value
            tlsinfo["OCSP URLs"] = [ desc.access_location.value for desc in ocsp if desc.access_method == x509.AuthorityInformationAccessOID.OCSP ]
        except x509.ExtensionNotFound:
            pass
        
        try:
            basic_constraints = cert.extensions.get_extension_for_class(x509.BasicConstraints)
            tlsinfo["Basic Constraints"] = {"CA": basic_constraints.value.ca, "Path Length": basic_constraints.value.path_length}
        except x509.ExtensionNotFound:
            pass
        
        return tlsinfo
    else:
        return tlsinfo
        
        