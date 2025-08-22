#Importing libraries
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

#LangChain is  used to provide a standardized framework for building document processing pipelines
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv
from src.config import VECTORSTORE_PATH, USE_OPENAI, EMBEDDING_MODEL

#Loading environment variables
load_dotenv()

class FinancialPolicyChatbot:
    def __init__(self):
        """
        Initialize the Financial Policy Chatbot
        """
        self.vectorstore = None
        self.memory = ConversationBufferMemory(
            memory_key="chat_history", 
            return_messages=True
        )
        
        #Initialize the embeddings
        if USE_OPENAI:
            from langchain_community.embeddings import OpenAIEmbeddings
            self.embeddings = OpenAIEmbeddings()
        else:
            #Check if sentence-transformers is available for HuggingFace embeddings
            try:
                import sentence_transformers
                self.embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
            except ImportError:
                raise ImportError(
                    "Could not import sentence_transformers python package. "
                    "Please install it with `pip install sentence-transformers`."
                )
    
    def load_vectorstore(self):
        """
        Load the pre-built vector store
        """
        if not os.path.exists(VECTORSTORE_PATH):
            raise FileNotFoundError(
                f"Vector store not found at {VECTORSTORE_PATH}. "
                f"Please run build_knowledge_base.py first."
            )
        
        print("Loading vector store...")
        self.vectorstore = FAISS.load_local(VECTORSTORE_PATH, self.embeddings, allow_dangerous_deserialization=True)
        print("Vector store loaded successfully!")
    
    def initialize_chatbot(self):
        """
        Initialize the complete chatbot
        """
        self.load_vectorstore()
        print("Chatbot initialized and ready!")
    
    def ask_question(self, question: str):
        """
        Ask a question about the financial policy document
        Returns the most relevant text chunks from the document
        """
        if not self.vectorstore:
            raise ValueError("Chatbot not initialized. Call initialize_chatbot() first.")
        
        try:
            #fetching the most relevant documents
            relevant_docs = self.vectorstore.similarity_search(question, k=3)
            
            if not relevant_docs:
                return {
                    "answer": "I couldn't find relevant information in the document to answer your question.",
                    "sources": [],
                    "question": question
                }
            
            # Creating a simple answer by combining the most relevant information running for loop
            answer_parts = []
            for i, doc in enumerate(relevant_docs, 1):
                answer_parts.append(f"From page {doc.metadata.get('page', 'Unknown')}: {doc.page_content}")
            
            answer = "\n\n".join(answer_parts)
            
            # Extract source information
            sources = []
            for doc in relevant_docs:
                page_num = doc.metadata.get("page", "Unknown")
                content_preview = doc.page_content[:150] + "..." if len(doc.page_content) > 150 else doc.page_content
                sources.append({
                    "page": page_num,
                    "content_preview": content_preview,
                    "full_content": doc.page_content
                })
            
            return {
                "answer": f"I found this information in the financial policy document:\n\n{answer}",
                "sources": sources,
                "question": question
            }
            
        except Exception as e:
            return {
                "answer": f"I encountered an error while processing your question: {str(e)}",
                "sources": [],
                "question": question
            }

def main():
    """
    Main function to run the chatbot in console mode
    """
    chatbot = FinancialPolicyChatbot()
    
    try:
        chatbot.initialize_chatbot()
        
        print("\n" + "="*60)
        print("FINANCIAL POLICY CHATBOT")
        print("="*60)
        print("I can answer questions about the financial policy document.")
        print("Type 'quit', 'exit', or 'bye' to end the conversation.")
        print("Type 'clear' to clear conversation history.")
        print("="*60)
        
        while True:
            try:
                question = input("\nYou: ").strip()
                
                if question.lower() in ['quit', 'exit', 'bye']:
                    print("Goodbye! Thank you for using the Financial Policy Chatbot.")
                    break
                
                if question.lower() == 'clear':
                    chatbot.memory.clear()
                    print("Conversation history cleared.")
                    continue
                
                if not question:
                    continue
                
                print("Thinking...", end=" ", flush=True)
                response = chatbot.ask_question(question)
                print("✅")  # Done thinking
                
                print(f"\nBot: {response['answer']}")
                
                if response['sources']:
                    print(f"\n📚 Sources (Page numbers):")
                    for i, source in enumerate(response['sources'], 1):
                        print(f"   {i}. Page {source['page']}: {source['content_preview']}")
                
                print("-" * 50)
                
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"\nError: {e}")
                continue
                
    except Exception as e:
        print(f"Failed to initialize chatbot: {e}")
        print("Please make sure you've run build_knowledge_base.py first.")

if __name__ == "__main__":
    main()