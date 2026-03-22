import asyncio
import time
from typing import Optional, Set, Type, Any, Dict
from enum import Enum
import aiohttp
from aiohttp import ClientResponse
from datetime import datetime, timezone
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.x509.extensions import SignedCertificateTimestamps, AuthorityKeyIdentifier, SubjectKeyIdentifier
from revoltlogger import Logger


class BackoffStrategy(Enum):
    CONSTANT = "constant"
    LINEAR = "linear"
    EXPONENTIAL = "exponential"


class TlsParser:
    """TLS / certificate parser that extracts browser-grade details from an aiohttp ClientResponse."""

    def __init__(self, verbose: bool = False):
        self.logger = Logger()
        self.verbose = verbose

    def _format_time_delta(self, delta) -> str:
        days = getattr(delta, "days", 0)
        seconds = getattr(delta, "seconds", 0)
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60

        parts = []
        if days > 0:
            parts.append(f"{days} day{'s' if days != 1 else ''}")
        if hours > 0:
            parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
        if minutes > 0 and days == 0:
            parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
        return ", ".join(parts) if parts else "0 minutes"

    def _calculate_validity_status(self, not_before: datetime, not_after: datetime) -> dict:
        """Calculate detailed validity status and timeline information."""
        now = datetime.now(timezone.utc)

        validity_info = {
            "status": "valid",
            "is_valid": False,
            "is_expired": False,
            "is_not_yet_valid": False,
        }

        if now < not_before:
            validity_info["status"] = "not_yet_valid"
            validity_info["is_not_yet_valid"] = True
            days_until_valid = (not_before - now).days
            validity_info["days_until_valid"] = days_until_valid
            validity_info["becomes_valid_in"] = self._format_time_delta(not_before - now)
            return validity_info

        if now > not_after:
            validity_info["status"] = "expired"
            validity_info["is_expired"] = True
            days_expired = (now - not_after).days
            validity_info["days_since_expired"] = days_expired
            validity_info["expired_ago"] = self._format_time_delta(now - not_after)
            return validity_info

        validity_info["is_valid"] = True
        days_until_expiry = (not_after - now).days
        validity_info["days_until_expiry"] = days_until_expiry
        validity_info["expires_in"] = self._format_time_delta(not_after - now)

        total_lifetime = (not_after - not_before).days if (not_after - not_before).days > 0 else 0
        validity_info["total_lifetime_days"] = total_lifetime

        days_used = (now - not_before).days if total_lifetime > 0 else 0
        validity_info["lifetime_used_days"] = days_used
        validity_info["lifetime_remaining_percent"] = round((days_until_expiry / total_lifetime) * 100, 2) if total_lifetime > 0 else 0

        if days_until_expiry <= 7:
            validity_info["warning"] = "critical"
            validity_info["warning_message"] = f"Certificate expires in {days_until_expiry} days - CRITICAL"
        elif days_until_expiry <= 30:
            validity_info["warning"] = "high"
            validity_info["warning_message"] = f"Certificate expires in {days_until_expiry} days - renewal recommended"
        elif days_until_expiry <= 90:
            validity_info["warning"] = "medium"
            validity_info["warning_message"] = f"Certificate expires in {days_until_expiry} days - plan renewal"
        else:
            validity_info["warning"] = "none"

        return validity_info

    def _get_common_name(self, subject_or_issuer) -> str:
        try:
            return subject_or_issuer.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value
        except Exception:
            return "N/A"

    def _get_organization(self, subject_or_issuer) -> str:
        try:
            return subject_or_issuer.get_attributes_for_oid(x509.NameOID.ORGANIZATION_NAME)[0].value
        except Exception:
            return "N/A"

    def _check_wildcard_certificate(self, cert) -> dict:
        wildcard_info = {"is_wildcard": False, "wildcard_domains": []}
        cn = self._get_common_name(cert.subject)
        if isinstance(cn, str) and cn.startswith("*."):
            wildcard_info["is_wildcard"] = True
            wildcard_info["wildcard_domains"].append(cn)
        try:
            san_extension = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
            for san in san_extension.value.get_values_for_type(x509.DNSName):
                if san.startswith("*."):
                    wildcard_info["is_wildcard"] = True
                    if san not in wildcard_info["wildcard_domains"]:
                        wildcard_info["wildcard_domains"].append(san)
        except x509.ExtensionNotFound:
            pass
        return wildcard_info

    def _get_certificate_type(self, cert) -> str:
        try:
            cert_policies = cert.extensions.get_extension_for_oid(x509.ExtensionOID.CERTIFICATE_POLICIES).value
            for policy in cert_policies:
                policy_oid = policy.policy_identifier.dotted_string
                if policy_oid.startswith("2.16.840.1.114412.2.1"):
                    return "EV (Extended Validation)"
                elif policy_oid.startswith("2.16.840.1.114028.10.1.2"):
                    return "EV (Extended Validation)"
        except x509.ExtensionNotFound:
            pass

        org = self._get_organization(cert.subject)
        if org != "N/A":
            return "OV (Organization Validation)"
        return "DV (Domain Validation)"

    def _get_certificate_strength(self, cert, public_key) -> dict:
        """Evaluate certificate cryptographic strength using conservative checks."""
        strength_info = {
            "overall_rating": "unknown",
            "key_strength": "unknown",
            "signature_strength": "unknown",
            "recommendations": []
        }

        key_size = getattr(public_key, "key_size", None)
        alg_name = public_key.__class__.__name__.lower()

        # Key strength heuristics
        if "rsa" in alg_name or "rsapublickey" in alg_name.lower():
            if key_size is None:
                strength_info["key_strength"] = "unknown"
            elif key_size >= 4096:
                strength_info["key_strength"] = "excellent"
            elif key_size >= 2048:
                strength_info["key_strength"] = "good"
            elif key_size >= 1024:
                strength_info["key_strength"] = "weak"
                strength_info["recommendations"].append("RSA key size < 2048 bits is deprecated")
            else:
                strength_info["key_strength"] = "insecure"
                strength_info["recommendations"].append("RSA key size is critically weak")

        elif "ellipticcurve" in alg_name or "ec" in alg_name:
            curve_name = getattr(public_key, "curve", None)
            curve_str = getattr(curve_name, "name", str(curve_name)) if curve_name else "unknown"
            if curve_str in ["secp384r1", "secp521r1"]:
                strength_info["key_strength"] = "excellent"
            elif curve_str == "secp256r1":
                strength_info["key_strength"] = "good"
            else:
                strength_info["key_strength"] = "moderate"

        elif "ed25519" in alg_name or "ed448" in alg_name:
            strength_info["key_strength"] = "excellent"

        # Signature algorithm check
        sig_algo = getattr(cert.signature_algorithm_oid, "_name", str(cert.signature_algorithm_oid)).lower()
        if "sha256" in sig_algo or "sha384" in sig_algo or "sha512" in sig_algo:
            strength_info["signature_strength"] = "good"
        elif "sha1" in sig_algo:
            strength_info["signature_strength"] = "weak"
            strength_info["recommendations"].append("SHA-1 signature algorithm is deprecated")
        elif "md5" in sig_algo:
            strength_info["signature_strength"] = "insecure"
            strength_info["recommendations"].append("MD5 signature algorithm is insecure")

        # Overall rating
        if strength_info["key_strength"] in ["excellent", "good"] and strength_info["signature_strength"] == "good":
            strength_info["overall_rating"] = "secure"
        elif strength_info["key_strength"] == "weak" or strength_info["signature_strength"] == "weak":
            strength_info["overall_rating"] = "weak"
        elif strength_info["key_strength"] == "insecure" or strength_info["signature_strength"] == "insecure":
            strength_info["overall_rating"] = "insecure"
        else:
            # if neither insecure nor excellent, default to moderate when unknown
            strength_info["overall_rating"] = "moderate"

        return strength_info

    async def tlsinfo(self, response: aiohttp.ClientResponse) -> dict:
        """
        Extract TLS certificate information from aiohttp response.
        Returns a dict (possibly empty) with all the rich fields you built.
        """
        tlsinfo: Dict[str, Any] = {}

        # response.connection is an undocumented aiohttp internal, but there is
        # no public API for accessing the transport's SSL info.  Guard heavily.
        if not response or not hasattr(response, "connection") or not response.connection:
            if self.verbose:
                self.logger.warn("No connection available in response")
            return tlsinfo

        try:
            transport = getattr(response.connection, "transport", None)
            if not transport:
                if self.verbose:
                    self.logger.warn("No transport available in connection")
                return tlsinfo

            ssl_object = transport.get_extra_info("ssl_object")
            if not ssl_object:
                if self.verbose:
                    self.logger.warn("No SSL object available - connection may not be HTTPS")
                return tlsinfo

            # FIX #1: removed dead-code duplicate getpeercert(True) fallback
            try:
                ssl_bin = ssl_object.getpeercert(True)
            except Exception:
                ssl_bin = None

            if not ssl_bin:
                if self.verbose:
                    self.logger.warn("Failed to get peer certificate in binary form")
                return tlsinfo

            cert = x509.load_der_x509_certificate(ssl_bin, default_backend())

            # Basic certificate information
            tlsinfo["serial_number"] = cert.serial_number
            tlsinfo["serial_number_hex"] = hex(cert.serial_number)
            tlsinfo["version"] = getattr(cert.version, "name", str(cert.version))
            tlsinfo["signature_algorithm"] = getattr(cert.signature_algorithm_oid, "_name", str(cert.signature_algorithm_oid))

            # Subject and issuer mapping (safe fallback)
            try:
                tlsinfo["subject"] = {attr.oid._name: attr.value for attr in cert.subject}
            except Exception:
                tlsinfo["subject"] = {}

            tlsinfo["subject_common_name"] = self._get_common_name(cert.subject)
            tlsinfo["subject_organization"] = self._get_organization(cert.subject)

            try:
                tlsinfo["issuer"] = {attr.oid._name: attr.value for attr in cert.issuer}
            except Exception:
                tlsinfo["issuer"] = {}

            tlsinfo["issuer_common_name"] = self._get_common_name(cert.issuer)
            tlsinfo["issuer_organization"] = self._get_organization(cert.issuer)

            # Validity (use UTC-aware attributes if available, fallback otherwise)
            not_before = getattr(cert, "not_valid_before_utc", None) or getattr(cert, "not_valid_before", None)
            not_after = getattr(cert, "not_valid_after_utc", None) or getattr(cert, "not_valid_after", None)

            # If naive datetimes, make them UTC-aware for consistent calculations
            if not_before and not_before.tzinfo is None:
                not_before = not_before.replace(tzinfo=timezone.utc)
            if not_after and not_after.tzinfo is None:
                not_after = not_after.replace(tzinfo=timezone.utc)

            tlsinfo["validity"] = {
                "not_before_utc": not_before.strftime("%Y-%m-%dT%H:%M:%S") if not_before else None,
                "not_after_utc": not_after.strftime("%Y-%m-%dT%H:%M:%S") if not_after else None,
            }

            tlsinfo["validity_status"] = self._calculate_validity_status(not_before, not_after) if (not_before and not_after) else {}

            tlsinfo["certificate_type"] = self._get_certificate_type(cert)
            tlsinfo["is_self_signed"] = (cert.issuer == cert.subject)
            tlsinfo["wildcard_info"] = self._check_wildcard_certificate(cert)

            public_key = cert.public_key()
            tlsinfo["public_key_algorithm"] = public_key.__class__.__name__
            tlsinfo["public_key_size"] = getattr(public_key, "key_size", None)

            tlsinfo["security_strength"] = self._get_certificate_strength(cert, public_key)

            tlsinfo["sha1_fingerprint"] = cert.fingerprint(hashes.SHA1()).hex()
            tlsinfo["sha256_fingerprint"] = cert.fingerprint(hashes.SHA256()).hex()
            try:
                tlsinfo["md5_fingerprint"] = cert.fingerprint(hashes.MD5()).hex()
            except Exception:
                tlsinfo["md5_fingerprint"] = None

            # Initialize placeholders
            tlsinfo.setdefault("subject_alternative_names", [])
            tlsinfo.setdefault("sans_count", 0)
            tlsinfo.setdefault("key_usage", {})
            tlsinfo.setdefault("extended_key_usage", [])
            tlsinfo.setdefault("certificate_policies", [])
            tlsinfo.setdefault("basic_constraints", {})
            tlsinfo.setdefault("authority_information_access", [])
            tlsinfo.setdefault("crl_distribution_points", [])
            tlsinfo.setdefault("ocsp_urls", [])
            tlsinfo.setdefault("signed_certificate_timestamps", [])
            tlsinfo.setdefault("authority_key_identifier", None)
            tlsinfo.setdefault("subject_key_identifier", None)
            tlsinfo.setdefault("critical_extensions", [])
            tlsinfo.setdefault("public_key_details", {})
            tlsinfo.setdefault("has_must_staple", False)

            # SANs
            try:
                san_extension = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
                sans = san_extension.value.get_values_for_type(x509.DNSName)
                tlsinfo["subject_alternative_names"] = sans
                tlsinfo["sans_count"] = len(sans)
            except x509.ExtensionNotFound:
                pass

            # Key Usage
            try:
                key_usage = cert.extensions.get_extension_for_class(x509.KeyUsage)
                ku = key_usage.value
                tlsinfo["key_usage"] = {
                    "digital_signature": ku.digital_signature,
                    "content_commitment": ku.content_commitment,
                    "key_encipherment": ku.key_encipherment,
                    "data_encipherment": ku.data_encipherment,
                    "key_agreement": ku.key_agreement,
                    "key_cert_sign": ku.key_cert_sign,
                    "crl_sign": ku.crl_sign,
                }
            except x509.ExtensionNotFound:
                pass

            # Extended Key Usage
            try:
                ext_key_usage = cert.extensions.get_extension_for_class(x509.ExtendedKeyUsage)
                tlsinfo["extended_key_usage"] = [eku.dotted_string for eku in ext_key_usage.value]
            except x509.ExtensionNotFound:
                pass

            # Cert policies
            try:
                cp = cert.extensions.get_extension_for_oid(x509.ExtensionOID.CERTIFICATE_POLICIES).value
                tlsinfo["certificate_policies"] = [{"policy": policy.policy_identifier.dotted_string} for policy in cp]
            except x509.ExtensionNotFound:
                pass

            # Authority Information Access (AIA)
            try:
                authority_info = cert.extensions.get_extension_for_oid(x509.ExtensionOID.AUTHORITY_INFORMATION_ACCESS).value
                tlsinfo["authority_information_access"] = [
                    f"{desc.access_method.dotted_string}: {getattr(desc.access_location, 'value', str(desc.access_location))}" for desc in authority_info
                ]
            except x509.ExtensionNotFound:
                pass

            # CRL Distribution Points
            try:
                crl_points = cert.extensions.get_extension_for_oid(x509.ExtensionOID.CRL_DISTRIBUTION_POINTS).value
                tlsinfo["crl_distribution_points"] = [dp.full_name[0].value for dp in crl_points if getattr(dp, "full_name", None)]
            except x509.ExtensionNotFound:
                pass

            # OCSP URLs (AIA filter)
            try:
                ocsp_ext = cert.extensions.get_extension_for_oid(x509.ExtensionOID.AUTHORITY_INFORMATION_ACCESS).value
                tlsinfo["ocsp_urls"] = [desc.access_location.value for desc in ocsp_ext if getattr(desc, "access_method", None) == x509.AuthorityInformationAccessOID.OCSP]
            except Exception:
                pass

            # Basic constraints
            try:
                basic_constraints = cert.extensions.get_extension_for_class(x509.BasicConstraints)
                bc = basic_constraints.value
                tlsinfo["basic_constraints"] = {"ca": bc.ca, "path_length": bc.path_length}
            except x509.ExtensionNotFound:
                pass

            # TLS Feature (must-staple)
            try:
                tls_feature = cert.extensions.get_extension_for_oid(x509.ExtensionOID.TLS_FEATURE).value
                for feature in tls_feature:
                    if feature == x509.TLSFeatureType.status_request:
                        tlsinfo["has_must_staple"] = True
                        break
            except x509.ExtensionNotFound:
                pass
            except Exception:
                pass

            # Signed Certificate Timestamps (SCTs)
            try:
                scts_extension = cert.extensions.get_extension_for_class(SignedCertificateTimestamps)
                for sct in scts_extension.value:
                    tlsinfo["signed_certificate_timestamps"].append({
                        "log_id": getattr(sct, "log_id", b"").hex(),
                        "timestamp_utc": getattr(getattr(sct, "timestamp", None), "strftime", lambda fmt: None)("%Y-%m-%dT%H:%M:%S"),
                        "signature_hex": getattr(sct, "signature", b"").hex(),
                        "version": getattr(getattr(sct, "version", None), "name", str(getattr(sct, "version", None)))
                    })
            except x509.ExtensionNotFound:
                pass
            except Exception:
                if self.verbose:
                    self.logger.warn("Error parsing SCTs", exc_info=True)

            # Authority Key Identifier
            try:
                aki_extension = cert.extensions.get_extension_for_class(AuthorityKeyIdentifier)
                aki_data = {}
                if getattr(aki_extension.value, "key_identifier", None):
                    aki_data["key_identifier"] = aki_extension.value.key_identifier.hex()
                if getattr(aki_extension.value, "authority_cert_issuer", None):
                    aki_data["authority_cert_issuer"] = [
                        {attr.oid._name: attr.value for attr in name}
                        for name in aki_extension.value.authority_cert_issuer
                    ]
                if getattr(aki_extension.value, "authority_cert_serial_number", None):
                    aki_data["authority_cert_serial_number"] = aki_extension.value.authority_cert_serial_number
                tlsinfo["authority_key_identifier"] = aki_data if aki_data else None
            except x509.ExtensionNotFound:
                pass
            except Exception:
                pass

            # Subject Key Identifier
            try:
                ski_extension = cert.extensions.get_extension_for_class(SubjectKeyIdentifier)
                tlsinfo["subject_key_identifier"] = ski_extension.value.digest.hex()
            except x509.ExtensionNotFound:
                pass

            # Critical extensions summary
            for ext in cert.extensions:
                try:
                    if ext.critical:
                        tlsinfo["critical_extensions"].append(ext.oid._name)
                except Exception:
                    pass

            # Public key details
            alg = public_key.__class__.__name__.lower()
            if "rsa" in alg:
                try:
                    numbers = public_key.public_numbers()
                    tlsinfo["public_key_details"]["algorithm"] = "RSA"
                    tlsinfo["public_key_details"]["modulus_hex"] = hex(numbers.n)
                    tlsinfo["public_key_details"]["public_exponent"] = numbers.e
                except Exception:
                    pass
            elif "elliptic" in alg or "ec" in alg:
                try:
                    tlsinfo["public_key_details"]["algorithm"] = "EC"
                    tlsinfo["public_key_details"]["curve"] = getattr(public_key.curve, "name", None)
                    tlsinfo["public_key_details"]["key_size"] = getattr(public_key, "key_size", None)
                except Exception:
                    pass
            elif "dsa" in alg:
                tlsinfo["public_key_details"]["algorithm"] = "DSA"
            elif "ed25519" in alg or "ed448" in alg:
                tlsinfo["public_key_details"]["algorithm"] = public_key.__class__.__name__

        except Exception as e:
            if self.verbose:
                self.logger.warn(f"Exception occurred in TlsParser.tlsinfo during processing: {e}")
            return {}

        return tlsinfo


