# PPStructure / PaddleOCR Runtime Verification

Run on: 2026-06-23

## Command

```bash
source ~/paddleocr-venv/bin/activate && python3 - <<'PY'
from paddleocr import PPStructure, PaddleOCR
from PIL import Image, ImageDraw
# create /tmp/table_test.png and run tests
PY
```

## Results

```text
/Users/ericstone/paddleocr-venv/lib/python3.12/site-packages/paddle/utils/cpp_extension/extension_utils.py:711: UserWarning: No ccache found. Please be aware that recompiling all source files may be required. You can download and install ccache from: https://github.com/ccache/ccache/blob/master/doc/INSTALL.md
  warnings.warn(warning_message)
=== Test 1: PPStructure on synthetic table image ===
Created /tmp/table_test.png
PPStructure result type: <class 'list'>
Number of regions: 2
Type: figure_caption Text: [{'text': '123', 'confidence': 0.9995484352111816, 'text_region': [[159.0, 71.0], [179.0, 71.0], [179.0, 84.0], [159.0, 84.0]]}]
Type: table Text: {'cell_bbox': [[6.210982322692871, 15.645989418029785, 86.83609008789062, 15.982629776000977, 87.85769653320312, 310.27142333984375, 6.066554546356201, 310.1891784667969], [136.44529724121094, 19.1454
SUCCESS: PPStructure works

=== Test 2: PaddleOCR(table=True).ocr() table output ===
PaddleOCR(table=True) result type: <class 'list'>
Number of result groups: 1
Group 0: type=<class 'list'>, len=4
   [[[18.0, 17.0], [43.0, 20.0], [42.0, 34.0], [16.0, 31.0]], ('Item', 0.9970865249633789)]
   [[[156.0, 19.0], [189.0, 19.0], [189.0, 33.0], [156.0, 33.0]], ('Value', 0.9998692274093628)]
   [[[18.0, 70.0], [42.0, 70.0], [42.0, 82.0], [18.0, 82.0]], ('Test', 0.9995043873786926)]
Contains table/html markers: False
SUCCESS: PaddleOCR(table=True) produced output

```

## Conclusion

- PPStructure ran successfully and returned structured regions including a `table` region.
- `PaddleOCR(table=True).ocr()` returned OCR text lines but no table/HTML markup on this simple synthetic image.
