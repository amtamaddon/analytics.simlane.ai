# ============================================================================
# SMS NOTIFICATION SYSTEM WITH HARDCODED CREDENTIALS
# ============================================================================

# Import Twilio (install with: pip install twilio)
try:
    from twilio.rest import Client as TwilioClient
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    print("⚠️  Twilio not installed. Run: pip install twilio")

import os

class SMSManager:
    def __init__(self):
        self.client = None
        self.from_number = None
        
        # HARDCODED TWILIO CREDENTIALS (replace with your actual credentials)
        HARDCODED_ACCOUNT_SID = "SK39d6808bf645f5c2588faa74cb48c3fd"
        HARDCODED_AUTH_TOKEN = "rh0cuRyyCztVX4tMEZyhfdfjlyqWcolh" 
        HARDCODED_FROM_NUMBER = "+1234567890"  # Your Twilio phone number
        
        # Try to initialize Twilio client
        if TWILIO_AVAILABLE:
            try:
                # First try hardcoded credentials
                if HARDCODED_ACCOUNT_SID != "your_account_sid_here":
                    self.client = TwilioClient(HARDCODED_ACCOUNT_SID, HARDCODED_AUTH_TOKEN)
                    self.from_number = HARDCODED_FROM_NUMBER
                    print("✅ Twilio initialized with hardcoded credentials")
                
                # Fallback to Streamlit secrets
                elif 'twilio' in st.secrets:
                    account_sid = st.secrets['twilio']['account_sid']
                    auth_token = st.secrets['twilio']['auth_token']
                    self.from_number = st.secrets['twilio'].get('from_number', '+1234567890')
                    self.client = TwilioClient(account_sid, auth_token)
                    print("✅ Twilio initialized with Streamlit secrets")
                
                # Fallback to environment variables
                elif all(k in os.environ for k in ['TWILIO_ACCOUNT_SID', 'TWILIO_AUTH_TOKEN']):
                    account_sid = os.environ['TWILIO_ACCOUNT_SID']
                    auth_token = os.environ['TWILIO_AUTH_TOKEN']
                    self.from_number = os.environ.get('TWILIO_FROM_NUMBER', '+1234567890')
                    self.client = TwilioClient(account_sid, auth_token)
                    print("✅ Twilio initialized with environment variables")
                
                else:
                    print("❌ No Twilio credentials found. Please configure hardcoded credentials.")
                    
            except Exception as e:
                print(f"❌ Failed to initialize Twilio: {str(e)}")
                if hasattr(st, 'error'):
                    st.error(f"Failed to initialize Twilio: {str(e)}")
        else:
            print("❌ Twilio library not available. Install with: pip install twilio")
    
    def send_sms(self, to_number, message):
        """Send an SMS message using Twilio."""
        if not TWILIO_AVAILABLE:
            return False, "Twilio library not installed. Run: pip install twilio"
        
        if not self.client:
            return False, "Twilio client not initialized. Please configure credentials."
        
        try:
            # Clean phone number format
            if not to_number.startswith('+'):
                to_number = '+1' + to_number.replace('-', '').replace('(', '').replace(')', '').replace(' ', '')
            
            message_obj = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_number
            )
            return True, f"Message sent successfully! SID: {message_obj.sid}"
        except Exception as e:
            return False, f"Failed to send SMS: {str(e)}"
    
    def send_risk_alert(self, phone_number, member_id, risk_level, days_to_churn):
        """Send a risk alert SMS for a specific member."""
        message = f"🚨 SIMLANE ALERT: Member {member_id} is at {risk_level} risk of churning in {days_to_churn} days. Take action now!"
        return self.send_sms(phone_number, message)
    
    def send_test_message(self, phone_number):
        """Send a test SMS message."""
        message = "🎯 Simlane.ai Test Message: Your SMS notifications are working correctly!"
        return self.send_sms(phone_number, message)
    
    def get_account_info(self):
        """Get Twilio account information to verify connection."""
        if not self.client:
            return None
        
        try:
            account = self.client.api.accounts(self.client.account_sid).fetch()
            return {
                'friendly_name': account.friendly_name,
                'status': account.status,
                'type': account.type,
                'sid': account.sid[:8] + '...'  # Only show first 8 chars for security
            }
        except Exception as e:
            return {'error': str(e)}

# Initialize SMS manager
sms_manager = SMSManager()

# ============================================================================
# INSTALLATION SCRIPT
# ============================================================================

def install_twilio():
    """Install Twilio package if not available."""
    import subprocess
    import sys
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "twilio"])
        print("✅ Twilio installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Twilio: {e}")
        return False

# ============================================================================
# CONFIGURATION HELPER
# ============================================================================

def setup_twilio_credentials():
    """Helper function to set up Twilio credentials."""
    print("""
    🔧 TWILIO SETUP INSTRUCTIONS:
    
    1. Get your Twilio credentials:
       - Go to https://console.twilio.com
       - Find your Account SID and Auth Token
       - Get a Twilio phone number
    
    2. Update the hardcoded credentials in SMSManager.__init__():
       HARDCODED_ACCOUNT_SID = "your_actual_account_sid"
       HARDCODED_AUTH_TOKEN = "your_actual_auth_token"
       HARDCODED_FROM_NUMBER = "+1your_twilio_number"
    
    3. Alternative setup methods:
    
       A) Streamlit secrets (.streamlit/secrets.toml):
       [twilio]
       account_sid = "your_account_sid"
       auth_token = "your_auth_token"
       from_number = "+1234567890"
       
       B) Environment variables:
       export TWILIO_ACCOUNT_SID="your_sid"
       export TWILIO_AUTH_TOKEN="your_token"
       export TWILIO_FROM_NUMBER="+1234567890"
    """)

# ============================================================================
# TESTING FUNCTIONS
# ============================================================================

def test_sms_functionality():
    """Test SMS functionality with hardcoded credentials."""
    print("🧪 Testing SMS functionality...")
    
    if not TWILIO_AVAILABLE:
        print("❌ Twilio not installed. Run: pip install twilio")
        return False
    
    # Test account info
    account_info = sms_manager.get_account_info()
    if account_info and 'error' not in account_info:
        print(f"✅ Twilio account connected: {account_info}")
    else:
        print(f"❌ Twilio connection failed: {account_info}")
        return False
    
    # Test message (you'll need to provide a real phone number)
    test_phone = "+1234567890"  # Replace with your phone number for testing
    success, message = sms_manager.send_test_message(test_phone)
    
    if success:
        print(f"✅ Test SMS sent: {message}")
        return True
    else:
        print(f"❌ Test SMS failed: {message}")
        return False

# Run setup instructions
if __name__ == "__main__":
    if not TWILIO_AVAILABLE:
        print("Installing Twilio...")
        install_twilio()
    else:
        setup_twilio_credentials()
        
    # Uncomment to run test (after setting up credentials)
    # test_sms_functionality()
