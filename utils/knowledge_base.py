import chromadb
from chromadb.utils import embedding_functions

class KnowledgeBase:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.ef = embedding_functions.DefaultEmbeddingFunction()
        self.collection = self.client.get_or_create_collection(
            name="company_knowledge",
            embedding_function=self.ef
        )
        if self.collection.count() == 0:
            self._seed_default_knowledge()

    def _seed_default_knowledge(self):
        default_docs = [
            "We helped a B2B SaaS company reduce their SDR cost by 80 percent by automating prospect research and outreach with AI agents. They went from spending 60000 dollars per year on manual research to 0.02 dollars per prospect.",
            "For a Series A fintech company we built an AI agent that analyzed 500 prospects per week and generated personalized outreach sequences. Their response rate increased from 8 percent to 23 percent.",
            "We specialize in building agentic AI systems for B2B sales teams. Our agents combine web research, computer vision, and predictive scoring to identify and engage the highest value prospects.",
            "A marketing agency hired us to build a multimodal AI that reads product screenshots and writes personalized cold emails. They closed 3 enterprise clients in the first month using the system.",
            "Our AI sales platform predicts closing probability with 80 percent accuracy by analyzing company research, visual signals from product screenshots, and LinkedIn activity together.",
        ]
        self.collection.add(
            documents=default_docs,
            ids=[f"doc_{i}" for i in range(len(default_docs))]
        )

    def add_document(self, content: str, doc_id: str):
        self.collection.add(documents=[content], ids=[doc_id])

    def search(self, query: str, n_results: int = 3) -> str:
        count = self.collection.count()
        if count == 0:
            return "No knowledge base documents found."
        results = self.collection.query(
            query_texts=[query],
            n_results=min(n_results, count)
        )
        docs = results.get("documents", [[]])[0]
        return "\n\n".join(docs) if docs else "No relevant knowledge found."