class HttpResponse:
    """Wrapper around aiohttp.ClientResponse with typed metadata fields.

    Provides direct attribute access for custom metadata (response_time, tlsinfo, etc.)
    and delegates all standard aiohttp response attributes to the underlying response.
    Works as an async context manager, matching aiohttp's ``async with`` pattern.
    """

    __slots__ = (
        "_response",
        "response_time",
        "attempt_number",
        "used_fallback",
        "requested_url",
        "tlsinfo",
    )

    def __init__(
        self,
        response: ClientResponse,
        *,
        response_time: float = 0.0,
        attempt_number: int = 1,
        used_fallback: bool = False,
        requested_url: str = "",
        tlsinfo: Dict[str, Any] | None = None,
    ) -> None:
        self._response = response
        self.response_time = response_time
        self.attempt_number = attempt_number
        self.used_fallback = used_fallback
        self.requested_url = requested_url
        self.tlsinfo = tlsinfo if tlsinfo is not None else {}

    # Delegate everything else to the real response
    def __getattr__(self, name: str) -> Any:
        return getattr(self._response, name)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._response.release()
        await self._response.wait_for_close()
        return False

    async def text(self, *args, **kwargs) -> str:
        return await self._response.text(*args, **kwargs)

    async def json(self, *args, **kwargs) -> Any:
        return await self._response.json(*args, **kwargs)

    async def read(self) -> bytes:
        return await self._response.read()


