from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

# Initialize Analyzer and Anonymizer
analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

text = "My name is John Doe and I live in New York."

# Analyze text to find sensitive entities
analyzer_results = analyzer.analyze(text=text, entities=["PERSON"], language="en")

# Anonymize using encryption operator with a proper length key
encryption_key = "a1b2c3d4e5f6g7h8" 
anonymized_result = anonymizer.anonymize(
    text=text,
    analyzer_results=analyzer_results,
    operators={"PERSON": OperatorConfig("encrypt", {"key": encryption_key})},
)

print(anonymized_result)