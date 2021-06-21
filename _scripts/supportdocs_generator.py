import frontmatter
import json
import os
import sys

DATA_JSON_DIR = "_data"
DEVELOPER_MODE = "debug" in sys.argv
if not DEVELOPER_MODE:
    GITHUB_USERNAME = os.environ.get("GITHUB_ACTOR")
    FULL_GITHUB_REPOSITORY = os.environ.get("GITHUB_REPOSITORY")
    GITHUB_REPOSITORY = FULL_GITHUB_REPOSITORY.split("/")[1]
    GITHUB_BRANCH = (
        os.environ.get("GITHUB_REF").split("/")[-1]
        if os.environ.get("GITHUB_REF")
        else GITHUB_REPOSITORY
    )
else:
    GITHUB_USERNAME = "demo"
    FULL_GITHUB_REPOSITORY = "demo/SupportDocs"
    GITHUB_REPOSITORY = FULL_GITHUB_REPOSITORY.split("/")[1]
    GITHUB_BRANCH = "DataSource"


def removePreexistingData():
    for root, _, files in os.walk(DATA_JSON_DIR):
        for file in files:
            if file.endswith(".json") and os.path.exists(os.path.join(root, file)):
                os.remove(os.path.join(root, file))
                print(f"DEBUG: Removed file {os.path.join(root, file)}")


def getLanguageDirs() -> list[str]:
    return [
        directory
        for directory in next(os.walk("."))[1]
        if not directory.startswith("_") and not directory.startswith(".")
    ]


def writeJsonData(directory: str):
    dataSourceFilePath = os.path.join(DATA_JSON_DIR, f"{directory}_supportDocs_dataSource")
    with open(dataSourceFilePath, "w") as dataSourceFile:
        for filePath in getAllFiles(directory):
            singleJsonData = parseMarkdown(filePath)
            print(f"DEBUG: Parse file {filePath}")
            dataSourceFile.write(json.dumps(singleJsonData, indent=4))
            dataSourceFile.write(",\n")
        dataSourceFile.write(json.dumps(getSingleJsonData("404 Page", ["SupportDocs Integrated File"], f"{directory}/404"), indent=4))
        print(f"DEBUG: Parse file {directory}/404")
    print(f"DEBUG: Write to file {dataSourceFilePath}")


def getAllFiles(directory: str) -> list[str]:
    allFiles = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".md") and file != "404.md":
                allFiles.append(os.path.join(root, file))
    return allFiles


def parseMarkdown(path: str) -> dict:
    with open(path) as md:
        fileTags = frontmatter.load(md).metadata
    if not checkTags(fileTags, ["title", "tags"]):
        return {"error": "Missing tags"}
    return getSingleJsonData(fileTags["title"], fileTags["tags"], path)


def checkTags(fileTags: list[str], tags: list[str]) -> bool:
    for tag in tags:
        if tag not in fileTags:
            return False
    return True


def getSingleJsonData(title: str, tags: list, path: str) -> dict:
    return {
        "title": title,
        "tags": [tags] if isinstance(tags, str) else tags,
        "url": f"https://{GITHUB_USERNAME}.github.io/{GITHUB_REPOSITORY}/{path.replace('.md', '')}",
    }


def main():

    # Remove preexisting data
    removePreexistingData()

    # Create _data folder
    if not os.path.exists(DATA_JSON_DIR):
        os.makedirs(DATA_JSON_DIR)
        print(f"DEBUG: Make dir {DATA_JSON_DIR}")

    # Write json file
    for languageDir in getLanguageDirs():
        writeJsonData(languageDir)


if __name__ == "__main__":
    main()
