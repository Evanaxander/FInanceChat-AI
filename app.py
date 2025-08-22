import streamlit as st
import sys
import os

# Adding src to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

#Importing the updated FinancialPolicyChatbot
from src.financial_chatbot import FinancialPolicyChatbot

def main():
    st.set_page_config(
        page_title="Financial Policy Chatbot",
        page_icon="💬",
        layout="wide"
    )
    
    st.title("💬 Financial Policy Chatbot")
    st.markdown("Ask questions about the financial policy document")
    
    # if statement to initialize chatbot
    if "chatbot" not in st.session_state:
        st.session_state.chatbot = FinancialPolicyChatbot()
        try:
            st.session_state.chatbot.initialize_chatbot()
            st.session_state.initialized = True
            st.success("Chatbot initialized successfully!")
        except Exception as e:
            st.error(f"Failed to initialize chatbot: {e}")
            st.info("Please run build_knowledge_base.py first to process the PDF.")
            st.session_state.initialized = False
            return
    
    #Initializing the chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    #Displaying chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "sources" in message and message["sources"]:
                with st.expander("View Sources"):
                    for source in message["sources"]:
                        st.markdown(f"**Page {source['page']}:** {source['content_preview']}")
    
    #Adding sidebar with information and controls so that its easier forthe user
    with st.sidebar:
        st.header("About")
        st.markdown("""
        This chatbot can answer questions about the financial policy document.
        
        **Features:**
        - Answers questions based on the policy document
        - Shows source page references
        - Maintains conversation context
        """)
        
        # Clear conversation button to resset and restart
        if st.button("Clear Conversation"):
            st.session_state.messages = []
            st.session_state.chatbot.memory.clear()
            st.success("Conversation cleared!")
            st.rerun()
    
    #Input for the chat option
    if prompt := st.chat_input("Ask a question about the financial policy..."):
        #this adds user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        #displaying user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        #receive chat bot response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = st.session_state.chatbot.ask_question(prompt)
                    st.markdown(response["answer"])
                    
                    if response["sources"]:
                        with st.expander("Sources Referenced"):
                            for i, source in enumerate(response["sources"], 1):
                                st.markdown(f"**{i}. Page {source['page']}:**")
                                st.markdown(f"*{source['content_preview']}*")
                                st.markdown("---")
                    
                    #Add assistant response to chat history
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": response["answer"],
                        "sources": response["sources"]
                    })
                    
                except Exception as e:
                    error_msg = f"Sorry, I encountered an error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": error_msg,
                        "sources": []
                    })

if __name__ == "__main__":
    main()