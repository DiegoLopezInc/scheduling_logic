import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from database import add_new_user


def setup_authenticator(config):
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        preauthorized=config['credentials']['usernames'].keys()
    )
    return authenticator, config


@st.dialog(" ", width='large')
def register_new_user(authenticator, config):
    try:
        email_of_registered_user, username_of_registered_user, name_of_registered_user = authenticator.register_user(pre_authorized=list(config['credentials']['usernames'].keys()), captcha=False, domains=["uncc.edu", "charlotte.edu"], merge_username_email=True)
        st.write('*Please make sure to use your uncc.edu or charlotte.edu email address*')
        if email_of_registered_user:
            add_new_user(config, email_of_registered_user, config['credentials']['usernames'][email_of_registered_user])
            st.success('User registered successfully')
            st.session_state['authentication_status'] = True
            st.session_state['name'] = name_of_registered_user
            st.session_state['username'] = email_of_registered_user
            st.rerun()
    except Exception as e:
        st.error(e)


def logout_user(_):
    print('Clearing!')
    keys_to_clear = [
        "events", 
        "username", 
        "name", 
        "authentication_status",
        "calendar",
        "event_names"
    ]
    for key in keys_to_clear:
        st.session_state.pop(key, None)
    st.rerun()




