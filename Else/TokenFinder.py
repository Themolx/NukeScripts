import nuke
import re

def get_path_tokens(path=None):
    if path is None:
        path = nuke.root().name()
    
    print(f"DEBUG: Analyzing path: {path}")
    
    # Define the regex pattern
    pattern = r'(?P<DISK>[A-Z]:)/(?P<PROJECT>\w+_\w+)/out/FILM/(?P<SEQUENCE>SQ\d+)/(?P<SHOT>SH\d+)/(?P<TASK>\w+)/render/(?P<VERSION>v\d+)/(?P<FILENAME>pp_FILM_(?P=SEQUENCE)_(?P=SHOT)_(?P=TASK)_(?P=VERSION)\.######\.exr)'
    
    # Try to match the pattern
    match = re.match(pattern, path)
    
    if match:
        tokens = match.groupdict()
        print("DEBUG: Extracted tokens:")
        for key, value in tokens.items():
            print(f"  {key}: {value}")
        return tokens
    else:
        print("DEBUG: Could not extract tokens from path")
        return None

# Test the function
if __name__ == "__main__":
    test_path = "Y:/20105_Pysna_film/out/FILM/SQ0530/SH0020/compositing_denoise/render/v005/pp_FILM_SQ0530_SH0020_compositing_denoise_v005.######.exr"
    tokens = get_path_tokens(test_path)
    if tokens:
        print("\nExtracted tokens:")
        for key, value in tokens.items():
            print(f"{key}: {value}")
    else:
        print("Failed to extract tokens")