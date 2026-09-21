"""Dry-run by default: remove old Lambda versions and unneeded ECR images.

Keeps the newest three published versions, all aliases, $LATEST and bootstrap.
Run while deployments are paused. Human AWS credentials are required.
"""
import argparse
import json
import subprocess


def aws(*args):
    output = subprocess.check_output(["aws", *args, "--output", "json"], text=True)
    return json.loads(output) if output.strip() else {}


def image_digest(function_name, version):
    result = aws("lambda", "get-function", "--function-name", function_name, "--qualifier", version)
    uri = result["Code"]["ResolvedImageUri"]
    return uri.rsplit("@", 1)[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--function-name", default="devops-portfolio")
    parser.add_argument("--repository", default="devops-portfolio")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    repository = aws("ecr", "describe-repositories", "--repository-names", args.repository)["repositories"][0]
    latest = aws("lambda", "get-function", "--function-name", args.function_name)
    if not latest["Code"]["ResolvedImageUri"].startswith(repository["repositoryUri"] + "@"):
        raise SystemExit("The function does not use this ECR repository; refusing cleanup.")
    versions = aws("lambda", "list-versions-by-function", "--function-name", args.function_name)["Versions"]
    numbered = sorted([v["Version"] for v in versions if v["Version"] != "$LATEST"], key=int, reverse=True)
    aliases = aws("lambda", "list-aliases", "--function-name", args.function_name)["Aliases"]
    keep = set(numbered[:3]) | {"$LATEST"}
    for alias in aliases:
        keep.add(alias["FunctionVersion"])
        keep.update(alias.get("RoutingConfig", {}).get("AdditionalVersionWeights", {}).keys())
    remove_versions = [v for v in numbered if v not in keep]
    keep_digests = {image_digest(args.function_name, version) for version in keep}
    images = aws("ecr", "describe-images", "--repository-name", args.repository)["imageDetails"]
    remove_images = [i for i in images if i["imageDigest"] not in keep_digests and "bootstrap" not in i.get("imageTags", [])]
    print(f"Function: {args.function_name}; repository: {args.repository}")
    print("Keep Lambda versions:", ", ".join(sorted(keep)))
    print("Delete Lambda versions:", ", ".join(remove_versions) or "none")
    for image in remove_images:
        print("Delete image:", image["imageDigest"], image.get("imageTags", []))
    if not args.apply:
        print("Dry run only. Review the list; add --apply to remove exactly these eligible resources.")
        return
    # Delete versions first; stop on any failure before touching their images.
    for version in remove_versions:
        aws("lambda", "delete-function", "--function-name", args.function_name, "--qualifier", version)
    for image in remove_images:
        result = aws("ecr", "batch-delete-image", "--repository-name", args.repository,
                     "--image-ids", f"imageDigest={image['imageDigest']}")
        if result.get("failures"):
            raise SystemExit(f"ECR deletion failed: {result['failures']}")
    print("Cleanup complete.")


if __name__ == "__main__":
    main()
