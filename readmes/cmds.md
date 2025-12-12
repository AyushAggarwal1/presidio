# Presidio Complete Guide: Commands & JSON Output

## 📋 Table of Contents
1. [Quick Start](#quick-start)
2. [Docker Commands](#docker-commands)
3. [API Commands](#api-commands)
4. [CLI Commands](#cli-commands)
5. [File Processing Commands](#file-processing-commands)
6. [JSON Output Examples](#json-output-examples)
7. [Advanced Usage](#advanced-usage)
8. [Troubleshooting](#troubleshooting)
9. [Local Script Commands](#local-script-commands)

---

## 🚀 Quick Start

### Start All Services
```bash
# Start all Presidio services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Health Check
```bash
# Check all services
curl http://localhost:5001/health  # Anonymizer
curl http://localhost:5002/health  # Analyzer
curl http://localhost:5003/health  # Image Redactor

# Combined health check
curl http://localhost:8080/api/health
```

---

## 🐳 Docker Commands

### Service Management
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart services
docker-compose restart

# Rebuild and start
docker-compose up --build -d

# View specific service logs
docker-compose logs -f presidio-analyzer
docker-compose logs -f presidio-anonymizer
docker-compose logs -f presidio-image-redactor
```

### Container Management
```bash
# Check running containers
docker ps

# Check resource usage
docker stats

# Clean up Docker
docker system prune -a

# Check container logs
docker logs <container_id>
```

---

## 🔧 API Commands

### Analyze Text
```bash
# Basic analysis
curl -X POST "http://localhost:5002/analyze" \
  -H "Content-Type: application/json" \
  -d '{"text": "John Doe, email john@example.com", "language": "en"}'

# Save to JSON file
curl -X POST "http://localhost:5002/analyze" \
  -H "Content-Type: application/json" \
  -d '{"text": "John Doe, email john@example.com", "language": "en"}' \
  | jq '.' > analysis_results.json

# Analyze with specific entities
curl -X POST "http://localhost:5002/analyze" \
  -H "Content-Type: application/json" \
  -d '{"text": "John Doe, email john@example.com", "language": "en", "entities": ["PERSON", "EMAIL_ADDRESS"]}' \
  | jq '.' > filtered_analysis.json
```

### Anonymize Text
```bash
# Step 1: Analyze first
ANALYSIS=$(curl -s -X POST "http://localhost:5002/analyze" \
  -H "Content-Type: application/json" \
  -d '{"text": "John Doe, email john@example.com", "language": "en"}')

# Step 2: Anonymize and save to JSON
curl -X POST "http://localhost:5001/anonymize" \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"John Doe, email john@example.com\", \"analyzer_results\": $ANALYSIS, \"anonymizers\": {\"DEFAULT\": {\"type\": \"replace\", \"new_value\": \"[REDACTED]\"}}}" \
  | jq '.' > anonymized_results.json
```

### Batch Processing with JSON Output
```bash
# Process multiple texts and save to JSON array
cat > input_texts.txt << EOF
John Doe, email john@example.com
Jane Smith, phone 555-123-4567
Company GSTIN: 27ABCDE1234F1Z5
EOF

# Process each line and save results
while IFS= read -r line; do
  echo "Processing: $line"
  curl -s -X POST "http://localhost:5002/analyze" \
    -H "Content-Type: application/json" \
    -d "{\"text\": \"$line\", \"language\": \"en\"}" \
    | jq --arg text "$line" '. + {input_text: $text}' >> batch_results.json
done < input_texts.txt

# Combine all results into single JSON array
jq -s '.' batch_results.json > combined_results.json
```

---

## 💻 CLI Commands

### Install Presidio CLI
```bash
# Install via pip
pip install presidio-cli

# Or use Docker
docker run -it --rm -v $(pwd):/workspace presidio-cli
```

### Basic CLI Usage
```bash
# Scan single file
presidio file.txt

# Scan directory
presidio /path/to/directory

# Scan with output to JSON
presidio file.txt --format json > results.json

# Scan with specific entities
presidio -d "entities: [PERSON, EMAIL_ADDRESS, CREDIT_CARD]" file.txt --format json > filtered_results.json
```

### CLI with Configuration
```bash
# Create configuration file
cat > .presidiocli << EOF
language: en
entities:
  - PERSON
  - EMAIL_ADDRESS
  - CREDIT_CARD
  - IN_GSTIN
ignore: |
  .git
  *.cfg
  node_modules
allow:
  - "allowed token"
EOF

# Use configuration
presidio -c .presidiocli /path/to/directory --format json > configured_results.json
```

### Advanced CLI Options
```bash
# Scan with custom threshold
presidio -d "threshold: 0.8" file.txt --format json > high_confidence_results.json

# Scan with allow list
presidio -d "allow: [\"John Doe\", \"example.com\"]" file.txt --format json > allowed_results.json

# Scan with ignore patterns
presidio -d "ignore: | .git *.log" /path/to/directory --format json > filtered_scan.json
```

---

## 🖥️ Local Script Commands

### Scan a single file
```bash
python3 presidio_scan.py /path/to/file.txt
```

### Scan a directory (recursive) and write results to a file
```bash
python3 presidio_scan.py /path/to/dir --output /tmp/results.json
```

### Scan a directory (non-recursive)
```bash
python3 presidio_scan.py /path/to/dir --no-recursive
```

### Filter using regex (allow)
```bash
python3 presidio_scan.py /repo --allow-regex '.*(secrets|prod).*'
```

### Filter using regex (ignore)
```bash
python3 presidio_scan.py /repo \
  --ignore-regex '.*node_modules.*' \
  --ignore-regex '.*\.min\.js$' \
  --ignore-regex '(^|/)\.'   # ignore hidden files/dirs
```

### Combine regex allow + ignore
```bash
python3 presidio_scan.py /repo \
  --allow-regex '.*/src/.*' \
  --ignore-regex '.*/src/vendor/.*' \
  --ignore-regex '.*/tests?/.*'
```

### Scan any UTF-8 readable file (ignore extension allowlist)
```bash
python3 presidio_scan.py /repo --scan-all-text
```

### Include additional extensions
```bash
python3 presidio_scan.py /repo \
  --ext .java --ext .go --ext .ts --ext .tsx
```

### Filter using shell globs (ignore)
```bash
python3 presidio_scan.py \
  /home/ayush/Desktop/accuknox/accuknox-frontend \
  --ignore-glob '**/node_modules/**' \
  --ignore-glob '*.json' \
  --output /tmp/results.json
```

### Filter using shell globs (allow + ignore)
```bash
python3 presidio_scan.py \
  /repo \
  --allow-glob '**/src/**' \
  --ignore-glob '**/src/vendor/**' \
  --ignore-glob '**/src/**/test/**'
```

### Combine glob filters and extensions
```bash
python3 presidio_scan.py /repo \
  --allow-glob '**/packages/**' \
  --ignore-glob '**/*.min.js' \
  --ext .go --ext .java
```

---

## 📄 File Processing Commands

### Text Files
```bash
# Process single text file
curl -X POST "http://localhost:5002/analyze" \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"$(cat document.txt | tr '\n' ' ')\", \"language\": \"en\"}" \
  | jq '.' > document_analysis.json

# Process multiple text files
for file in *.txt; do
  echo "Processing: $file"
  curl -s -X POST "http://localhost:5002/analyze" \
    -H "Content-Type: application/json" \
    -d "{\"text\": \"$(cat $file | tr '\n' ' ')\", \"language\": \"en\"}" \
    | jq --arg filename "$file" '. + {filename: $filename}' >> text_files_results.json
done
```

### CSV Files
```bash
# Process CSV file
curl -X POST "http://localhost:5002/analyze" \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"$(cat data.csv | tr '\n' ' ')\", \"language\": \"en\"}" \
  | jq '.' > csv_analysis.json

# Process CSV with anonymization
ANALYSIS=$(curl -s -X POST "http://localhost:5002/analyze" \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"$(cat data.csv | tr '\n' ' ')\", \"language\": \"en\"}")

curl -X POST "http://localhost:5001/anonymize" \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"$(cat data.csv | tr '\n' ' ')\", \"analyzer_results\": $ANALYSIS, \"anonymizers\": {\"DEFAULT\": {\"type\": \"replace\", \"new_value\": \"[REDACTED]\"}}}" \
  | jq '.' > csv_anonymized.json
```

### JSON Files
```bash
# Process JSON file
curl -X POST "http://localhost:5002/analyze" \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"$(cat config.json | tr '\n' ' ')\", \"language\": \"en\"}" \
  | jq '.' > json_analysis.json
```

### Directory Scanning
```bash
# Scan entire directory with JSON output
find /path/to/directory -name "*.txt" -o -name "*.csv" -o -name "*.json" | while read file; do
  echo "Processing: $file"
  curl -s -X POST "http://localhost:5002/analyze" \
    -H "Content-Type: application/json" \
    -d "{\"text\": \"$(cat $file | tr '\n' ' ')\", \"language\": \"en\"}" \
    | jq --arg filepath "$file" '. + {filepath: $filepath}' >> directory_scan.json
done
```

---

## 📊 JSON Output Examples

### Analysis Results JSON Structure
```json
[
  {
    "entity_type": "PERSON",
    "start": 0,
    "end": 8,
    "score": 0.85,
    "analysis_explanation": null
  },
  {
    "entity_type": "EMAIL_ADDRESS",
    "start": 16,
    "end": 32,
    "score": 1.0,
    "analysis_explanation": null
  },
  {
    "entity_type": "IN_GSTIN",
    "start": 40,
    "end": 55,
    "score": 1.0,
    "analysis_explanation": null
  }
]
```

### Anonymization Results JSON Structure
```json
{
  "text": "[REDACTED], email [REDACTED], GSTIN [REDACTED]",
  "items": [
    {
      "start": 0,
      "end": 10,
      "entity_type": "PERSON",
      "text": "[REDACTED]",
      "operator": "replace"
    },
    {
      "start": 18,
      "end": 28,
      "entity_type": "EMAIL_ADDRESS",
      "text": "[REDACTED]",
      "operator": "replace"
    }
  ]
}
```

### Combined Results JSON Structure
```json
{
  "input_text": "John Doe, email john@example.com, GSTIN 27ABCDE1234F1Z5",
  "analysis_results": [
    {
      "entity_type": "PERSON",
      "start": 0,
      "end": 8,
      "score": 0.85
    }
  ],
  "anonymized_text": "[REDACTED], email [REDACTED], GSTIN [REDACTED]",
  "timestamp": "2024-01-15T10:30:00Z",
  "processing_time_ms": 150
}
```

### Batch Processing JSON Structure
```json
[
  {
    "filename": "document1.txt",
    "filepath": "/path/to/document1.txt",
    "analysis_results": [...],
    "anonymized_text": "...",
    "entity_count": 5,
    "processing_time_ms": 120
  },
  {
    "filename": "document2.txt",
    "filepath": "/path/to/document2.txt",
    "analysis_results": [...],
    "anonymized_text": "...",
    "entity_count": 3,
    "processing_time_ms": 95
  }
]
```

---

## 🔧 Advanced Usage

### Custom Anonymization Rules
```bash
# Custom anonymization with different operators
curl -X POST "http://localhost:5001/anonymize" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "John Doe, email john@example.com, phone 555-123-4567",
    "analyzer_results": [...],
    "anonymizers": {
      "PERSON": {"type": "replace", "new_value": "[NAME]"},
      "EMAIL_ADDRESS": {"type": "hash"},
      "PHONE_NUMBER": {"type": "mask", "masking_char": "*", "chars_to_mask": 4, "from_end": true}
    }
  }' | jq '.' > custom_anonymized.json
```

### Performance Monitoring
```bash
# Monitor processing time
time curl -X POST "http://localhost:5002/analyze" \
  -H "Content-Type: application/json" \
  -d '{"text": "Your text here", "language": "en"}' \
  | jq '.' > timed_analysis.json

# Batch processing with timing
start_time=$(date +%s)
for file in *.txt; do
  echo "Processing: $file"
  curl -s -X POST "http://localhost:5002/analyze" \
    -H "Content-Type: application/json" \
    -d "{\"text\": \"$(cat $file | tr '\n' ' ')\", \"language\": \"en\"}" \
    | jq --arg file "$file" --arg start "$start_time" '. + {filename: $file, processing_time: (now - ($start | tonumber))}' >> performance_results.json
done
```

### Error Handling
```bash
# Process with error handling
process_file() {
  local file="$1"
  local output="$2"
  
  if curl -s -X POST "http://localhost:5002/analyze" \
    -H "Content-Type: application/json" \
    -d "{\"text\": \"$(cat $file | tr '\n' ' ')\", \"language\": \"en\"}" \
    | jq --arg file "$file" '. + {filename: $file, status: "success"}' >> "$output"; then
    echo "✅ Success: $file"
  else
    echo "❌ Failed: $file"
    echo "{\"filename\": \"$file\", \"status\": \"error\", \"error\": \"Processing failed\"}" >> "$output"
  fi
}

# Use the function
process_file "document.txt" "results.json"
```

---

## 🚨 Troubleshooting

### Service Issues
```bash
# Check if services are running
docker-compose ps

# Restart specific service
docker-compose restart presidio-analyzer

# Check service logs
docker-compose logs presidio-analyzer

# Check resource usage
docker stats
```

### Port Conflicts
```bash
# Check port usage
netstat -tulpn | grep :5001
netstat -tulpn | grep :5002
netstat -tulpn | grep :5003

# Kill processes on ports
sudo fuser -k 5001/tcp
sudo fuser -k 5002/tcp
sudo fuser -k 5003/tcp
```

### Memory Issues
```bash
# Check Docker memory usage
docker system df

# Clean up Docker
docker system prune -a

# Check container memory
docker stats --no-stream
```

### JSON Processing Issues
```bash
# Validate JSON output
jq '.' results.json

# Pretty print JSON
jq '.' results.json | less

# Extract specific fields
jq '.[] | {entity_type, score}' results.json

# Filter results by confidence
jq '.[] | select(.score > 0.8)' results.json

# Count entities
jq '[.[] | .entity_type] | group_by(.) | map({type: .[0], count: length})' results.json
```

---

## 📝 Example Scripts

### Complete Processing Script
```bash
#!/bin/bash
# presidio_process.sh - Complete file processing with JSON output

INPUT_DIR="$1"
OUTPUT_DIR="$2"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p "$OUTPUT_DIR"

echo "Processing files in: $INPUT_DIR"
echo "Output directory: $OUTPUT_DIR"

# Process all text files
find "$INPUT_DIR" -name "*.txt" -o -name "*.csv" -o -name "*.json" | while read file; do
  echo "Processing: $file"
  
  # Analyze
  ANALYSIS=$(curl -s -X POST "http://localhost:5002/analyze" \
    -H "Content-Type: application/json" \
    -d "{\"text\": \"$(cat $file | tr '\n' ' ')\", \"language\": \"en\"}")
  
  # Anonymize
  ANONYMIZED=$(curl -s -X POST "http://localhost:5001/anonymize" \
    -H "Content-Type: application/json" \
    -d "{\"text\": \"$(cat $file | tr '\n' ' ')\", \"analyzer_results\": $ANALYSIS, \"anonymizers\": {\"DEFAULT\": {\"type\": \"replace\", \"new_value\": \"[REDACTED]\"}}}")
  
  # Save combined results
  jq --arg file "$file" --arg analysis "$ANALYSIS" --arg anonymized "$ANONYMIZED" \
    '{filename: $file, analysis_results: ($analysis | fromjson), anonymized_result: ($anonymized | fromjson), timestamp: now}' \
    >> "$OUTPUT_DIR/processing_results_$TIMESTAMP.json"
done

echo "Processing complete. Results saved to: $OUTPUT_DIR/processing_results_$TIMESTAMP.json"
```

### Usage:
```bash
chmod +x presidio_process.sh
./presidio_process.sh /path/to/input /path/to/output
```

---

## 🎯 Quick Reference

| Task | Command | JSON Output |
|------|---------|-------------|
| Analyze text | `curl -X POST "http://localhost:5002/analyze" -H "Content-Type: application/json" -d '{"text": "text", "language": "en"}'` | `> results.json` |
| Anonymize text | `curl -X POST "http://localhost:5001/anonymize" -H "Content-Type: application/json" -d '{...}'` | `> anonymized.json` |
| Scan file | `presidio file.txt --format json` | `> scan_results.json` |
| Scan directory | `presidio /path/to/dir --format json` | `> directory_scan.json` |
| Health check | `curl http://localhost:8080/api/health` | `> health_status.json` |
| Batch process | `for file in *.txt; do curl ... done` | `> batch_results.json` |

---

## 🔗 Useful Links

- **GitHub**: https://github.com/microsoft/presidio
- **Documentation**: https://microsoft.github.io/presidio/
- **Web Interface**: http://localhost:8080/presidio_cors_ui.html
- **Health Check**: http://localhost:8080/api/health

---

**🚀 Your complete Presidio command reference with JSON output examples!**