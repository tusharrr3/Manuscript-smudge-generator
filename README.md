# 📜 Ancient Manuscript Authenticator

A Streamlit web application that transforms modern, clean images of Devanagari or Sanskrit text into weathered, historical-looking documents by applying realistic ink smudges and aging effects.

## Features

- **PNG Image Upload**: Upload clean manuscript images
- **Organic Smudge Generation**: Creates realistic, irregular ink smudges with feathered edges
- **Customizable Parameters**:
  - Number of smudges (1-5)
  - Smudge intensity/opacity (0.1-1.0)
- **Randomized Placement**: Each processing generates unique smudge patterns
- **Side-by-Side Comparison**: View original and aged versions together
- **Download Capability**: Save processed manuscripts as PNG files

## Technical Details

### Smudge Generation
- Uses PIL (Python Imaging Library) for image manipulation
- Creates organic shapes through multiple overlapping ellipses
- Applies Gaussian blur for soft, feathered edges
- Adds texture noise for realistic appearance
- Uses sepia/brown tones for historical authenticity

### Overlay Technique
- Employs alpha compositing for realistic blending
- Semi-transparent smudges preserve text readability
- Overlay blend mode simulates ink absorption into paper

## Installation

1. Clone or download this repository
2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Start the Streamlit app:
   ```bash
   streamlit run app.py
   ```

2. Open your web browser (should open automatically)

3. Upload a PNG image containing text

4. Adjust the aging parameters in the sidebar:
   - **Number of Smudges**: How many ink spots to apply
   - **Smudge Intensity**: How dark/visible the smudges appear

5. Click "Apply Aging Effect"

6. Download your aged manuscript

## Tips

- **Subtle aging**: Use 1-2 smudges at 0.3-0.4 intensity
- **Heavy aging**: Use 4-5 smudges at 0.7-0.9 intensity
- **Variation**: Process the same image multiple times for different random smudge patterns
- **Test readability**: Ensure text remains 100% readable after processing

## Requirements

- Python 3.8+
- Streamlit 1.31.0+
- Pillow 10.2.0+
- NumPy 1.26.3+

## Project Structure

```
ancient_manuscript_app/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## How It Works

1. **Image Upload**: User uploads a clean PNG image
2. **Smudge Creation**: Algorithm generates organic, irregular shapes using random overlapping circles
3. **Edge Feathering**: Gaussian blur creates soft, natural-looking edges
4. **Color Selection**: Random sepia/brown tones for historical authenticity
5. **Placement**: Smudges positioned randomly while avoiding extreme edges
6. **Compositing**: Alpha blending overlays smudges while preserving text visibility
7. **Display & Download**: Shows comparison and allows saving the result

## Academic Use

Perfect for:
- Digital humanities projects
- Historical document recreation
- Educational materials about manuscript preservation
- Typography and design exploration
- Sanskrit/Devanagari text presentations

## License

This project is open source and available for educational and academic use.
