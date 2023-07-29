import gradio as gr
import os
from modules import scripts
from modules import script_callbacks
from pathlib import Path
try:
    from send2trash import send2trash
    send2trash_installed = True
except ImportError:
    print("Delete_all Button: send2trash is not installed. recycle bin cannot be used.")
    send2trash_installed = False

delete_symbol = '清空当前输出目录'  # ❌
tab_current = None
image_files = []


def delete(filename):
    dir_path=[]
    tmpfilename=os.path.realpath(filename)
    file_list = os.listdir(os.path.dirname(tmpfilename))
    for file_name in file_list:
        file_path = os.path.dirname(tmpfilename) + '/' + file_name
        if os.path.isfile(file_path):
            os.unlink(file_path)
        print("Delete_all Button: %s deleted." %(file_name))
    return

def sdelb_delete(delete_info):
    for image_file in reversed(image_files):
        if os.path.exists(image_file):
            name = os.path.basename(image_file)
            if not name.startswith('grid-'):
                delete(image_file)
                tmpfilename=os.path.realpath(image_file)
                file_dir=os.path.dirname(image_file)
                delete_info = f"目录 {file_dir} 已全部清空"
                break
        delete_info = "Could not delete anything"
    delete_info = f"<b>{delete_info}</b>"

    return delete_info

class Script(scripts.Script):
    def title(self):
        return "Add delete button"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def process(self, p):
        global image_files
        image_files = []

def on_after_component(component, **kwargs):
    global tab_current, sdelb_delete_info
    element = kwargs.get("elem_id")
    if element == "extras_tab" and tab_current is not None:
        sdelb_delete_button = gr.Button(value=delete_symbol)
        sdelb_delete_button.click(
            fn=sdelb_delete,
            inputs=[sdelb_delete_info],
            outputs=[sdelb_delete_info],
            _js=tab_current + "_sdelb_addEventListener",
        )
        tab_current = None
    elif element in ["txt2img_gallery", "img2img_gallery"]:
        tab_current = element.split("_", 1)[0]
        with gr.Column():
            sdelb_delete_info = gr.HTML(elem_id=tab_current + "_sdelb_delete2_info")
script_callbacks.on_after_component(on_after_component)

def on_image_saved(params : script_callbacks.ImageSaveParams):
    global image_files
    image_files.append(os.path.realpath(params.filename))
    
script_callbacks.on_image_saved(on_image_saved)
