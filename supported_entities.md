SUPPORTED_ENTITIES = [
    "ABA_ROUTING_NUMBER",
    "AGE",
    "AU_ABN",
    "AU_ACN",
    "AU_MEDICARE",
    "AU_TFN",
    "CREDIT_CARD",
    "CRYPTO",
    "DATE_TIME",
    "EMAIL",
    "EMAIL_ADDRESS",
    "ES_NIE",
    "ES_NIF",
    "FI_PERSONAL_IDENTITY_CODE",
    "IBAN_CODE",
    "ID",
    "IN_AADHAAR",
    "IN_GSTIN",
    "IN_PAN",
    "IN_PASSPORT",
    "IN_VEHICLE_REGISTRATION",
    "IN_VOTER",
    "IP_ADDRESS",
    "IT_DRIVER_LICENSE",
    "IT_FISCAL_CODE",
    "IT_IDENTITY_CARD",
    "IT_PASSPORT",
    "IT_VAT_CODE",
    "KR_RRN",
    "LOCATION",
    "MEDICAL_LICENSE",
    "NRP",
    "ORGANIZATION",
    "PERSON",
    "PHONE_NUMBER",
    "PL_PESEL",
    "SG_NRIC_FIN",
    "SG_UEN",
    "TH_TNIN",
    "UK_NHS",
    "UK_NINO",
    "URL",
    "US_BANK_NUMBER",
    "US_DRIVER_LICENSE",
    "US_ITIN",
    "US_PASSPORT",
    "US_SSN",
]

