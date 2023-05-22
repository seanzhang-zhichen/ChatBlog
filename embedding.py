import os
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.docstore.document import Document
import re
from bs4 import BeautifulSoup

os.environ["OPENAI_API_KEY"] = "你自己的key"


# 自定义句子分段的方式，保证句子不被截断
def split_paragraph(text, max_length=300):
    text = text.replace('\n', '') 
    text = text.replace('\n\n', '') 
    text = re.sub(r'\s+', ' ', text)
    """
    将文章分段
    """
    # 首先按照句子分割文章
    sentences = re.split('(；|。|！|\!|\.|？|\?)',text) 
    
    new_sents = []
    for i in range(int(len(sentences)/2)):
        sent = sentences[2*i] + sentences[2*i+1]
        new_sents.append(sent)
    if len(sentences) % 2 == 1:
      new_sents.append(sentences[len(sentences)-1])

    # 按照要求分段
    paragraphs = []
    current_length = 0
    current_paragraph = ""
    for sentence in new_sents:
        sentence_length = len(sentence)
        if current_length + sentence_length <= max_length:
            current_paragraph += sentence
            current_length += sentence_length
        else:
            paragraphs.append(current_paragraph.strip())
            current_paragraph = sentence
            current_length = sentence_length
    paragraphs.append(current_paragraph.strip())
    documents = []
    for paragraph in paragraphs:
        new_doc = Document(page_content=paragraph)
        print(new_doc)
        documents.append(new_doc)
    return documents

# 持久化向量数据
def persist_embedding(documents):
    # 将embedding数据持久化到本地磁盘
    persist_directory = 'db'
    embedding = OpenAIEmbeddings()
    vectordb = Chroma.from_documents(documents=documents, embedding=embedding, persist_directory=persist_directory)
    vectordb.persist()
    vectordb = None

def get_blog_text():
    data_path = 'blog.txt'
    with open(data_path, 'r') as f:
        data = f.read()
    soup = BeautifulSoup(data, 'lxml')
    text = soup.get_text()
    return text
    



if __name__ == "__main__":
    # embdding并且持久化
    content = get_blog_text()
    documents = split_paragraph(content)
    persist_embedding(documents)
