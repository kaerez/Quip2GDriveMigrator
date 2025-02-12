import argparse
import os
import re
import requests
import time


class Quip2GDriveMigrator:
    def __init__(self, api_token, throttle_threshold):
        self.api_token = api_token
        self.throttle_threshold = throttle_threshold
        self.base_url = "https://platform.quip.com/1"

    def _get_thread_content(self, thread_id):
        url = f"{self.base_url}/threads/{thread_id}"
        headers = {"Authorization": f"Bearer {self.api_token}"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    def _get_folder(self, folder_id):
        url = f"{self.base_url}/folders/{folder_id}"
        headers = {"Authorization": f"Bearer {self.api_token}"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    def _export_to_docx(self, thread_id, out_dir, title):
        url = f"{self.base_url}/threads/{thread_id}/export/docx"
        headers = {"Authorization": f"Bearer {self.api_token}"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # Deal with characters which are invalid for file path
        invalid_chars = r'[<>:"/\\|?*]'
        title = re.sub(invalid_chars, "_", title)

        if os.path.exists(title):
            return

        out_file = os.path.join(out_dir, title + ".docx")

        if os.path.isfile(out_file):
            print(f"File [{out_file}] already exists, skip it")
            return

        # Write the content to a .docx file
        with open(out_file, "wb") as file:
            file.write(response.content)

    def process(self, folder_id, out_dir):
        url_to_title_map = {}
        curr_folder = self._get_folder(folder_id)
        curr_folder_tile = curr_folder["folder"]["title"]
        curr_out_dir = os.path.join(out_dir, curr_folder_tile)
        os.makedirs(curr_out_dir, exist_ok=True)

        print(f"Processing folder [{curr_folder_tile}]")
        for child in curr_folder["children"]:
            child_folder_id = child.get("folder_id", None)
            child_thread_id = child.get("thread_id", None)

            if child_folder_id:
                child_url_to_title_map = self.process(child_folder_id, curr_out_dir)
                url_to_title_map.update(child_url_to_title_map)
            else:
                doc = self._get_thread_content(child_thread_id)
                id = doc["thread"]["id"]
                title = doc["thread"]["title"]
                url = doc["thread"]["link"]
                print(f"Downloading doc [{title}] to folder [{curr_out_dir}]")
                self._export_to_docx(id, curr_out_dir, title)
                url_to_title_map[url] = title
                time.sleep(self.throttle_threshold)

        return url_to_title_map


def main():
    parser = argparse.ArgumentParser(description="Quip doc to Google Drive Migrator")

    parser.add_argument(
        "-t", "--api_token", type=str, required=True, help="Access token for Quip API"
    )
    parser.add_argument(
        "-f", "--folder_id", type=str, required=True, help="ID of the Quip folder"
    )
    parser.add_argument(
        "-d",
        "--dest_folder",
        type=str,
        required=True,
        help="Full path for the destination folder at your local disk",
    )
    parser.add_argument(
        "-m",
        "--titl_to_url_map_file",
        type=str,
        required=True,
        help="Output file name in the destination folder that logs title to URL mappings",
    )
    parser.add_argument(
        "--throttle_threshold",
        type=int,
        default=2,
        help="Interval in seconds between each Quip API call (default=2)",
    )

    args = parser.parse_args()

    if not os.path.isdir(args.dest_folder):
        print(f"Destination folder [{args.dest_folder}] doesn't exist.")
        return

    migrator = Quip2GDriveMigrator(args.api_token, args.throttle_threshold)

    url_to_title_map = migrator.process(args.folder_id, args.dest_folder)

    with open(os.path.join(args.dest_folder, args.titl_to_url_map_file), "w") as writer:
        for url, title in url_to_title_map.items():
            writer.write(f"{title}\t{url}\n")


if __name__ == "__main__":
    main()
