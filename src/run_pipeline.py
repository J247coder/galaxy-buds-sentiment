"""Run clean -> sentiment -> database in one go (after collecting data)."""
import clean, sentiment, database

if __name__ == "__main__":
    clean.main()
    sentiment.main()
    database.main()
    print("Done. Now run:  streamlit run dashboard/app.py")
