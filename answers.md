1. How I handled timezone conflicts

I mostly avoided timezone conflicts within the SQL database by storing temporal data as an INTEGER unix timestamp, which is then processed as readable date and times after retrieval. When adding guests, the script always checks whether the selected datetime will conflict with the guests' working hours. Only after clicking "Confirm Appointment, and before doing any manipulation queries, the python script checks whether the selected datetime will conflict with the session user's own working hours.

2. Database optimization

Currently I tried to optimize queries to the database by making connections automatically close by putting it inside a "with" block. Although some optimization can still be made by not checking if the database file and table exists on each connection.

3. Additional Features

Had this web application be turned into a real product. My first change for it will be compartmentalization of its features. Right now its every function is defined within a single python script, which when possible I will try to define single-run functions in separate scripts so that streamlit would not automatically re-read every single one each time it refreshes. I also plan to use relational databases in a more nuanced manner. Right now the user can see whether they are the person making the appointment or not, but they still cannot see the user making the appointments for them. Some attention will also be given to its security and portability, as right now I have not setup a Django authentication nor I had created the Flask API in order to access the database. In conclusion, mostly due to the limited time I am able to develop it, this scheduling application in its current state is mostly a prototype and demonstrator rather than a usable build.

4. Session Management

As of this current build, I setup the session auto-logout by only checking the time elapsed upon its page changes after a streamlit "st.rerun()". As I am still trying to fin a way to implement a non-blocking periodical session-time checking in streamlit.