```json
{
  "entities": {
    "ABA_ROUTING_NUMBER": [
      "AbaRoutingRecognizer"
    ],
    "AGE": [
      "TransformersRecognizer"
    ],
    "AU_ABN": [
      "AuAbnRecognizer"
    ],
    "AU_ACN": [
      "AuAcnRecognizer"
    ],
    "AU_MEDICARE": [
      "AuMedicareRecognizer"
    ],
    "AU_TFN": [
      "AuTfnRecognizer"
    ],
    "CREDIT_CARD": [
      "CreditCardRecognizer"
    ],
    "CRYPTO": [
      "CryptoRecognizer"
    ],
    "DATE_TIME": [
      "DateRecognizer",
      "SpacyRecognizer",
      "StanzaRecognizer",
      "TransformersRecognizer"
    ],
    "EMAIL": [
      "TransformersRecognizer"
    ],
    "EMAIL_ADDRESS": [
      "EmailRecognizer"
    ],
    "ES_NIE": [
      "EsNieRecognizer"
    ],
    "ES_NIF": [
      "EsNifRecognizer"
    ],
    "FI_PERSONAL_IDENTITY_CODE": [
      "FiPersonalIdentityCodeRecognizer"
    ],
    "IBAN_CODE": [
      "IbanRecognizer"
    ],
    "ID": [
      "TransformersRecognizer"
    ],
    "IN_AADHAAR": [
      "InAadhaarRecognizer"
    ],
    "IN_GSTIN": [
      "InGstinRecognizer"
    ],
    "IN_PAN": [
      "InPanRecognizer"
    ],
    "IN_PASSPORT": [
      "InPassportRecognizer"
    ],
    "IN_VEHICLE_REGISTRATION": [
      "InVehicleRegistrationRecognizer"
    ],
    "IN_VOTER": [
      "InVoterRecognizer"
    ],
    "IP_ADDRESS": [
      "IpRecognizer"
    ],
    "IT_DRIVER_LICENSE": [
      "ItDriverLicenseRecognizer"
    ],
    "IT_FISCAL_CODE": [
      "ItFiscalCodeRecognizer"
    ],
    "IT_IDENTITY_CARD": [
      "ItIdentityCardRecognizer"
    ],
    "IT_PASSPORT": [
      "ItPassportRecognizer"
    ],
    "IT_VAT_CODE": [
      "ItVatCodeRecognizer"
    ],
    "KR_RRN": [
      "KrRrnRecognizer"
    ],
    "LOCATION": [
      "SpacyRecognizer",
      "StanzaRecognizer",
      "TransformersRecognizer"
    ],
    "MEDICAL_LICENSE": [
      "MedicalLicenseRecognizer"
    ],
    "NRP": [
      "SpacyRecognizer",
      "StanzaRecognizer"
    ],
    "ORGANIZATION": [
      "SpacyRecognizer",
      "StanzaRecognizer",
      "TransformersRecognizer"
    ],
    "PERSON": [
      "SpacyRecognizer",
      "StanzaRecognizer",
      "TransformersRecognizer"
    ],
    "PHONE_NUMBER": [
      "PhoneRecognizer",
      "TransformersRecognizer"
    ],
    "PL_PESEL": [
      "PlPeselRecognizer"
    ],
    "SG_NRIC_FIN": [
      "SgFinRecognizer"
    ],
    "SG_UEN": [
      "SgUenRecognizer"
    ],
    "TH_TNIN": [
      "ThTninRecognizer"
    ],
    "UK_NHS": [
      "NhsRecognizer"
    ],
    "UK_NINO": [
      "UkNinoRecognizer"
    ],
    "URL": [
      "UrlRecognizer"
    ],
    "US_BANK_NUMBER": [
      "UsBankRecognizer"
    ],
    "US_DRIVER_LICENSE": [
      "UsLicenseRecognizer"
    ],
    "US_ITIN": [
      "UsItinRecognizer"
    ],
    "US_PASSPORT": [
      "UsPassportRecognizer"
    ],
    "US_SSN": [
      "UsSsnRecognizer"
    ]
  },
  "detectors": {
    "EsNieRecognizer": {
      "class": "EsNieRecognizer",
      "module": "presidio_analyzer.predefined_recognizers.country_specific.spain.es_nie_recognizer",
      "file": "/home/ayush/Desktop/security-tools/ayush-presidio/presidio-analyzer/presidio_analyzer/predefined_recognizers/country_specific/spain/es_nie_recognizer.py"
    },
    "MedicalLicenseRecognizer": {
      "class": "MedicalLicenseRecognizer",
      "module": "presidio_analyzer.predefined_recognizers.country_specific.us.medical_license_recognizer",
      "file": "/home/ayush/Desktop/security-tools/ayush-presidio/presidio-analyzer/presidio_analyzer/predefined_recognizers/country_specific/us/medical_license_recognizer.py"
    },
    "SgFinRecognizer": {
      "class": "SgFinRecognizer",
      "module": "presidio_analyzer.predefined_recognizers.country_specific.singapore.sg_fin_recognizer",
      "file": "/home/ayush/Desktop/security-tools/ayush-presidio/presidio-analyzer/presidio_analyzer/predefined_recognizers/country_specific/singapore/sg_fin_recognizer.py"
    },
    "InGstinRecognizer": {
      "class": "InGstinRecognizer",
      "module": "presidio_analyzer.predefined_recognizers.country_specific.india.in_gstin_recognizer",
      "file": "/home/ayush/Desktop/security-tools/ayush-presidio/presidio-analyzer/presidio_analyzer/predefined_recognizers/country_specific/india/in_gstin_recognizer.py"
    },
    "UsItinRecognizer": {
      "class": "UsItinRecognizer",
      "module": "presidio_analyzer.predefined_recognizers.country_specific.us.us_itin_recognizer",
      "file": "/home/ayush/Desktop/security-tools/ayush-presidio/presidio-analyzer/presidio_analyzer/predefined_recognizers/country_specific/us/us_itin_recognizer.py"
    },
    "IbanRecognizer": {
      "class": "IbanRecognizer",
      "module": "presidio_analyzer.predefined_recognizers.generic.iban_recognizer",
      "file": "/home/ayush/Desktop/security-tools/ayush-presidio/presidio-analyzer/presidio_analyzer/predefined_recognizers/generic/iban_recognizer.py"
    },
    "StanzaRecognizer": {
      "class": "StanzaRecognizer",
      "module": "presidio_analyzer.predefined_recognizers.nlp_engine_recognizers.stanza_recognizer",
      "file": "/home/ayush/Desktop/security-tools/ayush-presidio/presidio-analyzer/presidio_analyzer/predefined_recognizers/nlp_engine_recognizers/stanza_recognizer.py"
    },
    "EmailRecognizer": {
      "class": "EmailRecognizer",
      "module": "presidio_analyzer.predefined_recognizers.generic.email_recognizer",
      "file": "/home/ayush/Desktop/security-tools/ayush-presidio/presidio-analyzer/presidio_analyzer/predefined_recognizers/generic/email_recognizer.py"
    },
    "PlPeselRecognizer": {
      "class": "PlPeselRecognizer",
      "module": "presidio_analyzer.predefined_recognizers.country_specific.poland.pl_pesel_recognizer",
      "file": "/home/ayush/Desktop/security-tools/ayush-presidio/presidio-analyzer/presidio_analyzer/predefined_recognizers/country_specific/poland/pl_pesel_recognizer.py"
    },
    "ItVatCodeRecognizer": {
      "class": "ItVatCodeRecognizer",
      "module": "presidio_analyzer.predefined_recognizers.country_specific.italy.it_vat_code",
      "file": "/home/ayush/Desktop/security-tools/ayush-presidio/presidio-analyzer/presidio_analyzer/predefined_recognizers/country_specific/italy/it_vat_code.py"
    },
    "UsLicenseRecognizer": {
      "class": "UsLicenseRecognizer",
      "module": "presidio_analyzer.predefined_recognizers.country_specific.us.us_driver_license_recognizer",
      "file": "/home/ayush/Desktop/security-tools/ayush-presidio/presidio-analyzer/presidio_analyzer/predefined_recognizers/country_specific/us/us_driver_license_recognizer.py"
    },
    "InPassportRecognizer": {
      "class": "InPassportRecognizer",
      "module": "presidio_analyzer.predefined_recognizers.country_specific.india.in_passport_recognizer",
      "file": "/home/ayush/Desktop/security-tools/ayush-presidio/presidio-analyzer/presidio_analyzer/predefined_recognizers/country_specific/india/in_passport_recognizer.py"
    },
    "SpacyRecognizer": {
      "class": "SpacyRecognizer",
      "module": "presidio_analyzer.predefined_recognizers.nlp_engine_recognizers.spacy_recognizer",
      "file": "/home/ayush/Desktop/security-tools/ayush-presidio/presidio-analyzer/presidio_analyzer/predefined_recognizers/nlp_engine_recognizers/spacy_recognizer.py"
    },
    "PhoneRecognizer": {
      "class": "PhoneRecognizer",
      "module": "presidio_analyzer.predefined_recognizers.generic.phone_recognizer",
      "file": "/home/ayush/Desktop/security-tools/ayush-presidio/presidio-analyzer/presidio_analyzer/predefined_recognizers/generic/phone_recognizer.py"
    },
    "KrRrnRecognizer": {
      "class": "KrRrnRecognizer",
      "module": "presidio_analyzer.predefined_recognizers.country_specific.korea.kr_rrn_recognizer",
      "file": "/home/ayush/Desktop/security-tools/ayush-presidio/presidio-analyzer/presidio_analyzer/predefined_recognizers/country_specific/korea/kr_rrn_recognizer.py"
    },
    "ItPassportRecognizer": {
      "class": "ItPassportRecognizer",
      "module": "presidio_analyzer.predefined_recognizers.country_specific.italy.it_passport_recognizer",
      "file": "/home/ayush/Desktop/security-tools/ayush-presidio/presidio-analyzer/presidio_analyzer/predefined_recognizers/country_specific/italy/it_passport_recognizer.py"
    },
    "UkNinoRecognizer": {
      "class": "UkNinoRecognizer",
      "module": "presidio_analyzer.predefined_recognizers.country_specific.uk.uk_nino_recognizer",
      "file": "/home/ayush/Desktop/security-tools/ayush-presidio/presidio-analyzer/presidio_analyzer/predefined_recognizers/country_specific/uk/uk_nino_recognizer.py"
    },
    "NhsRecognizer": {
      "class": "NhsRecognizer",
      "module": "presidio_analyzer.predefined_recognizers.country_specific.uk.uk_nhs_recognizer",
      "file": "/home/ayush/Desktop/security-tools/ayush-presidio/presidio-analyzer/presidio_analyzer/predefined_recognizers/country_specific/uk/uk_nhs_recognizer.py"
    },
    "InPanRecognizer": {
      "class": "InPanRecognizer",
      "module": "presidio_analyzer.predefined_recognizers.country_specific.india.in_pan_recognizer",
      "file": "/home/ayush/Desktop/security-tools/ayush-presidio/presidio-analyzer/presidio_analyzer/predefined_recognizers/country_specific/india/in_pan_recognizer.py"
    },
    "CreditCardRecognizer": {
      "class": "CreditCardRecognizer",
      "module": "presidio_analyzer.predefined_recognizers.generic.credit_card_recognizer",
      "file": "/home/ayush/Desktop/security-tools/ayush-presidio/presidio-analyzer/presidio_analyzer/predefined_recognizers/generic/credit_card_recognizer.py"
    },
    "UsSsnRecognizer": {
      "class": "UsSsnRecognizer",
      "module": "presidio_analyzer.predefined_recognizers.country_specific.us.us_ssn_recognizer",
      "file": "/home/ayush/Desktop/security-tools/ayush-presidio/presidio-analyzer/presidio_analyzer/predefined_recognizers/country_specific/us/us_ssn_recognizer.py"
    },
    "ItIdentityCardRecognizer": {
      "class": "ItIdentityCardRecognizer",
      "module": "presidio_analyzer.predefined_recognizers.country_specific.italy.it_identity_card_recognizer",
      "file": "/home/ayush/Desktop/security-tools/ayush-presidio/presidio-analyzer/presidio_analyzer/predefined_recognizers/country_specific/italy/it_identity_card_recognizer.py"
    },
    "DateRecognizer": {
      "class": "DateRecognizer",
      "module": "presidio_analyzer.predefined_recognizers.generic.date_recognizer",
      "file": "/home/ayush/Desktop/security-tools/ayush-presidio/presidio-analyzer/presidio_analyzer/predefined_recognizers/generic/date_recognizer.py"
    },
    "FiPersonalIdentityCodeRecognizer": {
      "class": "FiPersonalIdentityCodeRecognizer",
      "module": "presidio_analyzer.predefined_recognizers.country_specific.finland.fi_personal_identity_code_recognizer",
      "file": "/home/ayush/Desktop/security-tools/ayush-presidio/presidio-analyzer/presidio_analyzer/predefined_recognizers/country_specific/finland/fi_personal_identity_code_recognizer.py"
    },
    "EsNifRecognizer": {
      "class": "EsNifRecognizer",
      "module": "presidio_analyzer.predefined_recognizers.country_specific.spain.es_nif_recognizer",
      "file": "/home/ayush/Desktop/security-tools/ayush-presidio/presidio-analyzer/presidio_analyzer/predefined_recognizers/country_specific/spain/es_nif_recognizer.py"
    },
    "ItDriverLicenseRecognizer": {
      "class": "ItDriverLicenseRecognizer",
      "module": "presidio_analyzer.predefined_recognizers.country_specific.italy.it_driver_license_recognizer",
      "file": "/home/ayush/Desktop/security-tools/ayush-presidio/presidio-analyzer/presidio_analyzer/predefined_recognizers/country_specific/italy/it_driver_license_recognizer.py"
    },
    "AuTfnRecognizer": {
      "class": "AuTfnRecognizer",
      "module": "presidio_analyzer.predefined_recognizers.country_specific.australia.au_tfn_recognizer",
      "file": "/home/ayush/Desktop/security-tools/ayush-presidio/presidio-analyzer/presidio_analyzer/predefined_recognizers/country_specific/australia/au_tfn_recognizer.py"
    },
    "UsPassportRecognizer": {
      "class": "UsPassportRecognizer",
      "module": "presidio_analyzer.predefined_recognizers.country_specific.us.us_passport_recognizer",
      "file": "/home/ayush/Desktop/security-tools/ayush-presidio/presidio-analyzer/presidio_analyzer/predefined_recognizers/country_specific/us/us_passport_recognizer.py"
    },
    "AuAcnRecognizer": {
      "class": "AuAcnRecognizer",
      "module": "presidio_analyzer.predefined_recognizers.country_specific.australia.au_acn_recognizer",
      "file": "/home/ayush/Desktop/security-tools/ayush-presidio/presidio-analyzer/presidio_analyzer/predefined_recognizers/country_specific/australia/au_acn_recognizer.py"
    },
    "CryptoRecognizer": {
      "class": "CryptoRecognizer",
      "module": "presidio_analyzer.predefined_recognizers.generic.crypto_recognizer",
      "file": "/home/ayush/Desktop/security-tools/ayush-presidio/presidio-analyzer/presidio_analyzer/predefined_recognizers/generic/crypto_recognizer.py"
    },
    "TransformersRecognizer": {
      "class": "TransformersRecognizer",
      "module": "presidio_analyzer.predefined_recognizers.nlp_engine_recognizers.transformers_recognizer",
      "file": "/home/ayush/Desktop/security-tools/ayush-presidio/presidio-analyzer/presidio_analyzer/predefined_recognizers/nlp_engine_recognizers/transformers_recognizer.py"
    },
    "AbaRoutingRecognizer": {
      "class": "AbaRoutingRecognizer",
      "module": "presidio_analyzer.predefined_recognizers.country_specific.us.aba_routing_recognizer",
      "file": "/home/ayush/Desktop/security-tools/ayush-presidio/presidio-analyzer/presidio_analyzer/predefined_recognizers/country_specific/us/aba_routing_recognizer.py"
    },
    "UrlRecognizer": {
      "class": "UrlRecognizer",
      "module": "presidio_analyzer.predefined_recognizers.generic.url_recognizer",
      "file": "/home/ayush/Desktop/security-tools/ayush-presidio/presidio-analyzer/presidio_analyzer/predefined_recognizers/generic/url_recognizer.py"
    },
    "AuMedicareRecognizer": {
      "class": "AuMedicareRecognizer",
      "module": "presidio_analyzer.predefined_recognizers.country_specific.australia.au_medicare_recognizer",
      "file": "/home/ayush/Desktop/security-tools/ayush-presidio/presidio-analyzer/presidio_analyzer/predefined_recognizers/country_specific/australia/au_medicare_recognizer.py"
    },
    "IpRecognizer": {
      "class": "IpRecognizer",
      "module": "presidio_analyzer.predefined_recognizers.generic.ip_recognizer",
      "file": "/home/ayush/Desktop/security-tools/ayush-presidio/presidio-analyzer/presidio_analyzer/predefined_recognizers/generic/ip_recognizer.py"
    },
    "InAadhaarRecognizer": {
      "class": "InAadhaarRecognizer",
      "module": "presidio_analyzer.predefined_recognizers.country_specific.india.in_aadhaar_recognizer",
      "file": "/home/ayush/Desktop/security-tools/ayush-presidio/presidio-analyzer/presidio_analyzer/predefined_recognizers/country_specific/india/in_aadhaar_recognizer.py"
    },
    "AuAbnRecognizer": {
      "class": "AuAbnRecognizer",
      "module": "presidio_analyzer.predefined_recognizers.country_specific.australia.au_abn_recognizer",
      "file": "/home/ayush/Desktop/security-tools/ayush-presidio/presidio-analyzer/presidio_analyzer/predefined_recognizers/country_specific/australia/au_abn_recognizer.py"
    },
    "ItFiscalCodeRecognizer": {
      "class": "ItFiscalCodeRecognizer",
      "module": "presidio_analyzer.predefined_recognizers.country_specific.italy.it_fiscal_code_recognizer",
      "file": "/home/ayush/Desktop/security-tools/ayush-presidio/presidio-analyzer/presidio_analyzer/predefined_recognizers/country_specific/italy/it_fiscal_code_recognizer.py"
    },
    "ThTninRecognizer": {
      "class": "ThTninRecognizer",
      "module": "presidio_analyzer.predefined_recognizers.country_specific.thai.th_tnin_recognizer",
      "file": "/home/ayush/Desktop/security-tools/ayush-presidio/presidio-analyzer/presidio_analyzer/predefined_recognizers/country_specific/thai/th_tnin_recognizer.py"
    },
    "UsBankRecognizer": {
      "class": "UsBankRecognizer",
      "module": "presidio_analyzer.predefined_recognizers.country_specific.us.us_bank_recognizer",
      "file": "/home/ayush/Desktop/security-tools/ayush-presidio/presidio-analyzer/presidio_analyzer/predefined_recognizers/country_specific/us/us_bank_recognizer.py"
    },
    "InVoterRecognizer": {
      "class": "InVoterRecognizer",
      "module": "presidio_analyzer.predefined_recognizers.country_specific.india.in_voter_recognizer",
      "file": "/home/ayush/Desktop/security-tools/ayush-presidio/presidio-analyzer/presidio_analyzer/predefined_recognizers/country_specific/india/in_voter_recognizer.py"
    },
    "SgUenRecognizer": {
      "class": "SgUenRecognizer",
      "module": "presidio_analyzer.predefined_recognizers.country_specific.singapore.sg_uen_recognizer",
      "file": "/home/ayush/Desktop/security-tools/ayush-presidio/presidio-analyzer/presidio_analyzer/predefined_recognizers/country_specific/singapore/sg_uen_recognizer.py"
    },
    "InVehicleRegistrationRecognizer": {
      "class": "InVehicleRegistrationRecognizer",
      "module": "presidio_analyzer.predefined_recognizers.country_specific.india.in_vehicle_registration_recognizer",
      "file": "/home/ayush/Desktop/security-tools/ayush-presidio/presidio-analyzer/presidio_analyzer/predefined_recognizers/country_specific/india/in_vehicle_registration_recognizer.py"
    }
  }
}
```