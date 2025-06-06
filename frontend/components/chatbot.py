"""
Interactive Chatbot Component for Solar Analysis Guidance
Provides step-by-step guidance for users through the analysis process
"""

import streamlit as st
from typing import List, Dict, Any
import json

class SolarAnalysisChatbot:
    """Interactive chatbot for guiding users through solar analysis"""
    
    def __init__(self):
        self.conversation_history = []
        self.current_step = "welcome"
        self.user_context = {}
        
    def initialize_chatbot(self):
        """Initialize chatbot state"""
        if 'chatbot_messages' not in st.session_state:
            st.session_state.chatbot_messages = [
                {
                    "role": "assistant",
                    "content": "👋 Welcome to Solar Analysis Assistant! I'm here to guide you through the solar rooftop analysis process. What would you like to know?",
                    "timestamp": "now"
                }
            ]
        
        if 'chatbot_visible' not in st.session_state:
            st.session_state.chatbot_visible = False
            
    def get_response(self, user_message: str) -> str:
        """Generate contextual response based on user message and current state"""
        user_message_lower = user_message.lower()
        
        # Analyze user intent and provide appropriate guidance
        if any(word in user_message_lower for word in ['start', 'begin', 'how to', 'help']):
            return self._get_getting_started_response()
        elif any(word in user_message_lower for word in ['upload', 'image', 'photo', 'picture']):
            return self._get_upload_guidance()
        elif any(word in user_message_lower for word in ['analyze', 'analysis', 'process']):
            return self._get_analysis_guidance()
        elif any(word in user_message_lower for word in ['3d', 'visualization', 'model']):
            return self._get_3d_guidance()
        elif any(word in user_message_lower for word in ['report', 'download', 'pdf']):
            return self._get_report_guidance()
        elif any(word in user_message_lower for word in ['location', 'coordinates', 'latitude', 'longitude']):
            return self._get_location_guidance()
        elif any(word in user_message_lower for word in ['panel', 'solar', 'type']):
            return self._get_panel_guidance()
        elif any(word in user_message_lower for word in ['cost', 'price', 'money', 'savings']):
            return self._get_financial_guidance()
        elif any(word in user_message_lower for word in ['error', 'problem', 'issue', 'not working']):
            return self._get_troubleshooting_guidance()
        else:
            return self._get_general_guidance()
    
    def _get_getting_started_response(self) -> str:
        return """🚀 Here's how to get started with your solar analysis:

**Step 1: Upload Image** 📸
Upload a high-quality satellite image of your roof (preferably from Google Earth or similar)

**Step 2: Set Location** 📍  
Enter your exact latitude and longitude coordinates

**Step 3: Configure System** ⚙️
Choose your panel type, electricity rate, and installation cost

**Step 4: Analyze** 🔍
Click the "Analyze Roof" button to start processing

**Step 5: Review Results** 📊
Explore the interactive dashboard and 3D visualization

Would you like detailed guidance on any specific step?"""

    def _get_upload_guidance(self) -> str:
        return """📸 **Image Upload Guidelines:**

**Best Image Sources:**
• Google Earth (satellite view)
• Google Maps (satellite mode)
• Local GIS systems
• Professional drone photography

**Image Requirements:**
• High resolution (minimum 1024x1024 pixels)
• Clear roof visibility
• Minimal cloud cover
• Recent imagery preferred

**Supported Formats:** JPG, PNG, JPEG

**Tips for Best Results:**
• Zoom in close enough to see roof details clearly
• Ensure the entire roof is visible in the image
• Avoid images with heavy shadows or obstructions

Ready to upload your image?"""

    def _get_analysis_guidance(self) -> str:
        return """🔍 **Analysis Process Explained:**

**Analysis Modes Available:**
• **Standard Analysis**: Basic roof detection using computer vision
• **Professional Assessment**: Comprehensive analysis with AI recommendations

**What Happens During Analysis:**
1. **Roof Detection** - AI identifies your roof area and boundaries
2. **Solar Data** - Retrieves authentic NASA solar irradiance data
3. **Financial Modeling** - Calculates ROI, savings, and payback period
4. **AI Recommendations** - Generates optimal system configuration

**Processing Time:** 30 seconds - 2 minutes depending on mode

**Requirements Before Analysis:**
✅ Image uploaded
✅ Location coordinates set
✅ System parameters configured

Click "Analyze Roof" when ready!"""

    def _get_3d_guidance(self) -> str:
        return """🎯 **3D Visualization Features:**

**Interactive 3D Model:**
• Realistic roof reconstruction from your image
• Solar panel placement simulation
• Sun path visualization throughout the day
• Shading analysis with adjustable time controls

**Available Controls:**
• Rotate and zoom the 3D model
• Toggle panel visibility
• Adjust sun position by time of day
• View seasonal shading patterns

**Export Options:**
• Download 3D model files
• Generate high-resolution renderings
• Save optimal panel configurations

The 3D visualization appears after completing your roof analysis. It helps you visualize exactly how solar panels would look on your specific roof!"""

    def _get_report_guidance(self) -> str:
        return """📋 **Professional Report Generation:**

**Report Contents:**
• Executive summary with key findings
• Detailed technical analysis
• Financial projections and ROI calculations
• AI-generated recommendations
• 3D visualizations and diagrams

**Available Formats:**
• PDF Professional Report
• Technical Specification Sheet
• Financial Analysis Summary

**When to Generate:**
Reports are available after completing your roof analysis. You'll find the "Generate Report" button in the results section.

**Uses for Reports:**
• Share with contractors and installers
• Apply for solar incentives and permits
• Present to family or decision makers
• Keep for your records

Would you like me to guide you through the analysis process to get your report?"""

    def _get_location_guidance(self) -> str:
        return """📍 **Location Setup Instructions:**

**Finding Your Coordinates:**
1. Go to Google Maps
2. Right-click on your exact roof location
3. Copy the latitude and longitude numbers
4. Enter them in the configuration panel

**Example Format:**
• Latitude: 37.7749 (North is positive)
• Longitude: -122.4194 (West is negative)

**Why Location Matters:**
• Determines solar irradiance data
• Calculates optimal panel angles
• Identifies local regulations and incentives
• Provides accurate sun path modeling

**Accuracy is Important:**
The more precise your coordinates, the more accurate your solar analysis will be. Try to pinpoint your exact roof location rather than just your address."""

    def _get_panel_guidance(self) -> str:
        return """⚡ **Solar Panel Configuration:**

**Panel Types Available:**
• **Monocrystalline**: Higher efficiency, premium option
• **Polycrystalline**: Good balance of cost and performance  
• **Thin Film**: Lower cost, flexible installation

**Key Parameters to Set:**
• **Panel Type**: Affects efficiency calculations
• **Electricity Rate**: Your current cost per kWh
• **Installation Cost**: Price per watt for your area

**Getting Accurate Costs:**
• Check recent utility bills for your electricity rate
• Get quotes from local installers for installation costs
• Consider local incentives and rebates

**System Sizing:**
The analysis will automatically calculate optimal system size based on your roof area and energy needs."""

    def _get_financial_guidance(self) -> str:
        return """💰 **Financial Analysis Breakdown:**

**What We Calculate:**
• **ROI**: Return on investment percentage
• **Payback Period**: Years to recover initial investment
• **25-Year Savings**: Total savings over system lifetime
• **Monthly Savings**: Reduction in electricity bills

**Factors Considered:**
• System installation cost
• Federal and local incentives
• Net metering policies
• Electricity rate escalation
• System degradation over time

**Accuracy Notes:**
Our calculations use real NASA solar data and current federal incentive rates. Local incentives may vary - consult with local installers for the most current information.

**Next Steps After Analysis:**
Use the financial projections to compare quotes from installers and make informed decisions about your solar investment."""

    def _get_troubleshooting_guidance(self) -> str:
        return """🔧 **Troubleshooting Common Issues:**

**Image Upload Problems:**
• Ensure file is under 5MB
• Use JPG, PNG, or JPEG format
• Check image quality and resolution

**Analysis Not Starting:**
• Verify image is uploaded
• Check that coordinates are entered
• Ensure all required fields are filled

**Slow Processing:**
• Large images take longer to process
• Professional Assessment mode requires more time
• Please wait for completion before refreshing

**Unexpected Results:**
• Verify your coordinates are accurate
• Check image quality shows roof clearly
• Ensure electricity rate is correct

**Still Having Issues?**
• Try refreshing the page and starting over
• Check your internet connection
• Contact support if problems persist

What specific issue are you experiencing?"""

    def _get_general_guidance(self) -> str:
        responses = [
            "I'm here to help you with your solar analysis! You can ask me about uploading images, setting up your location, understanding the analysis process, or interpreting your results.",
            "Feel free to ask about any step in the solar analysis process. I can guide you through image upload, configuration, analysis, and report generation.",
            "I can help with questions about solar panels, financial calculations, 3D visualization, or troubleshooting any issues you encounter.",
            "What aspect of the solar analysis would you like to know more about? I'm here to make the process as smooth as possible!"
        ]
        import random
        return random.choice(responses)

    def render_chatbot_interface(self):
        """Render the chatbot interface with custom styling"""
        # CSS for chatbot styling
        st.markdown("""
        <style>
        .chatbot-container {
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            z-index: 1000;
        }
        
        .chatbot-toggle {
            background: linear-gradient(135deg, #3b82f6 0%, #1e3a8a 100%);
            color: white;
            border: none;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            font-size: 1.5rem;
            cursor: pointer;
            box-shadow: 0 8px 25px rgba(59, 130, 246, 0.3);
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            animation: pulse-glow 3s infinite;
        }
        
        @keyframes pulse-glow {
            0%, 100% { box-shadow: 0 8px 25px rgba(59, 130, 246, 0.3); }
            50% { box-shadow: 0 8px 35px rgba(59, 130, 246, 0.5); }
        }
        
        .chatbot-toggle:hover {
            transform: scale(1.1);
            box-shadow: 0 12px 35px rgba(59, 130, 246, 0.4);
        }
        
        .chatbot-panel {
            position: fixed;
            bottom: 100px;
            right: 2rem;
            width: 350px;
            height: 500px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.15);
            display: flex;
            flex-direction: column;
            overflow: hidden;
            border: 1px solid #e5e7eb;
        }
        
        .chatbot-header {
            background: linear-gradient(135deg, #3b82f6 0%, #1e3a8a 100%);
            color: white;
            padding: 1rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        .chatbot-messages {
            flex: 1;
            overflow-y: auto;
            padding: 1rem;
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
        }
        
        .message {
            max-width: 85%;
            padding: 0.75rem 1rem;
            border-radius: 18px;
            font-size: 0.9rem;
            line-height: 1.4;
            animation: messageSlide 0.3s ease-out;
        }
        
        @keyframes messageSlide {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .message.bot {
            background: #f3f4f6;
            color: #1f2937;
            align-self: flex-start;
            border-bottom-left-radius: 6px;
        }
        
        .message.user {
            background: #3b82f6;
            color: white;
            align-self: flex-end;
            border-bottom-right-radius: 6px;
        }
        
        .chatbot-input-container {
            padding: 1rem;
            border-top: 1px solid #e5e7eb;
            background: #f9fafb;
        }
        
        @media (max-width: 768px) {
            .chatbot-panel {
                width: 300px;
                height: 400px;
                right: 1rem;
                bottom: 80px;
            }
            
            .chatbot-container {
                bottom: 1rem;
                right: 1rem;
            }
        }
        </style>
        """, unsafe_allow_html=True)

        # Chatbot toggle button
        col1, col2, col3 = st.columns([8, 1, 1])
        with col3:
            if st.button("💬", key="chatbot_toggle", help="Open Solar Assistant", 
                        use_container_width=True):
                st.session_state.chatbot_visible = not st.session_state.chatbot_visible

        # Chatbot panel
        if st.session_state.chatbot_visible:
            with st.container():
                st.markdown("""
                <div class="chatbot-panel">
                    <div class="chatbot-header">
                        <h3 style="margin: 0; font-size: 1.1rem;">🌞 Solar Assistant</h3>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Messages container
                messages_container = st.container()
                with messages_container:
                    for message in st.session_state.chatbot_messages:
                        if message["role"] == "assistant":
                            st.markdown(f"""
                            <div class="message bot">
                                {message["content"]}
                            </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                            <div class="message user">
                                {message["content"]}
                            </div>
                            """, unsafe_allow_html=True)
                
                # Input area
                with st.container():
                    user_input = st.text_input(
                        "Ask me anything about solar analysis...",
                        key="chatbot_input",
                        placeholder="Type your question here...",
                        label_visibility="collapsed"
                    )
                    
                    col1, col2 = st.columns([4, 1])
                    with col2:
                        if st.button("Send", key="send_message", type="primary") and user_input:
                            # Add user message
                            st.session_state.chatbot_messages.append({
                                "role": "user",
                                "content": user_input,
                                "timestamp": "now"
                            })
                            
                            # Generate bot response
                            bot_response = self.get_response(user_input)
                            st.session_state.chatbot_messages.append({
                                "role": "assistant", 
                                "content": bot_response,
                                "timestamp": "now"
                            })
                            
                            # Clear input
                            st.session_state.chatbot_input = ""
                            st.rerun()

    def add_contextual_message(self, step: str, additional_info: str = ""):
        """Add contextual guidance message based on current step"""
        messages = {
            "image_uploaded": "Great! I see you've uploaded an image. Next, make sure to set your exact location coordinates for accurate solar data.",
            "location_set": "Perfect! Location configured. Now set your system parameters like panel type and electricity rate, then click 'Analyze Roof'.",
            "analysis_started": "Analysis in progress! I'm processing your roof image and gathering solar data. This usually takes 30-60 seconds.",
            "analysis_complete": "Excellent! Your analysis is complete. You can now explore the interactive dashboard, view the 3D model, and generate your professional report.",
            "error_occurred": f"I noticed an issue: {additional_info}. Let me help you resolve this quickly."
        }
        
        if step in messages:
            st.session_state.chatbot_messages.append({
                "role": "assistant",
                "content": messages[step],
                "timestamp": "now"
            })

    def get_quick_actions(self) -> List[str]:
        """Get quick action buttons based on current state"""
        actions = []
        
        if 'uploaded_file' not in st.session_state or st.session_state.uploaded_file is None:
            actions.append("How to upload image?")
        
        if 'latitude' not in st.session_state or not st.session_state.latitude:
            actions.append("How to set location?")
            
        if 'analysis_results' not in st.session_state:
            actions.append("Start analysis process")
        else:
            actions.append("Explain my results")
            actions.append("Generate report")
            
        return actions[:3]  # Limit to 3 quick actions