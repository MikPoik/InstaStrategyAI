
# Instagram Marketing Manager AI

A Streamlit-based web application that analyzes Instagram profiles and provides AI-powered marketing recommendations.

## Features

- Profile Analysis: Analyze Instagram profiles including followers, engagement rates, and posting patterns
- Content Planning: Generate AI-powered content plans for optimal engagement
- Strategy Recommendations: Get actionable recommendations to improve account performance
- Similar Account Analysis: Discover and analyze similar accounts in your niche
- Visual Analytics: View engagement metrics and posting schedules through interactive charts

## Setup

1. Set up required environment variables:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `HIKERAPI_TOKEN`: Your HikerAPI token
   - `DATABASE_URL`: PostgreSQL database URL
   - `INSTAGRAM_USERNAME`: Instagram username (optional)
   - `INSTAGRAM_PASSWORD`: Instagram password (optional)

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run database migrations:
   ```bash
   ./run_migrations.sh
   ```

4. Start the application:
   ```bash
   streamlit run main.py --server.port 5000
   ```

## Project Structure

- `main.py`: Main Streamlit application entry point
- `instagram_analyzer.py`: Instagram profile analysis logic
- `content_generator.py`: AI-powered content plan generation
- `strategy_recommender.py`: Marketing strategy recommendations
- `data_visualizer.py`: Visualization components
- `models.py`: Database models
- `database.py`: Database configuration and operations

## Technologies Used

- Python
- Streamlit
- OpenAI API
- HikerAPI
- PostgreSQL
- SQLAlchemy
- Flask-Migrate
- Plotly

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the MIT License.
