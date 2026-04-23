import pandas as pd
from sqlalchemy import create_engine, text
import streamlit as st
import hashlib

# READ CSV FILE
df = pd.read_csv(r"C:\Users\ragur\OneDrive\Documents\project assessment task\synthetic_client_queries.csv")

# DATABASE CONNECTION
engine = create_engine(
    'postgresql://postgres:******@localhost:5432/support_center_db'
)

# CREATE TABLE
create_table_query = text('''
CREATE TABLE IF NOT EXISTS support_queries_table(
    query_id SERIAL PRIMARY KEY,
    client_email TEXT,
    client_mobile TEXT,
    query_heading TEXT,
    query_description TEXT,
    status TEXT DEFAULT 'Open',
    date_raised TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_closed TIMESTAMP
)
''')

with engine.connect() as conn:
    conn.execute(create_table_query)
    conn.commit()


reading_data = pd.read_sql(
    'SELECT * FROM support_queries_table',
    engine
)

if reading_data.empty:

    if 'query_id' in df.columns:
        df = df.drop(columns=['query_id'])

    df.to_sql(
        'support_queries_table',
        engine,
        index=False,
        if_exists='append'
    )

# SESSION STATE
if 'page' not in st.session_state:
    st.session_state.page = 'login'


# LOGIN PAGE

if st.session_state.page == 'login':

    st.title('Client Query Management System')

    UserName = st.text_input('Enter UserName')

    Password = st.text_input(
        'Enter Password',
        type='password'
    )

    Role = st.selectbox(
        'Select Role',
        ['Client_Page', 'Support_Page'],
        index=None
    )

    if st.button('Login'):

        if UserName and Password and Role:

            hashlib_password = hashlib.sha256(
                Password.encode()
            ).hexdigest()

            st.success('Login Successful')

            st.session_state.page = Role

            st.rerun()

        else:
            st.error('Please Enter All Details')


# CLIENT PAGE

elif st.session_state.page == 'Client_Page':

    st.title('Client Query Submission Page')

    email = st.text_input('Enter Email')

    mobile_no = st.text_input('Enter Mobile Number')

    heading = st.text_input('Enter Query Heading')

    description = st.text_area('Enter Query Description')

    if st.button('Submit Query'):

        if email and mobile_no and heading and description:

            insert_query = text(f'''
            INSERT INTO support_queries_table
            (
                client_email,
                client_mobile,
                query_heading,
                query_description
            )

            VALUES
            (
                '{email}',
                '{mobile_no}',
                '{heading}',
                '{description}'
            )
            ''')

            with engine.connect() as conn:

                conn.execute(insert_query)

                conn.commit()

            st.success('Query Submitted Successfully')

        else:
            st.error('Please Fill All Details')

    st.divider()

    if st.button('Logout'):

        st.session_state.page = 'login'

        st.rerun()


# SUPPORT PAGE

elif st.session_state.page == 'Support_Page':

    st.title('Support Team Dashboard')

    # FILTER
    Filter_status = st.selectbox(
        'Filter By Status',
        ['All', 'Open', 'Closed']
    )

    if Filter_status == 'All':

        view_table = '''
        SELECT * FROM support_queries_table
        ORDER BY query_id
        '''

    else:

        view_table = f"""
        SELECT * FROM support_queries_table
        WHERE TRIM(LOWER(status))
        =
        TRIM(LOWER('{Filter_status}'))

        ORDER BY query_id
        """

    support_df = pd.read_sql(view_table, engine)

    st.dataframe(support_df)

    st.divider()

    # CLOSE QUERY
    st.subheader('Close Query')

    query_id = st.number_input(
        'Enter Query ID',
        min_value=1,
        step=1
    )

    if st.button('Close Query'):

        close_query = text(f'''
        UPDATE support_queries_table

        SET
            status='Closed',
            date_closed=CURRENT_TIMESTAMP

        WHERE query_id={query_id}
        ''')

        with engine.connect() as conn:

            conn.execute(close_query)

            conn.commit()

        st.success('Query Closed Successfully')

        st.rerun()

    st.divider()

    # LOGOUT
    if st.button('Logout'):

        st.session_state.page = 'login'

        st.rerun()