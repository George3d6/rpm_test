import shutil
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
import os
import raven_gen
from raven_gen import Matrix, MatrixType, Ruleset, RuleType
import numpy as np
import time
import json
from datetime import datetime


try:
    os.mkdir("test_results")
except:
    pass
np.random.seed(int(time.time()))

raven_gen.attribute.SIZE_MAX = 3
raven_gen.attribute.SIZE_MIN = 2

ruleset = Ruleset(size_rules=[RuleType.CONSTANT])
matrix_types = [
     MatrixType.FOUR_SHAPE_IN_SHAPE,
     MatrixType.NINE_SHAPE,
 ]

def crop(image_path, save_path):
    from PIL import Image
    image = Image.open(image_path)
    crop_size = (190, 190)

    original_size = image.size
    start_x = original_size[0] - crop_size[0]
    start_y = original_size[1] - crop_size[1]

    crop_box = (start_x, start_y, original_size[0], original_size[1])

    cropped_image = image.crop(crop_box)

    cropped_image.save(save_path)


def partial(image_path, save_path):
    from PIL import Image
    image = Image.open(image_path)
    crop_size = (190, 190)

    original_size = image.size
    start_x = original_size[0] - crop_size[0]
    start_y = original_size[1] - crop_size[1]

    crop_box = (start_x, start_y, original_size[0], original_size[1])

    draw = ImageDraw.Draw(image)
    draw.rectangle(crop_box, fill="white")

    image.save(save_path)

def gen_images(attempt=0):
    try:
        try:
            shutil.rmtree("test")
        except:
            pass
        os.mkdir("test")
        tp = f"test/"
        rpm = Matrix.make(np.random.choice(matrix_types),
                            ruleset=ruleset,
                            n_alternatives=5)
        rpm.save(tp,
                f"rpm",
                255,
                image_size=600,
                line_thickness=1,
                shape_border_thickness=1)
        for file in os.listdir(tp):
            crop(tp + file, tp + "crop_" + file)
        partial(tp + "rpm_answer.png", tp + "partial.png")
    except Exception as e:
        if attempt < 5:
            attempt += 1
            gen_images(attempt)
        else:
            raise e 


images, compare_images, correct_image = [], [], None
root = tk.Tk()
attempts = 0
rounds = 9
start_time = time.time()
photo_image = None
image_label = None
max_time = 60 * 5

def load_images():
    global images, compare_images, correct_image, image_label, photo_image
    images = []
    compare_images = []
    correct_image = None
    
    for i in range(5):
        image = Image.open(f"test/crop_rpm_alternative_{i}.png")
        compare_images.append(image)
    
    correct_image = Image.open(f"test/crop_rpm_answer.png")
    compare_images.append(correct_image)

    np.random.shuffle(compare_images)

    for image in compare_images:
        images.append(ImageTk.PhotoImage(image))

    image_path = "test/partial.png"
    pil_image = Image.open(image_path)
    photo_image = ImageTk.PhotoImage(pil_image)
    image_label = tk.Label(root, image=photo_image)
    image_label.grid(row=1, column=1)


def stop():
    global counter, attempts, root, start_time, max_time, rounds
    with open(f"test_results/res_{int(time.time())}_{datetime.now().hour}.json", "w") as fp:
        json.dump({
                    "correct": counter,
                    "attempts": attempts,
                    "max_rounds": rounds,
                    "used_time": time.time() - start_time,
                    "hour": datetime.now().hour,
                    "max_time": max_time,
                }, fp)
    shutil.rmtree("test")
    root.destroy()

def compare_to_ref(selected_image, buttons):
    global images, compare_images, correct_image, root, attempts, start_time, counter
    if selected_image.tobytes() == correct_image.tobytes():
        counter += 1
        counter_label.config(text=f"Matches: {counter}")
    
    attempts += 1
    rounds_label.config(text=f"Rounds: {attempts}")
        
    for widget in buttons:
        widget.destroy()
    image_label.destroy()
    
    if attempts >= rounds:
        stop()

    gen_images()
    load_images()
    create_image_buttons()

def create_image_buttons():
    global images, compare_images, correct_image, root
    buttons = []
    for i, image in enumerate(images):
        button = tk.Button(root, image=image, command=lambda i=i: compare_to_ref(compare_images[i], buttons))
        button.grid(row=6, column=2 + i)
        buttons.append(button)


def update_timer():
    global max_time
    elapsed_time = int(time.time() - start_time)
    timer_label.config(text=f"Time: {elapsed_time}/{max_time} s")
    root.after(1000, update_timer)
    if elapsed_time > max_time:
        stop()

root.title("Progressive Matrices")
gen_images()
load_images()

counter = 0
counter_label = tk.Label(root, text=f"Matches: {counter}")
counter_label.grid(row=7, column=2)

rounds_label = tk.Label(root, text=f"Rounds: {attempts}")
rounds_label.grid(row=7, column=3)

timer_label = tk.Label(root, text=f"Time: 0/{max_time} s")
timer_label.grid(row=7, column=4)

update_timer()

create_image_buttons()

root.mainloop()
