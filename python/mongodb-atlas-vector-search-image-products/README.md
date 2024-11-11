# MongoDB Atlas Vector Search (Images) on Fashion Products

# Atlas Vector Search on Fashion Products

How can a search be conducted for the visual attributes of products that were not included in the product's metadata?
To clarify further, imagine having millions of fashion products without any information about their color or category. You have the following basic data model:

```json
{
    "imageFile": "images/2.jpg",
    "price": 15.66,
    "discountPercentage": 7,
    "avgRating" : 3.47
}
```

Furthermore, our users wish to perform a search such as **"green shirts"** and our objective is to retrieve the products where the corresponding image (e.g., images/2.jpg) portrays a **green shirt**. This can be easily achieved using Vector Search.

Consider this search query: On the right side, you'll find a sample entry from a database that lacks metadata like the product's "color" or "category." Nevertheless, our search appears to be successful as it matches the visual attributes of the product.

In simpler terms, the application transforms the given texts into vectors, which are then sent to MongoDB Atlas. Using Atlas Search, the system compares these vectors with those in the collection and identifies the most similar vectors to the given one.

Another example:**"pink shoes"**

# Prerequisites

- MongoDB Atlas Cluster (M0 is ok if there is sufficient free space - 350kB)
- Download this small sample and upload the collection to your Atlas cluster:
Note: You can file this zip file already donloaded in the `encoder/` folder.
```bash
cd encoder

unzip dump.zip
```
Restore the dump into your Atlas cluster, making sure you update the user, password and uri:
```bash
mongorestore --uri="mongodb+srv://<user>:<password>@<your_altas_cluster>.mongodb.net/?authSource=admin" ./dump/vector_search/products.bson
```
  Note: this is a very small collection, 42 documents, and it has already the image embeddings, If you want to try with a bigger collection test with this product dataset (600MB) [here](https://www.kaggle.com/datasets/paramaggarwal/fashion-product-images-small). You will need to downloaded the compressed file, extract it and encode the images using the  `encoder/` folder.

Execution was successful with the following dependencies
  - Python 3.9.2 with the following libraries will be required
    - Flask==2.1.0
    - Pillow==9.3.0
    - pymongo[srv]==4.1.1
    - sentence_transformers==2.2.2
    - Werkzeug==2.2.2
  The `requirements.txt` file includes all the dependencies, in your Terminal, navigate to the `mongodb-atlas-vector-search-image-products` folder and run the folowing commands:
  ```bash
    python3 -m venv env
    source env/bin/activate
    pip3 install -r requirements.txt
  ```

# Steps to Install and Test

## Configure database connection

Please make the necessary changes to the `config/config_database.py` file by updating the database connection string, as well as the details of the database and collection.

## Create the Search Index

Please create the search index on the collection specified in the configuration file, and make sure to name the index as `vectorImg`. Use the following JSON for the index creation:

```json
{
  "fields": [
    {
      "numDimensions": 768,
      "path": "imageVector",
      "similarity": "cosine",
      "type": "vector"
    },
    {
      "path": "price",
      "type": "filter"
    },
    {
      "path": "averageRating",
      "type": "filter"
    },
    {
      "path": "discountPercentage",
      "type": "filter"
    }
  ]
}
```

## Run Image Encoding and Store the Vector in the database (Optional)

The product images have already been downloaded (check the `image/` folder under `encoder/`) 
These images were encoded on the application side and stored as vectors inside the database already.

Note: If you want to include new images, you can follow these steps to encode them. Switch to `encoder/` folder and make sure the `images/` folder includes all the image files and run the `encoder_and_loader.py`

```bash
$ python encoder_and_loader.py
```

It will create worker threads (It runs on 8 threads by default, you can configure this in the python file), and these threads will go through all the files under the `images/` folder and load the vectors inside the MongoDB collection.

The process may require a considerable amount of time, which is dependent on the hardware resources available on the machine. If the machine has 8 cores, it might take several hours (3-4) to complete. The application itself is the limiting factor as it generates the embeddings for the images. Increasing the cluster size will not expedite this operation. This operation is not resumable, in other words, if somehow this loader crashes, it will start from scratch (by deleting data in the target collection).

Once the process is finished, you can verify the collection using the instructions provided below.


## Run the Web Application to Search for Products

Switch to `webapp/` folder and run `flask_server.py`.

```bash
$ python flask_server.py
```

This web application has 2 pages:

For a simple product search, open a browser and navigate to `http://localhost:5010/`.
For advanced search (conditions using filters and sort), navigate to `http://localhost:5010/advanced`.
