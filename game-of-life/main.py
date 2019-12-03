
from tkinter import *
from tkinter import messagebox, filedialog
from PIL import Image as Img
from PIL import ImageTk, ImageDraw
import os
from gol import *


class FileManager:
    """Static class that loads and saves a board to a file, reports the result in a message."""

    def load(board: Board) -> bool:
        """Open a file dialog and read a board from a file."""

        file_name = filedialog.askopenfilename(
            initialdir = os.getcwd(), title = 'Select file', 
            filetypes = (('Text files','*.txt'),('All files','*.*'))
            )

        if not file_name:
            return False

        try:
            f = open(file_name,'r')
            contents = f.read()
            f.close()
        except OSError:
            messagebox.showinfo(message = 'Could not read the file ' + file_name + '.')
            return False
      
        if not board.read_from_string(contents):
            messagebox.showinfo(message = 'You have chosen wrong or a damaged file.')
            return False

        return True

    def save(board: Board) -> bool:
        """Open a file dialog and save a board to a file."""

        file_name = filedialog.asksaveasfilename(
            initialdir = os.getcwd(), title = 'Select file', 
            filetypes = (('Text files','*.txt'),('All files','*.*'))
            )

        if not file_name:
            return False

        try:
            f = open(file_name,'w+')
            f.write(board.save_to_string())
            f.close()
        except OSError:
            messagebox.showinfo(message = 'Could not write to the file ' + filename + '.')
            return False

        messagebox.showinfo(message = 'The board was successfully saved.')
        return True


class TkState:
    """Static class that can switch the state of tkinter widgets."""

    def enable(widget_list: list) -> None:
        """Enable all widgets in the widget list."""

        for widget in widget_list:
            widget.configure(state='normal')

    def disable(widget_list: list) -> None:
        """Disable all widgets in the widget list."""

        for widget in widget_list:
            widget.configure(state='disabled')


