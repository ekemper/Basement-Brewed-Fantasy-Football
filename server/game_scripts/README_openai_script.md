# OpenAI Game Script Generator

This script generates fantasy football game scripts using OpenAI's chat completion endpoint for each game in the `game-sample.json` file.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up your OpenAI API key:**
   
   Create a `.env` file in the root directory and add your OpenAI API key
   
   Alternatively, you can set the environment variable directly:
   ```bash
   export OPENAI_API_KEY...
   ```

## Usage

Run the script from the root directory:

```bash
python openai_game_script_generator.py
```

## What it does

1. **Reads game data** from `game-sample.json`
2. **Loads the prompt template** from `game-script-generator-prompt.md`
3. **Processes each game** by calling OpenAI's chat completion endpoint
4. **Generates 4-5 sentence game scripts** following the fantasy football analysis framework
5. **Saves results** to `game_scripts_output.json`
6. **Displays results** in the console

## Output

The script creates a JSON file (`game_scripts_output.json`) containing:
- Total number of games processed
- Generation timestamp
- Individual results for each game with:
  - Game ID and matchup
  - Original game data
  - Generated script

## Features

- **Error handling** for missing files and API errors
- **Rate limiting protection** with 1-second delays between API calls
- **Cost optimization** using gpt-4o-mini model
- **Comprehensive logging** of progress and results
- **Structured output** in both JSON and console formats

## Requirements

- Python 3.7+
- OpenAI API key
- Internet connection for API calls

## Cost Considerations

The script uses the `gpt-4o-mini` model for cost efficiency. With 16 games in the sample file, expect minimal API costs (typically under $0.10 total).

## Troubleshooting

- **"OPENAI_API_KEY not set"**: Ensure your API key is properly configured in the .env file
- **"File not found"**: Make sure `game-sample.json` and `game-script-generator-prompt.md` are in the same directory
- **API errors**: Check your OpenAI account balance and API key validity 