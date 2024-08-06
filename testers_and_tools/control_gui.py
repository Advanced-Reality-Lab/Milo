import tkinter as tk
from collections import defaultdict
import threading
import tkinter.filedialog
# from testers_and_tools.scripts import tts_google, generate_text, input_sentence_updater
# from service.edit_fl_bar_service import api,set_notifier




class ControlApp(tk.Frame):
    def __init__(self, master=None):
        super().__init__()
        self.menu = tk.Menu(self.master)
        self.file_menu = tk.Menu(self.menu)
        self.master = master
        self.create_menu()
        self.create_widgets()
        # self.input_updater = input_sentence_updater()
        self.pack()

    def create_menu(self):
        self.master.config(menu=self.menu)
        self.menu.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Open Conversation", command=self.open_conversation)
        self.file_menu.add_command(label="Save Conversation", command=self.save_conversation)

    def open_conversation(self):
        self.input_conversation.delete(1.0, tk.END)
        self.input_conversation.insert(tk.END, open(tkinter.filedialog.askopenfilename()).read())

    def save_conversation(self):
        open(tkinter.filedialog.asksaveasfilename(), 'w').write(self.input_conversation.get(1.0, tk.END))


    def create_widgets(self):
        self.prompt = tk.Label(self, text="Prompt:")
        self.prompt.pack(side="top")

        self.input_conversation = tk.Text(self, height=10, width=50)
        self.input_conversation.pack(side="top")

        self.output_result = tk.Text(self, height=10, width=50)
        self.output_result.pack(side="top")


        self.start_flask_services = tk.Button(self, text="Start Flask Services", fg="blue",
                                              command=self.start_flask_services)
        self.start_flask_services.pack(side="bottom")
        self.cat_output_to_input = tk.Button(self, text="Cat output to input", fg="blue",
                                          command=self.cat_output_to_input)
        self.cat_output_to_input.pack(side="bottom")
        self.generate_text = tk.Button(self, text="Generate text", fg="blue",
                                       command=self.generate_text)
        self.generate_text.pack(side="bottom")

        self.send_text_to_tts = tk.Button(self, text="Send text to TTS", fg="blue",
                                          command=self.send_text_to_tts)
        self.send_text_to_tts.pack(side="bottom")

        self.quit = tk.Button(self, text="QUIT", fg="red",
                              command=self.master.destroy)
        self.quit.pack(side="bottom")

    def generate_text(self):
        self.output_result.delete(1.0, tk.END)
        # self.output_result.insert(tk.END, generate_text(self.input_conversation.get(1.0, tk.END)[-1000:]))

    def cat_output_to_input(self):
        self.input_conversation.insert(tk.END, self.output_result.get(1.0, tk.END))

    def send_text_to_tts(self):
        pass
        # tts_google(self.output_result.get(1.0, tk.END))

    def start_flask_services(self):
        pass
        # threading.Thread(target=api.run, args=('0.0.0.0', 5000)).start()


if __name__ == '__main__':
    root = tk.Tk()
    app = ControlApp(master=root)
    app.mainloop()