class Application:
    """Game of life application."""

    # CONSTRUCTION
    # region
    def __init__(self, master: Tk) -> None:
        """Initialize the application, create constants and GUI."""

        def create_window_constants() -> None:
            """Create constants used for the window and widgets."""

            self.WIDTH = 1000
            self.HEIGHT = 600

            self.WIDGET_PAD = 5         # Widget padding
            self.MAIN_BG = '#eeeeee'    # Main background

            self.FONT_LARGE = ('Courier',24)
            self.FONT_NORMAL = ('Courier', 12)
            self.FONT_SMALL = ('Courier', 10)

        def create_gol_constants() -> None:
            """Create constants for GOL objects."""

            self.INITIAL_RULE = 'B3/R23'
            self.INVALID_RULE_MESSAGE = (
                'Invalid rule.\n\n'
                'Set the rule in the format "Bx/Ry", where x and y are numbers of neighbors that:\n'
                'x: causes a birth of a cell\n'
                'y: allows a living cell to remain alive\n\n'
                'Numbers 0 and 9 cannot belong to x and y.'
                )

            self.BOARD_WIDTH = 1000
            self.BOARD_HEIGHT = 1000
            self.BOARD_BG = (0, 0, 0)
            self.BOARD_STROKE = (50, 50, 50)
            self.BOARD_FILL = (255, 255, 255)

            self.IMAGE_MAX_WIDTH = 2000
            self.IMAGE_MAX_HEIGHT = 2000
            self.CELL_SIZES = [3, 5, 10, 20, 30, 50]
            self.INITIAL_ZOOM = len(self.CELL_SIZES) // 2

            self.TIMES_PER_GEN = [3000, 2000, 1500, 1000, 700, 400, 200, 100, 50]
            self.INITIAL_TIME_PER_GEN = len(self.TIMES_PER_GEN) // 2

        def init_window(master: Tk) -> None:
            """Initialize the window."""

            master.geometry(str(self.WIDTH) + 'x' + str(self.HEIGHT))
            master.configure(background = self.MAIN_BG)

            master.bind('<Left>', self.on_left_key)
            master.bind('<Right>', self.on_right_key)
            master.bind('<Up>', self.on_up_key)
            master.bind('<Down>', self.on_down_key)
            master.bind('<KeyPress>', self.on_key_press)

        def init_gol_objects(master: Tk) -> None:
            """Create and initialize objects from GOL module."""

            self.rule = Rule('B','R','/')
            self.rule.try_set_rule(self.INITIAL_RULE)

            self.board = None           # Original (can be editted) - for reset
            self.anim_board = None      # Animated board

            self.painter = Painter()
            self.painter.reset(self.IMAGE_MAX_WIDTH, self.IMAGE_MAX_HEIGHT,
                               self.CELL_SIZES, self.BOARD_BG, self.BOARD_STROKE)
            self.painter.fill = self.BOARD_FILL
            self.painter.zoom = self.INITIAL_ZOOM
            self.painter.canvas = self.canvas

            self.animator = Animator(master)
            self.animator.painter = self.painter
            self.animator.time_per_gen = self.TIMES_PER_GEN[self.INITIAL_TIME_PER_GEN]
            self.animator.on_new_gen = self.on_new_generation

        self.master = master
        create_window_constants()
        create_gol_constants()

        init_window(master)
        self.create_top_frame(master)
        self.create_right_frame(master)
        self.create_left_frame(master)
        init_gol_objects(master)

        # Fixes toggle mode as add or remove mode
        self.edit_toggle_mode = None

    def create_top_frame(self, master: Tk) -> None:
        """Create the top frame (heading)."""

        top_frame = Frame(master, pady=4*self.WIDGET_PAD, bg=self.MAIN_BG)
        top_frame.pack(side=TOP, fill=X)

        heading = Label(top_frame, text="GAME OF LIFE", font=self.FONT_LARGE, bg=self.MAIN_BG)
        heading.pack()

    def create_right_frame(self, master: Tk) -> None:
        """Create the right frame (file, editting and settings menus) with the parent MASTER."""

        def create_file_menu(master: Widget) -> None:
            """Create the file menu with the parent MASTER."""

            file_menu = Frame(master, bg=self.MAIN_BG)
            file_menu.pack(side=TOP,fill=X)

            new_board_button = Button(file_menu, text='New board', font=self.FONT_NORMAL,
                                      command=self.on_new_board)
            new_board_button.pack(side=TOP, anchor=W, pady=self.WIDGET_PAD)

            open_button = Button(file_menu, text='Open', font=self.FONT_NORMAL,
                                 command=self.on_open)
            open_button.pack(side=LEFT, padx=(0,self.WIDGET_PAD), pady=(0,self.WIDGET_PAD))

            save_button = Button(file_menu, text='Save', font=self.FONT_NORMAL,
                                 command=self.on_save)
            save_button.pack(side=LEFT, pady=(0,self.WIDGET_PAD))

        def create_edit_menu(master: Widget) -> None:
            """Create the editing menu with the parent MASTER."""

            def create_mode_buttons(master: Widget, mode_var: IntVar) -> None:
                """Create mode buttons with the variable MODE_VAR and the parent MASTER."""

                add = Radiobutton(master, text='Add', font=self.FONT_NORMAL,
                                         variable=mode_var, value=0)
                remove = Radiobutton(master, text='Remove', font=self.FONT_NORMAL,
                                         variable=mode_var, value=1)
                toggle = Radiobutton(master, text='Toggle', font=self.FONT_NORMAL,
                                         variable=mode_var, value=2)

                add.pack(anchor=W, padx=self.WIDGET_PAD, pady=(self.WIDGET_PAD,0))
                remove.pack(anchor=W, padx=self.WIDGET_PAD, pady=(self.WIDGET_PAD,0))
                toggle.pack(anchor=W, padx=self.WIDGET_PAD, pady=self.WIDGET_PAD)

            self.edit_menu = LabelFrame(master, text='Editing', font=self.FONT_SMALL,
                                        bg=self.MAIN_BG)
            self.edit_menu.pack(side=TOP, fill=X, pady=self.WIDGET_PAD)

            self.edit_mode = IntVar()
            self.edit_mode.set(0)

            create_mode_buttons(self.edit_menu, self.edit_mode)

        def create_settings_menu(master: Widget) -> None:
            """Create settings menu with the parent MASTER."""

            def create_speed_widgets(master: Widget) -> None:
                """Create speed widgets with the parent MASTER."""

                speed_label = Label(master, text='Speed:', font=self.FONT_NORMAL, bg=self.MAIN_BG)
                speed_label.grid(row=0, column=0, sticky=W, padx=self.WIDGET_PAD, 
                                 pady=(self.WIDGET_PAD,0))

                self.speed_scale = Scale(
                    master, from_=0, to=len(self.TIMES_PER_GEN)-1, resolution=1, orient=HORIZONTAL,
                    bg=self.MAIN_BG, font=self.FONT_SMALL, command=self.on_speed_change)
                self.speed_scale.set(self.INITIAL_TIME_PER_GEN)
                self.speed_scale.grid(row=0, column=1, sticky=W+E, padx=(0,self.WIDGET_PAD),
                                      pady=(self.WIDGET_PAD,0))

            def create_zoom_widgets(master: Widget) -> None:
                """Create zoom widgets with the parent MASTER."""

                zoom_label = Label(master, text='Zoom:', font=self.FONT_NORMAL, bg=self.MAIN_BG)
                zoom_label.grid(row=1, column=0, sticky=W, padx=self.WIDGET_PAD,
                                pady=(0,self.WIDGET_PAD*2))

                self.zoom_scale = Scale(
                    master, from_=0, to=len(self.CELL_SIZES)-1, resolution=1, orient=HORIZONTAL,
                    bg=self.MAIN_BG, font=self.FONT_SMALL, command=self.on_zoom_change)
                self.zoom_scale.set(self.INITIAL_ZOOM)
                self.zoom_scale.grid(row=1, column=1 ,sticky=W+E, padx=(0,self.WIDGET_PAD),
                                     pady=(0,self.WIDGET_PAD*2))

            def create_rule_widgets(master: Widget) -> None:
                """Create rule widgets with the parent MASTER."""

                rule_label = Label(master, text='Rule:', font=self.FONT_NORMAL, bg=self.MAIN_BG)
                rule_label.grid(row=2, column=0, sticky=W, padx=self.WIDGET_PAD,
                                pady=(0,self.WIDGET_PAD))

                self.rule_entry = Entry(master, font=self.FONT_NORMAL)
                self.rule_entry.grid(row=2, column=1, sticky=W+E, padx=(0,self.WIDGET_PAD),
                                     pady=(0,self.WIDGET_PAD))
                self.rule_entry.insert(0, self.INITIAL_RULE)

                rule_button = Button(master, text='Set Rule', font=self.FONT_NORMAL, bg=self.MAIN_BG,
                                     command=self.on_set_rule)
                rule_button.grid(row=3, column=1, sticky=E, padx=(0,self.WIDGET_PAD),
                                 pady=(0,self.WIDGET_PAD))

            self.settings_menu = LabelFrame(master,text='Settings', font=self.FONT_SMALL,
                                            bg=self.MAIN_BG)
            self.settings_menu.pack(side=TOP, pady=self.WIDGET_PAD)

            create_speed_widgets(self.settings_menu)
            create_zoom_widgets(self.settings_menu)
            create_rule_widgets(self.settings_menu)

        right_frame = Frame(master, bg=self.MAIN_BG)
        right_frame.pack(side=RIGHT, fill=Y, padx = 20, pady=(0,20))

        create_file_menu(right_frame)
        create_settings_menu(right_frame)
        create_edit_menu(right_frame)
        TkState.disable(self.settings_menu.winfo_children())
        TkState.disable(self.edit_menu.winfo_children())

        quit_button = Button(right_frame, text='QUIT', fg='red', font=self.FONT_NORMAL,
                             command=master.destroy)
        quit_button.pack(side=BOTTOM, anchor=E, ipadx=20, ipady=10)

    def create_left_frame(self, master: Tk) -> None:
        """Create the left frame (animation menu, canvas) with the parent MASTER."""

        def create_animation_menu(master: Widget) -> None:
            """Create the animation menu with the parent MASTER."""

            def create_gen_labels(master: Widget) -> None:
                """Create generation labels with the parent MASTER."""

                gen_label = Label(master, text='Gen:', font=self.FONT_NORMAL, bg=self.MAIN_BG)
                gen_label.pack(side=LEFT)
                self.gen_number = Label(master, text=0, font=self.FONT_NORMAL, bg=self.MAIN_BG)
                self.gen_number.pack(side=LEFT)

            def create_rule_labels(master: Widget) -> None:
                """Create rule labels with the parent MASTER."""

                rule_label = Label(master, text='Rule:', font=self.FONT_NORMAL, bg=self.MAIN_BG)
                rule_label.pack(side=LEFT, padx=(50,0))
                self.rule_name = Label(master, text=self.INITIAL_RULE, font=self.FONT_NORMAL,
                                       bg=self.MAIN_BG)
                self.rule_name.pack(side=LEFT)

            def create_anim_buttons(master: Widget) -> None:
                """Create animation buttons with the parent MASTER."""

                reset_button = Button(master, text='Reset', font=self.FONT_NORMAL,
                                      command=self.on_reset)
                reset_button.pack(side=RIGHT)
                self.step_button = Button(master, text='Step', font=self.FONT_NORMAL,
                                          command=self.on_step)
                self.step_button.pack(side=RIGHT, padx=self.WIDGET_PAD)
                self.play_button = Button(master, text='Play', font=self.FONT_NORMAL,
                                          command=self.on_play)
                self.play_button.pack(side=RIGHT)

            animation_menu = Frame(master, bg=self.MAIN_BG, pady=self.WIDGET_PAD)
            animation_menu.pack(side=TOP, fill=X)

            create_gen_labels(animation_menu)
            create_rule_labels(animation_menu)
            create_anim_buttons(animation_menu)

        def create_board_canvas(master: Widget) -> None:
            """Create board canvas with the parent MASTER."""

            self.canvas = Canvas(master, bg='black')
            self.canvas.bind('<Configure>', self.on_canvas_resize)
            self.canvas.bind("<B1-Motion>", self.on_canvas_click)
            self.canvas.bind("<Button-1>", self.on_canvas_click)
            self.canvas.bind("<ButtonRelease-1>", self.on_canvas_mouse_release)
            self.canvas.pack(fill=BOTH, expand = TRUE)

        left_frame = Frame(master, bg=self.MAIN_BG)
        left_frame.pack(fill=BOTH, expand=TRUE, padx=20, pady=(0,20))

        create_animation_menu(left_frame)
        board_frame = Frame(left_frame)
        board_frame.pack(fill=BOTH, expand=TRUE)
        create_board_canvas(board_frame)
    # endregion

    # EVENTS
    # region
    def on_new_board(self) -> None:
        """Create new boards, initialize widgets."""

        self.stop_animation()

        self.board = self.empty_board()
        self.anim_board = self.empty_board()

        self.init_new_board()
        self.painter.draw_board()
   
    def on_open(self) -> None:
        """Load a board from a file using the FileManager."""

        self.stop_animation()
        self.anim_board = self.empty_board()
        
        if FileManager.load(self.anim_board):
            self.board = Board()
            self.board.copy(self.anim_board)

            self.init_new_board()
            self.painter.draw_board()

    def on_save(self) -> None:
        """Saves a board using FileManager."""

        if self.board == None:
            return

        self.on_reset()
        FileManager.save(self.board)

    def on_play(self) -> None:
        """Toggle the animation."""

        if self.board == None:
            return

        if self.animator.is_running:
            self.stop_animation()
        else:
            self.play_animation()

    def on_step(self) -> None:
        """Compute and draw a new generation."""

        if self.board == None:
            return

        TkState.disable(self.edit_menu.winfo_children())
        self.anim_board.next_gen()
        self.on_new_generation()
        self.painter.draw_board()

    def on_reset(self) -> None:
        """Reset the animation and the animation board."""

        if self.board == None:
            return
        
        self.stop_animation()
        self.anim_board.copy(self.board)
        self.gen_number.config(text = 0)
        TkState.enable(self.edit_menu.winfo_children())
        
        self.painter.draw_board()

    def on_new_generation(self) -> None:
        """Update the generation number."""

        self.gen_number.config(text = self.anim_board.generation)
  
    def on_speed_change(self, event) -> None:
        """Set the value from the speed scale as a new animation speed."""

        speed_level = int(self.speed_scale.get())
        self.animator.time_per_gen = self.TIMES_PER_GEN[speed_level]

    def on_zoom_change(self, event) -> None:
        """Sets the value from the zoom scale as a new zoom level."""

        zoom_level = int(self.zoom_scale.get())
        self.painter.zoom = zoom_level
        self.painter.draw_board()

    def on_key_press(self, event) -> None:
        """Zoom in or zoom out."""

        if self.master.focus_get() == self.rule_entry:
            return

        if event.char == "+":
            self.painter.zoom += 1
            self.zoom_scale.set(self.painter.zoom)
            # DO NOT draw a board here - will be drawn when changing zoom scale
        elif event.char == "-":
            self.painter.zoom -= 1
            self.zoom_scale.set(self.painter.zoom)

    def on_set_rule(self) -> None:
        """Try to set the text from the rule entry as a new rule."""

        self.stop_animation()
        self.master.focus()     # Move the cursor away from the rule entry
        rule_text = str(self.rule_entry.get())

        if not self.rule.try_set_rule(rule_text):
            messagebox.showinfo(message = self.INVALID_RULE_MESSAGE)
            return

        self.rule_name.configure(text = rule_text)

        self.board.birth_rule = self.rule.birth_rule
        self.board.remain_rule = self.rule.remain_rule
        self.anim_board.birth_rule = self.rule.birth_rule
        self.anim_board.remain_rule = self.rule.remain_rule

    def on_canvas_click(self, event) -> None:
        """Edit boards - add or remove a cell."""
        
        def edit_board(board: Board, mode: int, i: int, j: int) -> None:
            """Add or remove a cell at the position (i, j) depending on the current mode."""

            if mode == 0:
                board.add(i, j)
            elif mode == 1:
                board.remove(i, j)
            elif mode == 2:
                if self.edit_toggle_mode == "add":
                    board.add(i, j)
                elif self.edit_toggle_mode == "remove":
                    board.remove(i, j)
                else:
                    if board.is_alive(i, j):
                        self.edit_toggle_mode = "remove"
                        board.remove(i, j)
                    else:
                        self.edit_toggle_mode = "add"
                        board.add(i, j)

        if (self.board == None or
            self.anim_board.generation > 0 or
            self.animator.is_running):
            return

        i, j = self.painter.cell_index_from_coord(event.x, event.y)
        if i == -1 or j == -1:
            return

        mode = self.edit_mode.get()
        edit_board(self.anim_board, mode, i, j)
        edit_board(self.board, mode, i, j)

        self.painter.draw_board()
    
    def on_canvas_mouse_release(self, event) -> None:
        """Reset the current toggle mode."""

        self.edit_toggle_mode = None

    def on_canvas_resize(self, event) -> None:
        """Adjust the painter to the new size of the canvas."""

        self.painter.adjust_to_canvas()
        self.painter.draw_board()

    def on_left_key(self, event) -> None:
        """Move the view to the left."""

        self.move_view(-1, 0)

    def on_right_key(self, event) -> None:
        """Move the view to the right."""

        self.move_view(1, 0)

    def on_up_key(self, event) -> None:
        """Move the view up."""

        self.move_view(0, -1)

    def on_down_key(self, event) -> None:
        """Move the view down."""

        self.move_view(0, 1)
    # endregion

    def empty_board(self) -> Board:
        """Return an empty board with the initial size."""

        board = Board()
        board.birth_rule = self.rule.birth_rule
        board.remain_rule = self.rule.remain_rule
        board.empty_board(self.BOARD_HEIGHT, self.BOARD_WIDTH)

        return board

    def init_new_board(self) -> None:
        """Initialize the application after a new board was created."""

        TkState.enable(self.settings_menu.winfo_children())
        TkState.enable(self.edit_menu.winfo_children())

        self.gen_number.config(text = 0)
        self.speed_scale.set(self.INITIAL_TIME_PER_GEN)
        self.zoom_scale.set(self.INITIAL_ZOOM)

        self.animator.board = self.anim_board
        self.painter.board = self.anim_board
        self.painter.adjust_to_canvas()

    def play_animation(self) -> None:
        """Start the animation."""

        if self.board == None:
            return

        TkState.disable(self.edit_menu.winfo_children())
        TkState.disable([self.step_button])

        self.play_button.configure(text="Stop")
        self.animator.play()

    def stop_animation(self) -> None:
        """Pause the animation."""

        if self.board == None:
            return

        self.animator.stop()
        self.play_button.configure(text="Play")

        # If board has not been changed yet, enable editing
        if self.anim_board.generation == 0:
            TkState.enable(self.edit_menu.winfo_children())
        TkState.enable([self.step_button])

    def move_view(self, right: int, bottom: int) -> None:
        """Move the view of the board in the given direction."""

        focused = self.master.focus_get()
        if self.board == None or focused == self.rule_entry:
            return

        self.painter.move_view(right, bottom)
        self.painter.draw_board()
    

def main():
    root = Tk()
    root.title('Game of Life')
    app = Application(root)
    root.mainloop()

if __name__ == '__main__':
    main()
