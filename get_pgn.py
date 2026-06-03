from PIL import Image
import os

def main():
    gif = Image.open("C:\\Users\\420\\OneDrive\\学习\\编程\\lazy-bear-desktop\\自嘲熊打字.gif")
    for frame in range(gif.n_frames):
        gif.seek(frame)
        gif.save(f"bear_frame_{frame}.png")

if __name__ == "__main__":
    main()