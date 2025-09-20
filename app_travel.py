import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from langchain.memory import ConversationBufferMemory
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load your OpenAI API key from environment variables or Streamlit secrets
openai_api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")

# Initialize Chat Model
chat = ChatOpenAI(
    temperature=0.7,
    openai_api_key=openai_api_key,
    model="gpt-4o-mini"  # or gpt-3.5-turbo
)

# App Configuration
st.set_page_config(
    page_title="Malaysia Travel Planner - LeafletBot", 
    page_icon="🇲🇾", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Malaysia Theme
st.markdown("""
<style>
    /* Main background - Malaysia flag colors inspired */
    .main {
        background: linear-gradient(135deg, #CC0001 0%, #FFFFFF 50%, #010066 100%);
    }
    
    /* Sidebar styling - Malaysian nature colors */
    .css-1d391kg {
        background: linear-gradient(180deg, #228B22 0%, #006400 100%);
    }
    
    /* Chat messages styling */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    
    /* Header styling */
    .travel-header {
        background: linear-gradient(90deg, #FF6B6B, #4ECDC4, #45B7D1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    /* Travel banner */
    .travel-banner {
        background: linear-gradient(45deg, #FF9A8B, #A8E6CF);
        padding: 20px;
        border-radius: 15px;
        margin: 20px 0;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 10px 20px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        border-radius: 25px;
        border: 2px solid #4ECDC4;
    }
</style>
""", unsafe_allow_html=True)

# Malaysia Travel Header with Banner
st.markdown('<h1 class="travel-header">🇲🇾 Malaysia Travel Planner</h1>', unsafe_allow_html=True)
st.markdown("""
<div class="travel-banner">
    <h3> Discover Malaysia with AI </h3>
    <p>Your intelligent guide to exploring Peninsular & East Malaysia - from KL's skyline to Borneo's rainforests!</p>
</div>
""", unsafe_allow_html=True)

# Initialize conversation memory
if "memory" not in st.session_state:
    st.session_state.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# # Malaysia Travel Sidebar
# with st.sidebar:
#     st.markdown("""
#     <div style="background: linear-gradient(45deg, #CC0001, #010066); padding: 15px; border-radius: 10px; margin-bottom: 20px;">
#         <h3 style="color: white; margin: 0;">🇲🇾 Malaysia Travel Planner</h3>
#     </div>
#     """, unsafe_allow_html=True)
    
#     st.markdown("""
#     ### 🎯 **What I Can Plan For You:**
#     - **🗺️ Multiple Itineraries** - At least 2 different options
#     - **💰 Budget Breakdown** - Cost per person analysis
#     - **🚌 Transport Options** - Flights, buses, trains within Malaysia
#     - **🏨 Accommodation** - From budget to luxury stays
#     - **🍜 Food Experiences** - Must-try Malaysian cuisine
#     - **🎭 Cultural Activities** - Festivals, temples, heritage sites
    
#     ### 🏝️ **Malaysian Regions:**
#     - **🏙️ Peninsular Malaysia**
#       - Kuala Lumpur & Selangor
#       - Penang (Georgetown)
#       - Malacca (Historical)
#       - Pahang (Cameron Highlands)
#       - Johor (Legoland)
#       - Perak, Kedah, Terengganu
    
#     - **🌳 East Malaysia (Borneo)**
#       - Sabah (Mount Kinabalu)
#       - Sarawak (Kuching)
#       - Labuan
    
#     ### 🏖️ **Travel Themes:**
#     - 🏖️ **Coastal** - Langkawi, Tioman, Perhentian
#     - 🎉 **Holiday/Festival** - CNY, Hari Raya, Deepavali
#     - 👨‍👩‍👧‍👦 **Kids Friendly** - Theme parks, zoos, interactive museums
#     - 🏛️ **Cultural** - Heritage sites, temples, museums
#     - 🌿 **Nature** - National parks, highlands, wildlife
#     - 🍜 **Food Tours** - Street food, local markets
#     """)
    
    # Input Collection Section
    st.markdown("---")
    st.markdown("### 📋 **Quick Planning Form:**")
    
    # Store form data in session state
    if 'form_data' not in st.session_state:
        st.session_state.form_data = {}
    
    with st.form("malaysia_travel_form"):
        starting_destination = st.text_input(
            "🛫 Starting From (City/Country):",
            placeholder="e.g., Kuala Lumpur, Singapore, Bangkok"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            budget_per_pax = st.number_input(
                "💰 Budget per Person (MYR):",
                min_value=100,
                max_value=10000,
                value=1000,
                step=100
            )
        
        with col2:
            duration = st.number_input(
                "📅 Duration (Days):",
                min_value=1,
                max_value=30,
                value=5,
                step=1
            )
        
        travel_preferences = st.multiselect(
            "🎯 Travel Preferences:",
            ["Coastal/Beach", "Cultural/Heritage", "Nature/Wildlife", 
             "Food Tour", "Kids Friendly", "Adventure Sports", 
             "Shopping", "Nightlife", "Photography", "Budget Travel"]
        )
        
        additional_notes = st.text_area(
            "📝 Additional Requirements:",
            placeholder="Any specific places you want to visit, dietary restrictions, mobility needs, etc."
        )
        
        submitted = st.form_submit_button("🗺️ Generate Malaysia Itineraries", use_container_width=True)
        
        if submitted:
            st.session_state.form_data = {
                'starting_destination': starting_destination,
                'budget_per_pax': budget_per_pax,
                'duration': duration,
                'preferences': travel_preferences,
                'additional_notes': additional_notes
            }
            
            # Create structured prompt for Malaysia itinerary
            structured_prompt = f"""
Create detailed Malaysia travel itineraries with these requirements:

**Trip Details:**
- Starting from: {starting_destination}
- Budget per person: MYR {budget_per_pax}
- Duration: {duration} days
- Preferences: {', '.join(travel_preferences) if travel_preferences else 'General sightseeing'}
- Additional notes: {additional_notes if additional_notes else 'None'}

**Provide AT LEAST 2 different itinerary options** with complete details including:
1. Day-by-day breakdown
2. Transportation costs within Malaysia
3. Accommodation recommendations
4. Food suggestions
5. Activity costs
6. Total budget breakdown

Focus only on destinations within Malaysia (Peninsular Malaysia and East Malaysia/Borneo).
"""
            
            # Add to chat
            if 'messages' not in st.session_state:
                st.session_state.messages = []
            
            st.session_state.messages.append({"role": "user", "content": structured_prompt})
            st.rerun()

    st.markdown("---")
    
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.memory.clear()
        if 'form_data' in st.session_state:
            del st.session_state.form_data
        st.rerun()
    
    st.markdown("""
    ### 🇲🇾 **Malaysia Quick Facts:**
    - **Currency**: Malaysian Ringgit (MYR)
    - **Languages**: Bahasa Malaysia, English
    - **Climate**: Tropical, hot & humid year-round
    - **Best Time**: Dry season varies by region
    - **Visa**: Many countries get visa-free entry
    
    <div style="background: rgba(255,255,255,0.1); padding: 10px; border-radius: 8px; margin-top: 20px;">
        <p style="font-size: 12px; color: #666; margin: 0;">🇲🇾 Discover Malaysia - Truly Asia!</p>
    </div>
    """, unsafe_allow_html=True)


# Malaysia-Specific Travel System Prompt
system_prompt = SystemMessage(
    content="""
You are Malaysia Travel Planner, an expert travel agent specializing EXCLUSIVELY in Malaysia tourism.

## Your Expertise Area:
**ONLY MALAYSIA** - You plan trips within Malaysia only (Peninsular Malaysia and East Malaysia/Borneo).

## Core Mission:
Create detailed Malaysia travel itineraries that showcase the country's diversity - from bustling KL to pristine Borneo rainforests.

## MANDATORY Requirements:
1. **Always provide AT LEAST 2 different itinerary options** for any request
2. **Focus ONLY on destinations within Malaysia**
3. **Include costs in Malaysian Ringgit (MYR)**
4. **Consider domestic transportation** (flights, buses, trains, ferries within Malaysia)

## For Malaysia Itineraries, Use This Structure:

### **ITINERARY OPTION 1: [Theme Name]**
1. ** Overview**: Theme, highlights, total cost per person
2. ** Getting There**: From starting point to first Malaysian destination
3. ** Accommodation**: Specific hotel/hostel recommendations with prices
4. ** Day-by-Day Plan**: 
   - Day 1: Location, activities, meals, costs
   - Day 2: Location, activities, meals, costs
   - [Continue for all days]
5. ** Transportation**: Domestic travel costs (flights, buses, trains)
6. ** Food Highlights**: Must-try Malaysian dishes and where to find them
7. ** Total Budget**: Complete breakdown per person

### **ITINERARY OPTION 2: [Alternative Theme Name]**
[Same structure as Option 1]

## Malaysia Regions to Consider:

**Peninsular Malaysia:**
- Kuala Lumpur & Selangor (KLCC, Batu Caves, Putrajaya)
- Penang (Georgetown, food scene)
- Malacca (Historical sites)
- Cameron Highlands (Tea plantations, cool weather)
- Langkawi (Beaches, duty-free)
- Johor (Legoland, city attractions)
- Pahang (Tioman Island, Genting Highlands)
- Kelantan, Terengganu (East Coast beaches, culture)
- Perak (Ipoh, heritage towns)
- Kedah (Alor Setar, rice fields)

**East Malaysia (Borneo):**
- Sabah (Kota Kinabalu, Mount Kinabalu, Semporna)
- Sarawak (Kuching, Miri, longhouses)
- Labuan (Duty-free island)

## Travel Themes to Offer:
-  **Coastal/Beach**: Langkawi, Tioman, Perhentian, Redang
-  **Cultural/Heritage**: KL, Penang, Malacca, Sarawak longhouses
-  **Nature/Wildlife**: Borneo, Taman Negara, Cameron Highlands
-  **Food Tour**: Penang, KL, Ipoh, Kuching
-  **Kids Friendly**: Legoland, Sunway Lagoon, Zoo Negara, Aquaria KLCC
-  **Adventure**: Mount Kinabalu, white water rafting, jungle trekking

## Budget Considerations (MYR per person per day):
- **Budget**: RM 80-150 (hostels, street food, public transport)
- **Mid-range**: RM 150-300 (hotels, mix of local/restaurant food)
- **Luxury**: RM 300+ (high-end hotels, fine dining)

## Key Guidelines:
- **Malaysia Only**: Never suggest destinations outside Malaysia
- **Multiple Options**: Always provide at least 2 different itineraries
- **Practical Details**: Include specific costs, transport schedules, booking tips
- **Cultural Sensitivity**: Respect Malaysia's multicultural society (Malay, Chinese, Indian, indigenous)
- **Seasonal Awareness**: Consider monsoons, festivals (CNY, Hari Raya, Deepavali)
- **Local Experiences**: Street food, night markets, cultural festivals

## Currency & Costs:
- All prices in Malaysian Ringgit (MYR)
- Include domestic flight costs (KL-Kota Kinabalu ~RM 200-400)
- Bus costs (KL-Penang ~RM 35-50)
- Accommodation ranges clearly stated

## Safety & Cultural Notes:
- Malaysia is generally safe for tourists
- Respect religious customs (mosque visits, Ramadan)
- Halal food considerations
- Language: Bahasa Malaysia, English widely spoken
- Tipping: Not mandatory but appreciated
"""
)

def create_conversational_response(user_input, memory):
    # Get conversation history
    chat_history = memory.chat_memory.messages
    
    # Build messages for the API call
    messages = [system_prompt] + chat_history + [HumanMessage(content=user_input)]
    
    # Get response from OpenAI
    response = chat(messages)
    
    # Store in memory
    memory.chat_memory.add_user_message(user_input)
    memory.chat_memory.add_ai_message(response.content)
    
    return response.content

# Initialize chat messages
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant", 
            "content": "🇲🇾 Selamat datang! I'm your Malaysia Travel Planner! \n\nI specialize exclusively in creating amazing travel experiences within Malaysia - from the bustling streets of Kuala Lumpur to the pristine rainforests of Borneo! 🏙️🌳\n\n**Here's how I can help you:**\n- 🗺️ **Multiple Itinerary Options** - I'll always give you at least 2 different plans\n- 💰 **Budget Planning** - Detailed costs in Malaysian Ringgit (MYR)\n- 🏝️ **Regional Expertise** - Peninsular Malaysia & East Malaysia (Borneo)\n- 🎯 **Theme-based Travel** - Coastal, cultural, nature, food tours, kids-friendly\n\n**Quick Start Options:**\n1. 📋 **Use the sidebar form** for structured planning\n2. 💬 **Chat with me directly** - 'Plan a 5-day trip to Malaysia for RM 2000 per person'\n\n**Popular Malaysia Experiences:**\n- 🏖️ Island hopping in Langkawi\n- 🍜 Street food tours in Penang\n- 🏛️ Historical exploration in Malacca\n- 🦧 Wildlife adventures in Borneo\n- 🏔️ Cool highlands in Cameron Highlands\n\nWhat kind of Malaysian adventure are you dreaming of?"
        }
    ]

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

    # Chat input
if prompt := st.chat_input("Ask me about Malaysia travel or describe your dream Malaysian adventure... 🇲🇾"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate assistant response
    with st.chat_message("assistant"):
        with st.spinner("🌱 Planning your sustainable adventure..."):
            try:
                response = create_conversational_response(prompt, st.session_state.memory)
                st.markdown(response)
                
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response})
                
            except Exception as e:
                error_msg = "🚨 Oops! I encountered an issue while planning your Malaysia trip. Please make sure your OpenAI API key is configured correctly and try again!\n\n💡 **Tip**: You can also use the Quick Planning Form in the sidebar for structured itinerary generation."
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
