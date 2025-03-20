import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import mysql.connector
import pandas as pd

title_selection=st.sidebar.selectbox('Select Option',['Interactive Visualization','Interactive Filtering Functionality'],index=0)

if title_selection=='Interactive Filtering Functionality':
 # Function to connect to MySQL and retrieve data
    def get_movies(duration, rating, vote_count,genre):
        try:
            conn = mysql.connector.connect(
                host = "gateway01.ap-southeast-1.prod.aws.tidbcloud.com",
                port = 4000,
                user = "S1JGjbu3NW9Qwsb.root",
                password = "Arqlcq2tfSdaevjy",
                database = "logeshwaran",
            )
            mycursor = conn.cursor()
            
            query = """
            SELECT movie, duration, rating, votes, genre FROM logeshwaran.imdb
            WHERE duration <= %s AND rating <= %s AND votes <= %s AND genre=%s
            """
            
            mycursor.execute(query, (duration, rating, vote_count, genre))
            results = mycursor.fetchall()
            
            mycursor.close()
            conn.close()
            
            return pd.DataFrame(results, columns=["Movie", "Duration (Mins)", "Rating", "Votes",'Genre'])
        
        except mysql.connector.Error as err:
            st.error(f"Error: {err}")
            return pd.DataFrame()

    # Streamlit UI
    st.title("Interactive Filtering Functionality of IMDB 2024 Movies Data")

    st.sidebar.header("Filtering Criteria")
    duration = st.sidebar.number_input("Select Duration (minutes)", min_value=0,max_value=363,step=60)
    rating = st.sidebar.slider("Select Rating", min_value=0,max_value=10,step=1)
    vote_count = st.sidebar.number_input("Select Votes", min_value=0, max_value=611000,step=10000)
    genre=st.sidebar.selectbox('Select Genre',['Action','Adventure','Crime','Documentary','Horror','Romance'])

    if st.sidebar.button("Fetch Movies"):
        df = get_movies(duration, rating, vote_count,genre)
        if not df.empty:
            st.write("### Movies Matching Criteria")
            st.dataframe(df)
        else:
            st.write("No movies found with the given criteria.")

if title_selection=='Interactive Visualization':
    # Load Data from TiDB Cloud

    def load_data(query):
        conn = mysql.connector.connect(
            host = "gateway01.ap-southeast-1.prod.aws.tidbcloud.com",
            port = 4000,
            user = "S1JGjbu3NW9Qwsb.root",
            password = "Arqlcq2tfSdaevjy",
            database = "logeshwaran",
        )
        cursor = conn.cursor()
        cursor.execute(query)
        data = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]  # Get column names
        conn.close()
        return pd.DataFrame(data, columns=columns)

    # Streamlit UI
    st.title("Interactive Visualization of IMDB 2024 Movies Data")

    # Top 10 Movies by Rating and Votes
    st.header("1. Top 10 Movies by Rating and Votes")
    top_movies = load_data("SELECT movie, rating, votes, genre FROM logeshwaran.imdb ORDER BY rating DESC, votes DESC LIMIT 10")
    st.dataframe(top_movies)

    # Genre Distribution
    st.header("2. Genre Distribution")
    genre_counts = load_data("SELECT Genre, COUNT(*) AS Count FROM imdb GROUP BY genre")
    fig, ax = plt.subplots()
    ax.bar(genre_counts["Genre"], genre_counts["Count"])
    ax.set_ylabel("Count")
    st.pyplot(fig)

    # Average Duration by Genre
    st.header("3. Average Duration by Genre")
    avg_duration = load_data("SELECT Genre, AVG(Duration) AS Avg_Duration FROM imdb GROUP BY Genre")
    fig, ax = plt.subplots()
    ax.barh(avg_duration["Genre"], avg_duration["Avg_Duration"])
    ax.set_xlabel("Duration (minutes)")
    st.pyplot(fig)

    # Voting Trends by Genre
    st.header("4. Voting Trends by Genre")
    avg_votes = load_data("SELECT Genre, AVG(Votes) AS Avg_Votes FROM imdb GROUP BY Genre")
    fig, ax = plt.subplots()
    ax.bar(avg_votes["Genre"], avg_votes["Avg_Votes"])
    ax.set_ylabel("Average Votes")
    st.pyplot(fig)

    # Rating Distribution
    st.header("5. Rating Distribution")
    ratings = load_data("SELECT Rating FROM imdb")
    fig, ax = plt.subplots()
    sns.histplot(ratings["Rating"], bins=20, kde=True, ax=ax)
    st.pyplot(fig)

    # Genre-Based Rating Leaders
    st.header("6. Genre-Based Rating Leaders")
    top_rated_per_genre = load_data("SELECT Genre, Movie, Rating FROM imdb WHERE (Genre, Rating) IN (SELECT Genre, MAX(Rating) FROM imdb GROUP BY Genre)")
    st.dataframe(top_rated_per_genre)

    # Most Popular Genres by Voting
    st.header("7. Most Popular Genres by Voting")
    votes_by_genre = load_data("SELECT Genre, SUM(Votes) AS Total_Votes FROM imdb GROUP BY Genre")
    fig, ax = plt.subplots()
    ax.pie(votes_by_genre["Total_Votes"], labels=votes_by_genre["Genre"], autopct='%1.1f%%')
    st.pyplot(fig)

    # Duration Extremes
    st.header("8. Duration Extremes (Shortest and Longest Movies)")
    shortest_movie = load_data("SELECT Movie, Duration,Genre FROM imdb ORDER BY Duration ASC LIMIT 1")
    longest_movie = load_data("SELECT Movie, Duration, Genre FROM imdb ORDER BY Duration DESC LIMIT 1")
    st.dataframe(pd.concat([shortest_movie, longest_movie]))

    # Ratings by Genre (Heatmap)
    st.header("9. Ratings by Genre")
    rating_heatmap = load_data("SELECT Genre, AVG(Rating) AS Average_Rating FROM imdb GROUP BY Genre")
    fig, ax = plt.subplots()
    sns.heatmap(rating_heatmap.set_index("Genre").T, annot=True, cmap='coolwarm', ax=ax)
    st.pyplot(fig)

    # Correlation Analysis
    st.header("10. Correlation Analysis Between Ratings and Votes")
    rating_votes = load_data("SELECT Votes, Rating FROM imdb")
    fig, ax = plt.subplots()
    sns.scatterplot(x=rating_votes["Votes"], y=rating_votes["Rating"], ax=ax)
    ax.set_xlabel("Votes")
    ax.set_ylabel("Rating")
    st.pyplot(fig)