class _HttpResponseContextManager:
    """Awaitable + async-context-manager returned by RetryableHttp.request().

    Supports both patterns:
        resp = await client.request(...)           # await directly
        async with client.request(...) as resp:    # context manager
    """

    __slots__ = ("_coro", "_response")

    def __init__(self, coro):
        self._coro = coro
        self._response: HttpResponse | None = None

    def __await__(self):
        return self._coro.__await__()

    async def __aenter__(self) -> HttpResponse:
        self._response = await self._coro
        return self._response

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._response is not None:
            self._response._response.release()
            await self._response._response.wait_for_close()
        return False


class RetryableHttp:
    """Retryable HTTP client using composition over aiohttp.ClientSession.

    Wraps (not inherits) a ClientSession and adds:
    - Configurable retries with constant/linear/exponential backoff
    - HTTPS → HTTP fallback
    - TLS certificate parsing via TlsParser
    - Clean HttpResponse wrapper with typed metadata
    """

    DEFAULT_RETRYABLE_EXCEPTIONS: Set[Type[Exception]] = {
        aiohttp.ClientConnectionError,
        aiohttp.ClientConnectorError,
        aiohttp.ServerTimeoutError,
        aiohttp.ServerDisconnectedError,
        aiohttp.ClientOSError,
        aiohttp.ClientPayloadError,
        asyncio.TimeoutError,
        ConnectionError,
        OSError,
    }

    def __init__(
            self,
            *args,
            retries: int = 3,
            backoff_strategy: BackoffStrategy = BackoffStrategy.EXPONENTIAL,
            backoff_base: float = 0.5,
            backoff_max: float = 60.0,
            fallback_to_http: bool = True,
            fallback_retries: Optional[int] = None,
            retryable_exceptions: Optional[Set[Type[Exception]]] = None,
            debug: bool = False,
            tls_verbose: bool = False,
            **kwargs
    ):
        self._retries = max(0, retries)
        self._backoff_strategy = backoff_strategy
        self._backoff_base = backoff_base
        self._backoff_max = backoff_max
        self._fallback_to_http = fallback_to_http
        self._fallback_retries = fallback_retries if fallback_retries is not None else self._retries
        self._retryable_exceptions = retryable_exceptions or self.DEFAULT_RETRYABLE_EXCEPTIONS.copy()
        self._debug = debug
        self._logger = Logger()
        self._tls_parser = TlsParser(verbose=tls_verbose)
        self._session = aiohttp.ClientSession(*args, **kwargs)

    def _log_debug(self, message: str):
        if self._debug:
            self._logger.debug(message)

    def _calculate_backoff(self, attempt: int) -> float:
        if self._backoff_strategy == BackoffStrategy.CONSTANT:
            delay = self._backoff_base
        elif self._backoff_strategy == BackoffStrategy.LINEAR:
            delay = self._backoff_base * (attempt + 1)
        elif self._backoff_strategy == BackoffStrategy.EXPONENTIAL:
            delay = self._backoff_base * (2 ** attempt)
        else:
            delay = self._backoff_base
        return min(delay, self._backoff_max)

    def _should_retry_on_exception(self, exc: Exception) -> bool:
        return any(isinstance(exc, exc_type) for exc_type in self._retryable_exceptions)

    async def _do_request(self, method: str, str_or_url, **kwargs) -> HttpResponse:
        """Execute request with retries, fallback, and TLS parsing."""
        url = str(str_or_url)
        original_url = url
        last_exception = None

        # Primary attempts
        for attempt in range(self._retries + 1):
            try:
                self._log_debug(f"Attempt {attempt + 1}/{self._retries + 1} - {method} {url}")
                start_time = time.monotonic()

                response = await self._session._request(method, url, **kwargs)

                try:
                    elapsed = time.monotonic() - start_time

                    # Collect TLS info only for HTTPS
                    tls_data: Dict[str, Any] = {}
                    if url.startswith("https://"):
                        try:
                            tls_data = await self._tls_parser.tlsinfo(response)
                        except Exception as e:
                            self._log_debug(f"TLS parsing failed on attempt {attempt + 1} for {url}: {e}")

                    wrapped = HttpResponse(
                        response,
                        response_time=elapsed,
                        attempt_number=attempt + 1,
                        used_fallback=False,
                        requested_url=url,
                        tlsinfo=tls_data,
                    )

                    self._log_debug(f"Request succeeded on attempt {attempt + 1}: {method} {url} - {response.status} ({elapsed:.3f}s)")
                    return wrapped
                except BaseException:
                    response.close()
                    raise

            except Exception as e:
                last_exception = e
                self._log_debug(f"Attempt {attempt + 1}/{self._retries + 1} failed for {url}: {type(e).__name__}: {e}")

                if not self._should_retry_on_exception(e):
                    self._log_debug(f"Non-retryable exception for {url}: {type(e).__name__}")
                    raise

                if attempt < self._retries:
                    delay = self._calculate_backoff(attempt)
                    self._log_debug(f"Waiting {delay:.2f}s before retry")
                    await asyncio.sleep(delay)

        # HTTPS -> HTTP fallback
        if self._fallback_to_http and original_url.startswith('https://'):
            http_url = original_url.replace('https://', 'http://', 1)
            self._log_debug(f"Attempting HTTP fallback for {original_url} -> {http_url}")

            for attempt in range(self._fallback_retries + 1):
                try:
                    self._log_debug(f"Fallback attempt {attempt + 1}/{self._fallback_retries + 1} - {method} {http_url}")
                    start_time = time.monotonic()

                    response = await self._session._request(method, http_url, **kwargs)

                    try:
                        elapsed = time.monotonic() - start_time

                        # FIX #6: skip TLS parsing for HTTP — no SSL object exists
                        wrapped = HttpResponse(
                            response,
                            response_time=elapsed,
                            attempt_number=attempt + 1,
                            used_fallback=True,
                            requested_url=http_url,
                            tlsinfo={},
                        )

                        self._log_debug(f"HTTP fallback succeeded for {http_url}: {response.status} ({elapsed:.3f}s)")
                        return wrapped
                    except BaseException:
                        response.close()
                        raise

                except Exception as e:
                    last_exception = e
                    self._log_debug(f"Fallback attempt {attempt + 1}/{self._fallback_retries + 1} failed for {http_url}: {type(e).__name__}: {e}")

                    # FIX #5: raise immediately on non-retryable exception (consistent with primary path)
                    if not self._should_retry_on_exception(e):
                        self._log_debug(f"Non-retryable exception on fallback for {http_url}: {type(e).__name__}")
                        raise

                    if attempt < self._fallback_retries:
                        delay = self._calculate_backoff(attempt)
                        self._log_debug(f"Waiting {delay:.2f}s before fallback retry")
                        await asyncio.sleep(delay)

        self._log_debug(f"All attempts exhausted for {original_url}")
        if last_exception:
            raise last_exception
        else:
            raise Exception(f"Request failed for {original_url} - all retry attempts exhausted")

    def request(self, method: str, url, **kwargs) -> _HttpResponseContextManager:
        """Start an HTTP request. Returns an awaitable async context manager.

        Usage:
            async with client.request('GET', url) as resp:
                text = await resp.text()
        """
        return _HttpResponseContextManager(self._do_request(method, url, **kwargs))

    def get(self, url, **kwargs) -> _HttpResponseContextManager:
        return self.request("GET", url, **kwargs)

    def post(self, url, **kwargs) -> _HttpResponseContextManager:
        return self.request("POST", url, **kwargs)

    def put(self, url, **kwargs) -> _HttpResponseContextManager:
        return self.request("PUT", url, **kwargs)

    def delete(self, url, **kwargs) -> _HttpResponseContextManager:
        return self.request("DELETE", url, **kwargs)

    def head(self, url, **kwargs) -> _HttpResponseContextManager:
        return self.request("HEAD", url, **kwargs)

    def options(self, url, **kwargs) -> _HttpResponseContextManager:
        return self.request("OPTIONS", url, **kwargs)

    async def close(self) -> None:
        """Close the underlying aiohttp session."""
        await self._session.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
        return False
