# Pocket2Omnivore: Migration tool

## Usage

Step 1: Create a corresponding Python environment and install the necessary dependencies by running:

```bash
pip install -r requirements.txt
```

Step 2: Modify the environment variables in the `.env` file. You can apply for the api_key on the [API Keys](https://omnivore.app/settings/api) page of Omnivore.

Step 3: Export your existing articles from Pocket and store the generated html file in the folder `pocket_export`. File name should be `ril_export.html`

Step 4: Run your program.

```python
python sync_articles_to_omnivore.py
```

## Information

This script is intented to be used to import your articles previously stored in Pocket into Omnivore.
It will try to identify those articles and their information from the html file provided by Pocket.
When saving these articles into Omnivore, it will also try to add to them the following information:

- URL
- Title
- Date of creation
- Tags
- Archive status

  To add tags, it will first have to check if they already exist or not, and create them if they are missing.

## Credits

- [LeetaoGoooo/Import2Omnivore](https://github.com/LeetaoGoooo/Import2Omnivore): A tool to export articles from Matter and import them into Omnivore.
- [daviddavo/pocket2omnivore](https://github.com/daviddavo/pocket2omnivore): Jupiter Notebook with some steps by steps to import your articles from Pocket into Omnivore.
