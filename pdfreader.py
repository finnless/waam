

def pdf_reader(myPdf):
    from langchain.document_loaders import PyPDFLoader

    loader = PyPDFLoader(myPDF)
    pages = loader.load_and_split()
    pages[0]

    from langchain.vectorstores import FAISS
    from langchain.embeddings.openai import OpenAIEmbeddings

    faiss_index = FAISS.from_documents(pages, OpenAIEmbeddings())
    docs = faiss_index.similarity_search("How will the community be engaged?", k=2)
    for doc in docs:
        print(str(doc.metadata["page"]) + ":", doc.page_content)