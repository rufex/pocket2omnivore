import datetime as dt
import logging
import os
import random
import time
from typing import Dict, List, TypedDict

import requests


class Label(TypedDict):
    id: str
    name: str
    color: str
    description: str
    createdAt: str


class Omnivore:
    api = "https://api-prod.omnivore.app/api/graphql"
    headers = {"authorization": os.getenv("api_key")}  # your api key

    def _request_from_omnivore(self, payload: dict, retry=3) -> Dict:
        if not retry:
            logging.error("Retry timeout")
            return
        try:
            resp = requests.post(self.api, headers=self.headers, json=payload)
            if resp.status_code != 200:
                logging.error(f"Response Status from Omnivore: {resp.status_code}")
                logging.error(resp.text)
                return
            return resp.json()
        except Exception:
            logging.error(f"Request failed: {Exception}")
            time.sleep(random.randint(3, 5))
            return self._request_from_omnivore(payload, retry=retry - 1)

    def get_labels(self) -> List[Label]:
        """get all existing labels

        Returns:
            labels
        """
        body = """
            {

            labels {
                ... on LabelsSuccess {
                    labels {
            id
            name
            color
            description
            createdAt
                    }
                }
                ... on LabelsError {
                    errorCodes
                }
            }
        }
        """
        result = self._request_from_omnivore({"query": body})
        if not result:
            return
        return result["data"]["labels"]["labels"]

    def create_label(
        self, name: str = None, color: str = None, description: str = None
    ) -> Label:
        """create label

        Keyword Arguments:
            color -- color
            name -- name
            description -- descript

        Returns:
            label instance
        """
        body = """
            mutation {{
                createLabel(input: {{ color: "{color}", name: "{name}", description: "{description}" }}) 
                {{ ... on CreateLabelSuccess {{
                        label {{
                            id
                            name
                            color
                            description
                            createdAt
                            }}
                    }}
                    ... on CreateLabelError {{
                        errorCodes
                    }}
                }}
            }}
        """.format(
            color=color, name=name, description=description
        )
        result = self._request_from_omnivore({"query": body})
        if not result:
            logging.error(f"Creation of label failed (empty response)")
            return
        create_label_result = result["data"]["createLabel"]
        if "errorCodes" in create_label_result:
            logging.error(f'label:{name} {create_label_result["errorCodes"]}')
            return
        return create_label_result["label"]

    def set_labels(self, page_id: str, label_ids: List[str]) -> bool:
        """set page's label

        Arguments:
            page_id -- page id
            label_ids -- label id list

        Returns:
            set label success or not (bool)
        """
        set_label_mutation = """
            mutation SetLabels($input: SetLabelsInput!) {
                setLabels(input: $input) {
                    ... on SetLabelsSuccess {
                        labels {
                            ...LabelFields
                        }
                    }
                    ... on SetLabelsError {
                        errorCodes
                    }
                }
            }

            fragment LabelFields on Label {
                id
                name
                color
                description
                createdAt
            }

        """
        payload = {
            "query": set_label_mutation,
            "variables": {"input": {"pageId": page_id, "labelIds": label_ids}},
        }
        result = self._request_from_omnivore(payload)
        if not result:
            return False
        return True

    def save_page(self, url: str) -> str:
        """save page by url

        Arguments:
            url -- url

        Returns:
            article id if save url success
        """
        save_page_mutation = """
        mutation CreateArticleSavingRequest($input: CreateArticleSavingRequestInput!) {
            createArticleSavingRequest(input: $input) {
                ... on CreateArticleSavingRequestSuccess {
                    articleSavingRequest {
                        id
                        status
                    }
                }
                ... on CreateArticleSavingRequestError {
                    errorCodes
                }
            }
        }
        """
        payload = {"query": save_page_mutation, "variables": {"input": {"url": url}}}
        result = self._request_from_omnivore(payload)
        if not result:
            return
        return result["data"]["createArticleSavingRequest"]["articleSavingRequest"][
            "id"
        ]

    def archive_page(self, id: str, status: bool = True) -> bool:
        """Archive article by linkId

        Arguments:
            id -- link id
            status -- archive status (default True)

        Returns:
            archive link success or not (bool)
        """
        archive_page_mutation = """
        mutation ArchiveLinkRequest($input: ArchiveLinkInput!) {
            setLinkArchived(input: $input) {
                ... on ArchiveLinkSuccess {
                    linkId
                    message
                }
                ... on ArchiveLinkError {
                    errorCodes
                }
            }
        }
        """
        payload = {
            "query": archive_page_mutation,
            "variables": {"input": {"linkId": id, "archived": status}},
        }
        result = self._request_from_omnivore(payload)
        if not result:
            return False
        return True

    def update_page(
        self,
        page_id: str,
        date: dt.datetime = None,
        title: str = None,
        description: str = None,
    ) -> bool:
        """update page's details by pageId

        Arguments:
            pageId -- id
            date -- date in which the link was saved
            title -- title
            description -- description

        Returns:
            update page success or not (bool)
        """
        update_page_mutation = """
            mutation UpdatePageRequest($input: UpdatePageInput!) {
                updatePage(input: $input) {
                    ... on UpdatePageSuccess {
                        updatedPage {
                            ...ArticleFields
                        }
                    }
                    ... on UpdatePageError {
                        errorCodes
                    }
                }
            }
            fragment ArticleFields on Article {
                id
                savedAt
                title
                description
            }
            """
        payload = {
            "query": update_page_mutation,
            "variables": {
                "input": {
                    "pageId": page_id,
                    "savedAt": date.isoformat(),
                    "title": title,
                    "description": description,
                }
            },
        }
        result = self._request_from_omnivore(payload)
        if not result:
            return False
        return True
