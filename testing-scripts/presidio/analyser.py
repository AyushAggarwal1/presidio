from presidio_analyzer import PatternRecognizer, AnalyzerEngine
word_list = ["New York", "Texas", "Washington DC", "California", "Las vegas" ] 
text = "Our American tour covered New York, Texas and California in three weeks."

#create new pattern recognizer object
us_state_recognizer = PatternRecognizer(supported_entity="US STATES", deny_list=word_list)

#create analyzer engine object
analyzer = AnalyzerEngine()

#add the new recognizer to the existing registry
analyzer.registry.add_recognizer(us_state_recognizer)

result = analyzer.analyze(language="en", text=text)

for r in result:
    print(f"{r.entity_type}: '{text[r.start:r.end]}' "
          f"(start={r.start}, end={r.end}, score={r.score})")