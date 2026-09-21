"""Render a Kubernetes manifest without a template engine or extra dependencies."""
import argparse
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--image", required=True)
parser.add_argument("--version", required=True)
args = parser.parse_args()
template = Path(__file__).resolve().parents[1] / "k8s" / "app.yaml.tpl"
text = template.read_text(encoding="utf-8")
text = text.replace("__IMAGE_URI__", json.dumps(args.image))
text = text.replace("__APP_VERSION__", json.dumps(args.version))
print(text)
