from pymongo import MongoClient
from langchain_openai import AzureOpenAIEmbeddings
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_community.document_loaders import DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from PyPDF2 import PdfReader
import key_param


# Set the MongoDB URI, DB, Collection Names

client = MongoClient(key_param.MONGO_URI)
dbName = "langchain_demo"
collectionName = "collection_of_text_blobs"
collection = client[dbName][collectionName]

# Initialize the DirectoryLoader
loader = DirectoryLoader( './sample_files', glob="./*.txt", show_progress=True)
data = loader.load()

# Read text from the PDF
with open('./sample_files/MongoDBDeveloperTrainingProgramDatasheet_UpdatedMay2024.pdf', 'rb') as file:
    pdf = PdfReader(file)
    text = " ".join(page.extract_text() for page in pdf.pages)

# Chunk the PDF text
# https://python.langchain.com/v0.1/docs/modules/data_connection/document_transformers/recursive_text_splitter/
custom_text_splitter = RecursiveCharacterTextSplitter(
    # Set custom chunk size
    chunk_size = 1000,
    chunk_overlap  = 20,
    # Use length of the text as the size measure
    length_function = len,
    # Use only "\n\n" as the separator
    separators = ['\n']
)
custom_texts = custom_text_splitter.create_documents([text])




# Define the OpenAI Embedding Model we want to use for the source data
# The embedding model is different from the language generation model
embeddings = AzureOpenAIEmbeddings(azure_endpoint=key_param.AZURE_OPENAI_ENDPOINT, 
                                   openai_api_key=key_param.AZURE_OPENAI_API_KEY, 
                                   azure_deployment="text-embedding-ada-002", 
                                   openai_api_version="2023-05-15")

# Initialize the VectorStore, and
# vectorise the text from the documents using the specified embedding model, and insert them into the specified MongoDB collection
# https://api.python.langchain.com/en/latest/vectorstores/langchain_mongodb.vectorstores.MongoDBAtlasVectorSearch.html
vectorStore = MongoDBAtlasVectorSearch(embedding=embeddings, 
                                       collection=collection,
                                       embedding_key="embedding", 
                                       index_name="vector_index" )

vectorStore.add_documents(data)
vectorStore.add_documents(custom_texts)
