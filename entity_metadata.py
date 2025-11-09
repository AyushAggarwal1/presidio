"""
Entity metadata for Presidio supported entities.

Each entity has:
- title: Human-friendly name
- description: What the entity represents
- category: Logical grouping
- domain: Business/security domain
- severity: Relative privacy/security risk (Low/Medium/High/Critical)
- recommended_action: Suggested mitigation
- link: Optional reference URL (when available)
"""

from typing import Dict

# Base defaults used when an entity is not explicitly defined below.
DEFAULT_METADATA = {
    "category": "PII",
    "domain": "DSPM",
    "severity": "Medium",
    "recommended_action": "Mask, anonymize, or avoid storing this data in plaintext.",
    "link": "",
}

# Comprehensive metadata for supported entities in this repository.
# Keys must match Presidio entity_type values.
ENTITY_METADATA: Dict[str, Dict[str, str]] = {
    "ABA_ROUTING_NUMBER": {
        "title": "ABA Routing Number",
        "description": "US bank routing number identifying a financial institution.",
        "category": "Financial",
        "domain": "Banking",
        "severity": "High",
        "recommended_action": "Mask or tokenize; restrict exposure and storage.",
        "link": "https://en.wikipedia.org/wiki/Routing_transit_number",
    },
    "AGE": {
        "title": "Age",
        "description": "An individual's age or age range.",
        "category": "Demographic",
        "domain": "Privacy",
        "severity": "Low",
        "recommended_action": "Generalize or bucketize (e.g., 30-39) where possible.",
        "link": "",
    },
    "AU_ABN": {
        "title": "Australia ABN",
        "description": "Australian Business Number used to identify businesses.",
        "category": "Government ID",
        "domain": "Compliance",
        "severity": "Medium",
        "recommended_action": "Mask or store only when required; limit sharing.",
        "link": "https://abr.business.gov.au/Help/AbnFormat",
    },
    "AU_ACN": {
        "title": "Australia ACN",
        "description": "Australian Company Number assigned by ASIC.",
        "category": "Government ID",
        "domain": "Compliance",
        "severity": "Medium",
        "recommended_action": "Mask or store only when required; limit sharing.",
        "link": "https://asic.gov.au/for-business/starting-a-company/company-structure/company-name/acn/",
    },
    "AU_MEDICARE": {
        "title": "Australia Medicare Number",
        "description": "Australian Medicare card number used for healthcare services.",
        "category": "Health",
        "domain": "Healthcare",
        "severity": "High",
        "recommended_action": "Treat as sensitive health data; mask or tokenize.",
        "link": "",
    },
    "AU_TFN": {
        "title": "Australia TFN",
        "description": "Australian Tax File Number used for taxation purposes.",
        "category": "Government ID",
        "domain": "Taxation",
        "severity": "High",
        "recommended_action": "Mask, encrypt, or tokenize; restrict access.",
        "link": "https://www.ato.gov.au/Individuals/Tax-file-number/",
    },
    "CREDIT_CARD": {
        "title": "Credit Card Number",
        "description": "Payment card number (e.g., VISA, Mastercard).",
        "category": "Financial",
        "domain": "Payments",
        "severity": "Critical",
        "recommended_action": "Do not log; tokenize; store only per PCI DSS requirements.",
        "link": "https://www.pcisecuritystandards.org/",
    },
    "CRYPTO": {
        "title": "Cryptocurrency Wallet Address",
        "description": "Address identifying a blockchain wallet (e.g., BTC, ETH).",
        "category": "Financial",
        "domain": "Blockchain",
        "severity": "Medium",
        "recommended_action": "Avoid exposing; mask or truncate where feasible.",
        "link": "",
    },
    "DATE_TIME": {
        "title": "Date/Time",
        "description": "Specific dates or timestamps that might identify events.",
        "category": "Temporal",
        "domain": "Privacy",
        "severity": "Low",
        "recommended_action": "Reduce precision (e.g., day to month) if not needed.",
        "link": "",
    },
    "EMAIL": {
        "title": "Email (Free Text)",
        "description": "An email value extracted by language models.",
        "category": "Contact",
        "domain": "Communications",
        "severity": "Medium",
        "recommended_action": "Mask local-part; avoid logging unredacted emails.",
        "link": "",
    },
    "EMAIL_ADDRESS": {
        "title": "Email Address",
        "description": "A standard email address format (user@domain).",
        "category": "Contact",
        "domain": "Communications",
        "severity": "Medium",
        "recommended_action": "Mask local-part or hash; avoid logging.",
        "link": "https://en.wikipedia.org/wiki/Email_address",
    },
    "ES_NIE": {
        "title": "Spain NIE",
        "description": "Número de Identidad de Extranjero for foreign nationals in Spain.",
        "category": "Government ID",
        "domain": "Compliance",
        "severity": "High",
        "recommended_action": "Mask or tokenize; restrict access.",
        "link": "",
    },
    "ES_NIF": {
        "title": "Spain NIF",
        "description": "Número de Identificación Fiscal (tax identification number).",
        "category": "Government ID",
        "domain": "Taxation",
        "severity": "High",
        "recommended_action": "Mask or tokenize; restrict access.",
        "link": "",
    },
    "FI_PERSONAL_IDENTITY_CODE": {
        "title": "Finland Personal Identity Code",
        "description": "Finnish national identification number.",
        "category": "Government ID",
        "domain": "Compliance",
        "severity": "High",
        "recommended_action": "Mask or tokenize; restrict access.",
        "link": "",
    },
    "IBAN_CODE": {
        "title": "IBAN",
        "description": "International Bank Account Number used for cross-border payments.",
        "category": "Financial",
        "domain": "Banking",
        "severity": "High",
        "recommended_action": "Mask or tokenize; store per banking standards.",
        "link": "https://en.wikipedia.org/wiki/International_Bank_Account_Number",
    },
    "ID": {
        "title": "Identifier (Generic)",
        "description": "A generic identifier detected by language models.",
        "category": "Identifier",
        "domain": "Privacy",
        "severity": "Low",
        "recommended_action": "Review case-by-case; mask if it links to a person.",
        "link": "",
    },
    "IN_AADHAAR": {
        "title": "India Aadhaar Number",
        "description": "12-digit unique identity number issued by UIDAI.",
        "category": "Government ID",
        "domain": "Compliance",
        "severity": "High",
        "recommended_action": "Mask, encrypt, or tokenize; follow Indian privacy laws.",
        "link": "https://uidai.gov.in/",
    },
    "IN_GSTIN": {
        "title": "India GSTIN",
        "description": "Goods and Services Tax Identification Number in India.",
        "category": "Tax ID",
        "domain": "Taxation",
        "severity": "Medium",
        "recommended_action": "Mask or tokenize; restrict access.",
        "link": "",
    },
    "IN_PAN": {
        "title": "India PAN",
        "description": "Permanent Account Number used for tax purposes in India.",
        "category": "Tax ID",
        "domain": "Taxation",
        "severity": "High",
        "recommended_action": "Mask or tokenize; restrict access.",
        "link": "",
    },
    "IN_PASSPORT": {
        "title": "India Passport Number",
        "description": "Indian passport identifier.",
        "category": "Government ID",
        "domain": "Travel",
        "severity": "High",
        "recommended_action": "Mask or tokenize; restrict access.",
        "link": "",
    },
    "IN_VEHICLE_REGISTRATION": {
        "title": "India Vehicle Registration",
        "description": "Vehicle registration number issued in India.",
        "category": "Identifier",
        "domain": "Transport",
        "severity": "Low",
        "recommended_action": "Mask or truncate where feasible.",
        "link": "",
    },
    "IN_VOTER": {
        "title": "India Voter ID",
        "description": "Electoral photo identity card number in India.",
        "category": "Government ID",
        "domain": "Compliance",
        "severity": "High",
        "recommended_action": "Mask or tokenize; restrict access.",
        "link": "",
    },
    "IP_ADDRESS": {
        "title": "IP Address",
        "description": "IPv4 or IPv6 address identifying a device on a network.",
        "category": "Network",
        "domain": "Security",
        "severity": "Medium",
        "recommended_action": "Avoid logging full IPs; mask or hash if needed.",
        "link": "https://en.wikipedia.org/wiki/IP_address",
    },
    "IT_DRIVER_LICENSE": {
        "title": "Italy Driver's License",
        "description": "Italian driver's license number.",
        "category": "Government ID",
        "domain": "Transport",
        "severity": "High",
        "recommended_action": "Mask or tokenize; restrict access.",
        "link": "",
    },
    "IT_FISCAL_CODE": {
        "title": "Italy Fiscal Code",
        "description": "Italian tax code (Codice Fiscale).",
        "category": "Tax ID",
        "domain": "Taxation",
        "severity": "High",
        "recommended_action": "Mask or tokenize; restrict access.",
        "link": "",
    },
    "IT_IDENTITY_CARD": {
        "title": "Italy Identity Card",
        "description": "Italian national identity card number.",
        "category": "Government ID",
        "domain": "Compliance",
        "severity": "High",
        "recommended_action": "Mask or tokenize; restrict access.",
        "link": "",
    },
    "IT_PASSPORT": {
        "title": "Italy Passport Number",
        "description": "Italian passport identifier.",
        "category": "Government ID",
        "domain": "Travel",
        "severity": "High",
        "recommended_action": "Mask or tokenize; restrict access.",
        "link": "",
    },
    "IT_VAT_CODE": {
        "title": "Italy VAT Code",
        "description": "Italian Value Added Tax identification number.",
        "category": "Tax ID",
        "domain": "Taxation",
        "severity": "Medium",
        "recommended_action": "Mask or tokenize; restrict access.",
        "link": "",
    },
    "KR_RRN": {
        "title": "Korea RRN",
        "description": "Korean Resident Registration Number.",
        "category": "Government ID",
        "domain": "Compliance",
        "severity": "High",
        "recommended_action": "Mask, encrypt, or tokenize; restrict access.",
        "link": "",
    },
    "LOCATION": {
        "title": "Location",
        "description": "Geographic location, such as city, state, or country.",
        "category": "Demographic",
        "domain": "Privacy",
        "severity": "Low",
        "recommended_action": "Reduce precision when possible (e.g., city instead of address).",
        "link": "",
    },
    "MEDICAL_LICENSE": {
        "title": "US Medical License Number",
        "description": "License identifying a medical practitioner in the US.",
        "category": "Health",
        "domain": "Healthcare",
        "severity": "High",
        "recommended_action": "Treat as sensitive; mask or tokenize.",
        "link": "",
    },
    "NRP": {
        "title": "Not Real Person (NRP)",
        "description": "Label indicating text refers to a non-real person.",
        "category": "Annotation",
        "domain": "Privacy",
        "severity": "Low",
        "recommended_action": "Typically no action required.",
        "link": "",
    },
    "ORGANIZATION": {
        "title": "Organization",
        "description": "Named organization such as a company or institution.",
        "category": "Entity",
        "domain": "Privacy",
        "severity": "Low",
        "recommended_action": "Mask only if combined with other PII.",
        "link": "",
    },
    "PERSON": {
        "title": "Person",
        "description": "Name of a natural person.",
        "category": "Identity",
        "domain": "Privacy",
        "severity": "Medium",
        "recommended_action": "Mask names in logs and analytics outputs.",
        "link": "",
    },
    "PHONE_NUMBER": {
        "title": "Phone Number",
        "description": "Telephone number (international or local formats).",
        "category": "Contact",
        "domain": "Communications",
        "severity": "Medium",
        "recommended_action": "Mask or hash; avoid storing in plaintext.",
        "link": "",
    },
    "PL_PESEL": {
        "title": "Poland PESEL",
        "description": "Polish national identification number.",
        "category": "Government ID",
        "domain": "Compliance",
        "severity": "High",
        "recommended_action": "Mask or tokenize; restrict access.",
        "link": "",
    },
    "SG_NRIC_FIN": {
        "title": "Singapore NRIC/FIN",
        "description": "Singapore National Registration Identity Card or Foreign Identification Number.",
        "category": "Government ID",
        "domain": "Compliance",
        "severity": "High",
        "recommended_action": "Mask or tokenize; restrict access.",
        "link": "",
    },
    "SG_UEN": {
        "title": "Singapore UEN",
        "description": "Unique Entity Number for Singapore-registered entities.",
        "category": "Government ID",
        "domain": "Compliance",
        "severity": "Medium",
        "recommended_action": "Mask or store only when required; limit sharing.",
        "link": "",
    },
    "TH_TNIN": {
        "title": "Thailand TNIN",
        "description": "Thai Tax Identification Number.",
        "category": "Tax ID",
        "domain": "Taxation",
        "severity": "High",
        "recommended_action": "Mask or tokenize; restrict access.",
        "link": "",
    },
    "UK_NHS": {
        "title": "UK NHS Number",
        "description": "United Kingdom National Health Service identifier.",
        "category": "Health",
        "domain": "Healthcare",
        "severity": "High",
        "recommended_action": "Treat as sensitive health data; mask or tokenize.",
        "link": "",
    },
    "UK_NINO": {
        "title": "UK National Insurance Number",
        "description": "UK social security number used for tax and benefits.",
        "category": "Government ID",
        "domain": "Taxation",
        "severity": "High",
        "recommended_action": "Mask, encrypt, or tokenize; restrict access.",
        "link": "",
    },
    "URL": {
        "title": "URL",
        "description": "Uniform Resource Locator representing a web address.",
        "category": "Identifier",
        "domain": "Web",
        "severity": "Low",
        "recommended_action": "Remove query parameters if sensitive; avoid logging secrets.",
        "link": "https://en.wikipedia.org/wiki/URL",
    },
    "US_BANK_NUMBER": {
        "title": "US Bank Account Number",
        "description": "Bank account number associated with a US financial institution.",
        "category": "Financial",
        "domain": "Banking",
        "severity": "Critical",
        "recommended_action": "Tokenize; never store or log in plaintext.",
        "link": "",
    },
    "US_DRIVER_LICENSE": {
        "title": "US Driver's License",
        "description": "US state-issued driver's license number.",
        "category": "Government ID",
        "domain": "Transport",
        "severity": "High",
        "recommended_action": "Mask or tokenize; restrict access.",
        "link": "",
    },
    "US_ITIN": {
        "title": "US ITIN",
        "description": "Individual Taxpayer Identification Number used for US tax processing.",
        "category": "Tax ID",
        "domain": "Taxation",
        "severity": "High",
        "recommended_action": "Mask or tokenize; restrict access.",
        "link": "",
    },
    "US_PASSPORT": {
        "title": "US Passport Number",
        "description": "United States passport identifier.",
        "category": "Government ID",
        "domain": "Travel",
        "severity": "High",
        "recommended_action": "Mask or tokenize; restrict access.",
        "link": "",
    },
    "US_SSN": {
        "title": "US Social Security Number",
        "description": "US federal identification number for individuals.",
        "category": "Government ID",
        "domain": "Compliance",
        "severity": "Critical",
        "recommended_action": "Tokenize; never log; restrict and monitor access.",
        "link": "https://www.ssa.gov/ssnumber/",
    },
}


def _auto_title(entity_type: str) -> str:
    return entity_type.replace("_", " ").title() if entity_type else "Unknown"


def get_entity_metadata(entity_type: str) -> Dict[str, str]:
    """
    Return metadata for the requested entity_type.
    Falls back to generated title/description and DEFAULT_METADATA if not explicitly defined.
    """
    meta = ENTITY_METADATA.get(entity_type, {})
    if meta:
        # Ensure domain aligns with DSPM consistently
        meta_out = dict(meta)
        meta_out["domain"] = "DSPM"
        return meta_out
    # Build a sensible fallback
    title = _auto_title(entity_type)
    description = f"{title} detected by Presidio."
    fallback = dict(DEFAULT_METADATA)
    fallback.update({"title": title, "description": description})
    return fallback


